from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database.db import init_db
from routes.donor_routes import donor_bp
from routes.request_routes import request_bp
from routes.webhook_routes import webhook_bp
from routes.admin_routes import admin_bp
from services.scheduler import start_scheduler

def create_app():
    app = Flask(__name__)
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
    def health():
        return jsonify({
            "status": "RaktSetu API is running 🩸",
            "version": "1.0.0"
        })

    # 404 handler
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Route not found"}), 404

    # 500 handler
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)