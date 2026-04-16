from backend.database.db import db
from datetime import datetime

class Donor(db.Model):
    __tablename__ = "donors"

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    phone          = db.Column(db.String(15), unique=True, nullable=False)
    blood_group    = db.Column(db.String(5), nullable=False)
    latitude       = db.Column(db.Numeric(10, 8))
    longitude      = db.Column(db.Numeric(11, 8))
    pincode        = db.Column(db.String(6))
    city           = db.Column(db.String(100))
    is_active      = db.Column(db.Boolean, default=True)
    last_confirmed = db.Column(db.DateTime, default=datetime.utcnow)
    last_donated   = db.Column(db.DateTime, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    alerts   = db.relationship("DonorAlert", backref="donor", lazy=True)
    history  = db.relationship("DonationHistory", backref="donor", lazy=True)

    def to_dict(self):
        return {
            "id":             self.id,
            "name":           self.name,
            "phone":          self.phone,
            "blood_group":    self.blood_group,
            "latitude":       float(self.latitude) if self.latitude else None,
            "longitude":      float(self.longitude) if self.longitude else None,
            "pincode":        self.pincode,
            "city":           self.city,
            "is_active":      self.is_active,
            "last_confirmed": self.last_confirmed.isoformat() if self.last_confirmed else None,
            "last_donated":   self.last_donated.isoformat() if self.last_donated else None,
            "created_at":     self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Donor {self.name} | {self.blood_group} | Active: {self.is_active}>"