---
title: Go Templates
type: docs
prev: docs/frontend/
next: docs/frontend/templ
sidebar:
  open: true
weight: 36
---

## Overview

Lemmego's template rendering system uses Go's `html/template` package with a caching layer and convention-based discovery of layouts and partials.

## Template Conventions

Templates follow a naming convention that determines their role:

| Suffix | Purpose | Example |
|--------|---------|---------|
| `*.page.gohtml` | Page template (full page) | `index.page.gohtml` |
| `*.layout.gohtml` | Layout template (wraps page) | `base.layout.gohtml` |
| `*.partial.gohtml` | Partial/snippet | `header.partial.gohtml` |

The template engine automatically discovers layouts and partials by walking up the directory tree from the page's location.

## Rendering a Template

```go
import "github.com/lemmego/api/res"

func handler(c app.Context) error {
    tmpl := res.NewTemplate(c, "index.page.gohtml")
    tmpl = tmpl.WithData(map[string]any{
        "title": "Welcome",
        "users": users,
    })
    return c.Render(tmpl)
}
```

## Template with Data

```go
tmpl := res.NewTemplate(c, "index.page.gohtml")
tmpl = tmpl.
    WithData(map[string]any{
        "title": "Users",
        "items": items,
    }).
    WithIntMap(map[string]int{
        "count": total,
    }).
    WithBoolMap(map[string]bool{
        "isAdmin": isAdmin,
    }).
    WithValidationErrors(errs)
```

## Custom Functions

```go
tmpl := res.NewTemplate(c, "index.page.gohtml")
tmpl = tmpl.WithFuncMap(template.FuncMap{
    "formatDate": func(t time.Time) string {
        return t.Format("January 2, 2006")
    },
})
```

## Layout Templates

Layout templates wrap page content. The engine discovers `*.layout.gohtml` files in parent directories:

```html
<!-- templates/base.layout.gohtml -->
<!DOCTYPE html>
<html>
<head>
    <title>{{block "title" .}}My App{{end}}</title>
</head>
<body>
    <nav>{{block "nav" .}}{{end}}</nav>
    <main>{{block "content" .}}{{end}}</main>
</body>
</html>
```

```html
<!-- templates/index.page.gohtml -->
{{define "title"}}Home{{end}}
{{define "content"}}
    <h1>Welcome {{.title}}</h1>
{{end}}
```

## Partial Templates

Partials are reusable snippets, discovered automatically from parent directories:

```html
<!-- templates/header.partial.gohtml -->
<header>
    <h1>{{.appName}}</h1>
</header>
```

## Template Cache

Templates are parsed and cached at application startup in `init()`:

```go
func init() {
    createTemplateCache()
}
```

The cache walks the `templates/` directory, parses all `*.page.gohtml` files, and discovers their layouts and partials. This means template parsing errors are caught at startup, not at request time.

## Error Pages

The generated project includes error pages for common HTTP status codes:

- `401.page.gohtml` — Unauthorized
- `403.page.gohtml` — Forbidden
- `404.page.gohtml` — Not Found
- `419.page.gohtml` — Page Expired (CSRF)
- `500.page.gohtml` — Internal Server Error
