---
title: Prologue
type: docs
weight: -1
sidebar:
  open: true
---

Welcome to the Lemmego documentation. This guide covers everything you need to build full-stack web applications with Go using the Lemmego framework.

## Getting Started

If you're new here, start with [Installation](/docs/installation/) to set up the CLI, then follow the [Quick Start](/docs/quick-start/) guide to create your first project.

## What is Lemmego?

Lemmego is a modern, full-stack web framework for Go that combines the productivity of Laravel/Rails with the type safety and performance of Go. Built around a plugin-based architecture and a powerful type-safe database abstraction layer (GPA), it enables rapid application development without sacrificing compile-time safety.

Key features:

- **Type-safe database layer** — GPA provides compile-time type safety across SQL, NoSQL, and KV stores with generic `Repository[T]`
- **Plugin architecture** — Extend the framework through providers without modifying core code
- **Multiple frontends** — Go Templates, Templ, or Inertia.js with React/Vue
- **Full-featured HTTP layer** — Chi-based routing, two-level middleware, input validation, typed errors
- **CLI tools** — Project scaffolding, code generators, migration management
- **File storage** — Unified abstraction for local, S3, and GCS

## Documentation Sections

{{< cards >}}
{{< card link="../installation" title="Installation" subtitle="Install the lemmego CLI" icon="terminal" >}}
{{< card link="../quick-start" title="Quick Start" subtitle="Create and run your first project" icon="fire" >}}
{{< card link="../http" title="HTTP Layer" subtitle="Routing, middleware, request/response handling" icon="annotation" >}}
{{< card link="../database" title="Database" subtitle="GPA — the Go Persistence API" icon="database" >}}
{{< card link="../migrations" title="Migrations" subtitle="Schema builder & database versioning" icon="folder-tree" >}}
{{< card link="../frontend" title="Frontend" subtitle="Templ, Inertia, Go templates, Vite" icon="sparkles" >}}
{{< /cards >}}
