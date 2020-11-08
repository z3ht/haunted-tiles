import os
from expiringdict import ExpiringDict
from dotenv import load_dotenv
from flask import Flask, request, abort
import uuid

from haunted_tiles.examples import hello_world
from haunted_tiles.utils import return_json
from haunted_tiles import strategies
from haunted_tiles.preprocess import format_side, format_game_state


load_dotenv(verbose=True)
app = Flask(__name__)
game_cache = ExpiringDict(max_len=1000, max_age_seconds=60*60)


@app.before_request
def verify_header():
    reques = request
    # Prevents other teams from stealing our algorithm. The front end code must contain the api-token.
    if "Api-Token" not in request.args or request.args["Api-Token"] != os.getenv("HAUNTED_TILES_API_TOKEN"):
        abort(401)


# POST
@app.route('/')
@return_json
def create_game():
    for item in ["Side", "Strategy"]:
        if item not in request.args:
            abort(400)

    available_strategies = {
        "basic": strategies.Basic
    }

    side = format_side(request.args["Side"])
    strategy = request.args["Strategy"].lower()

    if request.args["Strategy"].lower() not in available_strategies:
        abort(400)

    if "Game-State" not in request.args:
        abort(400)

    if side not in ['home', 'away']:
        abort(400)

    game_state = format_game_state(request.args["Game-State"])
    game_id = uuid.uuid4().hex.upper()[0:6]

    game_cache[game_id] = available_strategies[strategy](game_state=game_state, side=side)

    return game_id


# POST
@app.route('/update')
def update():
    if "Game-Id" not in request.args or request.args["Game-Id"] not in game_cache:
        abort(400)

    if "Game-State" not in request.args or request.args["Game-State"].lower():
        abort(400)

    game_state = format_game_state(request.args["Game-State"])
    game_cache[request.args["Game-Id"]].update(game_state=game_state)


# GET
@app.route('/move')
@return_json
def move():
    if "Game-Id" not in request.args or request.args["Game-Id"] not in game_cache:
        abort(400)

    return game_cache[request.args["Game-Id"]].move()


# GET
@app.route('/hello_world')
@return_json
def test():
    return hello_world()


if __name__ == "__main__":
    os.environ["FLASK_ENV"] = "development"
    app.run(ssl_context="adhoc", port=8421, debug=True)
