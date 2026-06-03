import logging
import json
import os
from flask import Flask, request, jsonify
from config import FLASK_SECRET_KEY, FLASK_HOST, FLASK_PORT, DEBUG
from assistant import PersonalAssistant
from whatsapp_handler import WhatsAppHandler
from reminder_manager import ReminderManager
from email_manager import EmailManager
from calendar_manager import CalendarManager
from task_manager import TaskManager

# Configure logging
logging.basicConfig(
          level=logging.INFO,
          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
          handlers=[
                        logging.FileHandler('assistant.log'),
                        logging.StreamHandler()
          ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

ENV_RAILWAY_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')

# Initialize components
logger.info("Initializing Personal AI Assistant components...")

assistant = PersonalAssistant()
whatsapp = WhatsAppHandler()
reminder_mgr = ReminderManager(whatsapp)

@app.route('/health', methods=['GET'])
def health_check():
          return jsonify({'status': 'healthy', 'service': 'Personal AI Assistant'}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
          try:
                        incoming_msg = request.values.get('Body', '').strip()
                        from_number = request.values.get('From', '')

              if not whatsapp.is_owner(from_number):
                                logger.warning(f"Unauthorized access attempt from {from_number}")
                                return '', 403

        logger.info(f"Received message from owner: {incoming_msg[:50]}...")

        response_text = assistant.process_message(incoming_msg, from_number)

        success = whatsapp.send_message(whatsapp.owner_number, response_text)
        if not success:
                          logger.error("Failed to send response via WhatsApp")

        return '', 200

except Exception as e:
        logger.error(f"Error in webhook: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/send_whatsapp', methods=['POST'])
def send_whatsapp():
          try:
                        data = request.json
                        to_number = data.get('to')
                        message = data.get('message')
                        confirmed = data.get('confirmed', False)

        if not to_number or not message:
                          return jsonify({'error': 'Missing to or message'}), 400

        if not confirmed:
                          return jsonify({
                                                'requires_confirmation': True,
                                                'message': f'Send message to {to_number}?',
                                                'preview': message
                          }), 200

        success = whatsapp.send_message(to_number, message)
        if success:
                          return jsonify({'status': 'sent'}), 200
else:
            return jsonify({'error': 'Failed to send'}), 500

except Exception as e:
        logger.error(f"Error sending WhatsApp: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/oauth2callback', methods=['GET'])
def oauth2callback():
          try:
                        from google_auth_oauthlib.flow import Flow
                        from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SCOPES

        flow = Flow.from_client_secrets_file(
                          GOOGLE_CREDENTIALS_FILE,
                          scopes=GOOGLE_SCOPES,
                          redirect_uri=request.base_url
        )
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        token_data = {
                          'token': credentials.token,
                          'refresh_token': credentials.refresh_token,
                          'token_uri': credentials.token_uri,
                          'client_id': credentials.client_id,
                          'client_secret': credentials.client_secret,
                          'scopes': list(credentials.scopes) if credentials.scopes else []
        }

        with open('google_token.json', 'w') as f:
                          json.dump(token_data, f)

        logger.info("Google OAuth2 credentials saved successfully")
        return 'Google authentication successful! You can close this window.', 200

except Exception as e:
        logger.error(f"OAuth callback error: {e}", exc_info=True)
        return f'Authentication error: {str(e)}', 500

@app.route('/authorize_google', methods=['GET'])
def authorize_google():
          try:
                        from google_auth_oauthlib.flow import Flow
                        from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SCOPES

        if ENV_RAILWAY_URL:
                          redirect_uri = f"https://{ENV_RAILWAY_URL}/oauth2callback"
else:
            redirect_uri = request.host_url.rstrip('/') + '/oauth2callback'

        flow = Flow.from_client_secrets_file(
                          GOOGLE_CREDENTIALS_FILE,
                          scopes=GOOGLE_SCOPES,
                          redirect_uri=redirect_uri
        )
        authorization_url, state = flow.authorization_url(
                          access_type='offline',
                          include_granted_scopes='true'
        )
        return jsonify({'authorization_url': authorization_url}), 200

except Exception as e:
        logger.error(f"Error creating auth URL: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
          logger.info(f"Starting Personal AI Assistant on {FLASK_HOST}:{FLASK_PORT}")
    reminder_mgr.start()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG)
