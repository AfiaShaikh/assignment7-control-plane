FROM python:3.12-slim
ARG APP_VERSION=1.0
ENV APP_VERSION=${APP_VERSION} PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY app.py index.html ./
USER 10001:10001
EXPOSE 5000
CMD ["python", "app.py"]
