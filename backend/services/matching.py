import math
from datetime import datetime
from backend.database.db import db
from backend.models.donor import Donor
from backend.models.request import EmergencyRequest
from backend.models.alert import DonorAlert
from backend.models.donation import DonationHistory
from backend.services.eligibility import is_eligible_to_donate
from backend.config import Config


# ─────────────────────────────────────────
# HAVERSINE FORMULA
# Calculates distance between two GPS coordinates in KM
# ─────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in KM

    lat1, lon1, lat2, lon2 = map(math.radians, [
        float(lat1), float(lon1), float(lat2), float(lon2)
    ])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    return round(R * c, 2)  # Distance in KM


# ─────────────────────────────────────────
# FIND NEAREST ELIGIBLE DONORS
# ─────────────────────────────────────────
def find_nearby_donors(blood_group, req_lat, req_lon, radius_km, exclude_donor_ids=[]):
    """
    Find active, eligible donors of matching blood group
    within given radius, sorted by distance.
    """
    # Fetch all active donors with matching blood group
    candidates = Donor.query.filter_by(
        blood_group=blood_group,
        is_active=True
    ).all()

    results = []

    for donor in candidates:

        # Skip already alerted donors
        if donor.id in exclude_donor_ids:
            continue

        # Skip donors without GPS coordinates
        if donor.latitude is None or donor.longitude is None:
            continue

        # Check eligibility (90-day gap)
        eligible, reason = is_eligible_to_donate(donor)
        if not eligible:
            continue

        # Calculate distance
        distance = haversine(req_lat, req_lon, donor.latitude, donor.longitude)

        # Only include donors within radius
        if distance <= radius_km:
            results.append({
                "donor": donor,
                "distance_km": distance
            })

    # Sort by nearest first
    results.sort(key=lambda x: x["distance_km"])

    return results


# ─────────────────────────────────────────
# SEND FIRST BATCH OF ALERTS
# ─────────────────────────────────────────
def send_initial_alerts(request_id):
    """
    Called when a new emergency request is posted.
    Finds nearest 5 eligible donors and creates alert records.
    Returns list of donors alerted.
    """
    from services.whatsapp import send_emergency_alert

    request = EmergencyRequest.query.get(request_id)
    if not request:
        return []

    nearby = find_nearby_donors(
        blood_group=request.blood_group,
        req_lat=request.latitude,
        req_lon=request.longitude,
        radius_km=Config.INITIAL_RADIUS_KM
    )

    # Take only first batch
    batch = nearby[:Config.INITIAL_DONOR_BATCH]
    alerted = []

    for item in batch:
        donor = item["donor"]
        distance = item["distance_km"]

        # Create alert record in DB
        alert = DonorAlert(
            request_id=request_id,
            donor_id=donor.id,
            radius_batch=1
        )
        db.session.add(alert)

        # Send WhatsApp message
        send_emergency_alert(
            donor_phone=donor.phone,
            donor_name=donor.name,
            blood_group=request.blood_group,
            hospital=request.hospital_name,
            distance=str(distance)
        )

        alerted.append(donor)

    db.session.commit()
    return alerted


# ─────────────────────────────────────────
# EXPAND RADIUS — called after 10 mins no response
# ─────────────────────────────────────────
def expand_and_alert(request_id, batch_number):
    """
    Expands search radius and alerts next batch of donors.
    Called by scheduler after EXPAND_WAIT_MINUTES.
    """
    from services.whatsapp import send_emergency_alert

    request = EmergencyRequest.query.get(request_id)
    if not request or request.status != "open":
        return []

    # Get already alerted donor IDs to avoid duplicates
    already_alerted = [
        a.donor_id for a in DonorAlert.query.filter_by(request_id=request_id).all()
    ]

    # Use expanded radius
    radius = Config.EXPAND_RADIUS_KM if batch_number == 2 else Config.MAX_RADIUS_KM

    nearby = find_nearby_donors(
        blood_group=request.blood_group,
        req_lat=request.latitude,
        req_lon=request.longitude,
        radius_km=radius,
        exclude_donor_ids=already_alerted
    )

    batch = nearby[:Config.INITIAL_DONOR_BATCH]
    alerted = []

    for item in batch:
        donor = item["donor"]
        distance = item["distance_km"]

        alert = DonorAlert(
            request_id=request_id,
            donor_id=donor.id,
            radius_batch=batch_number
        )
        db.session.add(alert)

        send_emergency_alert(
            donor_phone=donor.phone,
            donor_name=donor.name,
            blood_group=request.blood_group,
            hospital=request.hospital_name,
            distance=str(distance)
        )

        alerted.append(donor)

    db.session.commit()
    return alerted


# ─────────────────────────────────────────
# DONOR ACCEPTS — fulfill the request
# ─────────────────────────────────────────
def fulfill_request(donor_phone):
    """
    Called when donor replies HELP.
    Finds their open pending alert and marks request fulfilled.
    Notifies requester with donor contact.
    """
    from services.whatsapp import send_donor_confirmation

    donor = Donor.query.filter_by(phone=donor_phone).first()
    if not donor:
        return False, "Donor not found"

    # Find their pending alert
    alert = DonorAlert.query.filter_by(
        donor_id=donor.id,
        response="pending"
    ).order_by(DonorAlert.alerted_at.desc()).first()

    if not alert:
        return False, "No pending alert found"

    # Update alert response
    alert.response = "accepted"
    alert.responded_at = datetime.utcnow()

    # Get the emergency request
    request = EmergencyRequest.query.get(alert.request_id)
    if not request or request.status != "open":
        return False, "Request already fulfilled"

    # Mark request as fulfilled
    request.status = "fulfilled"
    request.fulfilled_at = datetime.utcnow()

    # Log donation
    donation = DonationHistory(
        donor_id=donor.id,
        donated_on=datetime.utcnow(),
        hospital=request.hospital_name,
        request_id=request.id
    )
    donor.last_donated = datetime.utcnow()

    db.session.add(donation)
    db.session.commit()

    # Notify requester
    send_donor_confirmation(
        requester_phone=request.requester_phone,
        donor_name=donor.name,
        donor_phone=donor.phone,
        distance="nearby"
    )

    return True, "Request fulfilled successfully"


# ─────────────────────────────────────────
# DONOR SKIPS — alert next donor in queue
# ─────────────────────────────────────────
def mark_donor_skipped(donor_phone):
    """
    Called when donor replies SKIP.
    Marks their alert as declined.
    """
    donor = Donor.query.filter_by(phone=donor_phone).first()
    if not donor:
        return False

    alert = DonorAlert.query.filter_by(
        donor_id=donor.id,
        response="pending"
    ).order_by(DonorAlert.alerted_at.desc()).first()

    if alert:
        alert.response = "declined"
        alert.responded_at = datetime.utcnow()
        db.session.commit()

    return True


# ─────────────────────────────────────────
# MARK DONOR ACTIVE — after YES ping reply
# ─────────────────────────────────────────
def mark_donor_active(donor_phone):
    donor = Donor.query.filter_by(phone=donor_phone).first()
    if donor:
        donor.is_active = True
        donor.last_confirmed = datetime.utcnow()
        db.session.commit()
        return True
    return False


# ─────────────────────────────────────────
# MARK DONOR INACTIVE — after NO ping reply
# ─────────────────────────────────────────
def mark_donor_inactive(donor_phone):
    donor = Donor.query.filter_by(phone=donor_phone).first()
    if donor:
        donor.is_active = False
        db.session.commit()
        return True
    return False