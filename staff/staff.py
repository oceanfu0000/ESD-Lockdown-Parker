from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

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

staff_blueprint = Blueprint("staff", __name__)

@staff_blueprint.route("/", methods=["POST"])
def create_staff():
    data = request.json
    if "name" in data and "pw" in data and "tele_id" in data:
        new_staff = Staff(name=data["name"], pw=data["pw"], tele_id=data["tele_id"])
        db.session.add(new_staff)
        db.session.commit()
        return jsonify({"message": "Staff member created successfully"}), 201
    else:
        return jsonify({"error": "Missing required fields"}), 400

@staff_blueprint.route("/", methods=["GET"])
def read_all_staff():
    staff_list = Staff.query.all()
    return jsonify([staff.to_dict() for staff in staff_list]), 200

@staff_blueprint.route("/<int:staff_id>", methods=["GET"])
def read_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if staff:
        return jsonify(staff.to_dict()), 200
    else:
        return jsonify({"error": "Staff member not found"}), 404

@staff_blueprint.route("/<int:staff_id>", methods=["PUT"])
def update_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if staff:
        data = request.json
        if "name" in data:
            staff.name = data["name"]
        if "pw" in data:
            staff.pw = data["pw"]
        if "tele_id" in data:
            staff.tele_id = data["tele_id"]
        db.session.commit()
        return jsonify({"message": "Staff member updated successfully"}), 200
    else:
        return jsonify({"error": "Staff member not found"}), 404

@staff_blueprint.route("/<int:staff_id>", methods=["DELETE"])
def delete_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if staff:
        db.session.delete(staff)
        db.session.commit()
        return jsonify({"message": "Staff member deleted successfully"}), 200
    else:
        return jsonify({"error": "Staff member not found"}), 404
