---
title: Deployment
type: docs
prev: docs/testing/
next: docs/session
sidebar:
  open: true
weight: 48
---

## Overview

Lemmego applications compile to a single binary, making deployment straightforward across any platform that supports Go.

## Production Build

### Build the Application

```shell
go build -o bin/app ./cmd/app
```

### Build Frontend Assets

```shell
lemmego build
```

This runs `templ generate` (if needed) and `npm run build` / `pnpm build` for production frontend assets.

## Production Configuration

### Environment Variables

Set these for production:

```shell
APP_ENV=production
APP_DEBUG=false
APP_PORT=8080
APP_URL=https://yourdomain.com

# Database
DB_CONNECTION=postgres
DB_HOST=your-db-host
DB_DATABASE=your-db-name
DB_USERNAME=your-db-user
DB_PASSWORD=your-db-password

# Session
SESSION_DRIVER=redis
SESSION_COOKIE=your_app_session
REDIS_HOST=your-redis-host

# Filesystem
FILESYSTEM_DISK=s3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_BUCKET=your-bucket

# Encryption
APP_KEY=base64:your-32-byte-key

# Auth (if using JWT)
JWT_SECRET=your-jwt-secret
```

### Graceful Shutdown

The framework supports graceful shutdown via `ShutdownProvider`:

```go
type MyProvider struct{}

func (p *MyProvider) Shutdown(ctx context.Context) error {
    // Close database connections, flush logs, etc.
    return nil
}
```

## Deployment Options

### Single Binary

```shell
# Build for your target platform
GOOS=linux GOARCH=amd64 go build -o bin/app ./cmd/app

# Deploy the binary and public/ directory
scp bin/app user@server:/opt/app/
scp -r public user@server:/opt/app/
scp .env user@server:/opt/app/
```

### Docker

```dockerfile
FROM golang:1.24 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN make build && go build -o bin/app ./cmd/app

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates
WORKDIR /app
COPY --from=builder /app/bin/app .
COPY --from=builder /app/public ./public
COPY --from=builder /app/.env .
EXPOSE 8080
CMD ["./app"]
```

### Process Manager

Use a process manager like supervisor or systemd:

```ini
[Unit]
Description=Lemmego App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/app
ExecStart=/opt/app/app
Restart=always
EnvironmentFile=/opt/app/.env

[Install]
WantedBy=multi-user.target
```

## Reverse Proxy

For production, run behind a reverse proxy (Nginx, Caddy, Traefik):

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /build/ {
        alias /opt/app/public/build/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```
