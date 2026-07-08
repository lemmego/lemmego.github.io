---
title: Configuration
type: docs
prev: docs/quick-start/
next: docs/project-structure/
weight: 3
---

## Overview

Lemmego uses a centralized configuration system that combines environment variables, `.env` files, and runtime configuration maps. The system supports dot-notation access, nested keys, and type-safe retrieval.

## The Config System

Configuration is managed via the `config` package (`github.com/lemmego/api/config`). It follows a singleton pattern and is auto-loaded at application startup.

### Setting Configuration

In your generated project, configuration is defined in `internal/configs/` files using Go `init()` functions:

```go
// internal/configs/app.go
package configs

import "github.com/lemmego/api/config"

func init() {
    config.Set("app", config.M{
        "name":  config.MustEnv("APP_NAME", "Lemmego"),
        "port":  config.MustEnv("APP_PORT", 8080),
        "env":   config.MustEnv("APP_ENV", "development"),
        "debug": config.MustEnv("APP_DEBUG", false),
    })
}
```

Config files are auto-loaded via a blank import in `cmd/app/main.go`:

```go
import _ "github.com/lemmego/lemmego/internal/configs"
```

### Reading Configuration

```go
port := config.Get("app.port").(int)
name := config.Get("app.name", "default").(string)
```

Or using the typed accessor on a `config.M` map:

```go
cfg := config.GetAll()
port := cfg.Int("app.port")
debug := cfg.Bool("app.debug")
```

Available accessor methods on `config.M`:
- `String(key, defaultVal...) string`
- `Int(key, defaultVal...) int`
- `Int64(key, defaultVal...) int64`
- `Bool(key, defaultVal...) bool`
- `Float64(key, defaultVal...) float64`
- `Duration(key, defaultVal...) time.Duration`
- `Time(key, defaultVal...) time.Time`

### Environment Variables

The framework loads `.env` files automatically via `github.com/joho/godotenv/autoload`. For type-safe environment variable access:

```go
port := config.MustEnv("APP_PORT", 8080)
debug := config.MustEnv("APP_DEBUG", false)
```

`MustEnv[T]` supports `string`, `int`, `float64`, and `bool` types.

## Configuration Sections

A generated project includes these configuration files:

### `app.go` — Application Settings

| Config Key | Env Variable | Default | Description |
|-----------|-------------|---------|-------------|
| `app.name` | `APP_NAME` | `Lemmego` | Application display name |
| `app.port` | `APP_PORT` | `8080` | HTTP server port |
| `app.env` | `APP_ENV` | `development` | Environment (`production`, `development`) |
| `app.debug` | `APP_DEBUG` | `false` | Enable debug mode |
| `app.url` | `APP_URL` | `http://localhost:8080` | Application URL |

### `database.go` — Database Connections

| Config Key | Env Variable | Default | Description |
|-----------|-------------|---------|-------------|
| `sql.default` | `DB_CONNECTION` | `sqlite` | Default connection name |
| `sql.connections.sqlite.database` | `DB_DATABASE` | `storage/database.sqlite` | SQLite path |
| `sql.connections.mysql.host` | `DB_HOST` | `127.0.0.1` | MySQL host |
| `sql.connections.mysql.port` | `DB_PORT` | `3306` | MySQL port |
| `keyvalue.redis.host` | `REDIS_HOST` | `127.0.0.1` | Redis host |

### `filesystems.go` — Storage Disks

| Config Key | Env Variable | Default | Description |
|-----------|-------------|---------|-------------|
| `filesystems.default` | `FILESYSTEM_DISK` | `local` | Default storage disk |
| `filesystems.disks.local.root` | — | `storage/app` | Local storage root |

### `session.go` — Session Configuration

| Config Key | Env Variable | Default | Description |
|-----------|-------------|---------|-------------|
| `session.driver` | `SESSION_DRIVER` | `file` | Session store driver |
| `session.lifetime` | `SESSION_LIFETIME` | `120` | Session lifetime (minutes) |
| `session.cookie` | `SESSION_COOKIE` | `lemmego_session` | Cookie name |

## Adding Custom Configuration

You can add your own configuration by creating new files in `internal/configs/`:

```go
// internal/configs/mail.go
package configs

import "github.com/lemmego/api/config"

func init() {
    config.Set("mail", config.M{
        "default":  config.MustEnv("MAIL_MAILER", "smtp"),
        "host":     config.MustEnv("MAIL_HOST", "smtp.mailtrap.io"),
        "port":     config.MustEnv("MAIL_PORT", 2525),
    })
}
```

Access your config anywhere in your application:

```go
mailHost := config.Get("mail.host").(string)
```
