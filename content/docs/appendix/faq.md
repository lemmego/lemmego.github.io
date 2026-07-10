---
title: FAQ
type: docs
prev: docs/appendix/
sidebar:
  open: true
weight: 70
---

## General

### What is Lemmego?

Lemmego is a full-stack web framework for Go that provides a complete toolkit for building web applications: HTTP routing, middleware, database abstraction, migrations, authentication, frontend integration, and CLI tooling.

### Is Lemmego production-ready?

Lemmego is experimental. The core framework (HTTP layer, sessions, config) and some GPA providers (GORM, Redis) are functional, but the project is under active development. Not recommended for production use yet.

### How is this different from other Go frameworks?

Unlike minimal routers or micro-frameworks, Lemmego provides a full application architecture: service containers, provider plugins, database abstraction, migrations, CLI generators, and frontend integration.

## Framework

### What Go version is required?

Go 1.24 or later (the framework uses generics extensively).

### Can I use Lemmego with just the HTTP layer?

Yes. The framework is modular. You can use the `api` package for HTTP routing and middleware without using GPA or the CLI.

### What frontend options are available?

Go Templates, Templ (type-safe Go templates), and Inertia.js with React or Vue. All three work with the Vite asset pipeline.

## Database

### What databases are supported?

Through GPA providers: PostgreSQL, MySQL, SQLite (via GORM or Bun), MongoDB, and Redis. The provider system makes it easy to add more.

### Can I use raw SQL?

Yes. SQL providers support `RawQuery`, `RawExec`, and `FindBySQL` for direct SQL access.

### What are entity hooks?

Lifecycle callbacks that run automatically during CRUD operations. You can validate, transform data, and implement cross-cutting concerns by implementing interfaces like `BeforeCreateHook`, `AfterFindHook`, etc.

## CLI

### How do I create a new project?

```shell
lemmego new my-project
```

### How do I generate code?

```shell
lemmego g model User        # Model
lemmego g handlers User     # CRUD handlers
lemmego g migration ...     # Migration
lemmego g input ...         # Validation input
lemmego g form ...          # Form component
```

### How do I run migrations?

```shell
lemmego run migrate up
lemmego run migrate down
lemmego run migrate status
```

## Troubleshooting

### The `lemmego` command is not found

Ensure `$GOPATH/bin` is in your PATH, or install via the installer script.

### `templ` files are not updating

Run `templ generate` manually or use `lemmego dev` which starts the templ watcher.

### Database connection fails

Check your `.env` file for correct `DB_CONNECTION`, `DB_HOST`, `DB_PORT`, and credentials.

### CSRF token mismatch

Ensure all state-changing forms include the `_token` field. For API routes, add them to the CSRF exclusion list.
