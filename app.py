import os
import psycopg2
import psycopg2.extras
from werkzeug.exceptions import BadRequest, NotFound
from datetime import datetime
import uvicorn
from pydantic import BaseModel, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

DB_TABLE_TRANSACTION = 'transactions'
DATE_FORMAT = '%Y-%m-%d'

class Settings(BaseSettings):
    ENV: str
    DEBUG: bool = True
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env")

def get_settings():
    return Settings()

class Transaction(BaseModel):
    amount: int
    date: datetime

    @validator('date', pre=True)
    def is_date_format_valid(cls, date_request):
        return datetime.strptime(date_request, DATE_FORMAT)

app = FastAPI()

@app.get('/favicon.ico', include_in_schema=False, status_code=200)
def favicon():
    return FileResponse('static/favicon.ico')

@app.get('/transactions', status_code=200)
def get_transactions():
    db_connection = _get_db_connection()
    cursor = db_connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute('select * from {}'.format(DB_TABLE_TRANSACTION))
    transactions = cursor.fetchall()
    cursor.close()
    db_connection.close()

    return transactions

@app.post('/transactions', status_code=201)
async def post_transaction(transaction: Transaction):
    amount = transaction.amount
    date   = transaction.date

    db_connection = _get_db_connection()
    cursor = db_connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute(
        'insert into {table} (amount, date) values (%(int)s, %(date)s) returning *'.format(table=DB_TABLE_TRANSACTION),
        {'str': DB_TABLE_TRANSACTION, 'int': amount, 'date': date}
    )
    transaction = cursor.fetchone()
    db_connection.commit()
    cursor.close()
    db_connection.close()

    transaction['date'] = transaction['date'].strftime(DATE_FORMAT)

    return transaction

@app.put('/transactions/{id}', status_code=200)
async def put_transaction(id: int, transaction: Transaction):
    amount = transaction.amount
    date   = transaction.date

    try:
        model_get_transaction(id)
    except NotFound as exception:
        raise HTTPException(status_code=404, detail=exception.description)

    db_connection = _get_db_connection()
    cursor = db_connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute(
        'update {table} set (amount, date) = (%(int)s, %(date)s) returning *'.format(table=DB_TABLE_TRANSACTION),
        {'str': DB_TABLE_TRANSACTION, 'int': amount, 'date': date}
    )
    transaction = cursor.fetchone()
    db_connection.commit()
    cursor.close()
    db_connection.close()

    transaction['date'] = transaction['date'].strftime(DATE_FORMAT)

    return transaction

@app.delete('/transactions/{id}', status_code=204)
def delete_transaction(id: int):
    try:
        model_get_transaction(id)
    except NotFound as exception:
        raise HTTPException(status_code=404, detail=exception.description)

    db_connection = _get_db_connection()
    cursor = db_connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute(
        'delete from {table} where id = %(int)s'.format(table=DB_TABLE_TRANSACTION),
        {'int': id}
    )
    db_connection.commit()
    cursor.close()
    db_connection.close()

    return ''

@app.get('/transactions/{id}', status_code=200)
def get_transaction(id):
    try:
        transaction = model_get_transaction(id)
    except NotFound as exception:
        raise HTTPException(status_code=404, detail=exception.description)
    transaction['date'] = transaction['date'].strftime(DATE_FORMAT)

    return transaction

# Future model

def model_get_transaction(id: int):
    db_connection = _get_db_connection()
    cursor = db_connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
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
