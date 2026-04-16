from backend.database.db import db
from datetime import datetime

class DonationHistory(db.Model):
    __tablename__ = "donation_history"

    id         = db.Column(db.Integer, primary_key=True)
    donor_id   = db.Column(db.Integer, db.ForeignKey("donors.id"), nullable=False)
    donated_on = db.Column(db.DateTime, nullable=False)
    hospital   = db.Column(db.String(200))
    request_id = db.Column(db.Integer, db.ForeignKey("emergency_requests.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "donor_id":   self.donor_id,
            "donated_on": self.donated_on.isoformat(),
            "hospital":   self.hospital,
            "request_id": self.request_id,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Donation donor={self.donor_id} on={self.donated_on}>"