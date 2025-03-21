from datetime import datetime, timezone, timedelta

from flask import abort

from src.repositories import IRepository
from src.schemas.contact_schema import ContactSchema
from src.schemas.deal_schema import DealSchema
from src.schemas.ticket_schema import TicketSchema


class CrmService:
    def __init__(self, crm_repo: IRepository):
        self.crm_repo = crm_repo

    def create_or_update_contact(self, contact_data: ContactSchema) -> dict:
        response = self.crm_repo.create_or_update_contact(contact_data)
        if not response.success:
            abort(400, description=response.error or response.details)
        return response.data

    def create_or_update_deal(self, deal_data: DealSchema) -> dict:
        contact_id = deal_data.contact_id
        if not contact_id:
            contact_id_response = self.crm_repo.get_contact_id_by_email(
                deal_data.contact_email
            )
            deal_data.contact_email = None
            if not contact_id_response.success:
                abort(
                    400,
                    description=contact_id_response.error
                    or contact_id_response.details,
                )
            contact_id = contact_id_response.data["id"]
        deal_data.contact_id = None
        response = self.crm_repo.create_or_update_deal(contact_id, deal_data)
        if not response.success:
            abort(400, description=response.error or response.details)
        return response.data

    def create_ticket(self, ticket_data: TicketSchema) -> dict:
        contact_id = ticket_data.contact_id
        if not contact_id:
            contact_id_response = self.crm_repo.get_contact_id_by_email(
                ticket_data.contact_email
            )
            ticket_data.contact_email = None
            if not contact_id_response.success:
                abort(
                    400,
                    description=contact_id_response.error
                    or contact_id_response.details,
                )
            contact_id = contact_id_response.data["id"]
        ticket_data.contact_id = None
        response = self.crm_repo.create_ticket(contact_id, ticket_data)
        if not response.success:
            abort(400, description=response.error or response.details)
        return response.data

    def get_new_crm_objects(self, page: int, size: int, start_date_str: str) -> dict:
        try:
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str)
            else:
                start_date = datetime.now(timezone.utc) - timedelta(days=7)
        except ValueError:
            abort(
                422,
                description="Invalid start_date format. Use ISO 8601 (e.g., 2024-03-01T00:00:00)",
            )
        response = self.crm_repo.get_new_crm_objects(page, size, start_date=start_date)
        if not response.success:
            abort(400, description=response.error or response.details)
        return response.data
