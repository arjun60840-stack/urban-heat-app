"""
Tests for /analysis endpoints and the calculate_risk helper.

All external HTTP calls (geocoding, weather) are mocked so tests are fast,
deterministic, and offline-safe.
"""
import pytest
from unittest.mock import patch, MagicMock

from backend.routers.analysis import calculate_risk


# ─── Direct unit tests for calculate_risk ────────────────────────────────────

class TestCalculateRisk:
    """Verify the four risk-level boundaries."""

    def test_calculate_risk_low_below_30(self):
        assert calculate_risk(25.0) == "Low"

    def test_calculate_risk_low_boundary_29_9(self):
        assert calculate_risk(29.9) == "Low"

    def test_calculate_risk_medium_at_30(self):
        assert calculate_risk(30.0) == "Medium"

    def test_calculate_risk_medium_at_34_9(self):
        assert calculate_risk(34.9) == "Medium"

    def test_calculate_risk_high_at_35(self):
        assert calculate_risk(35.0) == "High"

    def test_calculate_risk_high_at_39_9(self):
        assert calculate_risk(39.9) == "High"

    def test_calculate_risk_extreme_at_40(self):
        assert calculate_risk(40.0) == "Extreme"

    def test_calculate_risk_extreme_above_40(self):
        assert calculate_risk(50.0) == "Extreme"


# ─── Helpers to build mock HTTP responses ────────────────────────────────────

