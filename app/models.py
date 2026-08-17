"""Pydantic 数据模型：请求体、响应体与错误格式。

分层设计：
- TaskCreate  —— POST 请求体（客户端可写的字段）
- TaskUpdate  —— PATCH 请求体（全部可选，仅更新传入字段）
- Task        —— 响应体（包含服务端生成字段：id、时间戳）
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100, examples=["写周报"])
    description: str | None = Field(default=None, max_length=500, examples=["整理本周工作进展"])
    status: TaskStatus = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    """所有字段可选 —— 只更新客户端显式传入的字段（PATCH 语义）。"""

    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    status: TaskStatus | None = None


class Task(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    items: list[Task]
    total: int


class ErrorResponse(BaseModel):
    detail: str
    code: str
