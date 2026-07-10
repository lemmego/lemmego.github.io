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
func MyHandler(c app.Context) error {
    return c.JSON(app.M{
        "id":    1,
        "name":  "John",
        "email": "john@example.com",
    })
}
```

### HTML

```go
func MyHandler(c app.Context) error {
    return c.HTML([]byte("<h1>Hello</h1>"))
}
```

### Text

```go
func MyHandler(c app.Context) error {
    return c.Text([]byte("Hello, World!"))
}
```

### XML

Return XML responses from structs, maps, or raw strings:

```go
// From a map
func MyHandler(c app.Context) error {
    return c.XML(app.M{
        "status": "ok",
        "count":  42,
    })
}
// Produces: <response><status>ok</status><count>42</count></response>
```

```go
// From a struct
type Item struct {
    XMLName xml.Name `xml:"item"`
    ID      int      `xml:"id"`
    Name    string   `xml:"name"`
}

func MyHandler(c app.Context) error {
    return c.XML(Item{ID: 1, Name: "test"})
}
// Produces: <item><id>1</id><name>test</name></item>
```

```go
// From a raw string or bytes
func MyHandler(c app.Context) error {
    return c.XML("<status>ok</status>")
}
```

Combine with content negotiation:

```go
if c.WantsXML() {
    return c.XML(data)
}
return c.JSON(data)
```

### Redirect

```go
func MyHandler(c app.Context) error {
    return c.Redirect("/dashboard")
}

func MyHandler(c app.Context) error {
    return c.Back() // redirect to referrer
}
```

### File Responses

```go
// Serve a file from the filesystem
func MyHandler(c app.Context) error {
    return c.File("path/to/file.pdf")
}

// Serve a file from a storage disk
func MyHandler(c app.Context) error {
    return c.StorageFile("uploads/report.pdf")
}

// Download a file with a custom filename
func MyHandler(c app.Context) error {
    return c.Download("path/to/file.pdf", "report.pdf")
}
```

## Template Rendering

### Go Templates

Render Go HTML templates using the `res` package:

```go
import "github.com/lemmego/api/res"

func MyHandler(c app.Context) error {
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

func MyHandler(c app.Context) error {
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

func MyHandler(c app.Context) error {
    return inertia.Respond(c, "Users/Index", inertia.Props{
        "users": users,
    })
}
```

## Status Codes

Set custom HTTP status codes:

```go
func MyHandler(c app.Context) error {
    c.SetStatus(http.StatusCreated)
    return c.JSON(app.M{"id": 1})
}
```

## Setting Headers

```go
func MyHandler(c app.Context) error {
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
