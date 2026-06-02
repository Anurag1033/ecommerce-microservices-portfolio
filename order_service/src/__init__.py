from flask import Flask
from src.api.routes import order_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(order_blueprint)
    return app