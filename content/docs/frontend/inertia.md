---
title: Inertia.js
type: docs
prev: docs/frontend/templ
next: docs/frontend/vite
sidebar:
  open: true
weight: 38
---

## Overview

[Inertia.js](https://inertiajs.com/) enables building modern SPAs using server-side routing and client-side rendering with React or Vue. Lemmego includes a first-class Inertia adapter through the `inertia` package.

## Setup

The Inertia provider is registered in `bootstrap/providers.go`:

```go
func LoadProviders() []app.Provider {
    return []app.Provider{
        &inertia.Provider{},
    }
}
```

### Configuration

```go
&inertia.Provider{
    Config: &inertia.Config{
        Version: "1.0",
        SSR: inertia.SSRConfig{
            Enabled: true,
            Port:    13714,
        },
    },
}
```

Or using functional options:

```go
inertia.New(
    inertia.WithVersion("1.0"),
    inertia.WithSSRAt("http://127.0.0.1:13714"),
)
```

## Rendering a Page

```go
import "github.com/lemmego/inertia"

func handler(c app.Context) error {
    return inertia.Respond(c, "Users/Index", inertia.Props{
        "users": users,
    })
}
```

The page component name corresponds to a file in `resources/js/Pages/`:

```
resources/js/Pages/Users/Index.tsx
```

### With Shared Data

```go
inertia.Respond(c, "Users/Index", inertia.Props{
    "users": users,
    "filters": filters,
})
```

## Redirects

```go
// Server-side redirect
inertia.Redirect(c, "/dashboard")

// Redirect back
inertia.Back(c)

// External redirect (409 + X-Inertia-Location)
inertia.Location(c, "https://example.com")
```

## Prop Types

Inertia supports several prop types beyond simple key-value pairs:

### Optional Props

Only evaluated on partial reloads (when the prop is specifically requested):

```go
inertia.Respond(c, "Dashboard", inertia.Props{
    "users":          users,
    "notifications":  inertia.Optional(notifications),
})
```

### Always Props

Always included, even on partial reloads where not requested:

```go
inertia.Props{
    "csrf_token": inertia.Always(token),
}
```

### Deferred Props

Loaded asynchronously after the page renders:

```go
inertia.Props{
    "users": inertia.Defer(loadUsers, "default"),
}
```

Deferred props support groups for bundling related async loads:

```go
inertia.Props{
    "users":  inertia.Defer(loadUsers, "analytics"),
    "reports": inertia.Defer(loadReports, "analytics"),
}
```

### Merge Props

Values are merged with existing client-side data instead of replacing:

```go
inertia.Props{
    "filters": inertia.Merge(currentFilters),
}
```

### Scroll Props

For infinite scrolling with pagination metadata:

```go
inertia.Props{
    "items": inertia.Scroll(loadedItems, scrollConfig),
}
```

## Validation & Flash Messages

Validation errors from the server are automatically available on the client as `page.props.errors`:

```go
func store(c app.Context) error {
    input, _ := c.Input(&CreateUserInput{}).(*CreateUserInput)
    if err := input.Validate(); err != nil {
        return c.UnprocessableEntity(err)
    }
    // ...
}
```

Flash messages can be set manually:

```go
inertia.SetFlash(c, "success", "User created successfully!")
```

Or via the context:

```go
c.SetValidationError("email", "This email is already taken.")
```

## SSR (Server-Side Rendering)

Enable SSR in your provider configuration:

```go
inertia.New(
    inertia.WithSSRAt("http://127.0.0.1:13714"),
)
```

### Managing the SSR Server

Start the SSR server:

```shell
lemmego inertia-ssr start
```

Stop it:

```shell
lemmego inertia-ssr stop
```

Check status:

```shell
lemmego inertia-ssr check
```

The SSR server is configured with:

```shell
lemmego inertia-ssr start --port 13714 --host 127.0.0.1
```

### How SSR Works

1. For full page visits, Inertia renders the React/Vue app on the server
2. The HTML is sent to the client with all JavaScript and CSS
3. Subsequent navigation happens client-side (SPA mode)
4. SSR improves initial page load performance and SEO

## Context Helpers

The inertia package provides helpers accessible through the app context:

```go
// Set props
inertia.SetProps(c, inertia.Props{"key": "value"})
inertia.SetProp(c, "key", "value")

// Get props
props := inertia.GetProps(c)

// Validation errors
inertia.SetValidationErrors(c, errs)
inertia.GetValidationErrors(c)

// Flash messages
inertia.SetFlash(c, "type", "message")
inertia.GetFlash(c)

// Template data
inertia.SetTemplateData(c, data)
inertia.SetTemplateDatum(c, "key", value)
```

## Testing

The inertia package includes testing utilities:

```go
import "github.com/lemmego/inertia"

func TestPageResponse(t *testing.T) {
    // Create an assertable from a response
    assertion := inertia.AssertFromReader(resp.Body)
    
    assertion.AssertComponent("Users/Index")
    assertion.AssertVersion("1.0")
    assertion.AssertProps("users")
    assertion.AssertURL("/users")
}
```
