# app/__init__.py

from flask import Flask
from .config import Config
from .extensions import db, migrate, cors
from .routes.auth import auth_bp
from .routes.records import records_bp
from .routes.summary import summary_bp
from .routes.upload import upload_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(upload_bp)

    return app
