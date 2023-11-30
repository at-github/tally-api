from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict
import pytest

from app import app, get_db
import models.transaction as models


class Settings(BaseSettings):
    ENV: str
    DEBUG: bool = True
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env.test")


settings = Settings()
DATABASE_URL = "postgresql://{user}:{password}@{host}/{db_name}".format(
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    db_name=settings.DB_NAME
)
engine = create_engine(DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# GET /transactions
def test_list_transactions(db_session: Session):
    # Context
    db_transaction1 = add_transaction(db_session, date="2023-11-29")
    db_transaction2 = add_transaction(db_session, date="2023-11-30")

    # Action
    response = client.get('/transactions')

    # Assertions
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": db_transaction2.id,
            "amount": db_transaction2.amount,
            "date": db_transaction2.date.isoformat()
        }, {
            "id": db_transaction1.id,
            "amount": db_transaction1.amount,
            "date": db_transaction1.date.isoformat()
        }
    ]


def test_list_transactions_order_by_date_asc(db_session: Session):
    # Context
    db_transaction1 = add_transaction(db_session, date="2023-11-30")
    db_transaction2 = add_transaction(db_session, date="2024-11-29")

    # Action
    response = client.get('/transactions?sort=date&order=asc')

    # Assertions
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": db_transaction1.id,
            "amount": db_transaction1.amount,
            "date": db_transaction1.date.isoformat()
        }, {
            "id": db_transaction2.id,
            "amount": db_transaction2.amount,
            "date": db_transaction2.date.isoformat()
        }
    ]


def test_list_transactions_order_by_amount_desc(db_session: Session):
    # Context
    db_transaction1 = add_transaction(
        db_session,
        amount="203",
        date="2023-11-05"
    )
    db_transaction2 = add_transaction(
        db_session,
        amount="204",
        date="2023-11-04"
    )
    db_transaction3 = add_transaction(
        db_session,
        amount="205",
        date="2023-11-03"
    )

    # Action
    response = client.get('/transactions?sort=amount&order=desc')

    # Assertions
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": db_transaction3.id,
            "amount": db_transaction3.amount,
            "date": db_transaction3.date.isoformat()
        }, {
            "id": db_transaction2.id,
            "amount": db_transaction2.amount,
            "date": db_transaction2.date.isoformat()
        }, {
            "id": db_transaction1.id,
            "amount": db_transaction1.amount,
            "date": db_transaction1.date.isoformat()
        }
    ]


def test_list_empty_transaction():
    # Context
    # Table transaction is cleared before test, so the context is empty data

    # Action
    response = client.get('/transactions')

    # Assertions
    assert response.status_code == 200
    assert response.json() == []


# GET /transactions/{id}
def test_read_existing_transaction(db_session: Session):
    # Context
    amount = 700
    date = "2023-11-29"
    db_transaction = add_transaction(db_session, amount=amount, date=date)

    # Action
    response = client.get('/transactions/{id}'.format(id=db_transaction.id))

    # Assertions
    assert response.status_code == 200
    assert response.json() == {
        "id": db_transaction.id,
        "amount": amount,
        "date": date
    }


def test_read_unexisting_transaction():
    # Context
    # Table transaction is cleared before test, so the context is empty data

    # Action
    response = client.get('/transactions/{id}'.format(id=0))

    # Assertions
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Transaction not found"
    }


# POST /transactions
def test_create_transaction():
    # Context
    # Table transaction is cleared before test, so the context is empty data

    amount = 1000
    date = "2023-11-30"

    # Action
    response = client.post(
        '/transactions',
        json={
            "amount": amount,
            "date": date
        }
    )
    assert response.status_code == 201
    assert response.json().items() >= {
        "amount": amount,
        "date": date
    }.items()


def test_create_transaction_without_amount():
    # Context
    # Table transaction is cleared before test, so the context is empty data

    # Action
    response = client.post(
        '/transactions',
        json={"date": "2023-11-30"}
    )

    detail = response.json()["detail"][0]
    assert response.status_code == 422
    assert detail.items() >= {
        "msg": "Field required",
        "type": "missing",
        "loc": ["body", "amount"]
    }.items()


def test_create_transaction_without_date():
    # Context
    # Table transaction is cleared before test, so the context is empty data

    # Action
    response = client.post(
        '/transactions',
        json={"amount": 5000}
    )

    detail = response.json()["detail"][0]
    assert response.status_code == 422
    assert detail.items() >= {
        "msg": "Field required",
        "type": "missing",
        "loc": ["body", "date"]
    }.items()


# PUT /transactions
def test_edit_transaction(db_session: Session):
    # Context

    amount = 1100
    date = "2023-11-30"
    db_transaction = add_transaction(db_session, amount=amount, date=date)

    new_amount = amount + 1000
    new_date = "2024-12-03"
    # Action
    response = client.put(
        '/transactions/{id}'.format(id=db_transaction.id),
        json={
            "amount": new_amount,
            "date": new_date
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": db_transaction.id,
        "amount": new_amount,
        "date": new_date
    }


def test_edit_transaction_without_amount(db_session: Session):
    # Context
    db_transaction = add_transaction(
        db_session,
        amount=1200,
        date="2023-11-30"
    )

    # Action
    response = client.put(
        '/transactions/{id}'.format(id=db_transaction.id),
        json={"date": "2023-11-30"}
    )

    detail = response.json()["detail"][0]
    assert response.status_code == 422
    assert detail.items() >= {
        "msg": "Field required",
        "type": "missing",
        "loc": ["body", "amount"]
    }.items()


def test_edit_transaction_without_date(db_session: Session):
    # Context
    db_transaction = add_transaction(
        db_session,
        amount=1200,
        date="2023-11-30"
    )

    # Action
    response = client.put(
        '/transactions/{id}'.format(id=db_transaction.id),
        json={"amount": 5000}
    )

    detail = response.json()["detail"][0]
    assert response.status_code == 422
    assert detail.items() >= {
        "msg": "Field required",
        "type": "missing",
        "loc": ["body", "date"]
    }.items()


def test_update_unexisting_transaction():
    # Context
    # Table transaction is cleared before test, so the context is empty data

    # Action
    response = client.put(
        '/transactions/{id}'.format(id=0),
        json={"amount": 6000, "date": "2023-11-30"}
    )

    # Assertions
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Transaction not found"
    }


# DELETE /transactions
def test_delete_transaction(db_session: Session):
    # Context
    db_transaction = add_transaction(
        db_session,
        amount=1200,
        date="2023-11-30"
    )

    # Action
    response = client.delete('/transactions/{id}'.format(id=db_transaction.id))
    db_transactions = db_session.query(models.Transaction).all()

    # Assertions
    assert response.status_code == 204
    assert not db_transactions


def test_delete_unexisting_transaction(db_session):
    # Context
    # Table transaction is cleared before test, so the context is empty data

    # Action
    response = client.delete('/transactions/{id}'.format(id=0))

    # Assertions
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Transaction not found"
    }


@pytest.fixture(autouse=True)
def db_session():
    db_session = TestSessionLocal()
    db_session.query(models.Transaction).delete()
    db_session.commit()
    yield db_session
    db_session.close()


def add_transaction(
    session: Session,
    amount: int = 100,
    date: str = "2023-11-30"
):
    db_transaction = models.Transaction(
        amount=amount,
        date=date
    )
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)

    return db_transaction
