from pydantic import BaseModel, EmailStr, Field, PastDatetime


# validation Schemas

class ContactValidationSchema(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    phone_number: int
    birth_date: PastDatetime
    rest: str


class ContactValidationSchemaResponse(ContactValidationSchema):
    id: int = 1

    class Config:
        from_attributes = True
