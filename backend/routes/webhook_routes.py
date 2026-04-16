from flask import Blueprint, request, jsonify
from backend.config import Config
from backend.services.matching import fulfill_request, mark_donor_skipped, mark_donor_active, mark_donor_inactive
from backend.utils.helpers import format_phone

webhook_bp = Blueprint("webhook", __name__, url_prefix="/webhook")


# ─────────────────────────────────────────
# WEBHOOK VERIFICATION — One time setup
# GET /webhook
# ─────────────────────────────────────────
@webhook_bp.route("", methods=["GET"])
def verify_webhook():
    """
    Meta calls this once when you register the webhook URL.
    It sends a challenge — we echo it back to verify ownership.
    """
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == Config.VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return challenge, 200

    print("❌ Webhook verification failed — token mismatch")
    return "Forbidden", 403


# ─────────────────────────────────────────
# RECEIVE WHATSAPP REPLIES
# POST /webhook
# ─────────────────────────────────────────
@webhook_bp.route("", methods=["POST"])
def receive_message():
    """
    Meta sends donor replies here in real time.
    We parse the reply and trigger the right action.
    """
    data = request.json

    try:
        # Parse incoming WhatsApp message
        entry   = data["entry"][0]
        changes = entry["changes"][0]
        value   = changes["value"]

        # Only process if messages key exists
        if "messages" not in value:
            return jsonify({"status": "no message"}), 200

        message = value["messages"][0]
        sender_raw = message["from"]  # e.g. 919876543210
        sender_phone = format_phone(sender_raw)

        # Only handle text messages
        if message.get("type") != "text":
            return jsonify({"status": "non-text ignored"}), 200

        reply = message["text"]["body"].strip().upper()
        print(f"📩 Reply from {sender_phone}: {reply}")

        # ── Route reply to correct action ──
        if reply == "HELP":
            success, msg = fulfill_request(sender_phone)
            print(f"HELP handler: {msg}")

        elif reply == "SKIP":
            mark_donor_skipped(sender_phone)
            print(f"Donor {sender_phone} skipped")

        elif reply == "YES":
            mark_donor_active(sender_phone)
            print(f"Donor {sender_phone} confirmed active")

        elif reply == "NO":
            mark_donor_inactive(sender_phone)
            print(f"Donor {sender_phone} marked inactive")

        else:
            print(f"Unknown reply '{reply}' from {sender_phone} — ignored")

    except KeyError as e:
        print(f"Webhook parse error — missing key: {e}")
    except Exception as e:
        print(f"Webhook error: {e}")

    # Always return 200 to Meta — otherwise it retries endlessly
    return jsonify({"status": "ok"}), 200