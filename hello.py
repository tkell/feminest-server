import os
import urlparse
import json
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

    # OK, so this will read the JSON back out.  Rad.  
    res_string = redis.get(artist_name)
    res_dict = json.loads(res_string)

    return flask.jsonify(**res_dict)


@app.route('/find-data/<artist_name>', methods=['GET'])
def find_data(artist_name):

    # need to write something to redis here
    redis.set('artist_name', '{"artist": %s}' % artist_name)

    return "feminest::find %s" % (artist_name)