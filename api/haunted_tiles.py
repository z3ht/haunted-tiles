import os
from flask import Flask, request, Response, abort
from api.examples import hello_world

# NEVER import this in other files
app = Flask(__name__)


@app.before_request
def verify_header():
    if "Api-Token" not in request.headers or request.headers["Api-Token"] != os.getenv("HAUNTED_TILES_API_TOKEN"):
        abort(401)


@app.route('/')
def index():
    return hello_world()


def begin_app():
    app.run(ssl_context='adhoc', port=8421, debug=True)


if __name__ == "__main__":
    begin_app()
