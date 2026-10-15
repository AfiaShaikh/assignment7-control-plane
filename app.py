"""Small local-lab Flask application for assignment 7."""
import argparse
import os
import socket
from pathlib import Path
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
VERSION = os.environ.get('APP_VERSION', '1.0')
MESSAGE = os.environ.get('APP_MESSAGE', 'Hello from the DevOps assignment!')

@app.get('/')
def home():
    html = Path(__file__).with_name('index.html').read_text(encoding='utf-8')
    return render_template_string(html, version=VERSION, message=MESSAGE,
                                  hostname=socket.gethostname())

@app.get('/health')
def health():
    return jsonify(status='ok', version=VERSION)

def check():
    # Real HTTP-handler checks; a failure produces a nonzero build exit code.
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200, 'Home route failed'
        assert b'DevOps Demo' in response.data, 'Page heading is missing'
        response = client.get('/health')
        assert response.status_code == 200, 'Health route failed'
        assert response.json == {'status': 'ok', 'version': VERSION}
        assert client.get('/missing').status_code == 404
    print(f'PASS: home page, page content, health response, missing route; version={VERSION}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        check()
    else:
        app.run(host='0.0.0.0', port=5000, debug=False)
