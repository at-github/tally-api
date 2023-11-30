from pydantic import BaseModel, field_validator
from datetime import datetime, date

from constants import DATE_FORMAT


class TransactionBase(BaseModel):
    amount: int
    date: datetime | str

    @field_validator('date', mode="before")
    def is_date_format_valid(date_request: datetime | str):
        if (type(date_request) is date):
            return date_request.isoformat()

        return datetime.strptime(date_request, DATE_FORMAT)

    class ConfigDict:
        json_encoders = {
            datetime: lambda v: v.strftime(DATE_FORMAT)
        }


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: int

    class ConfigDict:
        from_attributes = True
