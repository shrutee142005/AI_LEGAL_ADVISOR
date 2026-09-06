import os
from flask import Flask, send_from_directory

from app.config import Config
from app.extensions import db

from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from app.routes.auth import auth_bp
from app.routes.chat import chat_bp
from app.routes.documnets import document_bp


migrate = Migrate()


def create_app():

    frontend_folder = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../frontend"
    )
)

    app = Flask(
    __name__,
    static_folder=frontend_folder,
    static_url_path="/frontend"
)

    app.config.from_object(Config)

    # ------------------------------------------
    # Database
    # ------------------------------------------

    db.init_app(app)

    # ------------------------------------------
    # Flask-Migrate
    # ------------------------------------------

    migrate.init_app(app, db)

    # ------------------------------------------
    # JWT
    # ------------------------------------------

    app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]

    JWTManager(app)

    # ------------------------------------------
    # Routes
    # ------------------------------------------

    app.register_blueprint(auth_bp)

    app.register_blueprint(chat_bp)

    app.register_blueprint(
        document_bp,
        url_prefix="/api/documents"
    )

    # ------------------------------------------
    # FRONTEND
    # ------------------------------------------

    @app.route("/")
    def home():

        return send_from_directory(
        frontend_folder,
        "index.html"
    )


    @app.route("/dashboard")
    def dashboard():

        return send_from_directory(
        frontend_folder,
        "dashboard.html"
    )

    @app.route("/chat")
    def chat():
    
            return send_from_directory(
            frontend_folder,
            "chat.html"
            )

    return app