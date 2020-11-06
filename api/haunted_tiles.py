import os
from flask import Flask, request, abort
from api.examples import hello_world
from dotenv import load_dotenv
from api.utils import return_json


load_dotenv(verbose=True)
app = Flask(__name__)


@app.before_request
def verify_header():
    # Prevents other teams from stealing our algorithm. The front end code must contain the api-token.
    if "Api-Token" not in request.args or request.args["Api-Token"] != os.getenv("HAUNTED_TILES_API_TOKEN"):
        abort(401)


@app.route('/')
@return_json
def index():
    return hello_world()


if __name__ == "__main__":
    os.environ["FLASK_ENV"] = "development"
    app.run(ssl_context="adhoc", port=8421, debug=True)
