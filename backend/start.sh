#!/bin/bash
# 启动后端服务

# 安装依赖
pip install -r requirements.txt

# 运行FastAPI服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
