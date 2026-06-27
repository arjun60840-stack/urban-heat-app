"""
Tests for /interventions endpoints.

No external calls are made by these endpoints — they are pure logic — so
mocking is only needed for logger calls (which we skip).
"""
import pytest


# ─── POST /interventions/recommendations ─────────────────────────────────────

class TestRecommendations:
    """Verify the recommendation engine returns the correct strategies
    for each risk category."""

    def test_extreme_risk_returns_cool_roofs_and_water_bodies(self, client):
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "Delhi", "risk_category": "Extreme"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["city_name"] == "Delhi"
        recs = body["recommendations"]
        assert len(recs) == 2
        types = [r["type"] for r in recs]
        assert "Cool Roofs" in types
        assert "Water Bodies" in types

    def test_extreme_risk_cool_roofs_details(self, client):
        """Cool Roofs entry should have expected impact and cooling effect."""
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "X", "risk_category": "Extreme"},
        )
        cool_roofs = resp.json()["recommendations"][0]
        assert cool_roofs["type"] == "Cool Roofs"
        assert cool_roofs["impact"] == "High"
        assert cool_roofs["cooling_effect_celsius"] == 1.5

    def test_extreme_risk_water_bodies_details(self, client):
        """Water Bodies entry should have expected cooling effect."""
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "X", "risk_category": "Extreme"},
        )
        water = resp.json()["recommendations"][1]
        assert water["type"] == "Water Bodies"
        assert water["cooling_effect_celsius"] == 2.0

    def test_high_risk_returns_tree_plantation_and_green_roofs(self, client):
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "Mumbai", "risk_category": "High"},
        )
        assert resp.status_code == 200
        body = resp.json()
        recs = body["recommendations"]
        assert len(recs) == 2
        types = [r["type"] for r in recs]
        assert "Tree Plantation" in types
        assert "Green Roofs" in types

    def test_high_risk_tree_plantation_details(self, client):
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "X", "risk_category": "High"},
        )
        tree = resp.json()["recommendations"][0]
        assert tree["type"] == "Tree Plantation"
        assert tree["impact"] == "Medium-High"
        assert tree["cooling_effect_celsius"] == 1.2

    def test_high_risk_green_roofs_details(self, client):
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "X", "risk_category": "High"},
        )
        green = resp.json()["recommendations"][1]
        assert green["type"] == "Green Roofs"
        assert green["impact"] == "Medium"
        assert green["cooling_effect_celsius"] == 0.8

    def test_medium_risk_returns_urban_parks_and_tree_plantation(self, client):
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "Pune", "risk_category": "Medium"},
        )
        assert resp.status_code == 200
        types = [r["type"] for r in resp.json()["recommendations"]]
        assert "Urban Parks" in types
        assert "Tree Plantation" in types

    def test_low_risk_also_returns_urban_parks_and_tree_plantation(self, client):
        """Low and Medium fall into the same 'else' branch."""
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "Ooty", "risk_category": "Low"},
        )
        assert resp.status_code == 200
        types = [r["type"] for r in resp.json()["recommendations"]]
        assert "Urban Parks" in types
        assert "Tree Plantation" in types

    def test_medium_risk_urban_parks_details(self, client):
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "X", "risk_category": "Medium"},
        )
        parks = resp.json()["recommendations"][0]
        assert parks["type"] == "Urban Parks"
        assert parks["cooling_effect_celsius"] == 1.0

    def test_medium_risk_tree_plantation_details(self, client):
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "X", "risk_category": "Medium"},
        )
        tree = resp.json()["recommendations"][1]
        assert tree["type"] == "Tree Plantation"
        assert tree["impact"] == "Low"
        assert tree["cooling_effect_celsius"] == 0.5

    def test_unknown_risk_falls_into_else_branch(self, client):
        """Any unrecognised risk category should hit the else branch."""
        resp = client.post(
            "/interventions/recommendations",
            json={"city_name": "X", "risk_category": "SuperHot"},
        )
        assert resp.status_code == 200
        types = [r["type"] for r in resp.json()["recommendations"]]
        assert "Urban Parks" in types


