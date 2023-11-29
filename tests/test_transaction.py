from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import app, get_db


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


def test_read_transaction():
    response = client.get('/transactions/1')
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "amount": 800,
        "date": "2024-01-01"
    }
