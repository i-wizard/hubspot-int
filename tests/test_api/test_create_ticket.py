import pytest
from src.schemas.responses.hubspot_repository_response import CreateTicketResponse


@pytest.fixture
def mock_create_ticket_repo(mocker):
    mock_repo = mocker.patch(
        "src.repositories.hubspot_repository.HubSpotRepository.create_ticket"
    )
    return mock_repo


# ---------------------- Test Cases ----------------------
def sample_data():
    return {
        "subject": "seventh Ticket",
        "description": "Create first ticket",
        "category": "general_inquiry",
        "pipeline": "start",
        "hs_ticket_priority": "LOW",
        "hs_pipeline_stage": 4,
        "deal_ids": ["34903331605"],
        "contact_id": "107645451131",
    }


def test_create_ticket_success(client, mock_create_ticket_repo):
    payload = sample_data()

    mock_create_ticket_repo.return_value = CreateTicketResponse(
        success=True, data={"id": "ticket123", "properties": payload}
    )

    response = client.post("/api/v1/crm/tickets", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == mock_create_ticket_repo.return_value.data["id"]
    assert data["properties"]["subject"] == payload["subject"]
    assert data["properties"]["description"] == payload["description"]
    assert data["properties"]["category"] == payload["category"]
    assert data["properties"]["pipeline"] == payload["pipeline"]
    mock_create_ticket_repo.assert_called_once()


@pytest.mark.parametrize(
    "missing_field",
    ["subject", "category", "pipeline", "hs_ticket_priority", "hs_pipeline_stage"],
)
def test_create_ticket_missing_fields(client, missing_field):
    payload = sample_data()
    payload.pop(missing_field)

    response = client.post("/api/v1/crm/tickets", json=payload)

    assert response.status_code == 422
    data = response.get_json()
    assert "details" in data and "error" in data
    assert data["details"][0]["loc"][0] == missing_field


def test_create_ticket_invalid_deal_ids_type(client):
    payload = sample_data()
    payload["deal_ids"] = "string_value"

    response = client.post("/api/v1/crm/tickets", json=payload)

    assert response.status_code == 422
    data = response.get_json()
    assert "Input should be a valid list" in data["details"][0]["msg"]
    assert data["details"][0]["loc"][0] == "deal_ids"


def test_create_ticket_hubspot_failure(client, mock_create_ticket_repo):
    payload = sample_data()

    mock_create_ticket_repo.return_value = CreateTicketResponse(
        success=False, details="Invalid API Key"
    )

    response = client.post("/api/v1/crm/tickets", json=payload)

    assert response.status_code == 400
    data = response.get_json()
    assert mock_create_ticket_repo.return_value.details in data["message"]
    assert "error" in data
