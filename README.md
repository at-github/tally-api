# Accounting tally app

## Getting started

### Configure the application

```shell
ENV=[production|development|test]
DEBUG=[True|False]
DB_HOST=db_host
DB_NAME='db name'
DB_USER='db user'
DB_PASSWORD='db password'
```
### Launch the app

```shell
# By default, env = production
uvicorn app:app --host hostdomain --port xxxx
```

```shell
# Or with live reload & env = development
uvicorn app:app --host hostdomain --port xxxx --reload --env-file .env.dev
```

#### Or see coverage
```shell
pytest --cov=. tests
```

## Other

### Launch tests

```shell
pytest

# Or
pytest -f --color yes
```

### Migration

```shell
#Create migration

alembic revision --autogenerate -m "Initial migration"
```

```shell
#Apply migration last migration

alembic upgrade head
```

```shell
#List migrations

alembic show ref
```

```shell
#Show specific migration

alembic show ref
```

```shell
#Restore specific migration

alembic downgrade ref
```
