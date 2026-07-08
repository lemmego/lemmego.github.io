---
title: Templ
type: docs
prev: docs/frontend/go-templates
next: docs/frontend/inertia
sidebar:
  open: true
weight: 37
---

## Overview

[Templ](https://templ.guide/) provides type-safe HTML templates that are compiled to Go code. Lemmego includes a `templ` package that bridges Templ components with the framework's rendering pipeline.

## Setup

The generated project includes Templ support out of the box. If you selected Templ as your frontend during `lemmego new`, the necessary files and configuration are already in place.

## Rendering a Templ Component

```go
import "github.com/lemmego/templ"

func handler(c app.Context) error {
    return c.Templ(components.Hello("World"))
}
```

Or using the package-level helper:

```go
return templ.Respond(c, components.Hello("World"))
```

## TemplResponse

The `TemplResponse` type implements the `Renderer` interface, enabling it to be used with `c.Render()`:

```go
response := templ.New(c, components.Page(data))
return c.Render(response)
```

## How It Works

1. `templ.New(ctx, component)` creates a `TemplResponse` wrapping a `templ.Component`
2. On render, it sets `Content-Type: text/html`, writes the HTTP status code, then calls `component.Render(ctx.RequestContext(), w)`

## Template Sources

Templ source files are located in `templates/`:

```
templates/
├── base-layout.templ     # Base layout component
├── index.templ           # Index page component
├── method.templ          # Method override helper
└── csrf.templ            # CSRF token helper
```

The generated `_templ.go` files (compiled from `.templ`) should not be edited directly.

## Development Workflow

During development, run Templ in watch mode:

```shell
lemmego dev
```

This starts `templ generate --watch` alongside air, so changes to `.templ` files are automatically recompiled and the server reloads.

## Example Component

```go
// templates/hello.templ
package components

templ Hello(name string) {
    <div class="greeting">
        <h1>Hello, { name }!</h1>
    </div>
}
```

Usage in a handler:

```go
func HelloHandler(c app.Context) error {
    return c.Templ(components.Hello(c.Query("name")))
}
```

## CSRF and Method Helpers

The generated project includes Templ helpers for CSRF tokens and method override:

```go
templ CsrfField() {
    <input type="hidden" name="_token" value={ templ.Raw(csrf.Token) }/>
}

templ MethodField(method string) {
    <input type="hidden" name="_method" value={ method }/>
}
```

Usage in forms:

```go
templ EditForm(task models.Task) {
    <form method="POST" action={ templ.URL("/tasks/" + strconv.Itoa(task.ID)) }>
        @MethodField("PUT")
        @CsrfField()
        <input type="text" name="title" value={ task.Title }/>
        <button type="submit">Update</button>
    </form>
}
```
