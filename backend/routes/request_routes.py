from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.models.request import EmergencyRequest
from backend.models.alert import DonorAlert
from backend.services.matching import send_initial_alerts
from backend.utils.validators import validate_request_data
from backend.utils.helpers import success_response, error_response

request_bp = Blueprint("requests", __name__, url_prefix="/api/requests")

@request_bp.route("/emergency", methods=["POST"])
def post_emergency():
    data = request.json
    errors = validate_request_data(data)
    if errors:
        return jsonify(error_response(errors)), 400

    emergency = EmergencyRequest(
        requester_name=data["requester_name"].strip(),
        requester_phone=data["requester_phone"].strip(),
        blood_group=data["blood_group"].strip().upper(),
        hospital_name=data["hospital_name"].strip(),
        hospital_address=data.get("hospital_address", "").strip(),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        units_needed=data.get("units_needed", 1),
        additional_notes=data.get("additional_notes", ""),
        status="open"
    )
    db.session.add(emergency)
    db.session.commit()

    try:
        alerted = send_initial_alerts(emergency.id)
        alerted_count = len(alerted)
    except Exception as e:
        print(f"Matching error: {e}")
        alerted_count = 0

    return jsonify(success_response(
        data={
            "request_id": emergency.id,
            "donors_alerted": alerted_count,
            "status": "open"
        },
        message=f"Emergency posted! {alerted_count} nearby donors alerted via WhatsApp."
    )), 201

@request_bp.route("/<int:request_id>/status", methods=["GET"])
def get_request_status(request_id):
    emergency = EmergencyRequest.query.get(request_id)
    if not emergency:
        return jsonify(error_response("Request not found")), 404

    alerts = DonorAlert.query.filter_by(request_id=request_id).all()
    alert_summary = {
        "total_alerted": len(alerts),
        "accepted":    sum(1 for a in alerts if a.response == "accepted"),
        "declined":    sum(1 for a in alerts if a.response == "declined"),
        "pending":     sum(1 for a in alerts if a.response == "pending"),
        "no_response": sum(1 for a in alerts if a.response == "no_response")
    }
    return jsonify(success_response(data={
        "request": emergency.to_dict(),
        "alert_summary": alert_summary
    }))

@request_bp.route("/open", methods=["GET"])
def get_open_requests():
    blood_group = request.args.get("blood_group")
    query = EmergencyRequest.query.filter_by(status="open")
    if blood_group:
        query = query.filter_by(blood_group=blood_group.upper())
    requests_list = query.order_by(EmergencyRequest.created_at.desc()).all()
    return jsonify(success_response(
        data=[r.to_dict() for r in requests_list],
        message=f"{len(requests_list)} open requests found"
    ))

@request_bp.route("/<int:request_id>/cancel", methods=["PATCH"])
def cancel_request(request_id):
    emergency = EmergencyRequest.query.get(request_id)
    if not emergency:
        return jsonify(error_response("Request not found")), 404
    if emergency.status != "open":
        return jsonify(error_response(f"Cannot cancel — request is already {emergency.status}")), 400
    emergency.status = "cancelled"
    db.session.commit()
    return jsonify(success_response(message="Request cancelled successfully"))