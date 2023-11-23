from sqlalchemy import Column, Integer, Date
from database import Base


# We will use this Base class we created before to create the SQLAlchemy models
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    date = Column(Date)
