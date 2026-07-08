---
title: Writing Migrations
type: docs
prev: docs/migrations/column-types
next: docs/migrations/running-migrations
sidebar:
  open: true
weight: 33
---

## Structure

Each migration file is a Go file in `internal/migrations/` with:

1. An `init()` function that registers the migration with the migrator
2. An `up` function that applies schema changes
3. A `down` function that reverts schema changes

## Registration

```go
func init() {
    migration.GetMigrator().AddMigration(&migration.Migration{
        Version: "20250706000001",
        Up:      mig_users_up,
        Down:    mig_users_down,
    })
}
```

The version should be a timestamp-based string (format: `YYYYMMDDHHMMSS`). The CLI auto-generates this when you run:

```shell
lemmego g migration create_users_table
```

## Writing Up Migrations

### Create Table

```go
func mig_up(tx *sql.Tx) error {
    schema := migration.Create("users", func(t *migration.Table) {
        t.BigIncrements("id")
        t.String("name").NotNull()
        t.String("email").Unique()
        t.String("password").NotNull()
        t.Timestamps()
    }).Build()
    _, err := tx.Exec(schema)
    return err
}
```

### Alter Table

```go
func mig_up(tx *sql.Tx) error {
    schema := migration.Alter("users", func(t *migration.Table) {
        t.String("phone").Nullable().After("email")
        t.Boolean("is_verified").Default(false)
    }).Build()
    _, err := tx.Exec(schema)
    return err
}
```

### Drop Table

```go
func mig_up(tx *sql.Tx) error {
    _, err := tx.Exec(migration.Drop("old_sessions"))
    return err
}
```

### Foreign Keys

```go
func mig_up(tx *sql.Tx) error {
    schema := migration.Create("posts", func(t *migration.Table) {
        t.BigIncrements("id")
        t.String("title").NotNull()
        t.Text("body")
        t.ForeignID("user_id").Constrained()
        t.Timestamps()
    }).Build()
    _, err := tx.Exec(schema)
    return err
}
```

### With Indexes

```go
func mig_up(tx *sql.Tx) error {
    schema := migration.Create("posts", func(t *migration.Table) {
        t.BigIncrements("id")
        t.String("slug").Unique()
        t.String("status")
        t.Index("status")
    }).Build()
    _, err := tx.Exec(schema)
    return err
}
```

## Writing Down Migrations

The down function should revert what the up function did:

```go
func mig_down(tx *sql.Tx) error {
    _, err := tx.Exec(migration.Drop("posts"))
    return err
}
```

Or for alter operations:

```go
func mig_down(tx *sql.Tx) error {
    schema := migration.Alter("users", func(t *migration.Table) {
        t.DropColumn("phone")
    }).Build()
    _, err := tx.Exec(schema)
    return err
}
```

## Complete Example

```go
package migrations

import (
    "database/sql"
    "github.com/lemmego/migration"
)

func init() {
    migration.GetMigrator().AddMigration(&migration.Migration{
        Version: "20250706000001",
        Up:      mig_users_up,
        Down:    mig_users_down,
    })
}

func mig_users_up(tx *sql.Tx) error {
    schema := migration.Create("users", func(t *migration.Table) {
        t.BigIncrements("id")
        t.String("name").NotNull()
        t.String("email").Unique().NotNull()
        t.String("password").NotNull()
        t.Timestamps()
        t.SoftDeletes()
    }).Build()
    _, err := tx.Exec(schema)
    return err
}

func mig_users_down(tx *sql.Tx) error {
    _, err := tx.Exec(migration.Drop("users"))
    return err
}
```
