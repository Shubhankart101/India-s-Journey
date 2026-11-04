FROM node:22-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_DEBUG=false PORT=8000 WEB_CONCURRENCY=2
# Node is only needed by `manage.py refresh_data` to re-export the catalogue.
RUN apt-get update && apt-get install -y --no-install-recommends nodejs && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY webapp/requirements.txt webapp/requirements.txt
RUN pip install --no-cache-dir -r webapp/requirements.txt
COPY . .
COPY --from=frontend /app/frontend/dist frontend/dist
RUN DJANGO_SECRET_KEY=build-only python webapp/manage.py collectstatic --noinput
# Bake the catalogue into the image's SQLite DB so cold starts (Fly stops idle machines) serve in seconds instead of
# re-importing thousands of rows before gunicorn listens; boot only re-imports when data/catalog.json changed.
RUN DJANGO_SECRET_KEY=build-only python webapp/manage.py migrate --noinput \
 && DJANGO_SECRET_KEY=build-only python webapp/manage.py import_catalog
EXPOSE 8000
CMD python webapp/manage.py migrate --noinput && python webapp/manage.py import_catalog --if-changed && gunicorn journey.wsgi --chdir webapp --bind 0.0.0.0:$PORT --workers $WEB_CONCURRENCY --timeout 60
