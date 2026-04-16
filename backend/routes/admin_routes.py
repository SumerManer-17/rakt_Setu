from flask import jsonify, Blueprint
from backend.models.donor import Donor
from backend.models.request import EmergencyRequest
from backend.models.alert import DonorAlert
from backend.models.donation import DonationHistory
from backend.utils.helpers import success_response

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/stats", methods=["GET"])
def get_stats():
    total_donors    = Donor.query.count()
    active_donors   = Donor.query.filter_by(is_active=True).count()
    inactive_donors = Donor.query.filter_by(is_active=False).count()
    open_requests   = EmergencyRequest.query.filter_by(status="open").count()
    fulfilled       = EmergencyRequest.query.filter_by(status="fulfilled").count()
    total_donations = DonationHistory.query.count()
    total_alerts    = DonorAlert.query.count()
    accepted_alerts = DonorAlert.query.filter_by(response="accepted").count()
    response_rate   = round((accepted_alerts / total_alerts) * 100, 1) if total_alerts > 0 else 0

    return jsonify(success_response(data={
        "donors":      {"total": total_donors, "active": active_donors, "inactive": inactive_donors},
        "requests":    {"open": open_requests, "fulfilled": fulfilled},
        "performance": {"total_alerts_sent": total_alerts, "total_donations": total_donations, "donor_response_rate": f"{response_rate}%"}
    }))

@admin_bp.route("/donors", methods=["GET"])
def get_all_donors():
    donors = Donor.query.order_by(Donor.created_at.desc()).all()
    return jsonify(success_response(data=[d.to_dict() for d in donors]))

@admin_bp.route("/requests", methods=["GET"])
def get_all_requests():
    requests = EmergencyRequest.query.order_by(EmergencyRequest.created_at.desc()).all()
    return jsonify(success_response(data=[r.to_dict() for r in requests]))

@admin_bp.route("/blood-groups", methods=["GET"])
def blood_group_stats():
    groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    stats = [{"blood_group": g, "total": Donor.query.filter_by(blood_group=g).count(),
              "active": Donor.query.filter_by(blood_group=g, is_active=True).count()} for g in groups]
    return jsonify(success_response(data=stats))