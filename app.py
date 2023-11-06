import os
import psycopg2
from flask import Flask, send_from_directory

DB_TABLE_TRANSACTION = 'transactions'

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
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    cursor.execute('select * from {}'.format(DB_TABLE_TRANSACTION))
    transactions = cursor.fetchall()
    cursor.close()
    db_connection.close()

    return transactions, 200

@app.post('/transactions')
def post_transaction():
    return fake_entity(), 201

@app.put('/transactions/<id>')
def put_transaction(id):
    return fake_entity(id=id), 200

@app.delete('/transactions/<id>')
def delete_transaction(id):
    return '', 204

@app.get('/transactions/<id>')
def get_transaction(id):
    return fake_entity(id=id), 200

@app.errorhandler(404)
def respond_not_found(error):
    return _respond_error('This page does not exist', error.code)

@app.errorhandler(405)
def respond_not_allowed(error):
    return _respond_error('Your are not allowed', error.code)

# Private
def _respond_error(message, status_code=400):
    return {
        'message': message,
        'status': status_code
    }, status_code

def get_db_connection():
    return psycopg2.connect(
        host=app.config['DB_HOST'],
        database=app.config['DB_NAME'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD']
    )
