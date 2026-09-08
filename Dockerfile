# syntax=docker/dockerfile:1
# Stufe 1: statische Seite mit MkDocs bauen
FROM python:3.12-slim AS build
WORKDIR /src
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Die Git-Historie liefert die "Zuletzt aktualisiert"-Daten; ohne .git greift der Build-Zeit-Fallback
ENV DISABLE_MKDOCS_2_WARNING=true
RUN mkdocs build --strict

# Stufe 2: unprivilegierter nginx liefert die Seite aus (Port 8080)
FROM nginxinc/nginx-unprivileged:1.27-alpine-slim
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/site /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/health || exit 1
