import os.path
from email.mime.text import MIMEText  
import base64 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

    except HttpError as error:
        print(f"An error occurred: {error}")


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
  
    # Send an email 
    # !!!! CHANGE HERE !!!
    sender_email = "serviceatpark@gmail.com"
    recipient_email = input("Enter recipient email address: ")
    subject = "Test Email from Python" 
    message_text = "Hello, this is a test email sent using the Gmail API and Python."   #change here accordingly

    send_email(service, sender_email, recipient_email, subject, message_text)

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()