def _mock_geocode_response(lat: float = 28.6139, lon: float = 77.2090):
    """Return a mock requests.Response for the geocoding API."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "results": [{"latitude": lat, "longitude": lon}]
    }
    return resp


def _mock_weather_response(temperature: float = 37.5):
    """Return a mock requests.Response for the weather API."""
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "current_weather": {"temperature": temperature}
    }
    return resp


# ─── POST /analysis/analyze-city ─────────────────────────────────────────────

class TestAnalyzeCity:
    """Integration tests for the analyze-city endpoint."""

    @patch("backend.routers.analysis.requests.get")
    def test_analyze_city_success(self, mock_get, client):
        """Geocode + weather succeed → record saved, correct risk returned."""
        mock_get.side_effect = [
            _mock_geocode_response(28.6139, 77.2090),
            _mock_weather_response(37.5),
        ]

        resp = client.post(
            "/analysis/analyze-city",
            json={"city_name": "Delhi"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        data = body["data"]
        assert data["city_name"] == "Delhi"
        assert data["avg_temperature"] == 37.5
        assert data["risk_category"] == "High"
        assert data["latitude"] == pytest.approx(28.6139)
        assert data["longitude"] == pytest.approx(77.2090)

    @patch("backend.routers.analysis.requests.get")
    def test_analyze_city_geocode_failure_uses_fallback(self, mock_get, client):
        """When geocoding fails, the endpoint falls back to NYC coords."""
        geocode_resp = MagicMock()
        geocode_resp.status_code = 200
        geocode_resp.json.return_value = {"results": []}  # empty results

        mock_get.side_effect = [
            geocode_resp,
            _mock_weather_response(32.0),
        ]

        resp = client.post(
            "/analysis/analyze-city",
            json={"city_name": "UnknownCity"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["latitude"] == pytest.approx(40.7128)
        assert body["data"]["longitude"] == pytest.approx(-74.0060)

    @patch("backend.routers.analysis.requests.get")
    def test_analyze_city_extreme_temperature(self, mock_get, client):
        """A temperature ≥ 40 should produce 'Extreme' risk."""
        mock_get.side_effect = [
            _mock_geocode_response(),
            _mock_weather_response(45.0),
        ]

        resp = client.post(
            "/analysis/analyze-city",
            json={"city_name": "Phoenix"},
        )

        assert resp.status_code == 200
        assert resp.json()["data"]["risk_category"] == "Extreme"

    @patch("backend.routers.analysis.requests.get")
    def test_analyze_city_saves_to_database(self, mock_get, client, db_session):
        """The endpoint should persist the analysis to the database."""
        mock_get.side_effect = [
            _mock_geocode_response(),
            _mock_weather_response(33.0),
        ]

        resp = client.post(
            "/analysis/analyze-city",
            json={"city_name": "TestCity"},
        )

        assert resp.status_code == 200
        # Verify the record was stored
        from backend.models import CityAnalysis
        row = db_session.query(CityAnalysis).filter_by(city_name="TestCity").first()
        assert row is not None
        assert row.avg_temperature == 33.0
        assert row.risk_category == "Medium"


# ─── GET /analysis/heat-map ──────────────────────────────────────────────────

class TestHeatMap:
    """Tests for the heat-map endpoint."""

    @patch("backend.routers.analysis.requests.get")
    def test_heat_map_returns_30_points(self, mock_get, client):
        """The endpoint should always return exactly 30 heatmap data points."""
        mock_get.side_effect = [
            _mock_geocode_response(12.97, 77.59),
            _mock_weather_response(35.0),
        ]

        resp = client.get("/analysis/heat-map?city_name=Bangalore")

        assert resp.status_code == 200
        body = resp.json()
        assert body["city_name"] == "Bangalore"
        assert len(body["heatmap_data"]) == 30

    @patch("backend.routers.analysis.requests.get")
    def test_heat_map_points_have_required_keys(self, mock_get, client):
        """Each data point must contain lat, lon, and intensity."""
        mock_get.side_effect = [
            _mock_geocode_response(),
            _mock_weather_response(35.0),
        ]

        resp = client.get("/analysis/heat-map?city_name=TestCity")

        assert resp.status_code == 200
        for point in resp.json()["heatmap_data"]:
            assert "lat" in point
            assert "lon" in point
            assert "intensity" in point
            assert 0.0 <= point["intensity"] <= 1.0

    @patch("backend.routers.analysis.requests.get")
    def test_heat_map_geocode_failure_uses_nyc_fallback(self, mock_get, client):
        """If geocoding fails, points should cluster around NYC coords."""
        geocode_resp = MagicMock()
        geocode_resp.status_code = 500  # server error
        mock_get.side_effect = [
            geocode_resp,
            _mock_weather_response(30.0),
        ]

        resp = client.get("/analysis/heat-map?city_name=Nowhere")

        assert resp.status_code == 200
        points = resp.json()["heatmap_data"]
        # Points should be near 40.7128, -74.006  (within ±0.06 offset)
        for p in points:
            assert 40.65 < p["lat"] < 40.78
            assert -74.07 < p["lon"] < -73.94


# ─── GET /analysis/hotspots ──────────────────────────────────────────────────

class TestHotspots:
    """Tests for the hotspots endpoint."""

    @patch("backend.routers.analysis.requests.get")
    def test_hotspots_returns_three_items(self, mock_get, client):
        """The response should always contain exactly 3 hotspots."""
        mock_get.side_effect = [
            _mock_geocode_response(),
            _mock_weather_response(36.0),
        ]

        resp = client.get("/analysis/hotspots?city_name=Mumbai")

        assert resp.status_code == 200
        body = resp.json()
        assert len(body["hotspots"]) == 3

    @patch("backend.routers.analysis.requests.get")
    def test_hotspots_contains_base_temperature_and_risk(self, mock_get, client):
        """The response must include base_temperature and overall_risk."""
        mock_get.side_effect = [
            _mock_geocode_response(),
            _mock_weather_response(36.0),
        ]

        resp = client.get("/analysis/hotspots?city_name=Mumbai")

        body = resp.json()
        assert body["base_temperature"] == 36.0
        assert body["overall_risk"] == "High"  # 36 → High

    @patch("backend.routers.analysis.requests.get")
    def test_hotspots_downtown_is_hotter(self, mock_get, client):
        """Downtown Concrete Core should be base+3.2°C."""
        mock_get.side_effect = [
            _mock_geocode_response(),
            _mock_weather_response(34.0),
        ]

        resp = client.get("/analysis/hotspots?city_name=CityX")

        body = resp.json()
        downtown = body["hotspots"][0]
        assert downtown["name"] == "Downtown Concrete Core"
        assert downtown["estimated_temp"] == pytest.approx(37.2)

    @patch("backend.routers.analysis.requests.get")
    def test_hotspots_residential_is_cooler(self, mock_get, client):
        """Residential Suburbs should be base−1.5°C."""
        mock_get.side_effect = [
            _mock_geocode_response(),
            _mock_weather_response(34.0),
        ]

        resp = client.get("/analysis/hotspots?city_name=CityX")

        body = resp.json()
        residential = body["hotspots"][2]
        assert residential["name"] == "Residential Suburbs"
        assert residential["estimated_temp"] == pytest.approx(32.5)

    @patch("backend.routers.analysis.requests.get")
    def test_hotspots_risk_levels_are_consistent(self, mock_get, client):
        """Each hotspot's risk must match calculate_risk(its temp)."""
        mock_get.side_effect = [
            _mock_geocode_response(),
            _mock_weather_response(38.0),
        ]

        resp = client.get("/analysis/hotspots?city_name=CityY")

        for hs in resp.json()["hotspots"]:
            assert hs["risk"] == calculate_risk(hs["estimated_temp"])
