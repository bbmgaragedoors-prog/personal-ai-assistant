import base64
import logging
import os
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import GOOGLE_SCOPES

logger = logging.getLogger(__name__)
TOKEN_FILE = "gmail_token.pickle"
CREDS_FILE = "google_credentials.json"


class EmailManager:
      """
          Manages Gmail operations: read unread emails and send emails.
              Uses OAuth2 for authentication.
                  """

    def __init__(self):
              self.service = self._authenticate()

    def _authenticate(self):
              """Authenticate with Gmail API."""
              creds = None
              if os.path.exists(TOKEN_FILE):
                            with open(TOKEN_FILE, "rb") as token:
                                              creds = pickle.load(token)

                        if not creds or not creds.valid:
                                      if creds and creds.expired and creds.refresh_token:
                                                        creds.refresh(Request())
                        else:
                if not os.path.exists(CREDS_FILE):
                                      logger.error(f"Missing {CREDS_FILE}. Download from Google Cloud Console.")
                                      return None
                                  flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, GOOGLE_SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "wb") as token:
                              pickle.dump(creds, token)

        return build("gmail", "v1", credentials=creds)

    def get_unread_emails(self, max_results: int = 5) -> dict:
              """Fetch unread emails from inbox."""
        if not self.service:
                      return {"error": "Gmail not authenticated"}
                  try:
                                results = self.service.users().messages().list(
                                                  userId="me",
                                                  labelIds=["INBOX", "UNREAD"],
                                                  maxResults=max_results
                                ).execute()

            messages = results.get("messages", [])
            if not messages:
                              return {"emails": [], "count": 0, "message": "No unread emails"}

            emails = []
            for msg in messages:
                              msg_data = self.service.users().messages().get(
                                                    userId="me", id=msg["id"], format="full"
                              ).execute()

                headers = {h["name"]: h["value"] for h in msg_data["payload"]["headers"]}
                snippet = msg_data.get("snippet", "")

                emails.append({
                                      "id": msg["id"],
                                      "from": headers.get("From", "Unknown"),
                                      "subject": headers.get("Subject", "No Subject"),
                                      "date": headers.get("Date", ""),
                                      "snippet": snippet
                })

            return {"emails": emails, "count": len(emails)}

except Exception as e:
            logger.error(f"Error reading emails: {e}")
            return {"error": str(e)}

    def send_email(self, to: str, subject: str, body: str) -> dict:
              """Send an email via Gmail."""
        if not self.service:
                      return {"error": "Gmail not authenticated"}
                  try:
                                message = MIMEMultipart()
                                message["to"] = to
                                message["subject"] = subject
                                message.attach(MIMEText(body, "plain"))

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            sent = self.service.users().messages().send(
                              userId="me", body={"raw": raw}
            ).execute()

            logger.info(f"Email sent to {to}, ID: {sent['id']}")
            return {"status": "sent", "id": sent["id"], "to": to, "subject": subject}

except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"error": str(e)}
