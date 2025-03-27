from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import os.path
from email.mime.text import MIMEText  
import base64 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

CORS(app)

email_blueprint = Blueprint("email", __name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def send_email(service, sender, to, subject, message_text):
    """Create and send an email message."""
    try:
        message = MIMEText(message_text)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        
        print(f"Message Id: {send_message['id']}")
        return {"message_id": send_message["id"], "status": "Email sent successfully"}

    except HttpError as error:
        print(f"An error occurred: {error}")
        return {"error": str(error)}, 400

def authenticate():
    """Authenticate and refresh the token automatically if needed."""
    creds = None
    # Check if token.json exists and load the stored credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no valid credentials, start the OAuth flow
    if not creds or not creds.valid:
        # If the token is expired but has a refresh token, refresh it automatically
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # Attempt to refresh the token silently
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None  # Clear the credentials if refreshing failed

        # If still no valid credentials, go through OAuth flow to authenticate the user
        if not creds or not creds.valid:
            # Only re-authenticate if token is invalid or refresh failed
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            # Save new credentials for future use
            with open("token.json", "w") as token:
                token.write(creds.to_json())

    # Return the authenticated Gmail API service
    return build("gmail", "v1", credentials=creds)

# TODO: Verify and Remove Comments from Hnin
@email_blueprint.route("/", methods=["POST"])
def sending_email():
  try:
    # Call the Gmail API
    # service = build("gmail", "v1", credentials=creds)
    service = authenticate()
  
    # Send an email 
    # !!!! CHANGE HERE !!!
    data = request.json  # Get data from request
    sender_email = "serviceatpark@gmail.com"
    
    # recipient_email = input("Enter recipient email address: ")
    # subject = "Test Email from Python" 
    # message_text = "Hello, this is a test email sent using the Gmail API and Python."   #change here accordingly
    
    recipient_email = data.get("to")
    subject = data.get("subject")
    message_text = data.get("message")

    response = send_email(service, sender_email, recipient_email, subject, message_text)
    return jsonify(response)

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    # print(f"An error occurred: {error}")
    return jsonify({"error": str(error)}), 500


app.register_blueprint(email_blueprint, url_prefix="/email")

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8088, debug=True)

