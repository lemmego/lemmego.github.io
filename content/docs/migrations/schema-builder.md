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
    t.String("name", 255).NotNull()
    t.String("email", 255).Unique()
    t.DateTime("created_at", 6).Nullable()
    t.DateTime("updated_at", 6).Nullable()
}).Build()
// Execute with: tx.Exec(schema)
```

## Altering Tables

```go
schema := migration.Alter("users", func(t *migration.Table) {
    t.String("phone", 255).Nullable()
    t.Boolean("is_active").Default(true)
}).Build()
```

## Dropping Tables

```go
err := migration.Drop("users")
// Returns "DROP TABLE IF EXISTS users"
```

## Renaming Columns

There is no table rename helper. Columns are renamed through `Alter`:

```go
schema := migration.Alter("users", func(t *migration.Table) {
    t.RenameColumn("email", "email_address")
}).Build()
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
t.String("email", 255).Unique()
t.String("name", 255).NotNull()
t.String("phone", 255).Nullable()
t.Integer("age").Default(18)
t.String("status", 255).Default("'active'")  // Note: SQL string literals need quotes
t.String("old_field", 255).Change()           // Modify existing column
```

**Important**: String defaults use SQL syntax — `Default("'active'")` means the SQL literal `'active'`.

## Timestamps and Soft Deletes

There are no `Timestamps()` or `SoftDeletes()` shortcuts — declare the columns:

```go
t.DateTime("created_at", 6).Nullable()
t.DateTime("updated_at", 6).Nullable()
t.DateTime("deleted_at", 6).Nullable()

t.DateTimeTz("published_at", 6).Nullable()   // with a time zone
```

A soft-delete column must be nullable, and the model field must be
`*time.Time` or `sql.NullTime`. See [Soft deletes](/docs/orm/writes#soft-deletes).

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

## Primary Keys

There is no `ID()` shortcut. Declare the key explicitly:

```go
t.BigIncrements("id").Primary()
```

On MySQL an auto-increment column must be a key; if you do not mark it, the
builder marks it for you rather than emitting DDL the server would refuse.
