# Task Manager API

一个从零构建的任务管理 REST API 服务，用于展示完整的 DevOps 工程实践：容器化、本地 Kubernetes 部署、CI/CD 自动化与规范的版本控制流程。

## 项目简介

Task Manager API 提供任务的增删改查（CRUD）能力：

- 创建任务（标题、描述、优先级、截止日期）
- 查询任务列表 / 单个任务
- 更新任务状态与内容
- 删除任务
- 健康检查端点（供 Kubernetes 探针使用）

项目目标不仅是 API 本身，而是覆盖从代码到部署的完整链路：

```
代码 → 测试 → Docker 镜像 → 本地 K8s 部署 → CI/CD 流水线
```

## 技术栈

| 领域 | 技术选型 |
| --- | --- |
| 语言 / 框架 | Python 3.12 + FastAPI |
| ASGI 服务器 | Uvicorn |
| 数据校验 | Pydantic |
| 测试 | pytest + httpx |
| 容器化 | Docker（多阶段构建） |
| 本地 K8s | kind / minikube |
| CI/CD | GitHub Actions |
| 镜像仓库 | GitHub Container Registry (ghcr.io) |

## 项目结构

> 随开发进度持续更新

```
task-manager-api/
├── app/                  # API 应用源码（待创建）
├── tests/                # 测试代码（待创建）
├── k8s/                  # Kubernetes manifests（待创建）
├── .github/workflows/    # CI/CD 流水线（待创建）
├── Dockerfile            # 容器镜像定义（待创建）
├── requirements.txt      # Python 依赖
└── README.md
```

## 本地开发环境搭建

> 占位 —— 后续随实现步骤完善

### 前置要求

- Python 3.12+
- Docker Desktop
- kind 或 minikube
- kubectl

### 快速开始

```bash
# 1. 克隆仓库
git clone <repo-url>
cd task-manager-api

# 2. 创建虚拟环境并安装依赖
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. 启动开发服务器
uvicorn app.main:app --reload

# 4. 访问 API 文档
# http://localhost:8000/docs
```

## API 文档

服务启动后，FastAPI 自动生成交互式文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 部署

> 占位 —— 容器化与 K8s 部署步骤将在后续章节补充

## CI/CD

> 占位 —— GitHub Actions 流水线说明将在后续章节补充
