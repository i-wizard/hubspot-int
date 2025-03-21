import pdb
from datetime import datetime, timezone, timedelta

import pytest

from src.schemas.responses.hubspot_repository_response import GetCrmObjectsResponse


@pytest.fixture
def mock_get_new_crm_objects(mocker):
    return mocker.patch(
        "src.services.crm_service.CrmService.get_new_crm_objects"
    )


def test_get_crm_objects_default_start_date(client, mock_get_new_crm_objects):
    mock_response_data = {
        "contacts": [{"id": "1", "properties": {}}],
        "deals": [{"id": "2", "properties": {}}],
        "tickets": [{"id": "3", "properties": {}}],
    }

    mock_get_new_crm_objects.return_value = GetCrmObjectsResponse(
        success=True, data=mock_response_data
    ).data

    response = client.get("/api/v1/crm/objects?page=1&size=5")

    assert response.status_code == 200
    data = response.get_json()
    assert "contacts" in data
    assert "deals" in data
    assert "tickets" in data
    mock_get_new_crm_objects.assert_called_once()
    # _, kwargs = mock_get_new_crm_objects.call_args
    # assert isinstance(kwargs["start_date"], datetime)


def test_get_crm_objects_with_custom_start_date(client, mock_get_new_crm_objects):
    mock_response_data = {
        "contacts": [],
        "deals": [],
        "tickets": [],
    }

    mock_get_new_crm_objects.return_value = GetCrmObjectsResponse(
        success=True, data=mock_response_data
    ).data

    start_date = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    response = client.get(f"/api/v1/crm/objects?start_date={start_date}&page=1&size=2")

    assert response.status_code == 200
    data = response.get_json()
    assert data["contacts"] == []
    assert data["deals"] == []
    assert data["tickets"] == []
    mock_get_new_crm_objects.assert_called_once()
    _, kwargs = mock_get_new_crm_objects.call_args
    assert "start_date_str" in kwargs


def test_get_crm_objects_invalid_start_date(client):
    response = client.get("/api/v1/crm/objects?start_date=03-01-2024")

    assert response.status_code == 422

def test_get_crm_objects_pagination(client, mock_get_new_crm_objects):
    mock_get_new_crm_objects.return_value = GetCrmObjectsResponse(
        success=True, data={"contacts": [], "deals": [], "tickets": []}
    ).data

    response = client.get("/api/v1/crm/objects?page=2&size=20")
    assert response.status_code == 200
    mock_get_new_crm_objects.assert_called_once()

    args, kwargs = mock_get_new_crm_objects.call_args
    assert args[0] == 2
    assert args[1] == 20
