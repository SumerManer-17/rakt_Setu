from datetime import datetime, timedelta
from backend.config import Config

def is_eligible_to_donate(donor):
    """
    Check if a donor is eligible to donate blood today.
    Rules:
    - Must be active
    - Must not have donated in the last 90 days
    """
    if not donor.is_active:
        return False, "Donor is currently inactive"

    if donor.last_donated is None:
        return True, "Eligible — never donated before"

    days_since_donation = (datetime.utcnow() - donor.last_donated).days

    if days_since_donation < Config.DONATION_GAP_DAYS:
        days_remaining = Config.DONATION_GAP_DAYS - days_since_donation
        return False, f"Ineligible — must wait {days_remaining} more days"

    return True, "Eligible to donate"


def days_until_eligible(donor):
    """
    Returns number of days until donor can donate again.
    Returns 0 if already eligible.
    """
    if donor.last_donated is None:
        return 0

    days_since = (datetime.utcnow() - donor.last_donated).days
    remaining = Config.DONATION_GAP_DAYS - days_since
    return max(0, remaining)


def next_eligible_date(donor):
    """
    Returns the date when the donor can donate next.
    """
    if donor.last_donated is None:
        return datetime.utcnow()

    return donor.last_donated + timedelta(days=Config.DONATION_GAP_DAYS)


def is_confirmation_overdue(donor):
    """
    Returns True if donor hasn't confirmed activity in 30+ days.
    """
    if donor.last_confirmed is None:
        return True

    days_since_confirmed = (datetime.utcnow() - donor.last_confirmed).days
    return days_since_confirmed >= Config.DONOR_PING_INTERVAL_DAYS