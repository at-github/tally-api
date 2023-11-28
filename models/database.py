from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str
    DEBUG: bool = True
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

DATABASE_URL = "postgresql://{user}:{password}@{host}/{db_name}".format(
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    db_name=settings.DB_NAME
)

engine = create_engine(DATABASE_URL)

"""
Each instance of the SessionLocal class will be a database session.
The class itself is not a database session yet.
But once we create an instance of the SessionLocal class,
this instance will be the actual database session.
"""
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""
Later we will inherit from this class
to create each of the database models or classes (the ORM models)
"""
Base = declarative_base()
