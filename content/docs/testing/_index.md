---
title: Testing
type: docs
prev: docs/filesystem/
next: docs/deployment/
sidebar:
  open: true
weight: 47
---

## Overview

Lemmego provides testing utilities for repository testing with in-memory databases and Inertia response assertions.

## Repository Testing

Use SQLite in-memory database for fast, isolated database tests:

```go
import (
    "testing"
    "github.com/lemmego/gpa"
    "github.com/lemmego/gpagorm"
)

func setupTestDB(t *testing.T) *gpagorm.Provider {
    t.Helper()
    
    provider, err := gpagorm.NewProvider(gpa.Config{
        Driver:   "sqlite",
        Database: "file::memory:?cache=shared",
    })
    if err != nil {
        t.Fatal(err)
    }
    
    // Auto-migrate
    provider.Migrate(&User{}, &Post{})
    
    return provider
}

func TestUserRepository_FindByID(t *testing.T) {
    provider := setupTestDB(t)
    repo := gpagorm.GetRepository[User](provider)
    
    user := &User{Name: "John", Email: "john@example.com"}
    repo.Create(ctx, user)
    
    found, err := repo.FindByID(ctx, user.ID)
    if err != nil {
        t.Fatal(err)
    }
    if found.Name != "John" {
        t.Errorf("expected John, got %s", found.Name)
    }
}
```

## Inertia Response Testing

The inertia package provides `Assertable` for testing Inertia responses:

```go
import "github.com/lemmego/inertia"

func TestUserIndex(t *testing.T) {
    // ... make request, get response
    
    assertion := inertia.AssertFromReader(resp.Body)
    
    assertion.AssertComponent("Users/Index")
    assertion.AssertVersion("1.0")
    assertion.AssertURL("/users")
    assertion.AssertProps("users")
    assertion.AssertEncryptHistory(false)
    assertion.AssertClearHistory(false)
    
    // Assert specific prop values
    props := assertion.AssertProps("users")
    // props contains the parsed prop data
}
```

Also supports creating assertions from strings, bytes, and JSON:

```go
assertion := inertia.AssertFromString(`{"component":"Users/Index","props":{...}}`)
assertion := inertia.AssertFromBytes(responseBytes)
```

## Testing Tips

### Entity Hooks

Test hooks by creating entities and verifying side effects:

```go
func TestUserBeforeCreate(t *testing.T) {
    provider := setupTestDB(t)
    repo := gpagorm.GetRepository[User](provider)
    
    user := &User{Email: "JOHN@EXAMPLE.COM"}
    repo.Create(ctx, user)
    
    if user.Email != "john@example.com" {
        t.Errorf("expected lowercased email, got %s", user.Email)
    }
}
```

### Transactions

```go
func TestTransaction(t *testing.T) {
    provider := setupTestDB(t)
    repo := gpagorm.GetRepository[User](provider)
    
    err := repo.Transaction(ctx, func(tx gpa.Transaction[User]) error {
        tx.Create(ctx, &User{Name: "Alice"})
        return fmt.Errorf("rollback")
    })
    
    // Transaction was rolled back, user shouldn't exist
    count, _ := repo.Count(ctx)
    if count != 0 {
        t.Error("expected 0 users after rollback")
    }
}
```
