import traceback
from datetime import timezone, datetime
from typing import Dict, Any, List, Union

import requests
from requests import RequestException

from src.config import logger
from src.repositories import IRepository
from src.schemas.contact_schema import ContactSchema
from src.schemas.deal_schema import DealSchema
from src.schemas.responses.hubspot_repository_response import (
    CreateOrUpdateContactResponse,
    CreateOrUpdateDealResponse,
    CreateTicketResponse,
    GetCrmObjectsResponse,
    GetContactIDByEmailResponse,
)
from src.schemas.ticket_schema import TicketSchema
from src.services.interfaces.token_interface import ITokenService


class HubSpotRepository(IRepository):
    BASE_URL = "https://api.hubapi.com"

    def __init__(self, token_service: ITokenService):
        self.token_service = token_service

    def _get_headers(self) -> Dict[str, str]:
        access_token = self.token_service.get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def create_or_update_contact(
        self, contact_data: ContactSchema
    ) -> CreateOrUpdateContactResponse:
        url = f"{self.BASE_URL}/crm/v3/objects/contacts"
        headers = self._get_headers()

        properties = contact_data.model_dump()
        # Use Hubspot's upsert  technique
        params = {"idProperty": "email"}
        payload = {"properties": properties}

        try:
            response = requests.post(url, headers=headers, json=payload, params=params)
            response_data = response.json()
        except (RequestException, ValueError) as e:
            logger.error(
                "Error creating/updating contact}",
                context={"error": e, "trace": traceback.format_exc()},
            )
            return CreateOrUpdateContactResponse(
                success=False,
                error="Failed to create or update contact in HubSpot.",
                details=str(e),
            )
        else:
            if response.ok:
                return CreateOrUpdateContactResponse(success=True, data=response_data)
            else:
                return CreateOrUpdateContactResponse(
                    success=False, details=response_data.get("errors")
                )

    def create_or_update_deal(
        self, contact_id: str, deal_data: DealSchema
    ) -> CreateOrUpdateDealResponse:
        url = f"{self.BASE_URL}/crm/v3/objects/deals"
        headers = self._get_headers()
        deal_dict = deal_data.model_dump(exclude_none=True)
        associations = [
            {
                "to": {"id": contact_id},
                "types": [
                    {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}
                ],
            }
        ]

        payload = {"properties": deal_dict, "associations": associations}

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 409:
                deal_id = self._get_deal_id_by_name(deal_data.dealname, headers)
                if deal_id:
                    response = self._update_deal(url, deal_id, headers, deal_dict)
            response_data = response.json()
        except (RequestException, ValueError) as e:
            logger.error(
                "Error creating/updating deal}",
                context={"error": e, "trace": traceback.format_exc()},
            )
            return CreateOrUpdateDealResponse(
                success=False,
                error="Failed to create or update contact in HubSpot.",
                details=str(e),
            )
        if response.ok:
            return CreateOrUpdateDealResponse(success=True, data=response_data)
        return CreateOrUpdateDealResponse(success=False, details=response_data)

    @staticmethod
    def _update_deal(url: str, deal_id: str, headers: dict, deal_dict: dict):
        update_url = f"{url}/{deal_id}"
        update_payload = {"properties": deal_dict}
        update_response = requests.patch(
            update_url, headers=headers, json=update_payload
        )
        update_response.raise_for_status()
        return update_response

    def create_ticket(
        self, contact_id: str, ticket_data: TicketSchema
    ) -> CreateTicketResponse:
        url = f"{self.BASE_URL}/crm/v3/objects/tickets"
        headers = self._get_headers()

        ticket_dict = ticket_data.model_dump(exclude_none=True)
        deal_ids = ticket_dict.pop("deal_ids")

        associations = [
            {
                "to": {"id": contact_id},
                "types": [
                    {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 16}
                ],
            }
        ]
        for deal_id in deal_ids:
            associations.append(
                {
                    "to": {"id": deal_id},
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 28,
                        }
                    ],
                }
            )

        payload = {"properties": ticket_dict, "associations": associations}
        try:
            response = requests.post(url, headers=headers, json=payload)
        except (RequestException, ValueError) as e:
            logger.error(
                "Error creating deal",
                context={"error": e, "trace": traceback.format_exc()},
            )
            return CreateTicketResponse(
                success=False,
                error="Error creating deal",
                details=str(e),
            )
        if response.ok:
            return CreateTicketResponse(success=True, data=response.json())
        return CreateTicketResponse(success=False, details=response.json())

    def get_new_crm_objects(
        self, page: int, size: int, start_date: datetime = None
    ) -> GetCrmObjectsResponse:
        headers = self._get_headers()
        objects = {"contacts": [], "deals": [], "tickets": []}

        try:
            # 1. Fetch contacts
            contacts = self._get_paginated_objects("contacts", page, size, headers)[
                "results"
            ]

            contact_ids = []
            associated_deals = []

            # 2. For each contact, fetch associated deals
            for contact in contacts:
                contact_id = contact.get("id")
                contact_ids.append(contact_id)

                associated_deal_refs = self._get_associated_objects(
                    from_id=contact_id,
                    from_object_type="contacts",
                    to_object_type="deals",
                    headers=headers,
                )

                # Fetch full deal details
                for deal_ref in associated_deal_refs:
                    deal_detail = self._get_single_object(
                        object_type="deals",
                        object_id=deal_ref["id"],
                        headers=headers,
                    )
                    if deal_detail:
                        associated_deals.append(deal_detail)

            # 4. Fetch tickets (paginated) — optionally, filter by recent creation time
            if start_date:
                tickets = self._get_tickets_with_created_filter(
                    start_date=start_date, headers=headers
                )
            else:
                tickets = tickets = self._get_paginated_objects(
                    "tickets", page, size, headers
                )

            # Final structure
            objects["contacts"] = contacts
            objects["deals"] = associated_deals
            objects["tickets"] = tickets

        except (RequestException, ValueError) as e:
            logger.error(
                "Error retrieving CRM objects",
                context={"error": e, "trace": traceback.format_exc()},
            )
            return GetCrmObjectsResponse(
                success=False,
                error="Error retrieving CRM objects",
                details=str(e),
            )

        return GetCrmObjectsResponse(success=True, data=objects)

    def _get_associated_objects(
        self,
        from_id: str,
        from_object_type: str,
        to_object_type: str,
        headers: dict,
    ) -> list[dict]:
        """
        Retrieves associated objects of a specific type for a given object.
        Example: Get deals linked to a contact.
        """
        url = f"{self.BASE_URL}/crm/v3/objects/{from_object_type}/{from_id}/associations/{to_object_type}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except (RequestException, ValueError) as e:
            logger.error(
                f"Error retrieving associated {to_object_type} for {from_object_type} {from_id}",
                context={"error": e, "trace": traceback.format_exc()},
            )
            return []

        results = response.json().get("results", [])
        # Extract associated object IDs
        associated_objects = [{"id": assoc["id"]} for assoc in results]
        return associated_objects

    def _get_single_object(
        self,
        object_type: str,
        object_id: str,
        headers: dict,
    ) -> Union[dict, None]:
        """
        Retrieves a single CRM object by type and ID.
        Example: Fetch deal details by ID.
        """
        url = f"{self.BASE_URL}/crm/v3/objects/{object_type}/{object_id}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except (RequestException, ValueError) as e:
            logger.error(
                f"Error retrieving {object_type} with ID {object_id}",
                context={"error": e, "trace": traceback.format_exc()},
            )
            return None

        return response.json()

    def _get_tickets_with_created_filter(
        self, start_date: datetime, headers: dict
    ) -> List[dict]:
        url = f"{self.BASE_URL}/crm/v3/objects/tickets/search"
        headers.update({"Content-Type": "application/json"})

        start_date_iso = start_date.astimezone(timezone.utc).isoformat()

        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "createdate",
                            "operator": "GTE",
                            "value": start_date_iso,
                        }
                    ]
                }
            ],
            "properties": ["subject", "content", "hs_pipeline", "createdate"],
            "limit": 100,
        }

        results = []
        after = None
        while True:
            if after:
                payload["after"] = after
            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                results.extend(data.get("results", []))
                after = data.get("paging", {}).get("next", {}).get("after")
                if not after:
                    break
            except (RequestException, ValueError) as e:
                logger.error(
                    "Error fetching filtered tickets",
                    context={"error": e, "trace": traceback.format_exc()},
                )
                break
        return results

    def _get_paginated_objects(
        self, object_type: str, page: int, size: int, headers: Dict[str, str]
    ) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/crm/v3/objects/{object_type}"
        params = {"limit": size, "after": (page - 1) * size}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_contact_id_by_email(self, email: str) -> GetContactIDByEmailResponse:
        url = f"{self.BASE_URL}/crm/v3/objects/contacts/search"
        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {"propertyName": "email", "operator": "EQ", "value": email}
                    ]
                }
            ],
            "properties": ["email"],
            "limit": 1,
        }
        try:
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])
            contact_id = results[0]["id"]
        except (RequestException, ValueError) as e:
            logger.error(
                "Error getting contact ID using email",
                context={"error": e, "trace": traceback.format_exc()},
            )
            return GetContactIDByEmailResponse(
                success=False,
                error="Error creating/updating deal",
                details=str(e),
            )
        return GetContactIDByEmailResponse(success=True, data={"id": contact_id})

    def _get_deal_id_by_name(self, dealname: str, headers: Dict[str, str]) -> str:
        url = f"{self.BASE_URL}/crm/v3/objects/deals/search"
        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "dealname",
                            "operator": "EQ",
                            "value": dealname,
                        }
                    ]
                }
            ],
            "properties": ["dealname"],
            "limit": 1,
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        return results[0]["id"] if results else None
