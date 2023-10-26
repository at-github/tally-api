import os
from flask import Flask, send_from_directory

def fake_entity(amount=10, date='2023-10-26'):
    return {'amount': amount, 'date': date}

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/transactions')
def get_transactions():
    return [fake_entity(), fake_entity()], 200

@app.errorhandler(404)
def page_not_found(error):
    return {
        'message': 'This page does not exist',
        'status': error.code
    }, error.code
