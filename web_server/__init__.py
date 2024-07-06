from flask import Flask


def init_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    return app
