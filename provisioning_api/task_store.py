from collections import defaultdict
from uuid import UUID
from .models import Task
from typing import Dict

class InMemoryTaskStore:
    def __init__(self):
        self._tasks: Dict[UUID, Task] = {}

    def add(self, task: Task):
        self._tasks[task.id] = task

    def get(self, task_id: UUID) -> Task | None:
        return self._tasks.get(task_id)
