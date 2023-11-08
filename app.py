import os
import psycopg2
import psycopg2.extras
from werkzeug.exceptions import BadRequest, NotFound
from datetime import datetime
from flask import Flask, request, send_from_directory

DB_TABLE_TRANSACTION = 'transactions'
DATE_FORMAT = '%Y-%m-%d'

def fake_entity(amount=10, date='2023-10-26', id=1):
    return {'id': id, 'amount': amount, 'date': date}

app = Flask(__name__)
app.config.from_prefixed_env()

@app.get('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.get('/transactions')
def get_transactions():
    db_connection = _get_db_connection()
    cursor = db_connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute('select * from {}'.format(DB_TABLE_TRANSACTION))
    transactions = cursor.fetchall()
    cursor.close()
    db_connection.close()

    return transactions, 200

@app.post('/transactions')
def post_transaction():
    body = request.get_json()
    try:
        amount = body['amount']
        date   = body['date']
    except KeyError as exception:
        raise BadRequest("Missing field: {}".format(exception))

    if type(amount) != int:
        raise BadRequest("Bad type for 'amount' field")

    if type(date) != str:
        raise BadRequest("Bad type for 'date' field")

    try:
        datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        raise BadRequest("Bad format for 'date' field: {}".format(DATE_FORMAT))

    db_connection = _get_db_connection()
    cursor = db_connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute(
        'insert into {table} (amount, date) values (%(int)s, %(date)s) returning *'.format(table=DB_TABLE_TRANSACTION),
        {'str': DB_TABLE_TRANSACTION, 'int': amount, 'date': date}
    )
    transaction = cursor.fetchone()
    cursor.close()
    db_connection.close()

    transaction['date'] = transaction['date'].strftime(DATE_FORMAT)

    return transaction, 201

@app.put('/transactions/<id>')
def put_transaction(id):
    return fake_entity(id=id), 200

@app.delete('/transactions/<id>')
def delete_transaction(id):
    return '', 204

@app.get('/transactions/<id>')
def get_transaction(id):
    if not id.isdigit():
        raise BadRequest("Bad type for 'id' field")

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

    transaction['date'] = transaction['date'].strftime(DATE_FORMAT)

    return transaction, 200

# Error handlers
@app.errorhandler(400)
def respond_not_found(error):
    return _respond_error(error.description, error.code)

@app.errorhandler(404)
def respond_not_found(error):
    return _respond_error(error.description, error.code)

@app.errorhandler(405)
def respond_not_allowed(error):
    return _respond_error('Your are not allowed', error.code)

# Private
def _respond_error(message, status_code=400):
    return {
        'message': message,
        'status': status_code
    }, status_code

def _get_db_connection():
    return psycopg2.connect(
        host=app.config['DB_HOST'],
        database=app.config['DB_NAME'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD']
    )
