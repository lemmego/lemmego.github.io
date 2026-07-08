---
title: Running Migrations
type: docs
prev: docs/migrations/writing-migrations
sidebar:
  open: true
weight: 34
---

## CLI Usage

Migrations are run through the application CLI:

### Up (Apply Pending)

```shell
lemmego run migrate up
```

Apply a specific number of migrations:

```shell
lemmego run migrate up --step=3
```

### Down (Rollback)

Rollback the last batch:

```shell
lemmego run migrate down
```

Rollback multiple batches:

```shell
lemmego run migrate down --step=2
```

### Status

```shell
lemmego run migrate status
```

Output:

```
[2025-07-06 00:00:01] create_users_table .................... 2025-07-06 12:00:00
[2025-07-06 00:00:02] create_posts_table .................... Pending
```

### Create New Migration

```shell
lemmego run migrate create create_posts_table
```

Or from outside the app:

```shell
lemmego g migration create_posts_table
```

## How Migration Tracking Works

The migration system creates a `schema_migrations` table in your database:

```sql
CREATE TABLE schema_migrations (
    version VARCHAR(255),
    batch INT
);
```

- **version** — The migration's version string (e.g., `20250706000001`)
- **batch** — The batch number when the migration was applied

When running `up`:

1. Pending migrations are collected in version order
2. A new batch number is created (max batch + 1)
3. Each migration runs inside a transaction
4. On success, the migration's version and batch are recorded
5. If any migration in the batch fails, only that migration is rolled back

When running `down`:

1. The last batch number is identified
2. Migrations in that batch are rolled back in reverse version order
3. Each rollback runs inside a transaction
4. The migration record is removed from `schema_migrations`

## Programmatic Use

```go
import "github.com/lemmego/migration"

m := migration.GetMigrator()

// Initialize (creates tracking table)
err := m.Init()

// Apply all pending migrations
err := m.Up(-1)

// Apply 2 migrations
err := m.Up(2)

// Rollback latest batch
err := m.Down(-1)

// Rollback 1 batch
err := m.Down(1)

// Print status
m.MigrationStatus()
```

## Database Connection

The migrator reads the `DB_DRIVER` environment variable to determine the dialect. Database connection parameters are configured through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_DRIVER` | `sqlite` | Database driver (`sqlite`, `mysql`, `pgsql`) |
| `DB_HOST` | `127.0.0.1` | Database host |
| `DB_PORT` | (driver default) | Database port |
| `DB_DATABASE` | `storage/database.sqlite` | Database name/path |
| `DB_USERNAME` | `root` | Database user |
| `DB_PASSWORD` | `` | Database password |

## Best Practices

- **One change per migration** — Keep migrations focused on a single schema change
- **Always write a down migration** — Ensure every change is reversible
- **Test both directions** — Run `up` then `down` to verify correctness
- **Don't modify existing migrations** — Create a new migration instead
- **Use version control** — Migrations should be committed to git
