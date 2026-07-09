---
title: Command Reference
type: docs
prev: docs/cli/
sidebar:
  open: true
weight: 41
---

## Project Scaffolding

### `lemmego new <dirname>`

Creates a new Lemmego project with interactive configuration.

**Arguments:**
- `<dirname>` — Directory name for the new project

**Interactive Prompts:**
- Module name (Go module path)
- Preset: `mvc` or `rest_api`
- ORM: `gorm` or `bun`
- Redis: yes/no
- Auth: yes/no
- GPA (experimental): yes/no (with `--exp` flag)
- Frontend preset (for `mvc`): Go Templates, Templ, Inertia React, Inertia Vue

**Flags:**
- `--exp` — Enable experimental GPA features

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
