"""
Tests for /ai endpoints (predict & chat).

- The predict endpoint uses random but is tested structurally.
- The chat endpoint is tested with GROQ_API_KEY absent (fallback) and present
  (mocked Groq client).
"""
import os
import pytest
from unittest.mock import patch, MagicMock


# ─── POST /ai/predict ────────────────────────────────────────────────────────

class TestPredict:
    """Tests for the future-heat prediction endpoint."""

    def test_predict_single_month(self, client):
        """months_ahead=1 → forecast list with 1 entry."""
        resp = client.post(
            "/ai/predict",
            json={"city_name": "Delhi", "months_ahead": 1},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["city_name"] == "Delhi"
        assert len(body["forecast"]) == 1

    def test_predict_twelve_months(self, client):
        """months_ahead=12 → forecast list with 12 entries."""
        resp = client.post(
            "/ai/predict",
            json={"city_name": "Mumbai", "months_ahead": 12},
        )
        body = resp.json()
        assert len(body["forecast"]) == 12

    def test_predict_default_months_ahead(self, client):
        """When months_ahead is omitted, schema defaults to 1."""
        resp = client.post(
            "/ai/predict",
            json={"city_name": "Pune"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["forecast"]) == 1

    def test_predict_month_names_are_correct(self, client):
        """First 12 entries should cycle through Jan→Dec."""
        expected = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]
        resp = client.post(
            "/ai/predict",
            json={"city_name": "X", "months_ahead": 12},
        )
        months = [e["month"] for e in resp.json()["forecast"]]
        assert months == expected

    def test_predict_month_names_cycle_after_12(self, client):
        """Month 13 should wrap back to Jan."""
        resp = client.post(
            "/ai/predict",
            json={"city_name": "X", "months_ahead": 13},
        )
        forecasts = resp.json()["forecast"]
        assert forecasts[0]["month"] == "Jan"
        assert forecasts[12]["month"] == "Jan"

    def test_predict_entries_have_predicted_avg_temp(self, client):
        """Every forecast entry must have a numeric predicted_avg_temp."""
        resp = client.post(
            "/ai/predict",
            json={"city_name": "X", "months_ahead": 6},
        )
        for entry in resp.json()["forecast"]:
            assert "predicted_avg_temp" in entry
            assert isinstance(entry["predicted_avg_temp"], (int, float))

    def test_predict_zero_months(self, client):
        """months_ahead=0 → empty forecast list (edge case)."""
        resp = client.post(
            "/ai/predict",
            json={"city_name": "X", "months_ahead": 0},
        )
        assert resp.status_code == 200
        assert resp.json()["forecast"] == []


# ─── POST /ai/chat — Fallback (no GROQ_API_KEY) ─────────────────────────────

class TestChatFallback:
    """When GROQ_API_KEY is missing or set to the placeholder, the endpoint
    should return a mock-mode response."""

    def test_chat_without_groq_key_returns_mock_response(self, client):
        """No GROQ_API_KEY → mock mode message."""
        # conftest.py already pops GROQ_API_KEY, but be explicit:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GROQ_API_KEY", None)

            resp = client.post(
                "/ai/chat",
                json={"message": "How to reduce heat?"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert "Mock Mode" in body["response"]
        assert "How to reduce heat?" in body["response"]

    def test_chat_with_placeholder_key_returns_mock_response(self, client):
        """GROQ_API_KEY='your_groq_api_key_here' is treated as missing."""
        with patch.dict(os.environ, {"GROQ_API_KEY": "your_groq_api_key_here"}):
            resp = client.post(
                "/ai/chat",
                json={"message": "Suggest parks"},
            )

        assert resp.status_code == 200
        assert "Mock Mode" in resp.json()["response"]

    def test_chat_fallback_includes_user_message(self, client):
        """The fallback response must echo the user's original message."""
        os.environ.pop("GROQ_API_KEY", None)
        resp = client.post(
            "/ai/chat",
            json={"message": "What is UHI?"},
        )
        assert "What is UHI?" in resp.json()["response"]

    def test_chat_with_context(self, client):
        """Supplying context should not break the fallback path."""
        os.environ.pop("GROQ_API_KEY", None)
        resp = client.post(
            "/ai/chat",
            json={
                "message": "Tell me more",
                "context": {"city": "Mumbai", "risk": "High"},
            },
        )
        assert resp.status_code == 200
        assert "Tell me more" in resp.json()["response"]


# ─── POST /ai/chat — With mocked Groq client ────────────────────────────────

class TestChatWithGroq:
    """When GROQ_API_KEY is set to a real-looking key, the endpoint should
    call the Groq API.  We mock it to avoid actual network calls."""

    @patch("groq.Groq")
    def test_chat_returns_mocked_ai_response(self, MockGroqClass, client):
        """Successful Groq call → response contains the model's text."""
        # Set up the mock chain: Groq() → client → .chat.completions.create()
        mock_message = MagicMock()
        mock_message.content = "Plant more trees to lower urban heat."

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        MockGroqClass.return_value = mock_client

        with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_real_key_here"}):
            resp = client.post(
                "/ai/chat",
                json={"message": "How to reduce urban heat?"},
            )

        assert resp.status_code == 200
        assert resp.json()["response"] == "Plant more trees to lower urban heat."

    @patch("groq.Groq")
    def test_chat_groq_api_error_returns_fallback(self, MockGroqClass, client):
        """If the Groq API raises an exception, the endpoint returns a
        fallback error message instead of crashing."""
        MockGroqClass.return_value.chat.completions.create.side_effect = (
            RuntimeError("API quota exceeded")
        )

        with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_real_key_here"}):
            resp = client.post(
                "/ai/chat",
                json={"message": "Hello"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert "Fallback" in body["response"]
        assert "Hello" in body["response"]

    @patch("groq.Groq")
    def test_chat_groq_called_with_correct_model(self, MockGroqClass, client):
        """The endpoint should request the llama-3.1-8b-instant model."""
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "ok"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        MockGroqClass.return_value = mock_client

        with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_real_key_here"}):
            client.post("/ai/chat", json={"message": "test"})

        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "llama-3.1-8b-instant"
        assert call_kwargs.kwargs["temperature"] == 0.7
        assert call_kwargs.kwargs["max_tokens"] == 150
