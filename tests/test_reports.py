"""
Tests for /reports endpoints.

The generate-report endpoint creates a real PDF via fpdf2, so we verify
the file is written to disk and clean up afterwards.
"""
import os
import glob
import pytest

REPORTS_DIR = "static/reports"


# ─── POST /reports/generate-report ───────────────────────────────────────────

class TestGenerateReport:
    """Tests for PDF report generation."""

    @pytest.fixture(autouse=True)
    def _ensure_reports_dir(self):
        """Make sure the reports directory exists before each test and clean
        up generated PDFs after each test."""
        os.makedirs(REPORTS_DIR, exist_ok=True)
        yield
        # Teardown: remove any PDFs generated during this test
        for pdf in glob.glob(os.path.join(REPORTS_DIR, "*_report.pdf")):
            try:
                os.remove(pdf)
            except OSError:
                pass

    def test_generate_report_returns_success(self, client):
        resp = client.post(
            "/reports/generate-report",
            json={
                "city_name": "Delhi",
                "data_summary": {
                    "temperature": "38°C",
                    "risk": "High",
                    "hotspots": "3",
                },
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["city_name"] == "Delhi"
        assert body["message"] == "Report generated successfully."

    def test_generate_report_has_report_url(self, client):
        """The response should include a report_url pointing to the PDF."""
        resp = client.post(
            "/reports/generate-report",
            json={
                "city_name": "Mumbai",
                "data_summary": {"risk": "Extreme"},
            },
        )
        body = resp.json()
        assert "report_url" in body
        assert body["report_url"] == "/static/reports/mumbai_report.pdf"

    def test_generate_report_creates_pdf_file(self, client):
        """The PDF file should actually exist on disk after the call."""
        client.post(
            "/reports/generate-report",
            json={
                "city_name": "Bangalore",
                "data_summary": {"temperature": "34°C"},
            },
        )
        expected_path = os.path.join(REPORTS_DIR, "bangalore_report.pdf")
        assert os.path.isfile(expected_path)

    def test_generate_report_pdf_not_empty(self, client):
        """Generated PDF should have non-zero size."""
        client.post(
            "/reports/generate-report",
            json={
                "city_name": "Chennai",
                "data_summary": {"risk": "Medium"},
            },
        )
        path = os.path.join(REPORTS_DIR, "chennai_report.pdf")
        assert os.path.getsize(path) > 0

    def test_generate_report_city_with_spaces(self, client):
        """City names with spaces should be lowercased + underscore-joined."""
        resp = client.post(
            "/reports/generate-report",
            json={
                "city_name": "New York",
                "data_summary": {"temperature": "30°C"},
            },
        )
        body = resp.json()
        assert body["report_url"] == "/static/reports/new_york_report.pdf"
        assert os.path.isfile(
            os.path.join(REPORTS_DIR, "new_york_report.pdf")
        )

    def test_generate_report_multiple_data_summary_keys(self, client):
        """Multiple data_summary keys should all appear in the PDF
        (we just verify the endpoint doesn't crash)."""
        resp = client.post(
            "/reports/generate-report",
            json={
                "city_name": "Pune",
                "data_summary": {
                    "temperature": "32°C",
                    "risk": "Medium",
                    "hotspots": "3",
                    "recommendation": "Plant trees",
                },
            },
        )
        assert resp.status_code == 200

    def test_generate_report_empty_data_summary(self, client):
        """An empty data_summary dict should still produce a valid report."""
        resp = client.post(
            "/reports/generate-report",
            json={
                "city_name": "Empty",
                "data_summary": {},
            },
        )
        assert resp.status_code == 200
        assert os.path.isfile(
            os.path.join(REPORTS_DIR, "empty_report.pdf")
        )

    def test_generate_report_overwrites_existing(self, client):
        """Calling the endpoint twice for the same city should not error."""
        payload = {
            "city_name": "Overwrite",
            "data_summary": {"risk": "Low"},
        }
        resp1 = client.post("/reports/generate-report", json=payload)
        resp2 = client.post("/reports/generate-report", json=payload)
        assert resp1.status_code == 200
        assert resp2.status_code == 200
