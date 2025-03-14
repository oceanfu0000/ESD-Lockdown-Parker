from supabase_client import supabase
from flask import Flask, jsonify


def get_guest(id):
    try:
        response = supabase.table("guest").select("*").eq("guest_id",id).execute()
        if response.data == "":
            return jsonify({"error": "no guest found"}),500
        return jsonify({"guest": response.data}),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
print(get_guest(1))