from fastapi.testclient import TestClient 
from openai import RateLimitError
from unittest.mock import AsyncMock, patch, MagicMock 
from app.main import app 
import httpx
import pytest

client = TestClient(app)


def make_mock_response(data: dict):
    mock_res = MagicMock()

    mock_parsed = MagicMock()
    for key, value in data.items():
        setattr(mock_parsed, key, value)

    mock_choice = MagicMock()
    mock_choice.message.parsed = mock_parsed
    mock_res.choices = [mock_choice]

    return mock_res


@pytest.mark.asyncio
async def test_analyze_job_returns_correct_structure(): 
    mock_result = { "job_title": "Junior Python Developer", 
                   "match_score": 75, 
                   "seniority_level": "junior", 
                   "required_skills": [], 
                   "main_tech_stack": ["Python"], 
                   "red_flags": [], 
                   "recommendation": "Стоит откликнуться" 
                   } 
    with patch("app.services.analyzer.client.beta.chat.completions.parse", new_callable=AsyncMock) as mock_parse: 
        mock_parse.return_value = make_mock_response(mock_result) 
        response = client.post("/analyze-job", json={ "job_description": "Junior Python Developer needed" }) 
        assert response.status_code == 200 
        assert response.json()["match_score"] == 75


@pytest.mark.asyncio
async def test_analyze_job_rate_limit_returns_429():
    mock_response = httpx.Response(
        status_code=429,
        content=b'{"error": {"message": "Rate limit reached"}}',
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )

    rate_limit_error = RateLimitError(
        message="Rate limit reached", response=mock_response, body=None
    )

    path = "app.services.analyzer.client.beta.chat.completions.parse"

    with patch(path, new_callable=AsyncMock) as mock_parse:
        mock_parse.side_effect = rate_limit_error

        response = client.post(
            "/analyze-job",
            json={"job_description": "Python Dev", "your_skills": ["Python"]},
        )

        assert response.status_code == 429
        assert "too many requests" in response.json()["detail"]
