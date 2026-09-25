---
title: CSRF Protection
type: docs
prev: docs/security/authentication
next: docs/security/encryption
sidebar:
  open: true
weight: 44
---

## Overview

CSRF (Cross-Site Request Forgery) protection is built into Lemmego through the `middleware.VerifyCSRF` middleware. It uses a double-submit cookie pattern with session-based tokens.

## How It Works

1. The first request in a session generates a random token with `crypto/rand` and
   stores it in the session under `_token`. Later requests reuse it — the token
   lives as long as the session does.
2. Every response that passes verification mirrors that token into an
   `XSRF-TOKEN` cookie (skipping `/static`), and exposes it on the request
   context as `_token`.
3. Reads — GET, HEAD and OPTIONS — are not verified.
4. Every other method is verified: the middleware compares the token the request
   carried against the one in the session, using `subtle.ConstantTimeCompare`.
5. A mismatch returns `c.PageExpired()`, which is HTTP 419.

### The token is not rotated per request

A CSRF token is a shared secret for the session, not a one-time nonce, and it is
deliberately left in place after a successful write.

Rotating on every verified request rejects any client still holding the previous
token — one whose request was already in flight, one that missed a `Set-Cookie`,
a second tab, or a page restored from the back/forward cache. Each of those gets
a 419, and stays broken until a full page load. Laravel, Rails and Django all
keep a per-session token for the same reason.

The token does change when the session itself is regenerated.

## CSRF Token Sources

The middleware checks for the token in this order, stopping at the first hit:

1. The `X-XSRF-TOKEN` header
2. A `_token` POST form field
3. A `_token` form value, which also covers the query string
4. A `_token` field in a JSON body

## Configuration

```go
middleware.VerifyCSRF(&middleware.CSRFOpts{
    ExcludePatterns: []string{"/api/.*", "/webhook"},
})
```

Excluded patterns are evaluated as regular expressions. Requests matching any pattern skip CSRF verification entirely.

## In Templates

### Go Templates

The middleware puts the token on the request context, so pass it through when
rendering:

```go
func TaskCreate(c app.Context) error {
    tmpl := res.NewTemplate(c, "tasks.page.gohtml").
        WithData(map[string]any{"_token": c.Get("_token")})
    return c.Render(tmpl)
}
```

```html
<form method="POST" action="/tasks">
    <input type="hidden" name="_token" value="{{ ._token }}">
</form>
```

### Templ

Generated projects ship a `csrf` component in `templates/csrf.templ` that reads
the token off the context:

```go
templ csrf() {
    if val, ok := ctx.Value("_token").(string); ok {
        <input type="hidden" name="_token" value={ val }/>
    }
}
```

Usage:

```go
<form method="POST" action="/tasks">
    @csrf()
</form>
```

### Inertia

CSRF tokens are automatically included in Inertia requests through the `XSRF-TOKEN` cookie.

## API Routes

For JSON API routes, exclude CSRF verification:

```go
middleware.VerifyCSRF(&middleware.CSRFOpts{
    ExcludePatterns: []string{"/api/.*"},
})
```

API clients should use token-based authentication (JWT or API keys) instead.

## Security Notes

- Tokens are generated using `crypto/rand`
- Token comparison uses `subtle.ConstantTimeCompare`, so it leaks nothing through timing
- The cookie carries the *same* value as the session token — that is the
  double-submit pattern. It is deliberately not `HttpOnly`, because the point is
  for JavaScript to read it and send it back in the `X-XSRF-TOKEN` header. The
  protection comes from the same-origin policy: a cross-site attacker can cause
  the cookie to be *sent*, but cannot *read* it to populate the header
- The cookie is `SameSite=Lax`, and `Secure` in production
- Excluded paths skip verification entirely, so exclude only routes that
  authenticate some other way
