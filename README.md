# Personal AI Assistant

A production-ready personal AI assistant powered by **GPT-4**, accessible via **WhatsApp**. It manages your emails, calendar, tasks, reminders, and searches the web — all through natural conversation.

## Features

- **WhatsApp Interface** — Chat with your assistant directly from WhatsApp
- - **GPT-4 Powered** — Understands natural language, handles complex requests
  - - **Gmail Integration** — Read unread emails and send emails
    - - **Google Calendar** — Add and view upcoming events
      - - **Task Manager** — Persistent to-do list with priorities and due dates
        - - **Smart Reminders** — Schedule reminders that arrive as WhatsApp messages
          - - **Web Search** — Real-time DuckDuckGo search (no API key needed)
            - - **Owner-Only Security** — Only responds to your WhatsApp number
              - - **Confirmation Gate** — Sending WhatsApp messages to others always requires your explicit YES
               
                - ## Architecture
               
                - ```
                  main.py               Flask server + Twilio webhook
                  assistant.py          GPT-4 core + tool routing + conversation memory
                  whatsapp_handler.py   Twilio send/receive + owner verification
                  email_manager.py      Gmail OAuth2 read/send
                  calendar_manager.py   Google Calendar OAuth2 add/list
                  task_manager.py       Local JSON task list
                  web_search.py         DuckDuckGo search + page fetch
                  reminder_manager.py   APScheduler-based reminders via WhatsApp
                  config.py             All configuration from .env
                  ```

                  ## Prerequisites

                  - Python 3.11+
                  - - A [Twilio account](https://twilio.com) with WhatsApp sandbox enabled
                    - - An [OpenAI account](https://platform.openai.com) with GPT-4 access
                      - - A [Google Cloud project](https://console.cloud.google.com) with Gmail + Calendar APIs enabled
                        - - A server with a public HTTPS URL (e.g. Railway, Render, VPS with ngrok)
                         
                          - ## Setup
                         
                          - ### 1. Clone the repository
                         
                          - ```bash
                            git clone https://github.com/bbmgaragedoors-prog/personal-ai-assistant.git
                            cd personal-ai-assistant
                            ```

                            ### 2. Install dependencies

                            ```bash
                            pip install -r requirements.txt
                            ```

                            ### 3. Configure environment variables

                            ```bash
                            cp .env.example .env
                            ```

                            Edit `.env` and fill in all values:

                            | Variable | Description |
                            |---|---|
                            | `OPENAI_API_KEY` | Your OpenAI API key |
                            | `TWILIO_ACCOUNT_SID` | Twilio Account SID |
                            | `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
                            | `TWILIO_WHATSAPP_NUMBER` | Your Twilio WhatsApp number (e.g. `whatsapp:+14155238886`) |
                            | `YOUR_WHATSAPP_NUMBER` | Your personal WhatsApp number (e.g. `whatsapp:+12125551234`) |
                            | `GOOGLE_CLIENT_ID` | Google OAuth2 Client ID |
                            | `GOOGLE_CLIENT_SECRET` | Google OAuth2 Client Secret |
                            | `OWNER_NAME` | Your name (used in the system prompt) |
                            | `TIMEZONE` | Your timezone (e.g. `America/New_York`) |

                            ### 4. Set up Google OAuth credentials

                            1. Go to [Google Cloud Console](https://console.cloud.google.com)
                            2. 2. Create a project and enable **Gmail API** and **Google Calendar API**
                               3. 3. Create **OAuth 2.0 Client ID** credentials (Desktop app type)
                                  4. 4. Download the JSON file and save it as `google_credentials.json` in the project root
                                     5. 5. On first run, a browser window will open to authorize access
                                       
                                        6. ### 5. Configure Twilio WhatsApp
                                       
                                        7. 1. In your Twilio console, go to **Messaging > Try it out > Send a WhatsApp message**
                                           2. 2. Follow the sandbox setup instructions
                                              3. 3. Set the webhook URL to: `https://YOUR_DOMAIN/webhook`
                                                
                                                 4. ### 6. Run the server
                                                
                                                 5. ```bash
                                                    python main.py
                                                    ```

                                                    For production use:

                                                    ```bash
                                                    gunicorn main:app --bind 0.0.0.0:5000 --workers 1 --threads 4
                                                    ```

                                                    > Use `--workers 1` to avoid shared state issues with the scheduler.
                                                    >
                                                    > ## Usage Examples
                                                    >
                                                    > Send these messages to your assistant on WhatsApp:
                                                    >
                                                    > | Message | Action |
                                                    > |---|---|
                                                    > | `What are my unread emails?` | Shows latest unread emails |
                                                    > | `Send an email to john@example.com about the meeting tomorrow` | Sends email |
                                                    > | `Add a meeting with the team on Friday at 2pm` | Creates calendar event |
                                                    > | `What do I have on my calendar this week?` | Lists upcoming events |
                                                    > | `Add task: Buy groceries, high priority` | Adds task |
                                                    > | `What are my pending tasks?` | Lists open tasks |
                                                    > | `Remind me to call mom at 6pm today` | Sets a reminder |
                                                    > | `Search for the latest news about AI` | Web search |
                                                    > | `Send a WhatsApp to +1234567890 saying I'll be late` | Asks for your confirmation first |
                                                    >
                                                    > ## Security
                                                    >
                                                    > - **Only your WhatsApp number** can interact with the assistant
                                                    > - - Messages from unknown numbers are silently ignored
                                                    >   - - Sending WhatsApp messages to third parties **always** requires your explicit confirmation
                                                    >     - - API keys and credentials are stored in `.env` (never committed to git)
                                                    >      
                                                    >       - ## License
                                                    >      
                                                    >       - MIT
