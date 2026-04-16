import os
from flask import Flask, jsonify,send_from_directory
from flask_cors import CORS
from backend.config import Config
from backend.database.db import init_db
from backend.routes.donor_routes import donor_bp
from backend.routes.request_routes import request_bp
from backend.routes.webhook_routes import webhook_bp
from backend.routes.admin_routes import admin_bp
from backend.services.scheduler import start_scheduler

def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(Config)

    # Enable CORS so frontend can talk to backend
    CORS(app,origins="*")

    print("DB URL:", app.config.get("SQLALCHEMY_DATABASE_URI"))
    # Initialize database
    init_db(app)

    # Register all route blueprints
    app.register_blueprint(donor_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(admin_bp)

    # Start background scheduler
    # start_scheduler(app)

    # Health check route
    @app.route("/")
    def home():
        return app.send_static_file("index.html")
    
    @app.route("/dashboard")
    def dashboard():
        return app.send_static_file("pages/dashboard.html")

    @app.route("/login")
    def login():
        return app.send_static_file("pages/login.html")

    @app.route("/register")
    def register():
        return app.send_static_file("pages/register.html")

    @app.route("/admin")
    def admin():
        return app.send_static_file("pages/admin.html")

    @app.route("/map")
    def map_page():
        return app.send_static_file("pages/map.html")

    @app.route("/emergency")
    def emergency():
        return app.send_static_file("pages/emergency.html")

    @app.route("/status")
    def status():
        return app.send_static_file("pages/status.html")

    # 404 handler
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Route not found"}), 404

    # 500 handler
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return app

app = create_app()

if __name__ == "__main__":
    
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)