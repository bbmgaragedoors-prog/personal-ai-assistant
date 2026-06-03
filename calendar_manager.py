import logging
import os
import pickle
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import GOOGLE_SCOPES, TIMEZONE

logger = logging.getLogger(__name__)
TOKEN_FILE = "calendar_token.pickle"
CREDS_FILE = "google_credentials.json"


class CalendarManager:
      """
          Manages Google Calendar: add events and retrieve upcoming events.
              Shares credentials file with EmailManager but uses separate token.
                  """

    def __init__(self):
              self.timezone = ZoneInfo(TIMEZONE)
              self.service = self._authenticate()

    def _authenticate(self):
              """Authenticate with Google Calendar API."""
              creds = None
              if os.path.exists(TOKEN_FILE):
                            with open(TOKEN_FILE, "rb") as token:
                                              creds = pickle.load(token)

                        if not creds or not creds.valid:
                                      if creds and creds.expired and creds.refresh_token:
                                                        creds.refresh(Request())
                        else:
                if not os.path.exists(CREDS_FILE):
                                      logger.error(f"Missing {CREDS_FILE}")
                                      return None
                                  flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, GOOGLE_SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "wb") as token:
                              pickle.dump(creds, token)

        return build("calendar", "v3", credentials=creds)

    def add_event(self, title: str, start_time: str, end_time: str, description: str = "") -> dict:
              """Add a new event to the primary calendar."""
        if not self.service:
                      return {"error": "Calendar not authenticated"}
                  try:
                                event = {
                                                  "summary": title,
                                                  "description": description,
                                                  "start": {"dateTime": start_time, "timeZone": TIMEZONE},
                                                  "end": {"dateTime": end_time, "timeZone": TIMEZONE},
                                }
                                created = self.service.events().insert(calendarId="primary", body=event).execute()
                                logger.info(f"Event created: {created.get('htmlLink')}")
                                return {
                                    "status": "created",
                                    "title": title,
                                    "start": start_time,
                                    "end": end_time,
                                    "link": created.get("htmlLink")
                                }
except Exception as e:
            logger.error(f"Error adding event: {e}")
            return {"error": str(e)}

    def get_upcoming_events(self, days_ahead: int = 7) -> dict:
              """Get upcoming events for the next N days."""
        if not self.service:
                      return {"error": "Calendar not authenticated"}
                  try:
                                now = datetime.now(tz=self.timezone)
                                time_min = now.isoformat()
                                time_max = (now + timedelta(days=days_ahead)).isoformat()

            events_result = self.service.events().list(
                              calendarId="primary",
                              timeMin=time_min,
                              timeMax=time_max,
                              maxResults=20,
                              singleEvents=True,
                              orderBy="startTime"
            ).execute()

            events = events_result.get("items", [])
            if not events:
                              return {"events": [], "message": f"No events in the next {days_ahead} days"}

            formatted = []
            for e in events:
                              start = e["start"].get("dateTime", e["start"].get("date"))
                              formatted.append({
                                  "title": e.get("summary", "No Title"),
                                  "start": start,
                                  "end": e["end"].get("dateTime", e["end"].get("date")),
                                  "description": e.get("description", "")
                              })

            return {"events": formatted, "count": len(formatted)}

except Exception as e:
            logger.error(f"Error getting events: {e}")
            return {"error": str(e)}
