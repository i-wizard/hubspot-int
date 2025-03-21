from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class DealSchema(BaseModel, extra="allow"):
    class DealStages(str, Enum):
        appointmentscheduled = "appointmentscheduled"
        qualifiedtobuy = "qualifiedtobuy"
        presentationscheduled = "presentationscheduled"
        decisionmakerboughtin = "decisionmakerboughtin"
        contractsent = "contractsent"
        closedwon = "closedwon"
        closedlost = "closedlost"

    dealname: str
    amount: float
    dealstage: DealStages
    contact_email: Optional[str] = None
    contact_id: Optional[str] = None

    @field_validator("contact_email")
    def lowercase_email(cls, v):
        return v.lower() if isinstance(v, str) else v


class DealSchemaResponse(BaseModel, extra="allow"): ...
