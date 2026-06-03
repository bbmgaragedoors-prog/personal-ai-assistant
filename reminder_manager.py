import json
import logging
import os
import uuid
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from zoneinfo import ZoneInfo
from config import TIMEZONE

logger = logging.getLogger(__name__)
REMINDERS_FILE = "reminders.json"


class ReminderManager:
      """
          Manages scheduled reminders using APScheduler.
              When a reminder fires, it sends a WhatsApp message to the owner.
                  """

    def __init__(self, whatsapp_handler=None):
              self.whatsapp_handler = whatsapp_handler
              self.timezone = ZoneInfo(TIMEZONE)
              self.reminders = self._load_reminders()
              self.scheduler = BackgroundScheduler(timezone=TIMEZONE)
              self.scheduler.start()
              self._reschedule_pending_reminders()
              logger.info("ReminderManager started")

    def _load_reminders(self) -> list:
              """Load reminders from persistent storage."""
              if os.path.exists(REMINDERS_FILE):
                            try:
                                              with open(REMINDERS_FILE, "r") as f:
                                                                    return json.load(f)
                            except Exception as e:
                                              logger.error(f"Error loading reminders: {e}")
                                      return []

          def _save_reminders(self):
                    """Save reminders to file."""
                    try:
                                  with open(REMINDERS_FILE, "w") as f:
                                                    json.dump(self.reminders, f, indent=2, default=str)
                    except Exception as e:
                                  logger.error(f"Error saving reminders: {e}")

                def set_reminder(self, message: str, remind_at: str) -> dict:
                          """
                                  Schedule a reminder.
                                          remind_at: ISO 8601 datetime string.
                                                  """
                          try:
                                        remind_dt = datetime.fromisoformat(remind_at)
                                        if remind_dt.tzinfo is None:
                                                          remind_dt = remind_dt.replace(tzinfo=self.timezone)

                                        if remind_dt <= datetime.now(tz=self.timezone):
                                                          return {"error": "Reminder time must be in the future"}

                                        reminder_id = str(uuid.uuid4())[:8]
                                        reminder = {
                                            "id": reminder_id,
                                            "message": message,
                                            "remind_at": remind_at,
                                            "fired": False,
                                            "created_at": datetime.now().isoformat()
                                        }

                              self.reminders.append(reminder)
            self._save_reminders()

            # Schedule the job
            self.scheduler.add_job(
                              self._fire_reminder,
                              trigger=DateTrigger(run_date=remind_dt),
                              args=[reminder_id, message],
                              id=reminder_id
            )

            logger.info(f"Reminder set for {remind_at}: {message}")
            return {
                              "status": "scheduled",
                              "id": reminder_id,
                              "message": message,
                              "remind_at": remind_at
            }

except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            return {"error": str(e)}

    def _fire_reminder(self, reminder_id: str, message: str):
              """Called by the scheduler when a reminder fires."""
        logger.info(f"Firing reminder {reminder_id}: {message}")

        # Mark as fired
        for r in self.reminders:
                      if r["id"] == reminder_id:
                                        r["fired"] = True
                                self._save_reminders()

        # Send WhatsApp notification to owner
        if self.whatsapp_handler:
                      self.whatsapp_handler.notify_owner(f"Reminder: {message}")
else:
            logger.warning("No WhatsApp handler - reminder fired but not delivered")

    def _reschedule_pending_reminders(self):
              """On startup, reschedule any reminders that haven't fired yet."""
        now = datetime.now(tz=self.timezone)
        rescheduled = 0
        for reminder in self.reminders:
                      if not reminder.get("fired", False):
                                        try:
                                                              remind_dt = datetime.fromisoformat(reminder["remind_at"])
                                                              if remind_dt.tzinfo is None:
                                                                                        remind_dt = remind_dt.replace(tzinfo=self.timezone)
                                                                                    if remind_dt > now:
                                                                                                              self.scheduler.add_job(
                                                                                                                                            self._fire_reminder,
                                                                                                                                            trigger=DateTrigger(run_date=remind_dt),
                                                                                                                                            args=[reminder["id"], reminder["message"]],
                                                                                                                                            id=reminder["id"]
                                                                                                                )
                                                                                                              rescheduled += 1
                                          except Exception as e:
                    logger.error(f"Error rescheduling reminder {reminder['id']}: {e}")
        logger.info(f"Rescheduled {rescheduled} pending reminders")

    def get_reminders(self) -> dict:
              """Get all pending (not yet fired) reminders."""
        pending = [r for r in self.reminders if not r.get("fired", False)]
        return {"reminders": pending, "count": len(pending)}

    def cancel_reminder(self, reminder_id: str) -> dict:
              """Cancel a scheduled reminder."""
        for r in self.reminders:
                      if r["id"] == reminder_id:
                                        r["fired"] = True  # Mark as done
                self._save_reminders()
                try:
                                      self.scheduler.remove_job(reminder_id)
except Exception:
                    pass
                return {"status": "cancelled", "id": reminder_id}
        return {"error": f"Reminder '{reminder_id}' not found"}

    def shutdown(self):
              """Gracefully stop the scheduler."""
        self.scheduler.shutdown(wait=False)
