import functools

from flask import request, jsonify
from pydantic import ValidationError


def validate_request(schema_class):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            try:
                data = schema_class(**request.get_json())
            except ValidationError as e:
                return jsonify({"error": "Invalid input", "details": e.errors()}), 422
            return func(data, *args, **kwargs)

        return wrapper

    return decorator
