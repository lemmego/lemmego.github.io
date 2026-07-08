---
title: Service Container
type: docs
prev: docs/core-concepts/application-bootstrap
next: docs/core-concepts/provider-plugin-system
sidebar:
  open: true
weight: 14
---

## Overview

The service container is a lightweight registry that stores and retrieves services by their Go type. It's the simplest form of dependency injection in Lemmego, used internally by the framework and by your application code.

## Adding Services

Register services via `app.AddService()`:

```go
type MyService struct {
    // ...
}

func (p *MyProvider) Provide(a app.App) error {
    svc := &MyService{}
    a.AddService(svc)
    return nil
}
```

## Retrieving Services

### Via the App Instance

```go
svc := a.Service(&MyService{}).(*MyService)
```

### Via the Generic Helper

```go
import "github.com/lemmego/api/app"

svc := app.Get[*MyService](a)
```

The generic `Get[T]` helper composes with type safety:

```go
session := app.Get[*session.Session](a)
filesystem := app.Get[*fs.FileSystem](a)
```

## Built-in Services

The framework registers several services through its providers:

| Service | Type | Provider |
|---------|------|----------|
| Session Manager | `*session.Session` | `session.Provider` |
| File System | `*fs.FileSystem` | `fs.Provider` |
| Database | `*gorm.DB` / `*bun.DB` | `gormconnector` / `bunconnector` |
| Inertia | `*inertia.Inertia` | `inertia.Provider` |
| Auth | `*auth.Auth` | `auth.Provider` |

## How It Works

The container uses reflection to store services by their pointer type:

```go
type serviceContainer struct {
    services map[reflect.Type]interface{}
    mutex    sync.RWMutex
}

func (sc *serviceContainer) Add(service interface{}) {
    t := reflect.TypeOf(service)
    sc.services[t] = service
}

func (sc *serviceContainer) Get(service interface{}) error {
    // Resolves the service by type and populates the provided pointer
}
```

## When to Use

Use the service container for:
- Framework internals (session, filesystem, database connections)
- Simple service registration where you need exactly one instance
- Services that need to be available across the entire application

For more advanced DI needs (multiple lifetimes, auto-resolution of dependencies, scoped instances), see the [Dependency Injection](/docs/core-concepts/dependency-injection/) page.
