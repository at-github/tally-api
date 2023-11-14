from pydantic import BaseModel
from datetime import datetime

DATE_FORMAT = '%Y-%m-%d'

class TransactionResponse(BaseModel):
    id: int
    amount: int
    date: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime(DATE_FORMAT)
        }
