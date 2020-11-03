import functools
import os
from flask import Flask, request, abort, jsonify
from api.examples import hello_world


def return_json(f):
    @functools.wraps(f)
    def inner(**kwargs):
        return jsonify(f(**kwargs))

    return inner


# NEVER import app in other files
app = Flask(__name__)


@app.before_request
def verify_header():
    # Prevents other teams from stealing our algorithm. The front end code must contain the api-token.
    if "Api-Token" not in request.headers or request.headers["Api-Token"] != os.getenv("HAUNTED_TILES_API_TOKEN"):
        abort(401)


@app.route('/')
@return_json
def index():
    return hello_world()


def begin_app():
    app.run(ssl_context=("./server.crt", "./server.key"), host="0.0.0.0", port=8421, debug=True)


if __name__ == "__main__":
    begin_app()
