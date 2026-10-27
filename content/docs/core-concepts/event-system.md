---
title: Event System
type: docs
prev: docs/core-concepts/dependency-injection
next: docs/logging
weight: 85
sidebar:
  open: true
---

Lemmego includes a simple pub/sub event system that allows you to hook into the application lifecycle and communicate between components without tight coupling.

## Using the EventEmitter

The `App` instance implements the `EventEmitter` interface:

```go
type EventEmitter interface {
    On(event string, listener EventListener)
    Dispatch(event string, payload ...any)
}

type EventListener func(payload any) error
```

{{< callout type="warning" >}}
**`Dispatch` returns nothing.** A listener's error is logged and the remaining
listeners still run, so there is no value for the caller to act on — writing
`if err := a.Dispatch(…)` does not compile.

Dispatch is also **synchronous, on the caller's goroutine**. It is right for
an observability hook and wrong for slow work: a listener that blocks blocks
the request. For anything that takes time, have the listener enqueue a
`tasker` job.
{{< /callout >}}

## Listening to Events

Register listeners in your provider or bootstrap code:

```go
func (p *MyProvider) Provide(a app.App) error {
    a.On(app.ServerStarted, func(payload any) error {
        slog.Info("Server is now listening!")
        return nil
    })
    return nil
}
```

## Built-in Lifecycle Events

The framework dispatches events during bootstrapping:

| Event Constant | When It Fires |
|---------------|---------------|
| `app.MiddlewareRegistering` | Before middleware is registered |
| `app.MiddlewareRegistered` | After middleware is registered |
| `app.RoutesRegistering` | Before routes are registered |
| `app.RoutesRegistered` | After routes are registered |
| `app.CommandsRegistering` | Before CLI commands are registered |
| `app.CommandsRegistered` | After CLI commands are registered |
| `app.ServicesRegistering` | Before providers run |
| `app.ServicesRegistered` | After all providers have run |
| `app.ServerStarted` | After the HTTP server starts listening |

## Dispatching Custom Events

```go
// Dispatch a custom event
a.Dispatch("user.registered", user)

// Listen for custom events
a.On("user.registered", func(payload any) error {
    user := payload.(*User)
    return sendWelcomeEmail(user.Email)
})
```

## Multiple Listeners

Multiple listeners can register for the same event. They all receive the payload when the event is dispatched:

```go
a.On("user.registered", sendWelcomeEmail)
a.On("user.registered", logRegistration)
a.On("user.registered", notifyAdmins)
```

## Shutdown Behavior

When the application shuts down gracefully:
- New event registrations are blocked
- Pending event dispatches complete
- All `ShutdownProvider` instances are notified

```go
a.On(app.ServerStarted, func(payload any) error {
    // This won't run if shutdown has begun
    return nil
})
```

## Error Handling

If a listener returns an error, the dispatch continues to other listeners. The error is not propagated:

```go
a.On("user.registered", func(payload any) error {
    // Even if this fails, other listeners still run
    return someOperation()
})
```

## Use Cases

- **Plugin hooks** — let plugins react to application events
- **Cache invalidation** — clear caches when data changes
- **Metrics** — record metrics at lifecycle points
- **Logging** — audit log important events
- **Notifications** — send emails, push notifications
