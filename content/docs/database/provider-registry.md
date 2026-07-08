---
title: Provider Registry
type: docs
prev: docs/database/
next: docs/database/generic-repository
sidebar:
  open: true
weight: 19
---

## Overview

The provider registry is a singleton that stores database provider instances by type and name. It uses Go generics for compile-time type inference.

## Architecture

Providers are stored in a two-level map:

```
providers map[string]map[string]Provider
           ^                ^
           |                +-- instance name (e.g., "primary", "cache")
           +-- provider type name (e.g., "gorm", "redis")
```

## Registration

### Register a Provider

```go
import (
    "github.com/lemmego/gpa"
    "github.com/lemmego/gpagorm"
    "github.com/lemmego/gparedis"
)

// Register a GORM provider as "primary"
gpa.Register[*gpagorm.Provider]("primary", gormProvider)

// Register with registry defaults
gpa.RegisterDefault[*gpagorm.Provider](gormProvider)

// Register a Redis provider as "cache"
gpa.Register[*gparedis.Provider]("cache", redisClient)
```

### From an Application Provider

```go
type DatabaseProvider struct{}

func (p *DatabaseProvider) Provide(a app.App) error {
    cfg := a.Config()
    provider, err := gpagorm.NewProvider(gpa.Config{
        Host:     cfg.String("database.host"),
        Port:     cfg.Int("database.port"),
        Database: cfg.String("database.name"),
    })
    if err != nil {
        return err
    }
    gpa.Register[*gpagorm.Provider]("default", provider)
    return nil
}
```

## Retrieval

### Type-Safe Retrieval

```go
// With compile-time type inference
primary := gpa.MustGet[*gpagorm.Provider]("primary")
cache := gpa.MustGet[*gparedis.Provider]("cache")

// With error handling
provider, err := gpa.Get[*gpagorm.Provider]("primary")
if err != nil {
    // handle error
}
```

### Default Instance

If no instance name is provided, the registry looks up `"default"`:

```go
provider := gpa.MustGet[*gpagorm.Provider]()
```

### Multiple Instances

```go
// Get all instances of a type
gormProviders, err := gpa.GetByType[*gpagorm.Provider]()
```

## Lifecycle Management

```go
// List registered types
types := gpa.ListTypes()

// List instances for a type
instances := gpa.ListInstances("gorm")

// Remove and close a provider
gpa.Remove("gorm", "primary")

// Remove and close all providers
gpa.RemoveAll()

// Health check
health := gpa.HealthCheck()
// Returns map[string]map[string]error — [type][instance]error
```

## Type Inference

The registry maps Go `reflect.Type` to provider type names. When `Register[T]` is called:

1. The provider's `ProviderInfo().Name` is used as the type key
2. `reflect.TypeOf(provider)` is mapped to this name
3. On `Get[T]()`, the type is looked up in reverse to find the correct provider

This means resolution is fully type-safe at compile time — no string matching required.

## Provider Interface

All providers implement:

```go
type Provider interface {
    Configure(config Config) error
    Health() error
    Close() error
    SupportedFeatures() []Feature
    ProviderInfo() ProviderInfo
}
```

And optionally one of:
- `SQLProvider` — for SQL databases (GORM, Bun)
- `KeyValueProvider` — for key-value stores (Redis)
- `DocumentProvider` — for document databases (MongoDB)
- `GraphProvider` — for graph databases
- `WideColumnProvider` — for wide-column stores

### Type Assertion Helpers

```go
if sqlProvider, ok := gpa.AsSQLProvider(provider); ok {
    db := sqlProvider.DB()
}

if gpa.IsSQLProvider(provider) {
    // provider is a SQL provider
}
```
