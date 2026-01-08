from unittest.mock import MagicMock, patch
import pytest
from backend.services.llm import batch_generate_questions

@patch("backend.services.llm.call_llm_api")
def test_batch_generate_questions_success(mock_call_llm_api):
    # Mock LLM response
    mock_response = """
    [
        {
            "type": "single_choice",
            "content": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "answer": "4",
            "score": 5
        }
    ]
    """
    mock_call_llm_api.return_value = (True, mock_response)

    api_config = {"base_url": "http://test", "api_key": "test"}
    success, questions, error = batch_generate_questions("Math", "single_choice", "easy", 1, api_config)

    assert success is True
    assert len(questions) == 1
    assert questions[0]["content"] == "What is 2+2?"
    assert questions[0]["answer"] == "4"

@patch("backend.services.llm.call_llm_api")
def test_batch_generate_questions_failure(mock_call_llm_api):
    mock_call_llm_api.return_value = (False, "API Error")

    api_config = {"base_url": "http://test", "api_key": "test"}
    success, questions, error = batch_generate_questions("Math", "single_choice", "easy", 1, api_config)

    assert success is False
    assert len(questions) == 0
    assert error == "API Error"

@patch("backend.services.llm.call_llm_api")
def test_batch_generate_questions_invalid_json(mock_call_llm_api):
    mock_call_llm_api.return_value = (True, "Not JSON")

    api_config = {"base_url": "http://test", "api_key": "test"}
    success, questions, error = batch_generate_questions("Math", "single_choice", "easy", 1, api_config)

    assert success is False
    assert "Failed to parse JSON" in error
