from enum import Enum
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

import models.transaction as models
from schemas.transaction import TransactionCreate, Transaction


class SortTransactionsEnum(Enum):
    DATE = 'date'
    AMOUNT = 'amount'


class OrderTransactionsEnum(Enum):
    ASC = 'asc'
    DESC = 'desc'


def get_transactions(
    db: Session,
    sort: SortTransactionsEnum = SortTransactionsEnum.DATE,
    order: OrderTransactionsEnum = OrderTransactionsEnum.DESC
):
    column_sorted = getattr(models.Transaction, sort.value)
    direction = asc if order.value == 'asc' else desc

    return db.query(models.Transaction).order_by(
        direction(column_sorted)
    ).all()


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


def update_transaction(
    db: Session,
    transaction_id: int,
    transaction: Transaction
):
    db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).update(transaction.__dict__)
    db.commit()

    return get_transaction(db, transaction_id)


def delete_transaction(db: Session, transaction_id: int):
    db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).delete()
    db.commit()
