from flask import Flask
import toml
import logging

app = Flask(__name__)
app.config.from_file('config.toml', toml.load)


@app.route('/')
def hello_world():
    return {}