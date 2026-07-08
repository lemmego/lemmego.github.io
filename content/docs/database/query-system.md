---
title: Query System
type: docs
prev: docs/database/generic-repository
next: docs/database/entity-hooks
sidebar:
  open: true
weight: 21
---

## Overview

GPA provides two ways to build queries: option-based (functional) and builder-based (fluent). Both produce the same `Query` object and support the same set of conditions.

## Conditions

Conditions are the building blocks of queries:

```go
// Basic conditions
gpa.Where("age", gpa.OpGreaterThan, 18)
gpa.Where("status", gpa.OpEqual, "active")
gpa.Where("name", gpa.OpLike, "%john%")

// Available operators
gpa.OpEqual              // =
gpa.OpNotEqual           // !=
gpa.OpGreaterThan        // >
gpa.OpGreaterThanOrEqual // >=
gpa.OpLessThan           // <
gpa.OpLessThanOrEqual    // <=
gpa.OpLike               // LIKE
gpa.OpNotLike            // NOT LIKE
gpa.OpIn                 // IN
gpa.OpNotIn              // NOT IN
gpa.OpBetween            // BETWEEN
gpa.OpIsNull             // IS NULL
gpa.OpIsNotNull          // IS NOT NULL
```

### Convenience Builders

```go
gpa.Where("age", gpa.OpGreaterThan, 18)
gpa.WhereIn("status", "active", "pending")
gpa.WhereLike("name", "%john%")
gpa.WhereNull("deleted_at")
gpa.WhereNotNull("email")
```

### Composite Conditions

```go
// AND condition
gpa.And(
    gpa.Where("age", gpa.OpGreaterThan, 18),
    gpa.Where("status", gpa.OpEqual, "active"),
)

// OR condition
gpa.Or(
    gpa.Where("role", gpa.OpEqual, "admin"),
    gpa.Where("role", gpa.OpEqual, "moderator"),
)
```

## Query Options (Functional API)

Pass options directly to repository methods:

```go
users, err := userRepo.Query(ctx,
    gpa.Where("age", gpa.OpGreaterThan, 18),
    gpa.Where("status", gpa.OpEqual, "active"),
    gpa.OrderBy("name", gpa.OrderAsc),
    gpa.Limit(10),
    gpa.Offset(20),
    gpa.Fields("id", "name", "email"),
    gpa.Preload("Profile", "Posts"),
    gpa.Distinct(),
)
```

### Sort and Pagination

```go
gpa.OrderBy("created_at", gpa.OrderDesc)
gpa.OrderBy("name", gpa.OrderAsc)
gpa.Limit(10)
gpa.Offset(20)
```

### Field Selection

```go
gpa.Fields("id", "name", "email")
// Same as:
gpa.Select("id", "name", "email")
```

### Joins

```go
gpa.Join("profiles", "profiles.user_id", "users.id")
gpa.InnerJoin("orders", "orders.user_id", "users.id")
gpa.LeftJoin("comments", "comments.user_id", "users.id")
gpa.RightJoin(...)
gpa.FullJoin(...)
```

### Grouping and Having

```go
gpa.GroupBy("status")
gpa.Having("count(*)", gpa.OpGreaterThan, 5)
```

### Locking

```go
gpa.Lock(gpa.LockForUpdate)
gpa.Lock(gpa.LockShared)
```

### Preloading Relationships

```go
gpa.Preload("Profile")
gpa.Preload("Posts.Comments")  // Nested eager loading
```

## Query Builder (Fluent API)

The fluent `QueryBuilder` provides a chainable alternative:

```go
qb := gpa.NewQueryBuilder[User]()

qb.Where("age", gpa.OpGreaterThan, 18).
   Where("active", gpa.OpEqual, true).
   OrderBy("name", gpa.OrderAsc).
   Limit(10).
   Offset(0).
   Preload("Profile")

// Execute
users, err := qb.Execute(ctx, userRepo)
user, err := qb.ExecuteOne(ctx, userRepo)
count, err := qb.Count(ctx, userRepo)
```

### Full Builder API

```go
qb := gpa.NewQueryBuilder[T]()

qb.Where(field, operator, value)
qb.OrderBy(field, direction)
qb.Limit(n)
qb.Offset(n)
qb.Select(fields...)      // Same as Fields()
qb.Join(table, on, ...)
qb.InnerJoin(table, on)
qb.LeftJoin(table, on)
qb.GroupBy(fields...)
qb.Having(field, operator, value)
qb.Distinct()
qb.Lock(lockType)
qb.Preload(relations...)

// Build the Query object without executing
query := qb.Build()
```

## Subqueries

```go
gpa.ExistsSubQuery("SELECT 1 FROM orders WHERE orders.user_id = users.id")
gpa.InSubQuery("user_id", "SELECT id FROM users WHERE active = true")
gpa.CorrelatedSubQuery("SELECT AVG(score) FROM reviews WHERE reviews.product_id = products.id")
```
