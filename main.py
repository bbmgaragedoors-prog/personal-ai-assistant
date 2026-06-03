import logging
import signal
import sys
from flask import Flask, request, Response
from config import FLASK_SECRET_KEY, PORT, DEBUG
from assistant import PersonalAssistant
from whatsapp_handler import WhatsAppHandler
from email_manager import EmailManager
from calendar_manager import CalendarManager
from task_manager import TaskManager
from web_search import WebSearch
from reminder_manager import ReminderManager

# Configure logging
logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
      handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("assistant.log")
      ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Initialize all components
logger.info("Initializing Personal AI Assistant...")

try:
      whatsapp = WhatsAppHandler()
      logger.info("WhatsApp handler ready")
except Exception as e:
      logger.error(f"WhatsApp init failed: {e}")
      whatsapp = None

try:
      email_mgr = EmailManager()
      logger.info("Email manager ready")
except Exception as e:
      logger.warning(f"Email manager init failed (will retry on use): {e}")
      email_mgr = None

try:
      calendar_mgr = CalendarManager()
      logger.info("Calendar manager ready")
except Exception as e:
      logger.warning(f"Calendar manager init failed: {e}")
      calendar_mgr = None

task_mgr = TaskManager()
web_search = WebSearch()

try:
      reminder_mgr = ReminderManager(whatsapp_handler=whatsapp)
      logger.info("Reminder manager ready")
except Exception as e:
      logger.warning(f"Reminder manager init failed: {e}")
      reminder_mgr = None

# Initialize the core assistant
assistant = PersonalAssistant(
      email_manager=email_mgr,
      calendar_manager=calendar_mgr,
      task_manager=task_mgr,
      web_search=web_search,
      reminder_manager=reminder_mgr,
      whatsapp_handler=whatsapp
)
logger.info("Personal AI Assistant initialized and ready!")


@app.route("/webhook", methods=["POST"])
def webhook():
      """
          Twilio WhatsApp webhook endpoint.
              Receives incoming WhatsApp messages and returns a TwiML response.
                  """
      from_number = request.form.get("From", "")
      body = request.form.get("Body", "").strip()

    logger.info(f"Incoming WhatsApp from {from_number}: {body[:80]}")

    if not body:
              return Response(whatsapp.create_twiml_response("Please send a text message."),
                                                      mimetype="application/xml")

    # Process through the assistant (security check inside)
    if whatsapp:
              response_text = whatsapp.process_incoming(from_number, body, assistant)
else:
          response_text = assistant.process_message(body)

    if not response_text:
              # Message from unknown number - no response
              return Response("", mimetype="application/xml")

    twiml = whatsapp.create_twiml_response(response_text)
    return Response(twiml, mimetype="application/xml")


@app.route("/health", methods=["GET"])
def health():
      """Health check endpoint."""
      return {
          "status": "ok",
          "components": {
              "whatsapp": whatsapp is not None,
              "email": email_mgr is not None,
              "calendar": calendar_mgr is not None,
              "tasks": True,
              "web_search": True,
              "reminders": reminder_mgr is not None
          }
      }


@app.route("/", methods=["GET"])
def index():
      return "Personal AI Assistant is running. Send messages via WhatsApp."


def handle_shutdown(sig, frame):
      """Graceful shutdown."""
      logger.info("Shutting down...")
      if reminder_mgr:
                reminder_mgr.shutdown()
            sys.exit(0)


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


if __name__ == "__main__":
      logger.info(f"Starting Flask server on port {PORT}")
    logger.info("Set your Twilio webhook URL to: https://YOUR_DOMAIN/webhook")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
