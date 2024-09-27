# index.py or routes.py

from flask import Flask, jsonify


def load_routes(app):
    """Register all the routes in the Flask app."""

    @app.route('/')
    def index():
        return jsonify({"message": "Hello, World!"})

    @app.route('/api/data')
    def data():
        return jsonify({"data": [1, 2, 3]})

# More routes can be added here
