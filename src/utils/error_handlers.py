from flask import jsonify

def handle_400_error(error):
    response = {"error": "Bad Request", "message": str(error)}
    return jsonify(response), 400

def handle_401_error(error):
    response = {"error": "Invalid Credentials", "message": str(error)}
    return jsonify(response), 401

def handle_404_error(error):
    response = {"error": "Not Found", "message": str(error)}
    return jsonify(response), 404

def handle_409_error(error):
    response = {"error": "Conflict", "message": str(error)}
    return jsonify(response), 409

def register_error_handlers(app):
    app.register_error_handler(400, handle_400_error)
    app.register_error_handler(401, handle_401_error)
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(409, handle_409_error)
