from backend.database.db import db
from datetime import datetime

class DonorAlert(db.Model):
    __tablename__ = "donor_alerts"

    id           = db.Column(db.Integer, primary_key=True)
    request_id   = db.Column(db.Integer, db.ForeignKey("emergency_requests.id"), nullable=False)
    donor_id     = db.Column(db.Integer, db.ForeignKey("donors.id"), nullable=False)
    alerted_at   = db.Column(db.DateTime, default=datetime.utcnow)
    response     = db.Column(db.String(20), default="pending")
    responded_at = db.Column(db.DateTime, nullable=True)
    radius_batch = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "id":           self.id,
            "request_id":   self.request_id,
            "donor_id":     self.donor_id,
            "alerted_at":   self.alerted_at.isoformat(),
            "response":     self.response,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "radius_batch": self.radius_batch
        }

    def __repr__(self):
        return f"<Alert request={self.request_id} donor={self.donor_id} response={self.response}>"