from pydantic import BaseModel, validator
from datetime import datetime

from constants import DATE_FORMAT


class TransactionRequest(BaseModel):
    amount: int
    date: datetime

    @validator('date', pre=True)
    def is_date_format_valid(cls, date_request):
        return datetime.strptime(date_request, DATE_FORMAT)
