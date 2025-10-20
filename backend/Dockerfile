<<<<<<< HEAD
﻿FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY default.conf.template /etc/nginx/conf.d/default.conf.template

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
=======
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add entrypoint that will run migrations and start Daphne
RUN chmod +x /app/manage.py
RUN chmod +x /app/entrypoint.sh || true

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
>>>>>>> 76a9566 (update)
