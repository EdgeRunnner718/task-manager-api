"""线程安全的内存任务存储。

使用 threading.RLock 保护所有读写操作。单进程内安全；
注意这是演示用实现 —— 多副本部署时数据不共享，生产环境应替换为数据库。
"""

import threading
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.models import Task, TaskCreate, TaskStatus, TaskUpdate


class TaskNotFoundError(Exception):
    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"task {task_id} not found")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TaskStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._tasks: dict[UUID, Task] = {}

    def create(self, data: TaskCreate) -> Task:
        with self._lock:
            now = _utcnow()
            task = Task(
                id=uuid4(),
                title=data.title,
                description=data.description,
                status=data.status,
                created_at=now,
                updated_at=now,
            )
            self._tasks[task.id] = task
            return task

    def get(self, task_id: UUID) -> Task:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise TaskNotFoundError(task_id)
            return task

    def list(self, status: TaskStatus | None = None) -> list[Task]:
        with self._lock:
            tasks = list(self._tasks.values())
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at)

    def update(self, task_id: UUID, data: TaskUpdate) -> Task:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise TaskNotFoundError(task_id)
            # exclude_unset=True：只覆盖客户端显式传入的字段
            changes = data.model_dump(exclude_unset=True)
            updated = task.model_copy(update={**changes, "updated_at": _utcnow()})
            self._tasks[task_id] = updated
            return updated

    def delete(self, task_id: UUID) -> None:
        with self._lock:
            if task_id not in self._tasks:
                raise TaskNotFoundError(task_id)
            del self._tasks[task_id]


# 单例 —— 整个应用共享一个存储实例
store = TaskStore()
