---
title: Middleware
type: docs
prev: docs/http/
sidebar:
  open: true
weight: 7
---

## Overview

Every incoming request passes through middleware before reaching your handler. Lemmego supports two middleware layers:

1. **HTTP Middleware** — wraps the entire router at the `net/http` level
2. **App Middleware** — operates on the Lemmego `Context` at the application level

## HTTP Middleware

HTTP middleware uses the standard `func(http.Handler) http.Handler` signature. These run first, before any routing.

### Built-in HTTP Middleware

```go
middleware.Recoverer()       // Panic recovery
middleware.RequestLogger()   // Request logging
middleware.MethodOverride    // PUT/DELETE via _method field
```

### Registration

HTTP middleware is registered in `bootstrap/http_middleware.go`:

```go
func LoadHTTPMiddlewares() []app.HTTPMiddleware {
    return []app.HTTPMiddleware{
        middleware.Recoverer(),
        middleware.RequestLogger(),
        middleware.MethodOverride,
    }
}
```

## App Middleware

App middleware uses `func(next Handler) Handler` and operates on the Lemmego `Context`.

### Built-in App Middleware

```go
middleware.VerifyCSRF(&middleware.CSRFOpts{})   // CSRF protection
```

### Registration

App middleware is registered in `bootstrap/middleware.go`:

```go
func LoadMiddlewares() []app.Handler {
    return []app.Handler{
        middleware.VerifyCSRF(&middleware.CSRFOpts{
            ExcludePatterns: []string{"/api/.*"},
        }),
    }
}
```

### Route-Scoped Middleware

Apply middleware to specific routes or groups:

```go
// Before middleware (runs before handler)
r.UseBefore(middleware.AuthRequired)

// Per-route middleware
api.Group("/admin").UseBefore(middleware.AdminOnly)

// After middleware (runs after handler)
r.UseAfter(middleware.ResponseLogger)
```

## Writing Custom Middleware

### App Middleware

```go
func RequestTimer(next app.Handler) app.Handler {
    return func(c app.Context) error {
        start := time.Now()
        err := next(c)
        duration := time.Since(start)
        slog.Info("request completed", "duration", duration)
        return err
    }
}
```

### HTTP Middleware

```go
func CORSMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "*")
        next.ServeHTTP(w, r)
    })
}
```

### Registration

```go
// bootstrap/middleware.go
func LoadMiddlewares() []app.Handler {
    return []app.Handler{
        RequestTimer,                    // Custom app middleware
        middleware.VerifyCSRF(nil),      // Built-in
    }
}

// bootstrap/http_middleware.go
func LoadHTTPMiddlewares() []app.HTTPMiddleware {
    return []app.HTTPMiddleware{
        CORSMiddleware,                  // Custom HTTP middleware
        middleware.Recoverer(),          // Built-in
    }
}
```

## Middleware Reference

### Recovery

Catches panics, logs the stack trace, and returns a 500 error. Supports development mode with stack traces in responses:

```go
middleware.Recovery()                                   // Default options
middleware.RecoveryWithOpts(middleware.DevelopmentRecoveryOpts)
middleware.RecoveryWithCustomFunc(customHandler)
```

### CSRF

Protects against cross-site request forgery using session-based tokens. Uses constant-time comparison and supports exclusion patterns:

```go
middleware.VerifyCSRF(&middleware.CSRFOpts{
    ExcludePatterns: []string{"/api/.*", "/webhook"},
})
```

CSRF tokens are rotated after each successful validation.

### Method Override

Enables PUT, PATCH, and DELETE on HTML forms via `_method` field or `X-HTTP-Method-Override` header:

```go
middleware.MethodOverride
```

Usage in forms:

```html
<form method="POST" action="/tasks/1">
    <input type="hidden" name="_method" value="DELETE">
</form>
```
