---
title: Migrations
type: docs
prev: docs/database/gormconnector
next: docs/migrations/schema-builder
sidebar:
  open: true
weight: 30
---

## Overview

Lemmego's migration system provides a version-controlled, bidirectional database schema evolution tool. It supports SQLite, MySQL, and PostgreSQL with a fluent schema builder DSL.

## Features

- **Bidirectional** — Up and Down migrations for safe rollbacks
- **Schema Builder DSL** — Fluent API for creating, altering, and dropping tables
- **Multi-Database** — SQLite, MySQL, PostgreSQL
- **Migration Tracking** — Tracks applied migrations in a `schema_migrations` table
- **Batch Management** — Migrations are grouped into batches for rollback
- **Savepoints** — Each migration runs in a transaction for atomicity

## Creating Migrations

Use the CLI to generate a migration file:

```shell
lemmego g migration create_users_table
```

This creates a timestamped file in `internal/migrations/`:

```go
// internal/migrations/20250706000001_create_users_table.go

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
        t.String("email").Unique()
        t.Timestamps()
    }).Build()
    _, err := tx.Exec(schema)
    return err
}

func mig_users_down(tx *sql.Tx) error {
    return migration.Drop("users")
}
```

## Running Migrations

### Up (Apply)

```shell
lemmego run migrate up
```

Or step by step:

```shell
lemmego run migrate up --step=2
```

### Down (Rollback)

Rollback the last batch:

```shell
lemmego run migrate down
```

Or rollback a specific number of batches:

```shell
lemmego run migrate down --step=2
```

### Status

Check which migrations are pending:

```shell
lemmego run migrate status
```

### Create from CLI

```shell
lemmego run migrate create create_posts_table
```

## How It Works

1. On `Init()`, the migrator creates a `schema_migrations` table (if it doesn't exist)
2. Already-applied migrations are marked as `done` in memory
3. Running `up` applies pending migrations in version order, grouped into a batch
4. Each migration runs inside a transaction — failure rolls back the individual migration
5. Running `down` rolls back the last N batches in reverse version order
