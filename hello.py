import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "feminest server 1.0"

@app.route('/get')
def get():
    return "feminest::get"

@app.route('/find')
def get():
    return "feminest::find"