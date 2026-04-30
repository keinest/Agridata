"""AgriData Platform — Flask application factory."""
import logging
import os
import time
import uuid

from flask import Flask, g, jsonify, request
from flask_cors import CORS

from backend.app.config import settings


def create_app() -> Flask:
    """Create and configure the Flask application."""

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["JSON_SORT_KEYS"] = False

    # Configure static files
    app.static_folder = '../../public'
    app.static_url_path = '/'

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS(
        app,
        origins=settings.CORS_ORIGINS,
        supports_credentials=settings.CORS_ALLOW_CREDENTIALS,
        methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # ── Request tracking middleware ───────────────────────────────────────
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:8]}"
        logger.info(
            "Incoming %s %s  request_id=%s",
            request.method,
            request.path,
            g.request_id,
        )

    @app.after_request
    def after_request(response):
        process_time = time.time() - getattr(g, "start_time", time.time())
        response.headers["X-Request-ID"] = getattr(g, "request_id", "")
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        logger.info(
            "Response %s  request_id=%s  duration=%.4fs",
            response.status_code,
            getattr(g, "request_id", ""),
            process_time,
        )
        return response

    # ── Global error handlers ─────────────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(exc):
        return jsonify({"detail": str(exc)}), 400

    @app.errorhandler(401)
    def unauthorized(exc):
        return jsonify({"detail": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(exc):
        return jsonify({"detail": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(exc):
        return jsonify({"detail": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable(exc):
        return jsonify({"detail": str(exc)}), 422

    @app.errorhandler(500)
    def internal_error(exc):
        logger.exception("Unhandled error: %s", exc)
        return jsonify({"detail": "Internal server error"}), 500

    # ── Register Blueprints ───────────────────────────────────────────────
    prefix = settings.API_PREFIX

    from backend.app.api.analytics import analytics_bp
    from backend.app.api.auth import auth_bp
    from backend.app.api.data_collection import data_collection_bp
    from backend.app.api.exploitations import exploitations_bp
    from backend.app.api.parcelles import parcelles_bp
    from backend.app.api.alertes import alertes_bp
    from backend.app.api.rapports import rapports_bp

    app.register_blueprint(auth_bp, url_prefix=f"{prefix}/auth")
    app.register_blueprint(exploitations_bp, url_prefix=f"{prefix}/exploitations")
    app.register_blueprint(parcelles_bp, url_prefix=f"{prefix}/parcelles")
    app.register_blueprint(data_collection_bp, url_prefix=f"{prefix}/data")
    app.register_blueprint(analytics_bp, url_prefix=f"{prefix}/analytics")
    app.register_blueprint(alertes_bp, url_prefix=f"{prefix}/alertes")
    app.register_blueprint(rapports_bp, url_prefix=f"{prefix}/rapports")

    # ── Health & root routes ──────────────────────────────────────────────
    @app.get("/health")
    def health_check():
        return jsonify({"status": "healthy"})

    @app.get("/")
    def root():
        from flask import send_from_directory
        return send_from_directory(app.static_folder, 'pages/index.html')

    @app.route('/<path:filename>')
    def serve_static(filename):
        from flask import send_from_directory, abort
        if filename.startswith('api/'):
            abort(404)
        try:
            return send_from_directory(app.static_folder, filename)
        except FileNotFoundError:
            abort(404)

    logger.info("Starting up AgriData Platform (Flask) v%s", settings.APP_VERSION)
    return app


# ── Application singleton used by Gunicorn / Vercel ──────────────────────
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=settings.DEBUG)
