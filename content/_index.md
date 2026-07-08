---
title: Lemmego — The full-stack framework for building web applications in Go
toc: false
---

Lemmego is a modern, full-stack web framework for Go that combines the productivity of Laravel/Rails with the type safety and performance of Go. Built around a plugin-based architecture and a powerful type-safe database abstraction layer (GPA), it enables rapid application development without sacrificing compile-time safety.

## Features

- **Type-safe database layer** — GPA provides compile-time type safety across SQL, NoSQL, and KV stores with generic `Repository[T]`
- **Plugin architecture** — Extend the framework through providers without modifying core code
- **Multiple frontends** — Go Templates, Templ, or Inertia.js with React/Vue
- **Full-featured HTTP layer** — Chi-based routing, two-level middleware, input validation, typed errors
- **CLI tools** — Project scaffolding, code generators, migration management
- **File storage** — Unified abstraction for local, S3, and GCS

## Get Started

{{< cards >}}
{{< card link="docs" title="Documentation" icon="book-open" subtitle="Learn the framework from the ground up" >}}
{{< card link="docs/installation" title="Installation" icon="terminal" subtitle="Install the lemmego CLI" >}}
{{< card link="docs/quick-start" title="Quick Start" icon="fire" subtitle="Create your first project in minutes" >}}
{{< /cards >}}

## What's Included

| Module | Description |
|--------|-------------|
| **API** | Core framework: routing, middleware, DI, sessions, config, validation |
| **GPA** | Type-safe database abstraction with multi-provider support |
| **CLI** | Project scaffolding and code generation |
| **Inertia** | Server-side adapter for Inertia.js SPAs |
| **Templ** | Bridge for type-safe Go templates |
| **Auth** | Session + JWT authentication with middleware |
| **Migrations** | Bidirectional database schema management |
| **File System** | Cloud-agnostic storage (local, S3, GCS) |
