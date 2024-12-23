from flask import Flask, g

from db.connnect_db import session
from web_server.routes import diagrams
# from global_config import GlobalConfig


def init_sqlalchemy(app: Flask) -> None:
    @app.before_request
    def db_session():
        """Assign session to each request"""
        g.db = session

    @app.teardown_request
    def remove_session(exception: str) -> None:
        """Remove session after each request"""
        db = g.db
        if db:
            if not exception:
                db.commit()
            else:
                db.rollback()
            db.close()


def init_app(config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    app.register_blueprint(diagrams)
    init_sqlalchemy(app)

    return app
