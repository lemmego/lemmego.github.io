---
title: Session
type: docs
prev: docs/deployment/
next: docs/logging
sidebar:
  open: true
weight: 49
---

## Overview

Session management is handled by the `session` package. It supports multiple storage backends and integrates with the framework's CSRF protection.

## Configuration

Session settings are in `internal/configs/session.go`:

```go
config.Set("session", config.M{
    "driver":   config.MustEnv("SESSION_DRIVER", "file"),
    "lifetime": config.MustEnv("SESSION_LIFETIME", 120),
    "cookie":   config.MustEnv("SESSION_COOKIE", "lemmego_session"),
    "domain":   config.MustEnv("SESSION_DOMAIN", ""),
    "path":     "/",
    "secure":   config.MustEnv("SESSION_SECURE", false),
    "http_only": true,
    "same_site": "lax",
})
```

## Storage Backends

### Memory

```go
config.Set("session", config.M{"driver": "memory"})
```

Sessions are stored in memory. Best for development or single-server deployments.

### File

```go
config.Set("session", config.M{"driver": "file"})
```

Sessions are persisted to disk (default: `storage/session/`). Includes automatic expiry cleanup.

### Redis

```go
config.Set("session", config.M{"driver": "redis"})
config.Set("keyvalue", config.M{
    "connections": config.M{"redis": config.M{
        "host": config.MustEnv("REDIS_HOST", "127.0.0.1"),
        "port": 6379,
    }},
})
```

Best for multi-server deployments and production use.

## Provider Registration

The session provider is registered in `bootstrap/providers.go`:

```go
func LoadProviders() []app.Provider {
    return []app.Provider{
        &session.Provider{},
    }
}
```

## Using Sessions

### In Request Context

```go
// Read
val := c.Session("key")
str := c.SessionString("key")

// Write
c.PutSession("key", value)

// Read and remove
val := c.PopSession("key")
str := c.PopSessionString("key")
```

### Via the Session Manager

```go
sess := app.Get[*session.Session](a)

// Standard scs.SessionManager API
err := sess.RenewToken(ctx)
err := sess.Destroy(ctx)
userID := sess.GetString(ctx, "user_id")
sess.Put(ctx, "last_activity", time.Now())
```

## Session & CSRF

The CSRF middleware keeps its token in the session, under `_token`. It is generated
once — on the first request of a session — and reused for as long as that session
lives, rather than being rotated per request; [CSRF Protection](/docs/security/csrf)
explains why. Destroying or regenerating the session therefore also invalidates the
CSRF token, and the next request issues a fresh one.

## Lifecycle

Session data is automatically loaded on request start and committed on response completion. You don't need to manually save session changes.
