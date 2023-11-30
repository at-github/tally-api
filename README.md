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

### Launch tests

```shell
pytest

# Or
pytest -f --color yes
```

#### Or see coverage
```shell
pytest --cov=. tests
```
