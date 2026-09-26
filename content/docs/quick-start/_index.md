---
title: Quick Start
type: docs
prev: docs/installation/
next: docs/http/
sidebar:
  open: true
weight: 2
---

## Creating an Application

Now that you have installed the `lemmego` CLI, you can create a new project:

```shell
lemmego new my-project
```

The first question asks how much you want to be asked:

- **Quick start** takes four answers — module name, preset, whether to scaffold
  authentication, and the frontend if this is an MVC project — and uses
  sensible defaults for the rest: SQLite, the [Lemmego ORM](/docs/orm/), a file
  cache, a SQL queue, file sessions and local storage.
- **Customise** pages through a driver for each part: the database, the SQL
  layer, the cache, the queue, sessions and storage.

The database, cache and queue can each be set to **None**, which leaves that
part out of the project entirely — no dependency, no provider, no config file.
See [the CLI reference](/docs/cli/#leaving-a-part-out).

Everything is also available as a flag with `--non-interactive`:

```shell
lemmego new my-project --non-interactive \
  --module github.com/username/my-project \
  --database postgres --cache redis --queue redis
```

Once configured, navigate into your project directory:

```shell
cd my-project
```

## Running the Application

Start the development server:

```shell
lemmego run
```

Or use hot-reload:

```shell
lemmego dev
```

The `dev` command orchestrates three parallel processes:
- **air** — Go hot reload on `:8080`
- **templ generate --watch** — Templ file watcher (if `.templ` files exist)
- **vite dev** — Frontend dev server (if `package.json` exists)

Visit `http://localhost:8080` in your browser — you should see the application's homepage.

## Development Workflow

The generated project includes a `Makefile` with common tasks:

| Command | Description |
|---------|-------------|
| `make run` | Start with hot reload (`air`) |
| `make watch` | Parallel templ + tailwind + air + file watcher |
| `make dev` | Frontend dev server |
| `make build` | Build frontend assets |
| `make migrate` | Run pending migrations |
| `make migration n=name` | Create a new migration |
| `make model n=name` | Generate a model |
| `make handlers n=name` | Generate CRUD handlers |
| `make input n=name` | Generate input validation |
| `make form n=name` | Generate a form component |

## Frontend Options

Lemmego supports multiple frontend approaches:

- **Go Templates** (`*.page.gohtml`) — server-rendered HTML with layouts and partials
- **Templ** (`*.templ`) — type-safe Go templates with compile-time checking
- **Inertia.js** with React or Vue — SPA-like experience with server-side routing

The `make watch` command handles Go Templates and Templ reloading. For Inertia, run `npm run dev` separately.

## Project Structure

After scaffolding, your project will have this structure:

```
├── bootstrap/          # Application bootstrap layer
│   ├── providers.go    # Service provider registration
│   ├── routes.go       # Route registration
│   ├── middleware.go   # App-level middleware
│   └── commands.go     # CLI commands
├── cmd/app/main.go     # Application entry point
├── internal/           
│   ├── commands/       # CLI command implementations
│   ├── configs/        # Configuration (auto-loaded)
│   ├── handlers/       # HTTP request handlers
│   ├── inputs/         # Input validation structs
│   ├── middleware/      # App-specific middleware
│   ├── migrations/     # Database migrations
│   ├── models/         # Domain models
│   ├── plugins/        # Extension point
│   ├── repos/          # Repository layer
│   └── routes/         # Route definitions
├── resources/          # Frontend source (JS, CSS, templates)
├── templates/          # Go/Templ templates
├── public/             # Compiled static assets
└── storage/            # Runtime data (database, sessions, uploads)
```
