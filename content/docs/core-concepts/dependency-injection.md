---
title: Dependency Injection
type: docs
prev: docs/core-concepts/provider-plugin-system
next: docs/core-concepts/event-system
sidebar:
  open: true
weight: 16
---

## Overview

The `di` package provides a full-featured dependency injection container with support for three service lifetimes, automatic dependency resolution, circular dependency detection, and scoped containers.

## Service Lifetimes

Three lifetimes determine when a service instance is created and how long it lives:

| Lifetime | Behavior |
|----------|----------|
| **Transient** | A new instance is created every time the service is resolved |
| **Singleton** | A single instance is created and shared for the lifetime of the container |
| **Scoped** | A single instance is created per scope (e.g., per HTTP request) |

## Basic Usage

```go
import "github.com/lemmego/api/di"

container := di.New()
```

### Registration

```go
// Singleton — one instance for the application lifetime
di.RegisterSingleton[*Database](container, func() *Database {
    return NewDatabase()
})

// Transient — new instance each time
di.RegisterTransient[*UserService](container, func(db *Database) *UserService {
    return NewUserService(db)
})

// Or register with explicit lifetime
di.Register[*UserService](container, di.Scoped, func() *UserService {
    return NewUserService()
})
```

### Resolution

```go
db, err := di.Resolve[*Database](container)
userSvc := di.MustResolve[*UserService](container)
```

### Check Registration

```go
if di.Has[*UserService](container) {
    svc := di.MustResolve[*UserService](container)
}
```

## Automatic Dependency Resolution

Factory functions can declare dependencies as parameters. The container resolves them automatically:

```go
di.RegisterSingleton[*Database](container, func() *Database {
    return NewDatabase("postgres://...")
})

di.RegisterTransient[*UserRepository](container, func(db *Database) *UserRepository {
    return NewUserRepository(db)
})

di.RegisterTransient[*UserService](container, func(repo *UserRepository) *UserService {
    return NewUserService(repo)
})

// Resolving UserService automatically resolves Database and UserRepository
svc := di.MustResolve[*UserService](container)
```

## Fluent API

The fluent `For[T]` API provides a cleaner registration syntax:

```go
di.For[*Database](container).
    AsSingleton().
    Use(func() *Database {
        return NewDatabase("postgres://...")
    })

di.For[*UserService](container).
    AsTransient().
    Use(func(db *Database) *UserService {
        return NewUserService(db)
    })

// Register an existing instance
di.For[*Config](container).
    AsSingleton().
    UseInstance(&Config{Port: 8080})
```

## Scoped Containers

Scoped services are useful for per-request dependencies:

```go
// Register a scoped service
di.For[*RequestContext](container).
    AsScoped().
    Use(func() *RequestContext {
        return &RequestContext{RequestID: uuid.New().String()}
    })

// Create a scope (e.g., per HTTP request)
scope := container.CreateScope()

// Resolving within the scope returns the same instance
ctx1 := di.MustResolve[*RequestContext](scope)
ctx2 := di.MustResolve[*RequestContext](scope)
// ctx1 == ctx2 (same instance within scope)

// Different scope = different instance
scope2 := container.CreateScope()
ctx3 := di.MustResolve[*RequestContext](scope2)
// ctx3 != ctx1 (different scope)
```

## Circular Dependency Detection

The container detects circular dependencies at resolution time and returns an error instead of entering an infinite loop.

## Container Access

The container instance itself can be injected into factories:

```go
di.For[*ServiceLocator](container).
    AsSingleton().
    Use(func(c *di.Container) *ServiceLocator {
        return &ServiceLocator{container: c}
    })
```

## When to Use DI

The `di` package is suitable for complex applications that need:
- Multiple service lifetimes (transient, singleton, scoped)
- Automatic dependency resolution
- Scoped request-based services
- Fluent registration syntax

For simpler cases, the service container (`app.AddService` / `app.Get[T]`) is sufficient.
