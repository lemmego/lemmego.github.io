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

[Inertia.js](https://inertiajs.com/) enables building modern SPAs using server-side routing and client-side rendering with React or Vue. Lemmego includes a first-class Inertia adapter through the `inertia` package that wraps `gonertia` without leaking its types.

## Setup

The Inertia provider is registered in `bootstrap/providers.go`:

```go
import (
    "github.com/lemmego/inertia"
)

func LoadProviders() []app.Provider {
    return []app.Provider{
        &inertia.Provider{
            Options: []inertia.Option{
                inertia.WithSSR(),
            },
        },
    }
}
```

The provider automatically configures default options: version from manifest file, and an in-memory flash provider.

### Options

| Option | Description |
|--------|-------------|
| `WithVersion(v string)` | Set a fixed asset version string |
| `WithVersionFromFile(path)` | Derive version from a file's checksum |
| `WithVersionFromFileFS(fs, path)` | Derive version from an embedded filesystem |
| `WithSSR()` | Enable SSR with auto-detected URL (Vite dev in dev, `127.0.0.1:13714` in prod) |
| `WithSSRAt(url)` | Enable SSR at a specific URL |
| `WithFlashProvider(p)` | Custom flash data provider |
| `WithContainerID(id)` | Root container element ID (default `"app"`) |
| `WithEncryptHistory()` | Enable history encryption |
| `WithJSONMarshaller(m)` | Custom JSON marshaller |
| `WithLogger(l)` | Custom logger |
| `WithSSRHTTPClient(c)` | Custom HTTP client for SSR |
| `WithVite(opts...)` | Full Vite integration with preloading |

## Rendering a Page

```go
import "github.com/lemmego/inertia"

func handler(c app.Context) error {
    return inertia.Respond(c, "Users/Index", map[string]any{
        "users": users,
    })
}
```

The page component name corresponds to a file in `resources/js/Pages/`:

```
resources/js/Pages/Users/Index.tsx
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

For PUT, PATCH, DELETE requests, the redirect uses HTTP 303 (See Other).

## Prop Types

Inertia supports several prop types through the inertia package:

### Optional Props

Only evaluated on partial reloads (when the prop is specifically requested):

```go
inertia.Respond(c, "Dashboard", map[string]any{
    "users":         users,
    "notifications": inertia.Optional(notifications),
})
```

### Always Props

Always included, even on partial reloads where not requested:

```go
map[string]any{
    "csrf_token": inertia.Always(token),
}
```

### Once Props

Sent only on the first visit:

```go
map[string]any{
    "onboarding": inertia.Once(tips),
}
```

### Deferred Props

Loaded asynchronously after the page renders:

```go
map[string]any{
    "users": inertia.Defer(loadUsers),
    "reports": inertia.Defer(loadReports, "analytics"),
}
```

Deferred props support groups for bundling related async loads. Use `.Merge()` to merge instead of overwrite:

```go
inertia.Defer(loadUsers).Merge()
```

### Merge Props

Values are merged with existing client-side data instead of replacing:

```go
map[string]any{
    "filters": inertia.Merge(currentFilters),
}
```

Also supports deep merging and append/prepend operations:

```go
inertia.DeepMerge(value)
inertia.Merge(value).Append("items")
inertia.Merge(value).Prepend("items")
inertia.Merge(value).MatchOn("page")
```

### Scroll Props

For infinite scrolling with pagination metadata:

```go
inertia.Respond(c, "Posts/Index", map[string]any{
    "items": inertia.Scroll(loadedItems,
        inertia.WithWrapper("data"),
        inertia.WithMetadata(inertia.ScrollMetadata{
            PageName:    "page",
            CurrentPage: 1,
            NextPage:    2,
        }),
    ),
})
```

## Validation & Flash Messages

Validation errors from the server are automatically available on the client as `page.props.errors`:

```go
func store(c app.Context) error {
    if err := input.Validate(); err != nil {
        return c.UnprocessableEntity(err)
    }
}
```

Flash and validation errors use `context.Context` helpers:

```go
ctx := c.RequestContext()

// Set validation errors
ctx = inertia.SetValidationError(ctx, "email", "This email is already taken.")
ctx = inertia.SetValidationErrors(ctx, inertia.ValidationErrors{"name": {"required"}})

// Get validation errors
errs := inertia.GetValidationErrors(ctx)

// Set flash messages
ctx = inertia.SetFlash(ctx, inertia.Flash{"success": "Created!"})
ctx = inertia.SetFlashValue(ctx, "message", "Welcome")

// Get flash messages
flash := inertia.GetFlash(ctx)
```

## SSR (Server-Side Rendering)

Enable SSR with auto-detection:

```go
&inertia.Provider{
    Options: []inertia.Option{
        inertia.WithSSR(),
    },
}
```

Or with a custom URL:

```go
inertia.WithSSRAt("http://127.0.0.1:13714")
```

### How SSR Works

1. For full page visits, Inertia renders the React/Vue app on the server
2. The HTML is sent to the client with all JavaScript and CSS
3. Subsequent navigation happens client-side (SPA mode)
4. SSR improves initial page load performance and SEO

### Managing the SSR Server

```shell
lemmego inertia-ssr start --port 13714 --host 127.0.0.1
lemmego inertia-ssr stop
lemmego inertia-ssr check
```

## Context Helpers

Props, template data, and history settings use `context.Context` and return a new context:

```go
ctx := c.RequestContext()

// Props
ctx = inertia.SetProps(ctx, map[string]any{"key": "value"})
ctx = inertia.SetProp(ctx, "key", "value")
props := inertia.GetProps(ctx)

// Template data
ctx = inertia.SetTemplateData(ctx, map[string]any{"appName": "MyApp"})
ctx = inertia.SetTemplateDatum(ctx, "key", "value")
data := inertia.GetTemplateData(ctx)

// History
ctx = inertia.SetEncryptHistory(ctx, true)
ctx = inertia.ClearHistory(ctx)
```

## Vite Integration

Two modes are available:

### Basic (default)

Auto-detected from Vite hot file (development) or manifest file (production). A `@vite` template function is shared automatically.

### Full Integration

Enable with preloading and CSP support:

```go
&inertia.Provider{
    Options: []inertia.Option{
        inertia.WithVite(
            inertia.WithEntryPoints("resources/js/app.tsx"),
            inertia.WithAggressivePreload(),
        ),
    },
}
```

Vite options: `WithEntryPoints`, `WithBuildManifest`, `WithHotFile`, `WithHotReloadPort`, `WithBuildDir`, `WithAggressivePreload`, `WithWaterfallPreload`, `WithIntegrity`, `WithoutPreloading`.

## Testing

```go
import "github.com/lemmego/inertia"

func TestPageResponse(t *testing.T) {
    assertion := inertia.AssertFromReader(t, resp.Body)

    assertion.AssertComponent("Users/Index")
    assertion.AssertVersion("1.0")
    assertion.AssertURL("/users")
    assertion.AssertProps(map[string]any{"users": nil})
    assertion.AssertEncryptHistory(false)
    assertion.AssertClearHistory(false)
}
```

Also supports `AssertFromString(t, body)` and `AssertFromBytes(t, body)` for parsing from different sources. Works with both Inertia JSON responses and HTML responses with `data-page` script tags.
