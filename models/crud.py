from sqlalchemy.orm import Session

import models.transaction as models
from schemas.transaction import TransactionCreate


def get_transactions(db: Session):
    return db.query(models.Transaction).all()


def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()


def create_transaction(db: Session, transaction: TransactionCreate):
    db_transaction = models.Transaction(
        amount=transaction.amount,
        date=transaction.date
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction
