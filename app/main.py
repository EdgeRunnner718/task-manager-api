"""Task Manager API —— FastAPI 应用入口。"""

import time
from uuid import UUID

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.logging_config import get_logger, setup_logging
from app.models import (
    ErrorResponse,
    Task,
    TaskCreate,
    TaskListResponse,
    TaskStatus,
    TaskUpdate,
)
from app.storage import TaskNotFoundError, store

setup_logging()
logger = get_logger("task_manager")

app = FastAPI(
    title="Task Manager API",
    version="0.1.0",
    description="任务管理 REST API —— DevOps 演示项目",
)


# ---------- 中间件：请求日志 ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ---------- 异常处理：统一错误格式 ----------
@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    logger.warning("task not found: %s (%s %s)", exc.task_id, request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(detail=str(exc), code="TASK_NOT_FOUND").model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """将 FastAPI 默认的 422 改写为 400，语义更贴近「请求格式错误」。"""
    logger.warning("validation error: %s %s -> %s", request.method, request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            detail="request validation failed",
            code="VALIDATION_ERROR",
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("unhandled error: %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(detail="internal server error", code="INTERNAL_ERROR").model_dump(),
    )


# ---------- 路由 ----------
@app.get("/health")
def health() -> dict:
    """健康检查 —— 供 Kubernetes liveness/readiness 探针使用。"""
    return {"status": "ok"}


@app.post(
    "/api/v1/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def create_task(data: TaskCreate) -> Task:
    task = store.create(data)
    logger.info("task created: %s", task.id)
    return task


@app.get("/api/v1/tasks", response_model=TaskListResponse)
def list_tasks(status: TaskStatus | None = None) -> TaskListResponse:
    tasks = store.list(status=status)
    return TaskListResponse(items=tasks, total=len(tasks))


@app.get(
    "/api/v1/tasks/{task_id}",
    response_model=Task,
    responses={404: {"model": ErrorResponse}},
)
def get_task(task_id: UUID) -> Task:
    return store.get(task_id)


@app.patch(
    "/api/v1/tasks/{task_id}",
    response_model=Task,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def update_task(task_id: UUID, data: TaskUpdate) -> Task:
    task = store.update(task_id, data)
    logger.info("task updated: %s", task.id)
    return task


@app.delete(
    "/api/v1/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_task(task_id: UUID) -> Response:
    store.delete(task_id)
    logger.info("task deleted: %s", task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
