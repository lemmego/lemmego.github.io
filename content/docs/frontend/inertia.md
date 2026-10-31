---
title: Inertia.js
type: docs
prev: docs/frontend/templ
next: docs/frontend/vite
weight: 33
sidebar:
  open: true
---

If you want React or Vue in your pages, the usual price is building two
applications: a Go API that returns JSON, and a JavaScript app with its own
router, its own data fetching and its own idea of what URL you are on. You
then keep those two in agreement forever.

[Inertia](https://inertiajs.com/) removes that second application. You keep
routing and data loading in Go exactly as you have been, and your handler
finishes by naming a component and handing it some data:

```go
return inertia.Respond(c, "Posts/Show", app.M{"post": post})
```

Inertia renders `Posts/Show.tsx` with that data as its **props**. There is no
API to design, no client-side router to keep in sync, and no duplicated URL
list — your routes are still the ones in `internal/routes/`.

What you get in return is that clicking a link does not reload the page.
Inertia fetches the next page's props over the network and swaps the
component, so the browser never goes blank.

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
| `WithSSRAt(url)` | Enable SSR and send renders to this URL |
| `WithSSRURL(url)` | Send renders to this URL without turning SSR on |
| `WithSSRTimeout(d)` | How long one render may take before it gives up |
| `WithFlashProvider(p)` | Custom flash data provider |
| `WithContainerID(id)` | Root container element ID (default `"app"`) |
| `WithEncryptHistory()` | Enable history encryption |
| `WithJSONMarshaller(m)` | Custom JSON marshaller |
| `WithLogger(l)` | Custom logger |
| `WithSSRHTTPClient(c)` | Custom HTTP client for SSR. Its transport is wrapped, so renders still resolve the renderer per request |
| `WithVite(opts...)` | Full Vite integration with preloading |

## Rendering a Page

```go
import "github.com/lemmego/inertia"

func MyHandler(c app.Context) error {
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
func Store(c app.Context) error {
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

Normally your React or Vue page is built in the browser, so the first thing a
visitor receives is an empty `<div>` and a bundle to run. Server-side
rendering runs that page in Node first and sends the finished HTML, which is
what a search engine reads and what a visitor sees before the bundle has
loaded.

Turn it on with one option:

```go
&inertia.Provider{
    Options: []inertia.Option{
        inertia.WithSSR(),
    },
}
```

### Which renderer answers

Two different things can render your pages, and knowing which one you are
using explains most of what you will see.

| | Where it runs | Needs a build | First render |
|---|---|---|---|
| **The Vite dev server** | `/__inertia_ssr` on your Vite port | no | slow — it compiles on demand |
| **The standalone renderer** | `node bootstrap/ssr/ssr.js` on `:13714` | `pnpm build:ssr` | fast |

`WithSSR()` picks one for you: the Vite dev server when `./public/hot` exists,
and the standalone renderer otherwise. That is the right default in
production, where there is no hot file.

In development you want the standalone renderer, and `lemmego dev` sets that
up for you — it starts the renderer whenever `bootstrap/ssr/ssr.js` exists and
points your application at it. Build the bundle once and you are done:

```shell
pnpm build:ssr
lemmego dev
```

The trade-off to know: that bundle is only as current as your last
`pnpm build:ssr`. Change a component and the browser picks it up over HMR,
but the server-rendered HTML keeps the old version until you rebuild.

### Choosing a renderer yourself

Point renders anywhere with an environment variable, which beats both the
hot file and whatever `LoadProviders` configured:

```shell
INERTIA_SSR_URL=http://127.0.0.1:13714
```

Naming a renderer does not turn rendering on. `INERTIA_SSR` still decides
that, so you can keep an address configured and switch rendering off for an
afternoon:

```shell
INERTIA_SSR=false
```

In Go the same two ideas are `WithSSRURL(url)` and `WithSSR()` /
`WithoutSSR()`; `WithSSRAt(url)` does both at once.

### When a render fails

Outside production a failed render is a **500 with the reason**, so you find
out immediately. In production the page falls back to client rendering, so a
visitor still gets a page.

That strictness is why a browser global read during render — `window`,
`document`, `localStorage` — shows up as an error rather than as a mysteriously
empty page. Move that code into an effect.

If you render through the Vite dev server, its first render after startup can
take tens of seconds while it compiles your pages, and it answers "not ready"
until then. Your application waits that out rather than reporting a failure,
so the first page is slow and then fine. A render against the standalone
renderer is bounded at three seconds, because it serves a bundle that was
finished before it started.

### Managing the standalone renderer yourself

`lemmego dev` handles this for you. Reach for these when you are running the
renderer outside it — in a container, or beside a production deployment:

```shell
lemmego inertia-ssr start --port 13714 --host 127.0.0.1
lemmego inertia-ssr stop
lemmego inertia-ssr check
```

`check` has two depths. By default it establishes that the renderer is alive;
give the provider a props-free component and it checks that real
server-rendered markup comes back:

```go
inertia.WithSSRProbeComponent("Health/Probe")
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
