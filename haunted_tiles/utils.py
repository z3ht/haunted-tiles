import functools
from flask import jsonify


def return_json(f):
    @functools.wraps(f)
    def inner(**kwargs):
        return jsonify(f(**kwargs))

    return inner
