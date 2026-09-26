---
title: "CLI & Generators"
type: docs
prev: docs/project-structure
next: docs/http/
sidebar:
  open: true
weight: 4.5
---

## Overview

The `lemmego` CLI is your primary tool for creating projects, generating code, and managing the development workflow.

## Installation

```shell
# Via installer
curl -fsSL https://raw.githubusercontent.com/lemmego/cli/refs/heads/main/installer.sh | sudo sh

# Via Go
go install github.com/lemmego/cli/cmd/lemmego@latest

# Via Homebrew (macOS)
brew install lemmego/tap/lemmego
```

Verify:

```shell
lemmego --version
```

## Project Scaffolding

### `lemmego new <dirname>`

Creates a new Lemmego project with interactive configuration.

**Arguments:**
- `<dirname>` — Directory name for the new project

**Interactive prompts.** The first question asks how much you want to be asked:

- **Quick start** — module name, preset, auth and (for MVC) the frontend.
  Everything else takes a sensible default: SQLite, the Lemmego ORM, a file
  cache, a SQL queue, file sessions and local storage.
- **Customise** — pages through a driver for each part of the project.

The full set of questions:

| Question | Options | Default |
|---|---|---|
| Module name | a Go module path | — |
| Preset | `mvc`, `rest_api` | `mvc` |
| Authentication | yes / no | yes |
| Frontend (MVC only) | Go Templates, Templ, Inertia React, Inertia Vue, Templ + Inertia React, Templ + Inertia Vue | Go Templates |
| Database | SQLite, PostgreSQL, MySQL, **None** | SQLite |
| SQL layer | [Lemmego ORM](/docs/orm/), GORM, Bun | Lemmego ORM |
| Cache | File, Memory, Redis, **None** | File |
| Queue | SQL, Redis, **None** | SQL |
| Sessions | File, Memory, Redis | File |
| Storage | Local, Amazon S3 | Local |
| GPA (experimental) | yes / no, with `--exp` | no |

**Flags**, for `--non-interactive`:

| Flag | |
|---|---|
| `--module <path>` | Go module path — required |
| `--preset <mvc\|rest_api>` | |
| `--frontend <preset>` | MVC only |
| `--database <sqlite\|mysql\|postgres\|none>` | |
| `--orm <orm\|gorm\|bun\|none>` | The SQL layer, not the backend |
| `--cache <file\|memory\|redis\|none>` | |
| `--queue <sql\|redis\|none>` | |
| `--session <file\|memory\|redis>` | |
| `--disk <local\|s3>` | |
| `--redis` | Use Redis for anything left unset |
| `--auth` | Scaffold registration, login and logout (default true) |
| `--gpa` | Wire the ORM through [GPA](/docs/database/) |
| `--exp` | Offer the experimental GPA question |

**Examples:**

```bash
# A blog on Postgres with Redis behind everything
lemmego new blog --non-interactive \
  --module github.com/me/blog \
  --database postgres --frontend inertia_react --redis

# A JSON API with no database, cache or queue
lemmego new api --non-interactive \
  --module github.com/me/api \
  --preset rest_api \
  --database none --cache none --queue none --auth=false
```

## Leaving a part out

The database, cache and queue each have a **None**. Choosing it removes the
dependency from `go.mod`, the provider from `bootstrap/providers.go`, the
configuration file from `internal/configs/`, and the environment variables
from `.env.example`. A project with all three set to none requires only
`github.com/lemmego/api`.

Sessions and storage have a driver choice but no None. The HTTP server wraps
its router in the session manager, and sessions carry the CSRF token,
validation errors and flash messages — an application without one could not
render its own error pages.

Two combinations are refused rather than scaffolded, because they would build
and then fail:

- a SQL queue with no database
- authentication with no database, since it scaffolds a users table, a
  migration and repositories that resolve the connection

**Post-creation:** Runs `go mod tidy`, generates app key, optionally builds frontend assets.

## Running & Development

### `lemmego run [args]`

Runs the application via `go run ./cmd/app`.

- Checks the project is a valid Lemmego project
- Generates Templ files if `.templ` files exist
- Builds frontend assets if `package.json` exists
- Passes any additional args to the Go binary

### `lemmego dev`

Starts the development server with hot reload. Orchestrates up to three parallel processes:

1. **air** — Go hot reload on `:8080`
2. **templ generate --watch** — Templ file watcher (if `.templ` files exist)
3. **vite dev** — Frontend dev server (if `package.json` exists)

Output is color-coded with `[air]`, `[templ]`, `[vite]` prefixes.

### `lemmego build`

Builds frontend assets:
- Runs `templ generate` if `.templ` files exist
- Runs `npm run build` / `yarn build` / `pnpm build` if `package.json` exists

## Code Generation

All `gen` subcommands support `-i` / `--interactive` for field-by-field configuration via TUI forms.

### `lemmego gen handlers <name>`

Generates CRUD handler stubs in `internal/handlers/`.

Creates 7 handler methods: `Index`, `Create`, `Show`, `Store`, `Edit`, `Update`, `Delete`.

```shell
lemmego g handlers Task
# Creates: internal/handlers/task_handlers.go
```

### `lemmego gen model <name>`

Generates a model struct in `internal/models/`.

```shell
lemmego g model Product
# Creates: internal/models/product.go
```

Supports field types: `int`, `uint`, `int64`, `uint64`, `float64`, `string`, `bool`, `time.Time`.

Supports relation types (via `-i`): one-to-one, one-to-many, many-to-one, many-to-many.

### `lemmego gen migration <name>`

Generates a timestamped migration file in `internal/migrations/`.

```shell
lemmego g migration create_orders_table
# Creates: internal/migrations/20250708120000_create_orders_table.go
```

### `lemmego gen input <name>`

Generates an input validation struct in `internal/inputs/`.

```shell
lemmego g input CreateOrder
# Creates: internal/inputs/create_order_input.go
```

Supports validation rules: Required, Unique (with table/column spec).

### `lemmego gen form <name>`

Generates a form component.

```shell
lemmego g form UserForm
lemmego g form UserForm -f templ    # Templ flavor
```

- React output (`-f react`, default): `resources/js/Pages/Forms/UserForm.tsx`
- Templ output (`-f templ`): `templates/user_form.templ`

Form field types: text, textarea, integer, decimal, boolean, radio, checkbox, dropdown, date, time, datetime, file.

## Maintenance

### `lemmego cache-clean`

Clears the local scaffold cache at `~/.cache/lemmego/scaffold`, forcing the CLI to use the embedded scaffold templates on the next `lemmego new`. Useful when you've updated the CLI binary and want to pick up fresh scaffold templates without waiting for the cache to expire.

```shell
lemmego cache-clean
```

## Inertia SSR

### `lemmego inertia-ssr start`

Starts the Inertia SSR Node.js server.

```shell
lemmego inertia-ssr start --port 13714 --host 127.0.0.1
```

Writes the process ID to `.ssr.pid`.

### `lemmego inertia-ssr stop`

Stops the running SSR server via PID file. Sends SIGTERM, falls back to SIGKILL.

### `lemmego inertia-ssr check`

Checks if the SSR server is running. Exits with code 1 if not.

## ORM-Specific Commands

### `lemmego gorm:model`

Interactive GORM model generation with `gorm:` struct tags.

### `lemmego gorm:repo`

Generates GORM repository files in `internal/repos/`.

### `lemmego bun:model`

Interactive Bun model generation with `bun:` struct tags.

### `lemmego bun:repo`

Generates Bun repository files in `internal/repos/`.
