from flask import Flask
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    from routes import init_routes

    init_routes(app)

    return app
