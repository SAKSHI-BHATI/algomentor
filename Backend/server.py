from pathlib import Path
import sys

from flask import Flask, jsonify


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from Backend.routes.inference import inference_bp


def create_app():
    app = Flask(__name__)

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    app.register_blueprint(inference_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
