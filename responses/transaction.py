from pydantic import BaseModel
from datetime import datetime

from constants import DATE_FORMAT


class TransactionResponse(BaseModel):
    id: int
    amount: int
    date: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime(DATE_FORMAT)
        }
