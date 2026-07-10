---
title: Error Handling
type: docs
prev: docs/http/response-handling
sidebar:
  open: true
weight: 10
---

## Typed HTTP Errors

Lemmego provides pre-defined sentinel errors for common HTTP status codes:

```go
app.ErrUnauthorized          // 401
app.ErrForbidden             // 403
app.ErrNotFound              // 404
app.ErrBadRequest            // 400
app.ErrMethodNotAllowed      // 405
app.ErrPageExpired           // 419
app.ErrUnprocessableEntity   // 422
app.ErrInternalServerError   // 500
```

Return them from handlers manually:

```go
func MyHandler(c app.Context) error {
    return app.ErrNotFound
}
```

## Context Error Helpers

The context provides convenience methods for common error responses:

```go
func MyHandler(c app.Context) error {
    return c.NotFound()
    return c.Unauthorized()
    return c.Forbidden()
    return c.BadRequest(err)
    return c.InternalServerError(err)
    return c.ValidationError(err)
    return c.PageExpired()
    return c.MethodNotAllowed()
    return c.UnprocessableEntity(err)
}
```

These methods automatically negotiate JSON vs HTML responses based on the request's `Accept` header.

## Error Map

The `ErrMap` lets you map error types to custom handler functions:

```go
// bootstrap/errmap.go
func LoadErrMap() app.ErrMap {
    return app.ErrMap{
        app.ErrNotFound: func(c app.Context) error {
            if c.WantsJSON() {
                return c.JSON(app.M{"error": "not found"})
            }
            return c.Render(res.NewTemplate(c, "404.page.gohtml"))
        },
        app.ErrUnauthorized: func(c app.Context) error {
            return c.Redirect("/login")
        },
        app.ErrInternalServerError: func(c app.Context) error {
            return c.Render(res.NewTemplate(c, "500.page.gohtml"))
        },
    }
}
```

The generated project includes default error pages for common status codes in `templates/`:
- `401.page.gohtml`
- `403.page.gohtml`
- `404.page.gohtml`
- `419.page.gohtml`
- `500.page.gohtml`

## Custom Error Types

Implement the `HttpError` interface for custom typed errors:

```go
type ValidationFailed struct {
    Field   string
    Message string
}

func (e *ValidationFailed) GetHttpMessage() app.HttpMessage {
    return app.HttpMessage{
        Status: http.StatusUnprocessableEntity,
        Message: e.Field + ": " + e.Message,
    }
}
```

## App-Level Error Handling

The framework's recovery middleware catches panics and returns appropriate responses:

```go
middleware.Recovery()                     // Production: log + 500
middleware.RecoveryWithOpts(middleware.DevelopmentRecoveryOpts) // Dev: log + stack trace
```
