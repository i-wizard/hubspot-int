from pydantic import BaseModel, EmailStr, field_validator


class ContactSchema(BaseModel, extra="allow"):
    email: EmailStr
    firstname: str
    lastname: str
    phone: str

    @field_validator("email")
    def lowercase_email(cls, v):
        return v.lower() if isinstance(v, str) else v


class ContactSchemaResponse(BaseModel, extra="allow"):
    ...