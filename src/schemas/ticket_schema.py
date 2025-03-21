from enum import Enum

from pydantic import BaseModel, Field, Extra
from typing import List, Optional


class TicketSchema(BaseModel, extra="allow"):
    class Category(str, Enum):
        general_inquiry = "general_inquiry"
        technical_issue = "technical_issue"
        billing = "billing"
        service_request = "service_request"
        meeting = "meeting"

    class Priority(str, Enum):
        low = "LOW"
        medium = "MEDIUM"
        high = "HIGH"
        urgent = "URGENT"

    class PipelineStage(int, Enum):
        one = 1
        two = 2
        three = 3
        four = 4

    subject: str
    description: str
    category: Category
    pipeline: str
    hs_ticket_priority: Priority
    hs_pipeline_stage: PipelineStage
    contact_email: Optional[str] = None
    contact_id: Optional[str] = None
    deal_ids: List[str]


class TicketSchemaResponse(BaseModel, extra="allow"): ...
