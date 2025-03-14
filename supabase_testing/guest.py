from flask import Flask, jsonify, request
# call supabase_client
from supabase_client import supabase


app = Flask(__name__)

# Check OTP in DB
# If exists, return Guest Details
# If not, return No Guest Found
@app.route('/validate/<int:otp>', methods=['PUT'])
def validate(otp):
    try:
        response = supabase.table("guest").select("*").eq("otp",otp).execute()
        if response.data == "":
            return jsonify({"error": "no guest found"}),500
        
        return jsonify({"guest": response.data}),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Check Guest Details using guest_id
# If no fields specified, return all
# If field specified (e.g./guest/1?field=loyalty_points), return loyalty_point only
@app.route('/guest/<int:id>', methods=['GET'])
def get_guest(id):
    try:
        # Fetch guest data from Supabase
        response = supabase.table("guest").select("*").eq("guest_id", id).execute()

        # If no data is found, return a 404 error
        if not response.data:
            return jsonify({"error": "No guest found"}), 404
        
        guest = response.data[0]  # Get the first guest

        # Check if the query parameter 'field' is provided to get a specific value
        field = request.args.get('field')

        if field and field in guest:
            # Return the specific field
            return jsonify({field: guest[field]}), 200
        else:
            # Return all guest details
            return jsonify({"guest": guest}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update Loyalty Points to Guest
# Get Information from Request Body (guest_id, points, operation (add, subtract))
@app.route('/updateloyalty', methods = ['PUT'])
def update_loyalty():
    try:
        # Get the request JSON data
        data = request.get_json()

        guest_id = data['guest_id']
        points = data['points']
        operation = data['operation']

        # Query the guest table to get current loyalty points
        response = supabase.table("guest").select("guest_id", "loyalty_points").eq("guest_id", guest_id).execute()
        
        if not response.data:
            return jsonify({"error": "Guest not found"}), 404

        # Extract the current loyalty points
        current_loyalty_points = response.data[0].get('loyalty_points')

        # Calculate the new loyalty points based on the operation
        if operation == 'add':
            new_loyalty_points = current_loyalty_points + points
        elif operation == 'subtract':
            new_loyalty_points = current_loyalty_points - points

        # Update the guest's loyalty points in the database
        update_response = supabase.table("guest").update({"loyalty_points": new_loyalty_points}).eq("guest_id", guest_id).execute()

        # Check if the update was successful
        if update_response:
            return jsonify({"message": "Loyalty points updated successfully", "new_loyalty_points": new_loyalty_points}), 200
        else:
            return jsonify({"error": "Failed to update loyalty points"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)