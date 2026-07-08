---
title: GPA Overview
type: docs
prev: docs/http/context
next: docs/database/provider-registry
sidebar:
  open: true
weight: 18
---

## What is GPA?

**GPA** (Go Persistence API) is the database abstraction layer at the heart of Lemmego. It provides a unified, type-safe persistence API across SQL, NoSQL, Key-Value, and Graph databases through a plugin-based adapter pattern.

### Key Features

- **Compile-time type safety** — Generic `Repository[T]` returns `*T` and `[]*T` directly, no `interface{}` casting
- **Unified API** — Same CRUD operations across SQL, MongoDB, Redis, and more
- **Plugin architecture** — Swap database backends without application code changes
- **No runtime reflection** — Go generics provide type safety without runtime overhead
- **Entity hooks** — Lifecycle callbacks for validation, timestamps, and business logic

### Architecture

```
Application Code
      |
      v
+----------------------------+
|  Repository[T]             |  <-- Primary API (generic CRUD)
|  Transaction[T]            |
|  QueryBuilder[T]           |
+----------------------------+
      |
      v
+----------------------------+
|  ProviderRegistry          |  <-- Singleton registry (type-safe)
+----------------------------+
      |
      v
+----------------------------+
|  Provider (interface)      |  <-- Base interface
+----------------------------+
      |
      +-- SQLProvider ---------+--> GORM, Bun
      |                        +--> SQLRepository[T], MigratableRepository[T]
      |
      +-- KeyValueProvider ---+--> Redis
      |                        +--> Basic/Batch/TTL/Increment/Pattern KV repos
      |
      +-- DocumentProvider ---+--> MongoDB
      |                        +--> DocumentRepository[T] (aggregation, geo, text)
      |
      +-- GraphProvider ------+--> Neo4j (future)
      |
      +-- WideColumnProvider -+--> Cassandra (future)
```

### Available Providers

| Provider | Package | Type | Status |
|----------|---------|------|--------|
| GORM | `github.com/lemmego/gpagorm` | SQL | Production-ready |
| Bun | `github.com/lemmego/gpabun` | SQL | In development |
| MongoDB | `github.com/lemmego/gpamongo` | Document | In development |
| Redis | `github.com/lemmego/gparedis` | Key-Value | Production-ready |

### Quick Example

```go
import (
    "github.com/lemmego/gpa"
    "github.com/lemmego/gpagorm"
)

// Create a GORM provider
provider, _ := gpagorm.NewProvider(config)

// Register with the global registry
gpa.Register[*gpagorm.Provider]("primary", provider)

// Create a type-safe repository
userRepo := gpagorm.GetRepository[User]()

// Type-safe CRUD
user, _ := userRepo.FindByID(ctx, 1)   // Returns *User
users, _ := userRepo.FindAll(ctx)       // Returns []*User
userRepo.Create(ctx, &User{Name: "Jane"})
```
