from flask import Flask

from .database import db
from .routes import bp


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory for the protocol management site."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite://" if test_config else "sqlite:///protocols.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(bp)

    return app
