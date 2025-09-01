# ---------- Frontend build stage ----------
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json ./
COPY frontend/package-lock.json ./
RUN npm ci || npm install
COPY frontend/ .
RUN npm run build

# ---------- Backend runtime stage ----------
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Build deps for some Python wheels; removed later to keep image slim
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Python deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY backend/ .

# Copy frontend build to /app/static (served by FastAPI)
RUN mkdir -p /app/static
COPY --from=frontend-build /app/frontend/dist /app/static

# Trim build deps
RUN apt-get purge -y build-essential || true && apt-get autoremove -y || true

ENV PORT=8080
EXPOSE 8080

CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080" ]
