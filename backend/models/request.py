from backend.database.db import db
from datetime import datetime

class EmergencyRequest(db.Model):
    __tablename__ = "emergency_requests"

    id                = db.Column(db.Integer, primary_key=True)
    requester_name    = db.Column(db.String(100), nullable=False)
    requester_phone   = db.Column(db.String(15), nullable=False)
    blood_group       = db.Column(db.String(5), nullable=False)
    hospital_name     = db.Column(db.String(200), nullable=False)
    hospital_address  = db.Column(db.String(300))
    latitude          = db.Column(db.Numeric(10, 8))
    longitude         = db.Column(db.Numeric(11, 8))
    units_needed      = db.Column(db.Integer, default=1)
    additional_notes  = db.Column(db.Text)
    status            = db.Column(db.String(20), default="open")
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)
    fulfilled_at      = db.Column(db.DateTime, nullable=True)

    # Relationships
    alerts = db.relationship("DonorAlert", backref="request", lazy=True)

    def to_dict(self):
        return {
            "id":               self.id,
            "requester_name":   self.requester_name,
            "requester_phone":  self.requester_phone,
            "blood_group":      self.blood_group,
            "hospital_name":    self.hospital_name,
            "hospital_address": self.hospital_address,
            "latitude":         float(self.latitude) if self.latitude else None,
            "longitude":        float(self.longitude) if self.longitude else None,
            "units_needed":     self.units_needed,
            "additional_notes": self.additional_notes,
            "status":           self.status,
            "created_at":       self.created_at.isoformat(),
            "fulfilled_at":     self.fulfilled_at.isoformat() if self.fulfilled_at else None
        }

    def __repr__(self):
        return f"<Request {self.id} | {self.blood_group} | {self.status}>"