# ─── POST /interventions/simulate ────────────────────────────────────────────

class TestSimulate:
    """Verify the simulation math:
        temp_reduction = (trees_added × 0.001) + (cool_roofs_area × 0.0005)
        improvement_score = min(100, int(temp_reduction × 20))
    """

    def test_simulate_basic_calculation(self, client):
        """trees=1000, roofs=2000 → reduction = 1.0 + 1.0 = 2.0"""
        resp = client.post(
            "/interventions/simulate",
            json={
                "city_name": "Delhi",
                "trees_added": 1000,
                "cool_roofs_area": 2000.0,
                "new_water_bodies": 0,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["city_name"] == "Delhi"
        assert body["predicted_temp_reduction_celsius"] == pytest.approx(2.0)
        assert body["improvement_score"] == 40  # min(100, int(2.0 * 20))

    def test_simulate_zero_inputs(self, client):
        """All zeroes → 0.0 reduction, 0 improvement."""
        resp = client.post(
            "/interventions/simulate",
            json={
                "city_name": "TestCity",
                "trees_added": 0,
                "cool_roofs_area": 0.0,
                "new_water_bodies": 0,
            },
        )
        body = resp.json()
        assert body["predicted_temp_reduction_celsius"] == 0.0
        assert body["improvement_score"] == 0

    def test_simulate_only_trees(self, client):
        """500 trees → 0.5°C reduction."""
        resp = client.post(
            "/interventions/simulate",
            json={
                "city_name": "A",
                "trees_added": 500,
                "cool_roofs_area": 0.0,
            },
        )
        assert resp.json()["predicted_temp_reduction_celsius"] == pytest.approx(0.5)

    def test_simulate_only_cool_roofs(self, client):
        """4000 sqm cool roofs → 2.0°C reduction."""
        resp = client.post(
            "/interventions/simulate",
            json={
                "city_name": "B",
                "trees_added": 0,
                "cool_roofs_area": 4000.0,
            },
        )
        assert resp.json()["predicted_temp_reduction_celsius"] == pytest.approx(2.0)

    def test_simulate_improvement_score_capped_at_100(self, client):
        """Very large inputs should cap improvement_score at 100."""
        resp = client.post(
            "/interventions/simulate",
            json={
                "city_name": "Huge",
                "trees_added": 100_000,
                "cool_roofs_area": 100_000.0,
            },
        )
        body = resp.json()
        assert body["improvement_score"] == 100

    def test_simulate_rounding(self, client):
        """Verify the result is rounded to 2 decimal places."""
        resp = client.post(
            "/interventions/simulate",
            json={
                "city_name": "R",
                "trees_added": 123,
                "cool_roofs_area": 456.0,
            },
        )
        reduction = resp.json()["predicted_temp_reduction_celsius"]
        # (123 * 0.001) + (456 * 0.0005) = 0.123 + 0.228 = 0.351 → round to 0.35
        assert reduction == pytest.approx(0.35)

    def test_simulate_water_bodies_ignored_in_formula(self, client):
        """new_water_bodies is accepted but doesn't affect calculation yet."""
        resp1 = client.post(
            "/interventions/simulate",
            json={
                "city_name": "X",
                "trees_added": 100,
                "cool_roofs_area": 100.0,
                "new_water_bodies": 0,
            },
        )
        resp2 = client.post(
            "/interventions/simulate",
            json={
                "city_name": "X",
                "trees_added": 100,
                "cool_roofs_area": 100.0,
                "new_water_bodies": 50,
            },
        )
        assert (
            resp1.json()["predicted_temp_reduction_celsius"]
            == resp2.json()["predicted_temp_reduction_celsius"]
        )
