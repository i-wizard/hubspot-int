from abc import ABC, abstractmethod

from src.schemas.contact_schema import ContactSchema
from src.schemas.deal_schema import DealSchema
from src.schemas.responses.hubspot_repository_response import (
    CreateOrUpdateContactResponse,
    CreateTicketResponse,
    CreateOrUpdateDealResponse,
    GetCrmObjectsResponse,
    GetContactIDByEmailResponse,
)
from src.schemas.ticket_schema import TicketSchema


class IRepository(ABC):
    @abstractmethod
    def create_or_update_contact(
        self, data: ContactSchema
    ) -> CreateOrUpdateContactResponse:
        pass

    @abstractmethod
    def create_or_update_deal(
        self, contact_id: str, data: DealSchema
    ) -> CreateOrUpdateDealResponse:
        pass

    @abstractmethod
    def create_ticket(
        self, contact_id: str, data: TicketSchema
    ) -> CreateTicketResponse:
        pass

    @abstractmethod
    def get_new_crm_objects(self, page: int, size: int, **kwargs) -> GetCrmObjectsResponse:
        pass

    @abstractmethod
    def get_contact_id_by_email(self, email: str) -> GetContactIDByEmailResponse:
        pass

