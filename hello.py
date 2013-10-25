import os
from flask import Flask
from flask import request

import redis

#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
#redis = redis.from_url(redis_url)

#url = urlparse.urlparse(os.environ.get('REDISCLOUD_URL'))
#r = redis.Redis(host=url.hostname, port=url.port, password=url.password)

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
    #redis.set('test-key', 'test-value')

    return "feminest::get %s" % artist_name


@app.route('/find-data/<artist_name>', methods=['GET'])
def find_data(artist_name):

    # need to write something to redis here
    #val = redis.get('test-key', 'test-value')

    return "feminest::find %s - %s" % (artist_name, val)