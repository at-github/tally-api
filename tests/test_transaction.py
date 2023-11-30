from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
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


# GET /transactions/{id}
def test_read_existing_transaction(db_session):
    # Context
    amount = 700
    date = "2023-11-29"
    db_transaction = models.Transaction(
        amount=amount,
        date=date
    )
    db_session.add(db_transaction)
    db_session.commit()
    db_session.refresh(db_transaction)

    # Action
    response = client.get('/transactions/{id}'.format(id=db_transaction.id))

    # Assertions
    assert response.status_code == 200
    assert response.json() == {
        "id": db_transaction.id,
        "amount": amount,
        "date": date
    }


@pytest.fixture(autouse=True)
def db_session():
    yield TestSessionLocal()
