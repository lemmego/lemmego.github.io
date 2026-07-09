---
title: Caching
type: docs
prev: docs/services/logging
next: docs/services/queue
sidebar:
  open: true
weight: 51
---

## Overview

The `cache` package defines a `Store` interface for caching operations. Currently, a file-based implementation exists as a stub, with the interface designed for multiple backend providers.

## Cache Interface

```go
type Store interface {
    Get(key string) (interface{}, error)
    Many(keys []string) (map[string]interface{}, error)
    Put(key string, value interface{}, ttl time.Duration) error
    PutMany(values map[string]interface{}, ttl time.Duration) error
    Increment(key string, value int64) (int64, error)
    Decrement(key string, value int64) (int64, error)
    Forever(key string, value interface{}) error
    Forget(key string) error
    Flush() error
    GetPrefix() string
}
```

## Usage Pattern

```go
store := cache.NewFileStore("storage/cache")

// Check cache first
if cached, err := store.Get("users:active"); err == nil {
    return cached.([]User)
}

// Miss — load from database
users := loadActiveUsers()

// Store in cache
store.Put("users:active", users, 5*time.Minute)
return users
```

## Status

The cache package is a work in progress. The current implementation provides the interface definition and a basic file store. For production caching, use Redis through the GPA Redis provider.

## Future Providers

Planned cache backends:
- Redis (via go-redis)
- Memcached
- In-memory (sync.Map-based)
- Database-backed
