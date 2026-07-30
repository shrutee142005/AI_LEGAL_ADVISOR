from flask import Flask
from app.config import Config
from app.extensions import db
from flask_jwt_extended import JWTManager
from app.routes.auth import auth_bp
from app.routes.chat import chat_bp
from app.routes.documnets import document_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]

    jwt = JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(document_bp,url_prefix="/api/documents")

    @app.route("/")
    def home():
        return {"message": "AI Legal Advisor Backend is running"}

    return app


