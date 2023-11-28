from pydantic import BaseModel, validator
from datetime import datetime, date

from constants import DATE_FORMAT


class TransactionBase(BaseModel):
    amount: int
    date: datetime | str

    @validator('date', pre=True)
    def is_date_format_valid(date_request: datetime | str):
        if (type(date_request) is datetime):
            return date_request

        if (type(date_request) is date):
            return date_request

        return datetime.strptime(date_request, DATE_FORMAT)

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime(DATE_FORMAT)
        }


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: int

    class Config:
        from_attributes = True
