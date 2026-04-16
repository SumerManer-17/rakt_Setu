from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.models.donor import Donor
from backend.models.donation import DonationHistory
from backend.services.whatsapp import send_registration_confirmation
from backend.services.eligibility import days_until_eligible, next_eligible_date, is_eligible_to_donate
from backend.utils.validators import validate_donor_data
from utils.helpers import success_response, error_response, calculate_freshness_label
from datetime import datetime

donor_bp = Blueprint("donor", __name__, url_prefix="/api/donors")

@donor_bp.route("/register", methods=["POST"])
def register_donor():
    data = request.json
    errors = validate_donor_data(data)
    if errors:
        return jsonify(error_response(errors)), 400

    existing = Donor.query.filter_by(phone=data["phone"].strip()).first()
    if existing:
        return jsonify(error_response("This phone number is already registered")), 409

    donor = Donor(
        name=data["name"].strip(),
        phone=data["phone"].strip(),
        blood_group=data["blood_group"].strip().upper(),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        pincode=data.get("pincode", "").strip(),
        city=data.get("city", "").strip(),
        is_active=True,
        last_confirmed=datetime.utcnow()
    )
    db.session.add(donor)
    db.session.commit()

    try:
        send_registration_confirmation(donor.phone, donor.name, donor.blood_group)
    except Exception as e:
        print(f"WhatsApp send failed: {e}")

    return jsonify(success_response(
        data=donor.to_dict(),
        message="Registered successfully! You will receive a WhatsApp confirmation shortly."
    )), 201

@donor_bp.route("/active", methods=["GET"])
def get_active_donors():
    blood_group = request.args.get("blood_group")
    query = Donor.query.filter_by(is_active=True)
    if blood_group:
        query = query.filter_by(blood_group=blood_group.upper())
    donors = query.all()
    return jsonify(success_response(
        data=[d.to_dict() for d in donors],
        message=f"{len(donors)} active donors found"
    ))

@donor_bp.route("/<phone>", methods=["GET"])
def get_donor(phone):
    donor = Donor.query.filter_by(phone=phone.strip()).first()
    if not donor:
        return jsonify(error_response("Donor not found")), 404

    eligible, reason = is_eligible_to_donate(donor)
    history = DonationHistory.query.filter_by(donor_id=donor.id)\
        .order_by(DonationHistory.donated_on.desc()).all()

    profile = donor.to_dict()
    profile["eligibility"] = {
        "is_eligible": eligible,
        "reason": reason,
        "days_until_eligible": days_until_eligible(donor),
        "next_eligible_date": next_eligible_date(donor).strftime("%d %b %Y")
    }
    profile["freshness"] = calculate_freshness_label(donor.last_confirmed)
    profile["total_donations"] = len(history)
    profile["donation_history"] = [h.to_dict() for h in history]
    return jsonify(success_response(data=profile))

@donor_bp.route("/<phone>", methods=["PUT"])
def update_donor(phone):
    donor = Donor.query.filter_by(phone=phone.strip()).first()
    if not donor:
        return jsonify(error_response("Donor not found")), 404

    data = request.json
    if "name" in data:      donor.name      = data["name"].strip()
    if "city" in data:      donor.city      = data["city"].strip()
    if "pincode" in data:   donor.pincode   = data["pincode"].strip()
    if "latitude" in data:  donor.latitude  = data["latitude"]
    if "longitude" in data: donor.longitude = data["longitude"]
    if "is_active" in data: donor.is_active = data["is_active"]
    db.session.commit()
    return jsonify(success_response(data=donor.to_dict(), message="Profile updated successfully"))

@donor_bp.route("/<phone>/toggle", methods=["PATCH"])
def toggle_status(phone):
    donor = Donor.query.filter_by(phone=phone.strip()).first()
    if not donor:
        return jsonify(error_response("Donor not found")), 404

    donor.is_active = not donor.is_active
    if donor.is_active:
        donor.last_confirmed = datetime.utcnow()
    db.session.commit()
    status = "active" if donor.is_active else "inactive"
    return jsonify(success_response(message=f"Donor marked as {status}"))