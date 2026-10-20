---
title: Running Migrations
type: docs
prev: docs/migrations/writing-migrations
sidebar:
  open: true
weight: 34
---

## Commands

```shell
lemmego run migrate up          # apply everything pending
lemmego run migrate down        # roll back
lemmego run migrate status      # what has run and what has not
lemmego run migrate create -n create_users_table
```

Each of `up` and `down` takes `--step` (`-s`), and each of the three takes
`--driver` (`-d`) and `--dsn` (`-u`) to point at a database other than the
one the application is configured with.

## What `--step` counts

**Migrations, on both commands.** `--step 2` on `down` reverts the two most
recently applied migrations, not the two most recent batches.

That is worth stating because it used to count batches, and the two are the
same only when every batch holds one migration. A batch is one `migrate up`
run, so on any project whose schema went up in a single command — every
project on its first deploy — the latest batch is the entire schema, and
asking to undo one migration undid all of them. Fixed in v0.1.24; if you are
pinned below that, `down --step 1` is not what it says.

With no `--step`, `down` reverts the whole of the latest batch.

```shell
lemmego run migrate down --step 1    # the last migration
lemmego run migrate down             # the last batch
```

## One transaction per run

`up` opens a single transaction, runs every pending migration inside it, and
commits once — with a 30-second budget for the whole run. A failure anywhere
rolls back the entire run; there are no savepoints between migrations. `down`
works the same way.

This is what makes a failed deploy leave a schema that is either entirely
before or entirely after, and what makes
`CREATE INDEX CONCURRENTLY` impossible — see
[The whole batch is one transaction](/docs/migrations/writing-migrations#the-whole-batch-is-one-transaction).

## How it works

1. `Init()` creates the `schema_migrations` table if it is absent.
2. Migrations already recorded there are marked done in memory.
3. `up` applies the pending ones in version order and records them against a
   new batch number.
4. `down` reverts in reverse version order — a number of migrations, or the
   latest batch.

## Pointing at another database

The `--dsn` flag is how you run migrations against a scratch database, which
is the cheapest way to check that a migration is reversible before it reaches
anything you care about:

```shell
createdb myapp_scratch
lemmego run migrate up   -u "postgres://user@localhost:5432/myapp_scratch?sslmode=disable"
lemmego run migrate down -u "postgres://user@localhost:5432/myapp_scratch?sslmode=disable"
dropdb myapp_scratch
```

Up, down, and up again on a throwaway database catches the two failures a
review does not: a down that leaves a table behind because something still
references it, and an up that only works on an empty schema.

## Which database migrate connects to

`migrate` resolves its DSN in this order, taking the first that is set:

1. `--dsn`
2. `DATABASE_URL_UNPOOLED`
3. `DATABASE_URL`
4. the `DB_*` components — `DB_HOST`, `DB_PORT`, `DB_USERNAME`, `DB_PASSWORD`,
   `DB_DATABASE`, `DB_PARAMS`

A present-but-empty variable is treated as absent, so a stray line in a `.env`
does not shadow the next source.

Note `DB_PARAMS` is **separate** from the `options` map in
`internal/configs/database.go` that the application reads. `lib/pq` defaults to
`sslmode=require`, so a local PostgreSQL needs `DB_PARAMS=sslmode=disable` in
`.env` or migrations will fail to connect while the application itself is fine.

### Never migrate through a connection pooler

`DATABASE_URL_UNPOOLED` sits above `DATABASE_URL` for a specific reason, added
in `migration` v0.5.1.

Managed providers such as Neon and Supabase publish two URLs for one database:
a pooled one fronted by PgBouncer in transaction mode, and a direct one. Their
quickstarts point you at the pooled URL, so that is usually what ends up in
`DATABASE_URL` — and it is the wrong endpoint for a migration, twice over.

`lib/pq` issues every parameterised query on the *unnamed* prepared statement
over the extended protocol. Under transaction pooling a `Parse` from one
logical connection can pair with a `Bind` from another, and the migrator's own
bookkeeping queries are parameterised. So a schema change can fail partway
through a deploy, reporting a statement nobody wrote:

```text
pq: bind message supplies 2 parameters, but prepared statement "" requires 1
```

It is intermittent and happens in both directions. Measured on a real
deployment: of 30 concurrent parameterised queries, **28 failed through the
pooler and 0 failed direct**.

Pooled connections are also session-less by design, so anything a migration
does that outlives a single statement — an advisory lock, a `SET`, a
session-scoped temp table — applies to whichever backend answered rather than
to the migration.

Set both variables and the right endpoint is chosen for you:

```shell
DATABASE_URL=postgres://...-pooler.../db?sslmode=require
DATABASE_URL_UNPOOLED=postgres://.../db?sslmode=require
```

An explicit `--dsn` still wins, including when you deliberately want the pooled
endpoint.
