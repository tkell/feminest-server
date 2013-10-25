import os
from flask import Flask

app = Flask(__name__)



def get_artist_data(artist_name):
    pass


def find_artist_data(artist_name):
    pass


@app.route('/', methods=['GET'])
def hello():
    return "feminest server 1.0"

@app.route('/get-data', methods=['GET'])
def get_data():
    return "feminest::get"


@app.route('/find-data', methods=['GET'])
def find_data():
    return "feminest::find"