import pytest
from src.schemas.responses.hubspot_repository_response import (
    CreateOrUpdateDealResponse,
)


@pytest.fixture
def mock_create_deal_repo(mocker):
    mock_repo = mocker.patch(
        "src.repositories.hubspot_repository.HubSpotRepository.create_or_update_deal"
    )
    return mock_repo


# ---------------------- Test Cases ----------------------


def test_create_deal_success(client, mock_create_deal_repo):
    payload = {
        "dealname": "Test Deal",
        "amount": 5000.0,
        "contact_id": "12345",
        "dealstage":"appointmentscheduled"
    }

    mock_create_deal_repo.return_value = CreateOrUpdateDealResponse(
        success=True, data={"id": "deal123", "properties": payload}
    )

    response = client.post("/api/v1/crm/deals", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == mock_create_deal_repo.return_value.data["id"]
    assert data["properties"]["dealname"] == payload["dealname"]
    assert data["properties"]["amount"] == payload["amount"]
    assert data["properties"]["contact_id"] == payload["contact_id"]
    mock_create_deal_repo.assert_called_once()


@pytest.mark.parametrize("missing_field", ["dealname", "amount", "dealstage"])
def test_create_deal_missing_fields(client, missing_field):
    payload = {
        "dealname": "Test Deal",
        "amount": 5000.0,
        "dealstage": "appointmentscheduled",
    }
    payload.pop(missing_field)

    response = client.post("/api/v1/crm/deals", json=payload)

    assert response.status_code == 422
    data = response.get_json()
    assert "details" in data and "error" in data
    assert data["details"][0]["loc"][0] == missing_field


def test_create_deal_invalid_amount_type(client):
    payload = {
        "dealname": "Test Deal",
        "amount": "five thousand",  # Invalid type, should be float
        "contact_id": "12345",
    }

    response = client.post("/api/v1/crm/deals", json=payload)

    assert response.status_code == 422
    data = response.get_json()
    assert "Input should be a valid number"
