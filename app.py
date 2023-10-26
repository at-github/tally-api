import os
from flask import Flask, send_from_directory

def fake_entity(amount=10, date='2023-10-26'):
    return {'amount': amount, 'date': date}

app = Flask(__name__)

@app.get('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.get('/transactions')
def get_transactions():
    return [fake_entity(), fake_entity()], 200

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
