---
title: Schema Builder
type: docs
prev: docs/migrations/
next: docs/migrations/column-types
sidebar:
  open: true
weight: 31
---

## Overview

The schema builder provides a fluent API for creating, altering, and dropping database tables in a database-agnostic way.

## Creating Tables

```go
schema := migration.Create("users", func(t *migration.Table) {
    t.BigIncrements("id")
    t.String("name").NotNull()
    t.String("email").Unique()
    t.Timestamps()
}).Build()
// Execute with: tx.Exec(schema)
```

## Altering Tables

```go
schema := migration.Alter("users", func(t *migration.Table) {
    t.String("phone").Nullable()
    t.Boolean("is_active").Default(true)
}).Build()
```

## Dropping Tables

```go
err := migration.Drop("users")
// Returns "DROP TABLE IF EXISTS users"
```

## Renaming Tables

```go
migration.Rename("old_name", "new_name")
```

## Available Column Types

| Method | Description |
|--------|-------------|
| `Increments(name)` | Auto-incrementing integer (primary key) |
| `BigIncrements(name)` | Big auto-incrementing integer |
| `String(name, length)` | VARCHAR with optional length |
| `Text(name)` | TEXT field |
| `UUID(name)` | UUID field |
| `ULID(name)` | ULID field |
| `Integer(name)` | INT |
| `BigInteger(name)` | BIGINT |
| `TinyInt(name)` | TINYINT |
| `SmallInt(name)` | SMALLINT |
| `MediumInt(name)` | MEDIUMINT |
| `Binary(name)` | BLOB |
| `Boolean(name)` | BOOLEAN/TINYINT |
| `Char(name, length)` | CHAR with optional length |
| `DateTime(name, precision)` | DATETIME |
| `DateTimeTz(name, precision)` | DATETIME with timezone |
| `Date(name)` | DATE |
| `Time(name, precision)` | TIME |
| `Timestamp(name, precision)` | TIMESTAMP |
| `TimestampTz(name, precision)` | TIMESTAMP with timezone |
| `Decimal(name, precision, scale)` | DECIMAL |
| `Double(name)` | DOUBLE |
| `Float(name, precision)` | FLOAT |
| `Enum(name, values)` | ENUM |
| `UnsignedInteger(name)` | UNSIGNED INT |
| `UnsignedBigInteger(name)` | UNSIGNED BIGINT |

## Column Modifiers

```go
t.String("email").Unique()
t.String("name").NotNull()
t.String("phone").Nullable()
t.Integer("age").Default(18)
t.String("status").Default("'active'")  // Note: SQL string literals need quotes
t.String("old_field").Change()           // Modify existing column
```

**Important**: String defaults use SQL syntax — `Default("'active'")` means the SQL literal `'active'`.

## Timestamps Helper

```go
t.Timestamps()
// Adds: created_at TIMESTAMP NULL, updated_at TIMESTAMP NULL

t.SoftDeletes()
// Adds: deleted_at TIMESTAMP NULL

t.SoftDeletesTz(precision)
// Adds: deleted_at TIMESTAMPTZ(precision) NULL
```

## Constraints

### Primary Keys

```go
t.PrimaryKey("id")
t.PrimaryKey("order_id", "product_id") // Composite
t.DropPrimaryKey("pk_name")             // Drop primary key
```

### Indexes

```go
t.Index("email")                         // Single column
t.Index("email", "status")               // Composite
t.DropIndex("index_name")                // Drop index
```

### Unique Keys

```go
t.UniqueKey("email")                     // Single column
t.UniqueKey("email", "status")           // Composite
t.DropUniqueKey("unique_key_name")       // Drop unique
```

### Foreign Keys

```go
t.Foreign("user_id").References("id").On("users").OnDelete("cascade")
t.ForeignID("user_id").Constrained()
// Convenience: references id on the pluralized table name
```

Full foreign key API:

```go
t.Foreign("user_id").
    References("id").
    On("users").
    OnDelete("cascade").
    OnUpdate("restrict")

t.ForeignID("user_id").
    Constrained()                           // Uses conventions
    ConstrainedFunc(func(fk *foreignKey) {  // Custom
        fk.OnDelete("set null")
    })
```

## Helper Methods

```go
t.ID()
// Shortcut for BigIncrements("id")

t.StringTimestamps()
// created_at DATETIME, updated_at DATETIME (not nullable)
```
