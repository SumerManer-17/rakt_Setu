from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from backend.config import Config


scheduler = BackgroundScheduler()


def start_scheduler(app):
    """Initialize and start all scheduled jobs"""

    # Job 1: Monthly donor activity ping — runs on 1st of every month at 10 AM
    scheduler.add_job(
        func=lambda: monthly_donor_ping(app),
        trigger="cron",
        day=1,
        hour=10,
        minute=0,
        id="monthly_ping"
    )

    # Job 2: Mark non-responders as inactive — runs every day at midnight
    scheduler.add_job(
        func=lambda: mark_non_responders_inactive(app),
        trigger="cron",
        hour=0,
        minute=0,
        id="inactive_checker"
    )

    # Job 3: Expire old open requests — runs every hour
    scheduler.add_job(
        func=lambda: expire_old_requests(app),
        trigger="interval",
        hours=1,
        id="request_expiry"
    )

    scheduler.start()
    print("✅ Scheduler started successfully")


# ─────────────────────────────────────────
# JOB 1: Send monthly pings to all active donors
# ─────────────────────────────────────────
def monthly_donor_ping(app):
    with app.app_context():
        from models.donor import Donor
        from services.whatsapp import send_activity_ping

        donors = Donor.query.filter_by(is_active=True).all()
        count = 0

        for donor in donors:
            try:
                send_activity_ping(donor.phone, donor.name)
                count += 1
            except Exception as e:
                print(f"Failed to ping donor {donor.id}: {e}")

        print(f"✅ Monthly ping sent to {count} donors")


# ─────────────────────────────────────────
# JOB 2: Mark donors inactive if no ping reply in 48 hours
# ─────────────────────────────────────────
def mark_non_responders_inactive(app):
    with app.app_context():
        from models.donor import Donor
        from database.db import db

        cutoff = datetime.utcnow() - timedelta(hours=Config.DONOR_INACTIVE_AFTER_HOURS)

        # Donors who haven't confirmed since cutoff
        overdue_donors = Donor.query.filter(
            Donor.is_active == True,
            Donor.last_confirmed < cutoff
        ).all()

        count = 0
        for donor in overdue_donors:
            # Only mark inactive if it's been more than 30 days since last confirmation
            days_since = (datetime.utcnow() - donor.last_confirmed).days
            if days_since >= Config.DONOR_PING_INTERVAL_DAYS + 2:  # 30 days + 48hr grace
                donor.is_active = False
                count += 1

        db.session.commit()
        print(f"✅ Marked {count} donors as inactive due to no response")


# ─────────────────────────────────────────
# JOB 3: Expire requests older than 24 hours
# ─────────────────────────────────────────
def expire_old_requests(app):
    with app.app_context():
        from models.request import EmergencyRequest
        from database.db import db

        cutoff = datetime.utcnow() - timedelta(hours=24)

        old_requests = EmergencyRequest.query.filter(
            EmergencyRequest.status == "open",
            EmergencyRequest.created_at < cutoff
        ).all()

        count = 0
        for req in old_requests:
            req.status = "expired"
            count += 1

        db.session.commit()
        if count:
            print(f"✅ Expired {count} old open requests")