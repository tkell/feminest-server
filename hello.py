import os
import urlparse
from flask import Flask
from flask import request

import redis
url = urlparse.urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost'))
redis = redis.Redis(host=url.hostname, port=url.port, db=0, password=url.password)

app = Flask(__name__)

def get_artist_data(artist_name):
    pass

def find_artist_data(artist_name):
    pass


@app.route('/', methods=['GET'])
def hello():
    return "feminest server 1.0"

@app.route('/get-data/<artist_name>', methods=['GET'])
def get_data(artist_name):

    # and get the same hard-coded key here
    redis.set('test-key-2', 'test-value')

    return "feminest::get %s" % artist_name


@app.route('/find-data/<artist_name>', methods=['GET'])
def find_data(artist_name):

    # need to write something to redis here
    val = redis.get('test-key')

    return "feminest::find %s - %s" % (artist_name, val)