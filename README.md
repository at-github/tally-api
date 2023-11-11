# Accounting tally app

## Getting started

### Configure the application

```shell
ENV=[development|production]
DEBUG=[True|False]
DB_HOST=db_host
DB_NAME='db name'
DB_USER='db user'
DB_PASSWORD='db password'
```
### Launch the app

```shell
uvicorn app:app --host hostdomain --port xxxx
```

```shell
# Or with live reload
uvicorn app:app --host hostdomain --port xxxx --reload
```
