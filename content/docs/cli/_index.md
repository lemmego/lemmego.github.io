---
title: CLI Reference
type: docs
prev: docs/frontend/vite
next: docs/cli/commands
sidebar:
  open: true
weight: 40
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

## Command Structure

```
lemmego
├── new <dirname>          Create a new project
├── run [args]             Run the application
├── dev                    Start development server (hot reload)
├── build                  Build frontend assets
├── gen (g)                Code generation (parent command)
│   ├── handlers (h)       Generate CRUD handlers
│   ├── model              Generate a model struct
│   ├── migration          Generate a migration file
│   ├── input              Generate an input validation struct
│   └── form               Generate a form component
├── inertia-ssr            Inertia SSR management (parent)
│   ├── start              Start SSR server
│   ├── stop               Stop SSR server
│   └── check              Check SSR server status
├── gorm:model (gorm:m)    Generate GORM model
├── gorm:repo (gorm:r)     Generate GORM repository
├── bun:model (bun:m)      Generate Bun model
└── bun:repo (bun:r)       Generate Bun repository
```
