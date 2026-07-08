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

Parses request bodies from JSON, form data, or query parameters based on the `Content-Type` header:

```go
func handler(c app.Context) error {
    var input CreateUserInput
    err := c.ParseInput(&input)
    if err != nil {
        return c.BadRequest(err)
    }
    return c.JSON(app.M{"input": input})
}
```

`ParseInput` automatically:
- Decodes JSON bodies (for `application/json` requests)
- Decodes form/query parameters (for form submissions)

### Input Structs and Validation

Define input structs with a `Validate()` method:

```go
type CreateUserInput struct {
    Name  string `json:"name"`
    Email string `json:"email"`
}

func (i *CreateUserInput) Validate() error {
    v := app.NewValidator()
    v.Field("name", i.Name).Required().Max(255)
    v.Field("email", i.Email).Required().Email()
    return v.Validate()
}
```

Use with the handler:

```go
func store(c app.Context) error {
    input, err := c.Input(&CreateUserInput{}).(*CreateUserInput)
    // input is automatically decoded and stored in context
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
func handler(c app.Context) error {
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
func upload(c app.Context) error {
    file, err := c.Upload("avatar", "avatars")
    if err != nil {
        return c.BadRequest(err)
    }
    return c.JSON(app.M{"path": file.Name()})
}
```

Parameters: the form field name, target directory, and an optional custom filename.
