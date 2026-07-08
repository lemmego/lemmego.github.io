---
title: Bun Connector
type: docs
prev: docs/database/providers/redis
next: docs/database/gormconnector
sidebar:
  open: true
weight: 29
---

## Overview

The `bunconnector` package provides an `app.Provider` that connects to databases using [uptrace/bun](https://github.com/uptrace/bun) and optionally registers a GPA provider.

## Usage

```go
func LoadProviders() []app.Provider {
    return []app.Provider{
        &bunconnector.Provider{
            UseGPA: true,
        },
    }
}
```

## Configuration

Reads from your application configuration (`internal/configs/database.go`):

```go
config.Set("sql", config.M{
    "default": "postgres",
    "connections": config.M{
        "postgres": config.M{
            "host":     config.MustEnv("DB_HOST", "127.0.0.1"),
            "port":     config.MustEnv("DB_PORT", 5432),
            "database": config.MustEnv("DB_DATABASE", "lemmego"),
            "username": config.MustEnv("DB_USERNAME", "root"),
            "password": config.MustEnv("DB_PASSWORD", ""),
        },
    },
})
```

## Without GPA

```go
&bunconnector.Provider{
    UseGPA: false,
}
```

When GPA is disabled, the raw `*bun.DB` is registered as a service:

```go
db := app.Get[*bun.DB](a)
```

## Supported Drivers

- PostgreSQL (`pgdialect`)
- MySQL (`mysqldialect`)
- SQLite (`sqlitedialect`)

## Connection Pooling

```go
config.Set("sql", config.M{
    "connections": config.M{
        "postgres": config.M{
            "host":           "127.0.0.1",
            "max_open_conns": 25,
            "max_idle_conns": 10,
            "conn_max_lifetime": "5m",
        },
    },
})
```

## Differences from GORM Connector

| Feature | GORM Connector | Bun Connector |
|---------|---------------|---------------|
| Auto-Migration | Yes | No |
| Supported Drivers | PostgreSQL, MySQL, SQLite, SQL Server | PostgreSQL, MySQL, SQLite |
| Dialects | GORM | Bun native |
| GPA Integration | Yes (gpagorm) | Yes (gpabun) |
