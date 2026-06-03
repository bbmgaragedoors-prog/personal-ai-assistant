import json
import logging
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, SYSTEM_PROMPT, MAX_HISTORY_LENGTH

logger = logging.getLogger(__name__)


class PersonalAssistant:
      """
          Core AI assistant powered by GPT-4.
              Manages conversation history and routes tool calls.
                  """

    def __init__(self, email_manager=None, calendar_manager=None,
                                  task_manager=None, web_search=None,
                                  reminder_manager=None, whatsapp_handler=None):
                                            self.client = OpenAI(api_key=OPENAI_API_KEY)
                                            self.conversation_history = []
                                            self.email_manager = email_manager
                                            self.calendar_manager = calendar_manager
                                            self.task_manager = task_manager
                                            self.web_search = web_search
                                            self.reminder_manager = reminder_manager
                                            self.whatsapp_handler = whatsapp_handler
                                            self.pending_confirmation = None  # Stores action awaiting owner approval
        self.tools = self._define_tools()

    def _define_tools(self):
              return [
                            {
                                              "type": "function",
                                              "function": {
                                                                    "name": "search_web",
                                                                    "description": "Search the web for current information",
                                                                    "parameters": {
                                                                                              "type": "object",
                                                                                              "properties": {
                                                                                                                            "query": {"type": "string", "description": "Search query"}
                                                                                                },
                                                                                              "required": ["query"]
                                                                    }
                                              }
                            },
                            {
                                              "type": "function",
                                              "function": {
                                                                    "name": "send_email",
                                                                    "description": "Send an email via Gmail",
                                                                    "parameters": {
                                                                                              "type": "object",
                                                                                              "properties": {
                                                                                                                            "to": {"type": "string"},
                                                                                                                            "subject": {"type": "string"},
                                                                                                                            "body": {"type": "string"}
                                                                                                },
                                                                                              "required": ["to", "subject", "body"]
                                                                    }
                                              }
                            },
                            {
                                              "type": "function",
                                              "function": {
                                                                    "name": "read_emails",
                                                                    "description": "Read recent unread emails from Gmail",
                                                                    "parameters": {
                                                                                              "type": "object",
                                                                                              "properties": {
                                                                                                                            "max_results": {"type": "integer", "default": 5}
                                                                                                }
                                                                    }
                                              }
                            },
                            {
                                              "type": "function",
                                              "function": {
                                                                    "name": "add_calendar_event",
                                                                    "description": "Add an event to Google Calendar",
                                                                    "parameters": {
                                                                                              "type": "object",
                                                                                              "properties": {
                                                                                                                            "title": {"type": "string"},
                                                                                                                            "start_time": {"type": "string", "description": "ISO 8601 format"},
                                                                                                                            "end_time": {"type": "string"},
                                                                                                                            "description": {"type": "string"}
                                                                                                },
                                                                                              "required": ["title", "start_time", "end_time"]
                                                                    }
                                              }
                            },
                            {
                                              "type": "function",
                                              "function": {
                                                                    "name": "get_calendar_events",
                                                                    "description": "Get upcoming calendar events",
                                                                    "parameters": {
                                                                                              "type": "object",
                                                                                              "properties": {
                                                                                                                            "days_ahead": {"type": "integer", "default": 7}
                                                                                                }
                                                                    }
                                              }
                            },
                            {
                                              "type": "function",
                                              "function": {
                                                                    "name": "add_task",
                                                                    "description": "Add a task to the task list",
                                                                    "parameters": {
                                                                                              "type": "object",
                                                                                              "properties": {
                                                                                                                            "title": {"type": "string"},
                                                                                                                            "due_date": {"type": "string"},
                                                                                                                            "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                                                                                                },
                                                                                              "required": ["title"]
                                                                    }
                                              }
                            },
                            {
                                              "type": "function",
                                              "function": {
                                                                    "name": "get_tasks",
                                                                    "description": "Get current task list",
                                                                    "parameters": {"type": "object", "properties": {}}
                                              }
                            },
                            {
                                              "type": "function",
                                              "function": {
                                                                    "name": "complete_task",
                                                                    "description": "Mark a task as completed",
                                                                    "parameters": {
                                                                                              "type": "object",
                                                                                              "properties": {
                                                                                                                            "task_id": {"type": "string"}
                                                                                                },
                                                                                              "required": ["task_id"]
                                                                    }
                                              }
                            },
                            {
                                              "type": "function",
                                              "function": {
                                                                    "name": "set_reminder",
                                                                    "description": "Set a reminder for a specific time",
                                                                    "parameters": {
                                                                                              "type": "object",
                                                                                              "properties": {
                                                                                                                            "message": {"type": "string"},
                                                                                                                            "remind_at": {"type": "string", "description": "ISO 8601 datetime"}
                                                                                                },
                                                                                              "required": ["message", "remind_at"]
                                                                    }
                                              }
                            },
                            {
                                              "type": "function",
                                              "function": {
                                                                    "name": "send_whatsapp_message",
                                                                    "description": "Send a WhatsApp message to someone. ALWAYS requires owner confirmation first.",
                                                                    "parameters": {
                                                                                              "type": "object",
                                                                                              "properties": {
                                                                                                                            "to": {"type": "string", "description": "Phone number with country code"},
                                                                                                                            "message": {"type": "string"}
                                                                                                },
                                                                                              "required": ["to", "message"]
                                                                    }
                                              }
                            }
              ]

    def _execute_tool(self, tool_name, tool_args):
              """Execute a tool call and return the result."""
              try:
                            if tool_name == "search_web" and self.web_search:
                                              return self.web_search.search(tool_args["query"])

                            elif tool_name == "send_email" and self.email_manager:
                                              return self.email_manager.send_email(
                                                                    tool_args["to"], tool_args["subject"], tool_args["body"]
                                              )

                            elif tool_name == "read_emails" and self.email_manager:
                                              max_r = tool_args.get("max_results", 5)
                                              return self.email_manager.get_unread_emails(max_r)

                            elif tool_name == "add_calendar_event" and self.calendar_manager:
                                              return self.calendar_manager.add_event(
                                                                    tool_args["title"],
                                                                    tool_args["start_time"],
                                                                    tool_args["end_time"],
                                                                    tool_args.get("description", "")
                                              )

                            elif tool_name == "get_calendar_events" and self.calendar_manager:
                                              return self.calendar_manager.get_upcoming_events(
                                                                    tool_args.get("days_ahead", 7)
                                              )

                            elif tool_name == "add_task" and self.task_manager:
                                              return self.task_manager.add_task(
                                                                    tool_args["title"],
                                                                    tool_args.get("due_date"),
                                                                    tool_args.get("priority", "medium")
                                              )

                            elif tool_name == "get_tasks" and self.task_manager:
                                              return self.task_manager.get_tasks()

                            elif tool_name == "complete_task" and self.task_manager:
                                              return self.task_manager.complete_task(tool_args["task_id"])

                            elif tool_name == "set_reminder" and self.reminder_manager:
                                              return self.reminder_manager.set_reminder(
                                                                    tool_args["message"], tool_args["remind_at"]
                                              )

                            elif tool_name == "send_whatsapp_message":
                                              # This always requires owner confirmation - handled at a higher level
                                              return {"status": "pending_confirmation",
                                                                              "to": tool_args["to"],
                                                                              "message": tool_args["message"]}

                            else:
                                              return {"error": f"Tool '{tool_name}' not available"}

except Exception as e:
            logger.error(f"Tool {tool_name} error: {e}")
            return {"error": str(e)}

    def process_message(self, user_message):
              """
                      Process a message from the owner and return a response.
                              Handles tool calls automatically.
                                      """
              # Check if this is a confirmation for a pending action
              if self.pending_confirmation:
                            return self._handle_confirmation(user_message)

        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Trim history if too long
        if len(self.conversation_history) > MAX_HISTORY_LENGTH:
                      self.conversation_history = self.conversation_history[-MAX_HISTORY_LENGTH:]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.conversation_history

        # Agentic loop - keep calling GPT until no more tool calls
        while True:
                      response = self.client.chat.completions.create(
                                        model=OPENAI_MODEL,
                                        messages=messages,
                                        tools=self.tools,
                                        tool_choice="auto"
                      )

            choice = response.choices[0]
            messages.append(choice.message)

            if choice.finish_reason == "stop":
                              # Final text response
                              final_response = choice.message.content
                              self.conversation_history.append(
                                  {"role": "assistant", "content": final_response}
                              )
                              return final_response

elif choice.finish_reason == "tool_calls":
                  tool_results = []
                  whatsapp_pending = None

                for tool_call in choice.message.tool_calls:
                                      tool_name = tool_call.function.name
                                      tool_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    result = self._execute_tool(tool_name, tool_args)

                    # Check if WhatsApp message needs confirmation
                    if isinstance(result, dict) and result.get("status") == "pending_confirmation":
                                              whatsapp_pending = result
                                              result = {"status": "awaiting_owner_confirmation"}

                    tool_results.append({
                                              "role": "tool",
                                              "tool_call_id": tool_call.id,
                                              "content": json.dumps(result)
                    })

                messages.extend(tool_results)

                # If WhatsApp confirmation needed, pause and ask owner
                if whatsapp_pending:
                                      confirm_msg = (
                                                                f"I need your permission to send this WhatsApp message:\n"
                                                                f"To: {whatsapp_pending['to']}\n"
                                                                f"Message: {whatsapp_pending['message']}\n\n"
                                                                f"Reply YES to confirm or NO to cancel."
                                      )
                                      self.pending_confirmation = whatsapp_pending
                                      self.conversation_history.append(
                                          {"role": "assistant", "content": confirm_msg}
                                      )
                                      return confirm_msg
else:
                  break

        return "I encountered an issue processing your request. Please try again."

    def _handle_confirmation(self, user_message):
              """Handle owner's YES/NO for a pending WhatsApp send."""
              pending = self.pending_confirmation
              self.pending_confirmation = None

        if user_message.strip().upper() in ["YES", "Y", "CONFIRM", "OK", "SEND"]:
                      if self.whatsapp_handler:
                                        result = self.whatsapp_handler.send_message(
                                                              pending["to"], pending["message"]
                                        )
                                        response = f"WhatsApp message sent to {pending['to']} successfully."
        else:
                response = "WhatsApp handler not available."
        else:
            response = "Understood. The WhatsApp message was NOT sent."

        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def clear_history(self):
              """Clear conversation history."""
              self.conversation_history = []
              self.pending_confirmation = None
