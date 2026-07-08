---
title: Response Handling
type: docs
prev: docs/http/request-handling
sidebar:
  open: true
weight: 9
---

## Response Types

Lemmego's `Context` provides several response methods.

### JSON

```go
func handler(c app.Context) error {
    return c.JSON(app.M{
        "id":    1,
        "name":  "John",
        "email": "john@example.com",
    })
}
```

### HTML

```go
func handler(c app.Context) error {
    return c.HTML([]byte("<h1>Hello</h1>"))
}
```

### Text

```go
func handler(c app.Context) error {
    return c.Text([]byte("Hello, World!"))
}
```

### Redirect

```go
func handler(c app.Context) error {
    return c.Redirect("/dashboard")
}

func handler(c app.Context) error {
    return c.Back() // redirect to referrer
}
```

### File Responses

```go
// Serve a file from the filesystem
func handler(c app.Context) error {
    return c.File("path/to/file.pdf")
}

// Serve a file from a storage disk
func handler(c app.Context) error {
    return c.StorageFile("uploads/report.pdf")
}

// Download a file with a custom filename
func handler(c app.Context) error {
    return c.Download("path/to/file.pdf", "report.pdf")
}
```

## Template Rendering

### Go Templates

Render Go HTML templates using the `res` package:

```go
import "github.com/lemmego/api/res"

func handler(c app.Context) error {
    tmpl := res.NewTemplate(c, "index.page.gohtml")
    tmpl = tmpl.WithData(map[string]any{
        "title": "Hello World",
    })
    return c.Render(tmpl)
}
```

Templates follow naming conventions:
- `*.page.gohtml` — page templates
- `*.layout.gohtml` — layout templates
- `*.partial.gohtml` — partial/reusable templates

The template engine automatically discovers layouts and partials in parent directories.

### Templ

Render Templ components using the `templ` package:

```go
import "github.com/lemmego/templ"

func handler(c app.Context) error {
    return c.Templ(components.Hello("World"))
}
```

Alternatively:

```go
return templ.Respond(c, components.Hello("World"))
```

### Inertia

For Inertia.js responses:

```go
import "github.com/lemmego/inertia"

func handler(c app.Context) error {
    return inertia.Respond(c, "Users/Index", inertia.Props{
        "users": users,
    })
}
```

## Status Codes

Set custom HTTP status codes:

```go
func handler(c app.Context) error {
    c.SetStatus(http.StatusCreated)
    return c.JSON(app.M{"id": 1})
}
```

## Setting Headers

```go
func handler(c app.Context) error {
    c.SetHeader("X-Custom", "value")
    c.SetHeader("Cache-Control", "no-cache")
    return c.JSON(app.M{"ok": true})
}
```

## Response Status Helpers

```go
c.NoContent()           // 204
c.Error(status, err)    // Custom error with status
```
