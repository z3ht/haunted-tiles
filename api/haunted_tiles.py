import os
from flask import Flask, request
from api.examples import hello_world

# NEVER import this in other files
app = Flask(__name__)


@app.before_request
def verify_header():
    pass


@app.route('/')
def index():
    return hello_world()


def begin_app():
    app.run(ssl_context='adhoc', host="0.0.0.0", port=8421, debug=True)


if __name__ == "__main__":
    begin_app()
