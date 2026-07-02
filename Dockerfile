# SpeakUp Dockerfile — 前后端一体部署
FROM python:3.11-slim

WORKDIR /app

# 安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制前端构建产物
COPY frontend/dist/ ./frontend/dist/

# 暴露端口
EXPOSE 8080

# 启动
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
