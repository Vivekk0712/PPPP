"""
Unit tests for Planner Agent
Run with: pytest test_planner.py
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app, ProjectPlan, parse_gemini_response, build_gemini_prompt

client = TestClient(app)


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["agent"] == "planner"


def test_project_plan_validation():
    """Test ProjectPlan model validation"""
    valid_plan = {
        "name": "Test Project",
        "task_type": "image_classification",
        "framework": "pytorch",
        "dataset_source": "kaggle",
        "search_keywords": ["test", "dataset"],
        "preferred_model": "resnet18",
        "target_metric": "accuracy",
        "target_value": 0.9,
        "max_dataset_size_gb": 50
    }
    
    plan = ProjectPlan(**valid_plan)
    assert plan.name == "Test Project"
    assert plan.framework == "pytorch"
    assert len(plan.search_keywords) == 2


def test_parse_gemini_response_clean_json():
    """Test parsing clean JSON response"""
    json_str = '{"name": "Test", "search_keywords": ["test"]}'
    result = parse_gemini_response(json_str)
    assert result["name"] == "Test"


def test_parse_gemini_response_with_markdown():
    """Test parsing JSON wrapped in markdown"""
    json_str = '```json\n{"name": "Test", "search_keywords": ["test"]}\n```'
    result = parse_gemini_response(json_str)
    assert result["name"] == "Test"


def test_parse_gemini_response_invalid():
    """Test parsing invalid JSON"""
    with pytest.raises(ValueError):
        parse_gemini_response("not valid json")


def test_build_gemini_prompt():
    """Test prompt building"""
    prompt = build_gemini_prompt("Train a model for cats vs dogs")
    assert "cats vs dogs" in prompt
    assert "JSON" in prompt
    assert "search_keywords" in prompt


@patch('main.supabase')
@patch('main.model')
def test_handle_message_success(mock_model, mock_supabase):
    """Test successful message handling"""
    # Mock Gemini response
    mock_response = Mock()
    mock_response.text = '''{
        "name": "Cat Dog Classifier",
        "task_type": "image_classification",
        "framework": "pytorch",
        "dataset_source": "kaggle",
        "search_keywords": ["cats", "dogs"],
        "preferred_model": "resnet18",
        "target_metric": "accuracy",
        "target_value": 0.9,
        "max_dataset_size_gb": 50
    }'''
    mock_model.generate_content.return_value = mock_response
    
    # Mock Supabase insert
    mock_insert_result = Mock()
    mock_insert_result.data = [{"id": "test-project-id"}]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert_result
    
    # Test request
    response = client.post(
        "/agents/planner/handle_message",
        json={
            "user_id": "test-user",
            "session_id": "test-session",
            "message_text": "Train a model for cats vs dogs"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["project_id"] == "test-project-id"
    assert "Cat Dog Classifier" in data["plan"]["name"]


@patch('main.model')
def test_handle_message_gemini_error(mock_model):
    """Test handling Gemini API errors"""
    mock_model.generate_content.side_effect = Exception("API Error")
    
    response = client.post(
        "/agents/planner/handle_message",
        json={
            "user_id": "test-user",
            "session_id": "test-session",
            "message_text": "Train a model"
        }
    )
    
    assert response.status_code == 503


@patch('main.supabase')
def test_get_project_success(mock_supabase):
    """Test getting project by ID"""
    mock_result = Mock()
    mock_result.data = [{
        "id": "test-id",
        "name": "Test Project",
        "status": "pending_dataset"
    }]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
    
    response = client.get("/agents/planner/project/test-id")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"


@patch('main.supabase')
def test_get_project_not_found(mock_supabase):
    """Test getting non-existent project"""
    mock_result = Mock()
    mock_result.data = []
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
    
    response = client.get("/agents/planner/project/nonexistent")
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
