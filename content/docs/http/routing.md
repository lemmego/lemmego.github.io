---
title: Routing
type: docs
prev: docs/http/
sidebar:
  open: true
weight: 6
---

## Route Definitions

Routes are defined in `internal/routes/` using the application's `Router` interface. The framework supports all standard HTTP verbs.

```go
// internal/routes/web.go
package routes

func WebRoutes(a app.App) {
    r := a.Router()

    r.Get("/hello", func(c app.Context) error {
        return c.Text([]byte("World"))
    })

    r.Post("/submit", func(c app.Context) error {
        return c.JSON(app.M{"status": "ok"})
    })
}
```

## Route Parameters

Extract URL parameters using `c.Param()`:

```go
r.Get("/users/{id}", func(c app.Context) error {
    id := c.Param("id")
    return c.Text([]byte("User: " + id))
})
```

## Route Groups

Group routes under a common prefix with shared middleware:

```go
api := r.Group("/api")
api.Get("/users", handlers.UserIndex)
api.Post("/users", handlers.UserStore)

admin := r.Group("/admin")
admin.UseBefore(middleware.AdminAuth)
admin.Get("/dashboard", handlers.AdminDashboard)
```

Nested groups are also supported:

```go
v1 := api.Group("/v1")
v1.Get("/products", handlers.ProductIndex)
```

## Route Registration

Routes are registered via callbacks in `bootstrap/routes.go`:

```go
// bootstrap/routes.go
package bootstrap

func LoadRoutes() []app.RouteCallback {
    return []app.RouteCallback{
        routes.WebRoutes,
        routes.ApiRoutes,
    }
}
```

Each `RouteCallback` is a `func(a app.App)` that receives the full app instance and registers routes on `a.Router()`.

## Input Middleware

Use the router's `Input` middleware to automatically decode request bodies into typed structs:

```go
r.Post("/tasks", router.Input(&inputs.TaskInput{}), handlers.TaskStore)
```

The decoded input is stored in the request context and can be retrieved via `c.Input()`.

## Router API

```go
type Router interface {
    Group(prefix string) *routeGroup
    UseBefore(handlers ...Handler)
    UseAfter(handlers ...Handler)
    Get(pattern string, handlers ...Handler) *route
    Post(pattern string, handlers ...Handler) *route
    Put(pattern string, handlers ...Handler) *route
    Patch(pattern string, handlers ...Handler) *route
    Delete(pattern string, handlers ...Handler) *route
    Head(pattern string, handlers ...Handler) *route
    Options(pattern string, handlers ...Handler) *route
    Connect(pattern string, handlers ...Handler) *route
    Trace(pattern string, handlers ...Handler) *route
    Use(middlewares ...HTTPMiddleware)
    HasRoute(method string, pattern string) bool
    Handle(pattern string, handler http.Handler)
    HandleFunc(pattern string, handler func(http.ResponseWriter, *http.Request))
}
```
