---
title: Migrations
type: docs
prev: docs/database/bunconnector
next: docs/migrations/schema-builder
weight: 70
sidebar:
  open: true
---

## Overview

`lemmego/migration` is version-controlled, bidirectional schema evolution for
SQLite, MySQL and PostgreSQL, with a schema builder that renders the same
declaration differently on each.

A migration is a Go file with an up and a down function, both
`func(tx *sql.Tx) error`. The builder is there so that what all three drivers
can do is written once; `tx.Exec` is there, as a first-class escape hatch,
for what only one of them can.

```go
func mig_20250706000001_create_users_table_up(tx *sql.Tx) error {
    schema := migration.Create("users", func(t *migration.Table) {
        t.BigIncrements("id").Primary()
        t.String("email", 255)
        t.String("handle", 30)
        t.TimestampTz("created_at", 0).Default(migration.Expr("now()"))

        t.Check("users_handle_format", `handle ~ '^[a-z0-9][a-z0-9_]{1,29}$'`)
        t.Index("email").Unique().Name("users_email_key")
    }).Build()

    _, err := tx.Exec(schema)
    return err
}

func mig_20250706000001_create_users_table_down(tx *sql.Tx) error {
    _, err := tx.Exec(migration.Drop("users").Build())
    return err
}
```

## What it does

- **Bidirectional** — an up and a down per migration, so a deploy is
  reversible.
- **Dialect-aware** — one declaration, three renderings. Unsigned integers,
  timestamps with zones, inline versus standalone indexes, and every
  `ALTER TABLE` drop action differ between the drivers, and the builder knows
  how.
- **Refuses rather than guesses** — a partial index on MySQL, a tolerant drop
  on MySQL, a column change on SQLite: `Validate` reports each instead of
  emitting SQL the server will reject, or worse, SQL it will accept with the
  part you wanted silently missing.
- **Tracked** — applied migrations are recorded in `schema_migrations`,
  grouped into a batch per run.

## Getting started

Generate a migration:

```shell
lemmego g migration create_users_table
```

Apply it:

```shell
lemmego run migrate up
```

Then read [Schema Builder](/docs/migrations/schema-builder) for what you can
declare, [Column Types](/docs/migrations/column-types) for what each method
gives you per driver, [Writing Migrations](/docs/migrations/writing-migrations)
for the shape of a file and the one-transaction rule, and
[Running Migrations](/docs/migrations/running-migrations) for the CLI.

## Common pitfalls

Each is covered again in context. These three are worth knowing up front:

- **`TimestampTz(name, 0)`** — any other precision emits
  `TIMESTAMP WITH TIME ZONE(6)`, which PostgreSQL rejects.
- **`Enum` enforces nothing on SQLite** — MySQL gets a native `ENUM` and
  PostgreSQL a `TEXT` with a `CHECK`, but SQLite gets plain `TEXT` and no
  constraint. Use `String` plus `Check` if you need all three.
- **`ForeignID` is not a foreign key column** — it declares an
  auto-incrementing one. Use `UnsignedBigInt` plus `Foreign`.
