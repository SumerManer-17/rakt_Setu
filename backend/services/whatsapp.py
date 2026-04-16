import requests
from backend.config import Config


def _send_message(payload):
    """Base function to send any WhatsApp message"""
    headers = {
        "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(Config.WHATSAPP_BASE_URL, json=payload, headers=headers)
    return response.json()


# ─────────────────────────────────────────
# EMERGENCY ALERT TO DONOR
# ─────────────────────────────────────────
def send_emergency_alert(donor_phone, donor_name, blood_group, hospital, distance):
    """
    Sends emergency blood request alert to a nearby donor.
    Template: emergency_blood_alert
    Variables: donor_name, blood_group, hospital, distance
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": f"91{donor_phone}",
        "type": "template",
        "template": {
            "name": "emergency_blood_alert",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": donor_name},
                        {"type": "text", "text": blood_group},
                        {"type": "text", "text": hospital},
                        {"type": "text", "text": f"{distance} km away"}
                    ]
                }
            ]
        }
    }
    return _send_message(payload)


# ─────────────────────────────────────────
# MONTHLY ACTIVITY PING TO DONOR
# ─────────────────────────────────────────
def send_activity_ping(donor_phone, donor_name):
    """
    Sends monthly ping to confirm donor is still active.
    Template: monthly_donor_ping
    Variables: donor_name
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": f"91{donor_phone}",
        "type": "template",
        "template": {
            "name": "monthly_donor_ping",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": donor_name}
                    ]
                }
            ]
        }
    }
    return _send_message(payload)


# ─────────────────────────────────────────
# CONFIRMATION TO REQUESTER
# ─────────────────────────────────────────
def send_donor_confirmation(requester_phone, donor_name, donor_phone, distance):
    """
    Notifies requester that a donor has accepted.
    Template: donor_confirmed
    Variables: donor_name, donor_phone, distance
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": f"91{requester_phone}",
        "type": "template",
        "template": {
            "name": "donor_confirmed",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": donor_name},
                        {"type": "text", "text": donor_phone},
                        {"type": "text", "text": distance}
                    ]
                }
            ]
        }
    }
    return _send_message(payload)


# ─────────────────────────────────────────
# REGISTRATION CONFIRMATION TO DONOR
# ─────────────────────────────────────────
def send_registration_confirmation(donor_phone, donor_name, blood_group):
    """
    Sent to donor after successful registration.
    Template: registration_success
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": f"91{donor_phone}",
        "type": "template",
        "template": {
            "name": "registration_success",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": donor_name},
                        {"type": "text", "text": blood_group}
                    ]
                }
            ]
        }
    }
    return _send_message(payload)