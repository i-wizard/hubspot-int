import pytest
from src.schemas.responses.hubspot_repository_response import (
    CreateOrUpdateContactResponse,
)


@pytest.fixture
def mock_hubspot_repo(mocker):
    mock_repo = mocker.patch(
        "src.repositories.hubspot_repository.HubSpotRepository.create_or_update_contact"
    )
    return mock_repo


# ---------------------- Test Cases ----------------------


def test_create_contact_success(client, mock_hubspot_repo):
    payload = {
        "email": "test@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "phone": "+234796753422",
    }

    mock_hubspot_repo.return_value = CreateOrUpdateContactResponse(
        **{"success": True, "data": {"id": "12345", "properties": payload}}
    )

    response = client.post("/api/v1/crm/contacts", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert "id" in data
    assert data["id"] == mock_hubspot_repo.return_value.data["id"]
    assert "properties" in data
    assert data["properties"]["email"] == payload["email"]
    assert data["properties"]["firstname"] == payload["firstname"]
    assert data["properties"]["lastname"] == payload["lastname"]
    assert data["properties"]["phone"] == payload["phone"]
    mock_hubspot_repo.assert_called_once()


@pytest.mark.parametrize("missing_field", ["email", "firstname", "lastname", "phone"])
def test_create_contact_missing_fields(client, missing_field):
    payload = {
        "email": "test@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "phone": "123-456-7890",
    }
    payload.pop(missing_field)

    response = client.post("/api/v1/crm/contacts", json=payload)

    assert response.status_code == 422
    data = response.get_json()
    assert "details" in data and "error" in data
    assert data["details"][0]["loc"][0] == missing_field


def test_create_contact_invalid_email(client):
    payload = {
        "email": "invalid-email",
        "firstname": "John",
        "lastname": "Doe",
        "phone": "123-456-7890",
    }

    response = client.post("/api/v1/crm/contacts", json=payload)

    assert response.status_code == 422
    data = response.get_json()
    assert data["details"][0]["input"] == "invalid-email"


def test_create_contact_invalid_phone_type(client):
    payload = {
        "email": "test@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "phone": 1234567890,  # Should be a string
    }

    response = client.post("/api/v1/crm/contacts", json=payload)

    assert response.status_code == 422
    data = response.get_json()
    assert data["details"][0]["msg"] == "Input should be a valid string"
    assert data["details"][0]["loc"][0] == "phone"


#


def test_create_contact_hubspot_failure(client, mock_hubspot_repo):
    payload = {
        "email": "test@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "phone": "123-456-7890",
    }

    mock_hubspot_repo.return_value = CreateOrUpdateContactResponse(
        **{"success": False, "details": "Invalid API Key"}
    )

    response = client.post("/api/v1/crm/contacts", json=payload)

    assert response.status_code == 400
    data = response.get_json()

    assert mock_hubspot_repo.return_value.details in data["message"]
    assert "error" in data
