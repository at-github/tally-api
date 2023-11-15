from enum import Enum
import psycopg2
import psycopg2.extras
from werkzeug.exceptions import NotFound
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from responses.transaction import TransactionResponse
from requests.transaction import TransactionRequest

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


app = FastAPI()


@app.get('/favicon.ico', include_in_schema=False, status_code=200)
def favicon():
    return FileResponse('static/favicon.ico')


@app.get('/transactions', status_code=200)
def get_transactions(
        sort: SortTransactionsEnum | None = SortTransactionsEnum.DATE,
        order: OrderTransactionsEnum | None = OrderTransactionsEnum.DESC
) -> list[TransactionResponse]:
    db_connection = _get_db_connection()
    cursor = db_connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )
    cursor.execute(
        'select id, amount, date from {table} order by {sort} {order}'.format(
            table=DB_TABLE_TRANSACTION,
            sort=sort.value,
            order=order.value
        )
    )
    transactions = cursor.fetchall()
    cursor.close()
    db_connection.close()

    return transactions


@app.post('/transactions', status_code=201)
def post_transaction(transaction: TransactionRequest) -> TransactionResponse:
    amount = transaction.amount
    date = transaction.date

    db_connection = _get_db_connection()
    cursor = db_connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )
    cursor.execute(
        '''insert into {table} (amount, date)
        values (%(int)s, %(date)s) returning *'''.format(
            table=DB_TABLE_TRANSACTION
        ),
        {'int': amount, 'date': date}
    )
    transaction = cursor.fetchone()
    db_connection.commit()
    cursor.close()
    db_connection.close()

    return transaction


@app.put('/transactions/{id}', status_code=200)
def put_transaction(
    id: int,
    transaction: TransactionResponse
) -> TransactionResponse:
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
def delete_transaction(id: int) -> None:
    try:
        model_get_transaction(id)
    except NotFound as exception:
        raise HTTPException(status_code=404, detail=exception.description)

    db_connection = _get_db_connection()
    cursor = db_connection.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )
    cursor.execute(
        'delete from {table} where id = %(int)s'.format(
            table=DB_TABLE_TRANSACTION
        ),
        {'int': id}
    )
    db_connection.commit()
    cursor.close()
    db_connection.close()


@app.get('/transactions/{id}', status_code=200)
def get_transaction(id) -> TransactionResponse:
    try:
        return model_get_transaction(id)
    except NotFound as exception:
        raise HTTPException(status_code=404, detail=exception.description)

# Future model


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
