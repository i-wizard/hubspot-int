import pytest
from unittest.mock import patch

import requests

from src.repositories.hubspot_repository import HubSpotRepository
from src.schemas.contact_schema import ContactSchema
from src.schemas.deal_schema import DealSchema
from src.schemas.ticket_schema import TicketSchema
from src.services.interfaces.token_interface import ITokenService


# Dummy token service mock
class DummyTokenService(ITokenService):
    def refresh_access_token(self) -> None:
        pass

    def get_access_token(self):
        return "dummy_token"


@pytest.fixture
def repo():
    return HubSpotRepository(token_service=DummyTokenService())


@pytest.fixture
def contact_data():
    return ContactSchema(
        email="test@example.com",
        firstname="Test",
        lastname="User",
        phone="+234780963532",
    )


@pytest.fixture
def deal_data():
    return DealSchema(
        dealname="Test Deal",
        amount=1000,
        dealstage=DealSchema.DealStages.appointmentscheduled,
        contact_id="10764545113100",
    )


@pytest.fixture
def ticket_data():
    return TicketSchema(
        subject="Test Ticket",
        description="Test content",
        category=TicketSchema.Category.meeting,
        hs_ticket_priority=TicketSchema.Priority.high,
        hs_pipeline_stage=TicketSchema.PipelineStage.two,
        deal_ids=["deal1"],
        contact_id="10764545113100",
        pipeline="start",
    )


# ---------------------------
# Test create_or_update_contact
# ---------------------------
@patch("src.repositories.hubspot_repository.requests.post")
def test_create_or_update_contact_success(mock_post, repo, contact_data):
    mock_post.return_value.ok = True
    mock_post.return_value.json.return_value = {"id": "contact123"}

    response = repo.create_or_update_contact(contact_data)

    assert response.success is True
    assert response.data == {"id": "contact123"}
    mock_post.assert_called_once()


@patch("src.repositories.hubspot_repository.requests.post")
def test_create_or_update_contact_failure(mock_post, repo, contact_data):
    mock_post.side_effect = requests.RequestException("API Error")

    response = repo.create_or_update_contact(contact_data)

    assert response.success is False
    assert "Failed to create or update contact" in response.error
    mock_post.assert_called_once()


# ---------------------------
# Test create_or_update_deal
# ---------------------------
@patch("src.repositories.hubspot_repository.requests.post")
@patch("src.repositories.hubspot_repository.requests.patch")
def test_create_or_update_deal_success(mock_patch, mock_post, repo, deal_data):
    mock_post.return_value.status_code = 200
    mock_post.return_value.ok = True
    mock_post.return_value.json.return_value = {"id": "deal123"}

    response = repo.create_or_update_deal("contact123", deal_data)

    assert response.success is True
    assert response.data == {"id": "deal123"}
    mock_post.assert_called_once()
    mock_patch.assert_not_called()


@patch("src.repositories.hubspot_repository.requests.post")
@patch("src.repositories.hubspot_repository.requests.patch")
def test_create_or_update_deal_conflict_then_update(
    mock_patch, mock_post, repo, deal_data
):
    # Simulate 409 conflict
    mock_post.return_value.status_code = 409
    mock_post.return_value.json.return_value = {"message": "Conflict"}

    # Mock internal _get_deal_id_by_name and patch response
    with patch.object(repo, "_get_deal_id_by_name", return_value="deal456"):
        mock_patch.return_value.ok = True
        mock_patch.return_value.json.return_value = {"id": "deal456"}

        response = repo.create_or_update_deal("contact123", deal_data)

        assert response.success is True
        assert response.data == {"id": "deal456"}


@patch("src.repositories.hubspot_repository.requests.post")
def test_create_or_update_deal_failure(mock_post, repo, deal_data):
    mock_post.side_effect = requests.RequestException("API Error")

    response = repo.create_or_update_deal("contact123", deal_data)

    assert response.success is False
    assert "Failed to create or update contact" in response.error
    mock_post.assert_called_once()


# ---------------------------
# Test create_ticket
# ---------------------------
@patch("src.repositories.hubspot_repository.requests.post")
def test_create_ticket_success(mock_post, repo, ticket_data):
    mock_post.return_value.ok = True
    mock_post.return_value.json.return_value = {"id": "ticket123"}

    response = repo.create_ticket("contact123", ticket_data)

    assert response.success is True
    assert response.data == {"id": "ticket123"}
    mock_post.assert_called_once()


@patch("src.repositories.hubspot_repository.requests.post")
def test_create_ticket_failure(mock_post, repo, ticket_data):
    mock_post.side_effect = requests.RequestException("API Error")

    response = repo.create_ticket("contact123", ticket_data)

    assert response.success is False
    assert "Error creating deal" in response.error
    mock_post.assert_called_once()
