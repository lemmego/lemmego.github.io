---
title: Request Handling
type: docs
prev: docs/http/middleware
sidebar:
  open: true
weight: 8
---

## Input Parsing

The `req` package provides functions for parsing request data into Go structs.

### ParseInput

Parses the request body into a struct. The `Content-Type` header picks the decoder, and the decoder picks which struct tag it reads:

| Content-Type | Decoder | Tag |
|---|---|---|
| `application/json`, `*+json` | `encoding/json` | `json:` |
| `application/xml`, `text/xml`, `*+xml` | `encoding/xml` | `xml:` |
| anything else | the framework's form binder | `form:` |

"Anything else" covers URL-encoded forms, multipart forms, and a query string on a request with no body. Both bodies are bounded at 1 MiB.

```go
func MyHandler(c app.Context) error {
    var input CreateUserInput
    err := c.ParseInput(&input)
    if err != nil {
        return c.BadRequest(err)
    }
    return c.JSON(app.M{"input": input})
}
```

A field needs the tag for the content type it will actually arrive as. **A struct tagged only `json:` binds nothing from an HTML form** — the form binder reads `form:`, finds no name for the field and leaves it at its zero, so validation reports "required" for a field the person just filled in. Tag both when an endpoint serves both:

```go
Name  string `json:"name" form:"name"`
Email string `json:"email" form:"email"`
```

The form binder also handles what a browser really sends: an unchecked box is absent rather than `false`, a checked one is `on`; a repeated field binds to a slice as `tags`, `tags[]` or `tags[0]` alike; a pointer field distinguishes absent from present-and-empty; and a `*multipart.FileHeader` or `[]*multipart.FileHeader` field binds the uploaded files themselves.

### Input Structs and Validation

Define input structs with a `Validate()` method:

```go
type CreateUserInput struct {
    Name  string `json:"name" form:"name"`
    Email string `json:"email" form:"email"`
}

func (i *CreateUserInput) Validate() error {
    v := app.NewValidator()
    v.Field("name", i.Name).Required().Max(255)
    v.Field("email", i.Email).Required().Email()
    return v.Validate()
}

func NewCreateUserInput(c app.Context) (*CreateUserInput, error) {
    input := &CreateUserInput{}
    if err := c.ParseInput(input); err != nil {
        return nil, err
    }
    return input, input.Validate()
}
```

Use with the handler:

```go
func Store(c app.Context) error {
    input, err := NewCreateUserInput(c)
    if err != nil {
        return c.UnprocessableEntity(err)
    }
    // input is validated and ready to use
}
```

### Input Middleware

The router supports an `Input` middleware that decodes and validates before the handler runs:

```go
r.Post("/users", router.Input(&CreateUserInput{}), handlers.UserStore)
```

The decoded input is available in the handler via `c.Input()`:

```go
func UserStore(c app.Context) error {
    input := c.Input().(*CreateUserInput)
    // input is already validated
}
```

## JSON Body Decoding

For direct JSON decoding without struct binding:

```go
func MyHandler(c app.Context) error {
    var data map[string]any
    err := c.DecodeJSON(&data)
    if err != nil {
        return c.BadRequest(err)
    }
    return c.JSON(data)
}
```

The low-level `DecodeJSONBody` function enforces:
- 1MB maximum body size
- Rejection of unknown fields
- Single JSON object enforcement
- Detailed error messages

## Content-Type Detection

Check what format a client expects:

```go
if c.WantsJSON() {
    // Return JSON response
}
if c.WantsHTML() {
    // Return HTML response
}
if c.WantsXML() {
    // Return XML response
}
```

Check what format the client sent:

```go
if c.HasJSONRequest() { /* JSON body */ }
if c.HasFormDataRequest() { /* multipart form */ }
if c.HasFormURLEncodedRequest() { /* URL-encoded form */ }
```

## File Uploads

Handle file uploads with `c.Upload()`:

```go
func Upload(c app.Context) error {
    file, err := c.Upload("avatar", "avatars")
    if err != nil {
        return c.BadRequest(err)
    }
    return c.JSON(app.M{"path": file.Name()})
}
```

Parameters: the form field name, target directory, and an optional custom filename.
