---
title: Logging
type: docs
prev: docs/services/session
next: docs/services/caching
sidebar:
  open: true
weight: 52
---

## Overview

Lemmego provides a colorized structured logger built on Go's `log/slog` package. It outputs JSON-formatted logs with color-coded levels for terminal readability.

## Basic Usage

```go
import "github.com/lemmego/api/logger"

// Get the default logger
log := logger.Default()
log.Info("server started", "port", 8080)
log.Warn("slow request", "duration", "2.5s")
log.Error("database connection failed", "error", err)
```

## Log Levels

The logger supports standard slog levels with color coding:

| Level | Color | Method |
|-------|-------|--------|
| DEBUG | Green | `log.Debug(msg, args...)` |
| INFO | Cyan | `log.Info(msg, args...)` |
| WARN | Yellow | `log.Warn(msg, args...)` |
| ERROR | Red | `log.Error(msg, args...)` |

The minimum log level is controlled by `APP_DEBUG`:

```shell
APP_DEBUG=true   # Shows DEBUG and above
APP_DEBUG=false  # Shows INFO and above
```

## Verbose Logging

```go
log := logger.Verbose()
// Includes source file and line number in log output
```

## Custom Handler

```go
handler := logger.NewHandler(&logger.Options{
    Level: slog.LevelDebug,
})
slog.SetDefault(slog.New(handler))
```

## Observability Logger

For more advanced logging needs, the `observability` package provides a structured logger with rotation and field enrichment:

```go
import "github.com/lemmego/api/observability"

logger, err := observability.NewLogger(observability.LoggerConfig{
    Level:      observability.LevelInfo,
    Output:     "stdout",
    JSONOutput: true,
})

logger.Info(ctx, "user registered", map[string]any{
    "user_id": user.ID,
    "email":   user.Email,
})

// Enriched loggers
logger.WithRequestID(reqID).Info(ctx, "processing request")
logger.WithUserID(userID).Warn(ctx, "rate limit approaching")
```

## Metrics

The `observability` package also includes a metrics collector:

```go
metrics := observability.NewMetricsCollector(observability.MetricsConfig{
    Enabled: true,
})

// Record HTTP request metrics
observability.RecordHTTPRequest("GET", "/api/users", 200, 45*time.Millisecond)

// Custom metrics
metrics.IncrementCounter("page_views", 1)
metrics.SetGauge("active_users", 42)
metrics.RecordHistogram("response_time_ms", 145)
```

Metrics middleware automatically records HTTP request metrics:

```go
app.Use(observability.MetricsMiddleware)
```
