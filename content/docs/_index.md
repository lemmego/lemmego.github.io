---
title: Documentation
type: docs
next: docs/installation/
---

Lemmego is a full-stack web framework for Go that emphasizes rapid application development, type safety, and productivity. It follows a modular, plugin-based architecture with a powerful type-safe database abstraction layer (GPA) at its core.

## Prerequisites

Before diving in, you should have basic familiarity with Go. You'll also need:

- [Go 1.24+](https://go.dev/dl/)
- [Node.js](https://nodejs.org/en/download/package-manager) (for frontend tooling)
- [Air](https://github.com/air-verse/air) (for hot reloading)
- [Templ](https://templ.guide/quick-start/installation) (optional, for type-safe Go templates)

## Getting Started

{{< cards >}}
{{< card link="installation" title="Installation" subtitle="Install the lemmego CLI" icon="terminal" >}}
{{< card link="quick-start" title="Quick Start" subtitle="Create and run your first project" icon="fire" >}}
{{< card link="../configuration" title="Configuration" subtitle="Environment & app configuration" icon="adjustments" >}}
{{< card link="../project-structure" title="Project Structure" subtitle="Anatomy of a Lemmego project" icon="folder" >}}
{{< /cards >}}

## Core Concepts

{{< cards >}}
{{< card link="../core-concepts/application-bootstrap" title="Application Bootstrap" subtitle="The app lifecycle and bootstrapping pipeline" >}}
{{< card link="../core-concepts/service-container" title="Service Container" subtitle="Service registration and resolution" >}}
{{< card link="../core-concepts/provider-plugin-system" title="Provider & Plugin System" subtitle="Extending the framework through providers" >}}
{{< card link="../core-concepts/dependency-injection" title="Dependency Injection" subtitle="Type-safe DI with three lifetimes" >}}
{{< card link="../core-concepts/event-system" title="Event System" subtitle="Lifecycle events and pub/sub" >}}
{{< /cards >}}

## HTTP Layer

{{< cards >}}
{{< card link="../http" title="HTTP Lifecycle" subtitle="How requests flow through the application" >}}
{{< card link="../http/routing" title="Routing" subtitle="Define routes, groups, and parameters" >}}
{{< card link="../http/middleware" title="Middleware" subtitle="Request preprocessing and postprocessing" >}}
{{< card link="../http/request-handling" title="Request Handling" subtitle="Input parsing, validation, and binding" >}}
{{< card link="../http/response-handling" title="Response Handling" subtitle="JSON, HTML, redirects, and file responses" >}}
{{< card link="../http/error-handling" title="Error Handling" subtitle="Typed errors and error maps" >}}
{{< card link="../http/context" title="Context" subtitle="The request context API" >}}
{{< /cards >}}

## Database (GPA)

{{< cards >}}
{{< card link="../database" title="GPA Overview" subtitle="The Go Persistence API architecture" >}}
{{< /cards >}}

## More Sections

{{< cards >}}
{{< card link="../migrations" title="Migrations" subtitle="Schema builder & database migrations" >}}
{{< card link="../cli" title="CLI Reference" subtitle="Commands for code generation & development" >}}
{{< card link="../security" title="Security" subtitle="Auth, CSRF, encryption, validation" >}}
{{< card link="../frontend" title="Frontend" subtitle="Templ, Inertia, Go templates, Vite" >}}
{{< card link="../filesystem" title="File System" subtitle="Local, S3, GCS storage abstraction" >}}
{{< /cards >}}
