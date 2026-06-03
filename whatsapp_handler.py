import logging
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from config import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER, YOUR_WHATSAPP_NUMBER
)

logger = logging.getLogger(__name__)


class WhatsAppHandler:
      """
          Handles all WhatsApp communication via Twilio.
              Incoming messages are processed by the assistant.
                  Outgoing messages to OTHERS require owner confirmation.
                      Messages to the owner (notifications/reminders) are sent automatically.
                          """

    def __init__(self):
              self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
              self.from_number = TWILIO_WHATSAPP_NUMBER
              self.owner_number = YOUR_WHATSAPP_NUMBER

    def send_message(self, to: str, body: str) -> dict:
              """
                      Send a WhatsApp message to any number.
                              For messages to non-owner numbers, confirmation is handled by assistant.py.
                                      """
              try:
                            # Ensure number is in whatsapp: format
                            if not to.startswith("whatsapp:"):
                                              to = f"whatsapp:{to}"

                            message = self.client.messages.create(
                                from_=self.from_number,
                                body=body,
                                to=to
                            )
                            logger.info(f"Message sent to {to}, SID: {message.sid}")
                            return {"status": "sent", "sid": message.sid, "to": to}
except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return {"status": "error", "error": str(e)}

    def notify_owner(self, message: str) -> dict:
              """
                      Send a notification or reminder directly to the owner.
                              This does NOT require confirmation.
                                      """
              return self.send_message(self.owner_number, message)

    def process_incoming(self, from_number: str, body: str, assistant) -> str:
              """
                      Process an incoming WhatsApp message.
                              Only accepts messages from the owner's number.
                                      Returns the response text to send back.
                                              """
              # Security: only respond to owner
              normalized_from = from_number if from_number.startswith("whatsapp:") else f"whatsapp:{from_number}"
              normalized_owner = self.owner_number if self.owner_number.startswith("whatsapp:") else f"whatsapp:{self.owner_number}"

        if normalized_from != normalized_owner:
                      logger.warning(f"Received message from unknown number: {from_number}. Ignoring.")
                      return None  # Do not respond to non-owners

        logger.info(f"Processing message from owner: {body[:50]}...")
        response = assistant.process_message(body)
        return response

    def create_twiml_response(self, message: str) -> str:
              """Create a TwiML response for Twilio webhook."""
              resp = MessagingResponse()
              resp.message(message)
              return str(resp)
