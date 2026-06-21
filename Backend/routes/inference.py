from flask import Blueprint, jsonify, request

from Backend.services.model_service import model_service


inference_bp = Blueprint("inference", __name__, url_prefix="/api/inference")


@inference_bp.route("/next-step", methods=["POST"])
def next_step():
    payload = request.get_json(silent=True) or {}
    result = model_service.get_next_step(payload)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@inference_bp.route("/hints", methods=["POST"])
def get_hints():
    payload = request.get_json(silent=True) or {}
    result = model_service.get_hints(payload)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@inference_bp.route("/evaluate-understanding", methods=["POST"])
def evaluate_understanding():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    problem = payload.get("problem", "")
    result = model_service.evaluate_understanding(text, problem=problem)
    return jsonify(result), 200


@inference_bp.route("/evaluate-pseudocode", methods=["POST"])
def evaluate_pseudocode():
    payload = request.get_json(silent=True) or {}
    code = payload.get("code", "")
    result = model_service.evaluate_pseudocode(code)
    status_code = 200 if "error" not in result else 400
    return jsonify(result), status_code
