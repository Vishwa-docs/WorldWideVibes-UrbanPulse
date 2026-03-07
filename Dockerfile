# ── Stage 1: Build React frontend ─────────────────────────────────────
FROM node:20-slim AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ── Stage 2: Python backend + static frontend ────────────────────────
FROM python:3.11-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy built frontend into /app/static so FastAPI can serve it
COPY --from=frontend-build /build/dist ./static

ENV PORT=8000
EXPOSE 8000

CMD python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
