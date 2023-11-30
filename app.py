from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, declarative_base

import models.crud as crud
from models.crud import SortTransactionsEnum, OrderTransactionsEnum
from schemas.transaction import Transaction, TransactionCreate
from models.database import SessionLocal, engine

Base = declarative_base()
Base.metadata.create_all(bind=engine)


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
    return crud.get_transactions(db, sort, order)


@app.post('/transactions', status_code=201)
def post_transaction(
        transaction: TransactionCreate,
        db: Session = Depends(get_db)
) -> Transaction:
    return crud.create_transaction(db=db, transaction=transaction)


@app.put('/transactions/{id}', status_code=200)
def put_transaction(
    id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
) -> Transaction:
    db_transaction = crud.get_transaction(db, transaction_id=id)

    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return crud.update_transaction(
        db=db,
        transaction_id=id,
        transaction=transaction
    )


@app.delete('/transactions/{id}', status_code=204)
def delete_transaction(id: int, db: Session = Depends(get_db)) -> None:
    crud.delete_transaction(db, transaction_id=id)


@app.get('/transactions/{id}', status_code=200)
def get_transaction(
    id: int,
    db: Session = Depends(get_db)
) -> Transaction:
    db_transaction = crud.get_transaction(db, transaction_id=id)

    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return db_transaction
