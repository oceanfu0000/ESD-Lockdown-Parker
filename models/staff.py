from extensions import db

class Staff(db.Model):
    staff_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pw = db.Column(db.String(100), nullable=False)
    tele_id = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "staff_id": self.staff_id,
            "name": self.name,
            "pw": self.pw,
            "tele_id": self.tele_id
        }
