---
title: Context
type: docs
prev: docs/http/error-handling
sidebar:
  open: true
weight: 11
---

## Overview

The `Context` interface is the central request/response abstraction in Lemmego. Every handler receives a `Context` that provides access to the request, response, session, and application services.

```go
type Context interface {
    GetSetter
    HttpProvider
    App() App
    Next() error
}
```

## Request Data

### URL Parameters and Query Strings

```go
id := c.Param("id")           // Route parameter: /users/{id}
page := c.Query("page")       // Query string: ?page=2
```

### Request Body

```go
body := c.Body()              // Raw request body
```

### Request Metadata

```go
r := c.Request()              // *http.Request
w := c.ResponseWriter()        // http.ResponseWriter
ctx := c.RequestContext()      // context.Context
method := r.Method
path := r.URL.Path
```

## Request-Scoped Storage

Store and retrieve data across middleware and handlers:

```go
// Set in middleware
c.Set("user", currentUser)

// Get in handler
user := c.Get("user").(*User)
```

## Session Access

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

## Cookie Management

```go
// Read
cookie := c.Cookie("session_id")

// Write
c.SetCookie(&http.Cookie{
    Name:  "preference",
    Value: "dark-mode",
    Path:  "/",
})
```

## Headers

```go
// Read
ua := c.Header("User-Agent")

// Write
c.SetHeader("X-Request-Id", requestID)
```

## Status

```go
c.Status()                    // Get current status code
c.SetStatus(http.StatusCreated) // Set status
c.WriteStatus(http.StatusOK)  // Write status to response
```

## Reading State

```go
c.IsReading()                 // Is this a GET/HEAD/OPTIONS request?
```

## Referer

```go
ref := c.Referer()            // Referer header
```

## App Access

```go
a := c.App()                  // Access the App instance
cfg := a.Config()             // Configuration
sess := a.Session()           // Session manager
fs := a.FileSystem()          // Filesystem manager
```

## Middleware Chain

```go
func myMiddleware(next app.Handler) app.Handler {
    return func(c app.Context) error {
        // Pre-processing
        err := next(c) // Call the next handler
        // Post-processing
        return err
    }
}
```

## Validation

```go
v := c.Validator()                          // Get the app validator
v.Field("email", input.Email).Required().Email()
if err := v.Validate(); err != nil {
    return c.UnprocessableEntity(err)
}
```
