---
title: HTTP Lifecycle
type: docs
prev: docs/cli/
next: docs/http/routing
sidebar:
  open: true
weight: 5
---

## Request Lifecycle

Every HTTP request to a Lemmego application goes through a well-defined pipeline:

1. **Entry** — The Go HTTP server receives the request
2. **HTTP Middleware** — Global middleware runs first (recovery, logging, method override)
3. **Router** — Zero-dependency router matches the request to a route
4. **App Middleware** — Application-level middleware runs (CSRF, auth, etc.)
5. **Handler** — The route handler processes the request and returns a response
6. **Response** — The response is sent back to the client

## Two Middleware Layers

Lemmego has two distinct middleware systems:

- **HTTP Middleware** (`func(http.Handler) http.Handler`) — standard `net/http` middleware that wraps the entire router. Used for cross-cutting concerns like panic recovery and request logging.
- **App Middleware** (`func(next Handler) Handler`) — application-level middleware that operates on the Lemmego `Context`. Used for CSRF verification, authentication, and route-scoped logic.

## Next Steps

{{< cards >}}
{{< card link="routing" title="Routing" subtitle="Define routes, groups, and parameters" >}}
{{< card link="middleware" title="Middleware" subtitle="Preprocessing and postprocessing requests" >}}
{{< card link="request-handling" title="Request Handling" subtitle="Input parsing, validation, and binding" >}}
{{< card link="response-handling" title="Response Handling" subtitle="JSON, HTML, redirects, and file responses" >}}
{{< card link="error-handling" title="Error Handling" subtitle="Typed errors and custom error pages" >}}
{{< card link="context" title="Context" subtitle="The request context API" >}}
{{< /cards >}}
