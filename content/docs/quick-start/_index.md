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

This command will walk you through interactive prompts:

1. **Module name** — the Go module path (e.g., `github.com/username/my-project`)
2. **Preset** — choose between `mvc` (with frontend) or `rest_api` (backend-only)
3. **ORM** — select `gorm` or `bun` as the database ORM
4. **Redis** — enable or disable Redis support
5. **Auth** — enable or disable authentication scaffolding
6. **GPA** (experimental) — enable the Go Persistence API
7. **Frontend preset** (for `mvc`) — pick Go Templates, Templ, Inertia React, Inertia Vue, or combinations

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
