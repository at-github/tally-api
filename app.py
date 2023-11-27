from enum import Enum
import psycopg2
import psycopg2.extras
from werkzeug.exceptions import NotFound
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from requests.transaction import TransactionRequest
import models.crud
from schemas.transaction import Transaction, TransactionCreate
from models.database import SessionLocal, engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DB_TABLE_TRANSACTION = 'transactions'


class Settings(BaseSettings):
    ENV: str
    DEBUG: bool = True
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env")


class SortTransactionsEnum(Enum):
    DATE = 'date'
    AMOUNT = 'amount'


class OrderTransactionsEnum(Enum):
    ASC = 'asc'
    DESC = 'desc'


def get_settings():
    return Settings()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get('/favicon.ico', include_in_schema=False, status_code=200)
def favicon():
    return FileResponse('static/favicon.ico')


@app.get('/transactions', status_code=200)
def get_transactions(
        db: Session = Depends(get_db),
        sort: SortTransactionsEnum | None = SortTransactionsEnum.DATE,
        order: OrderTransactionsEnum | None = OrderTransactionsEnum.DESC
) -> list[Transaction]:
    return models.crud.get_transactions(db)


@app.post('/transactions', status_code=201)
def post_transaction(
        transaction: TransactionCreate,
        db: Session = Depends(get_db)
) -> Transaction:
    return models.crud.create_transaction(db=db, transaction=transaction)


@app.put('/transactions/{id}', status_code=200)
def put_transaction(id: int, transaction: TransactionRequest) -> Transaction:
    amount = transaction.amount
    date = transaction.date

    try:
        model_get_transaction(id)
    except NotFound as exception:
        raise HTTPException(status_code=404, detail=exception.description)

    db_connection = _get_db_connection()
    cursor = db_connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )
    cursor.execute(
        '''update {table} set (amount, date) = (%(int)s, %(date)s)
        returning *'''.format(
            table=DB_TABLE_TRANSACTION
        ),
        {'str': DB_TABLE_TRANSACTION, 'int': amount, 'date': date}
    )
    transaction = cursor.fetchone()
    db_connection.commit()
    cursor.close()
    db_connection.close()

    return transaction


@app.delete('/transactions/{id}', status_code=204)
def delete_transaction(id: int, db: Session = Depends(get_db)) -> None:
    models.crud.delete_transaction(db, transaction_id=id)


@app.get('/transactions/{id}', status_code=200)
def get_transaction(
    id: int,
    db: Session = Depends(get_db)
) -> Transaction:
    db_transaction = models.crud.get_transaction(db, transaction_id=id)

    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return db_transaction


def model_get_transaction(id: int):
    db_connection = _get_db_connection()
    cursor = db_connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )
    cursor.execute(
        'select * from {} where id = %(int)s'.format(DB_TABLE_TRANSACTION),
        {'int': id}
    )
    transaction = cursor.fetchone()
    cursor.close()
    db_connection.close()

    if transaction is None:
        raise NotFound("Transaction’s id '{}' not found".format(id))

    return transaction

# Private


def _get_db_connection():
    settings = get_settings()

    return psycopg2.connect(
        host=settings.DB_HOST,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
