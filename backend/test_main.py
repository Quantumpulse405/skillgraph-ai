import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app

client = TestClient(app)

def test_analyze_endpoint_missing_api_key():
    with patch.dict("os.environ", clear=True):
        response = client.post(
            "/analyze",
            json={"resume_text": "Python developer", "job_description_text": "Looking for Python dev"}
        )
        assert response.status_code == 500
        assert "GEMINI_API_KEY environment variable not set" in response.json()["detail"]

@patch("backend.main.genai.GenerativeModel")
def test_analyze_endpoint_success(mock_model_class):
    mock_model_instance = MagicMock()
    mock_response = MagicMock()

    mock_json_response = {
        "skills": ["Python"],
        "missing_skills": ["Docker"],
        "readiness_score": 80,
        "roadmap": ["Learn Docker"]
    }
    mock_response.text = json.dumps(mock_json_response)
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model_instance

    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake-api-key"}):
        response = client.post(
            "/analyze",
            json={"resume_text": "Python developer", "job_description_text": "Looking for Python dev"}
        )

        assert response.status_code == 200
        assert response.json() == mock_json_response

@patch("backend.main.genai.GenerativeModel")
def test_analyze_endpoint_invalid_json(mock_model_class):
    mock_model_instance = MagicMock()
    mock_response = MagicMock()

    mock_response.text = "invalid json"
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model_instance

    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake-api-key"}):
        response = client.post(
            "/analyze",
            json={"resume_text": "Python developer", "job_description_text": "Looking for Python dev"}
        )

        assert response.status_code == 500
        assert "Failed to parse JSON" in response.json()["detail"]
