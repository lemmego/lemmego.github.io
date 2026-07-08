---
title: Application Bootstrap
type: docs
prev: docs/core-concepts/
next: docs/core-concepts/service-container
sidebar:
  open: true
weight: 13
---

## Bootstrapping Pipeline

Every Lemmego application starts with a builder pattern in `cmd/app/main.go`:

```go
func main() {
    webApp := app.Configure()

    webApp.
        WithRoutes(bootstrap.LoadRoutes()).
        WithHTTPMiddlewares(bootstrap.LoadHTTPMiddlewares()).
        WithMiddlewares(bootstrap.LoadMiddlewares()).
        WithCommands(bootstrap.LoadCommands()).
        WithProviders(bootstrap.LoadProviders()).
        WithErrMap(bootstrap.LoadErrMap()).
    Run()
}
```

The `app.Configure()` function creates a new `AppEngine` instance using functional options:

```go
app.Configure(
    app.WithConfig(config.M{...}),
    app.WithRoutes([]RouteCallback{...}),
    app.WithProviders([]Provider{...}),
)
```

## Boot Order

When `Run()` is called, the framework initializes in this order:

1. **Configuration** — Config map is set up from `internal/configs/`
2. **Commands** — CLI commands are registered
3. **Events** — Middleware, routes, commands, and services events fire
4. **HTTP Middleware** — Global `net/http` middleware wraps the router
5. **Providers** — All service providers run their `Provide()` methods
6. **App Middleware** — Application-level middleware is registered
7. **Routes** — Route callbacks register all endpoints
8. **ErrMap** — Error-to-handler mappings are applied
9. **Server Start** — The HTTP server begins listening (or CLI executes)

## Run Modes

The application detects whether it's running as a web server or CLI command:

```go
// Returns true if command-line arguments were provided
a.RunningInConsole()

// Check the environment
a.InProduction()
a.Env("development")
```

If CLI arguments are provided, `Run()` executes the matching command instead of starting the web server.

## Lifecycle Events

The framework fires events at each stage of bootstrapping:

```go
app.ServerStarted            // Fired when the HTTP server starts
app.MiddlewareRegistering    // Before middleware is registered
app.MiddlewareRegistered     // After middleware is registered
app.RoutesRegistering        // Before routes are registered
app.RoutesRegistered         // After routes are registered
app.CommandsRegistering      // Before commands are registered
app.CommandsRegistered       // After commands are registered
app.ServicesRegistering      // Before services are registered
app.ServicesRegistered       // After services are registered
```

Listen to these events to hook into the application lifecycle (see [Event System](/docs/core-concepts/event-system/)).
