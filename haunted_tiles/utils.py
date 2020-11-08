import functools
import json


def return_json(f):
    @functools.wraps(f)
    def inner(**kwargs):
        return json.dumps(f(**kwargs))

    return inner
