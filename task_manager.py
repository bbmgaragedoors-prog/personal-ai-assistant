import json
import logging
import os
import uuid
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)
TASKS_FILE = "tasks.json"


class TaskManager:
      """
          Manages a persistent task list stored in a local JSON file.
              Supports add, list, complete, and delete operations.
                  """

    def __init__(self):
              self.tasks_file = TASKS_FILE
              self.tasks = self._load_tasks()

    def _load_tasks(self) -> list:
              """Load tasks from JSON file."""
              if os.path.exists(self.tasks_file):
                            try:
                                              with open(self.tasks_file, "r") as f:
                                                                    return json.load(f)
                            except Exception as e:
                                              logger.error(f"Error loading tasks: {e}")
                                      return []

          def _save_tasks(self):
                    """Save tasks to JSON file."""
                    try:
                                  with open(self.tasks_file, "w") as f:
                                                    json.dump(self.tasks, f, indent=2, default=str)
                    except Exception as e:
                                  logger.error(f"Error saving tasks: {e}")

                def add_task(self, title: str, due_date: Optional[str] = None, priority: str = "medium") -> dict:
                          """Add a new task."""
                          task = {
                              "id": str(uuid.uuid4())[:8],
                              "title": title,
                              "due_date": due_date,
                              "priority": priority,
                              "completed": False,
                              "created_at": datetime.now().isoformat()
                          }
                          self.tasks.append(task)
                          self._save_tasks()
                          logger.info(f"Task added: {title}")
                          return {"status": "added", "task": task}

    def get_tasks(self, include_completed: bool = False) -> dict:
              """Get all pending tasks."""
              tasks = self.tasks if include_completed else [t for t in self.tasks if not t["completed"]]

        # Sort by priority
              priority_order = {"high": 0, "medium": 1, "low": 2}
              tasks = sorted(tasks, key=lambda x: priority_order.get(x.get("priority", "medium"), 1))

        return {
                      "tasks": tasks,
                      "count": len(tasks),
                      "pending": len([t for t in self.tasks if not t["completed"]])
        }

    def complete_task(self, task_id: str) -> dict:
              """Mark a task as completed."""
              for task in self.tasks:
                            if task["id"] == task_id:
                                              task["completed"] = True
                                              task["completed_at"] = datetime.now().isoformat()
                                              self._save_tasks()
                                              return {"status": "completed", "task": task}
                                      return {"error": f"Task with ID '{task_id}' not found"}

          def delete_task(self, task_id: str) -> dict:
                    """Delete a task permanently."""
                    original_count = len(self.tasks)
                    self.tasks = [t for t in self.tasks if t["id"] != task_id]
                    if len(self.tasks) < original_count:
                                  self._save_tasks()
                                  return {"status": "deleted", "task_id": task_id}
                              return {"error": f"Task with ID '{task_id}' not found"}

    def get_overdue_tasks(self) -> dict:
              """Get tasks that are past their due date."""
        now = datetime.now()
        overdue = []
        for task in self.tasks:
                      if not task["completed"] and task.get("due_date"):
                                        try:
                                                              due = datetime.fromisoformat(task["due_date"])
                                                              if due < now:
                                                                                        overdue.append(task)
                                        except Exception:
                                                              pass
                                                  return {"overdue_tasks": overdue, "count": len(overdue)}
