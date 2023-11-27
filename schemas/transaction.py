from pydantic import BaseModel
from datetime import datetime

from constants import DATE_FORMAT


class TransactionBase(BaseModel):
    amount: int
    date: datetime


class TransactionCreate(TransactionBase):
    pass


# When is used? From documentation it's for read
class Transaction(TransactionBase):
    id: int

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime(DATE_FORMAT)
        }
