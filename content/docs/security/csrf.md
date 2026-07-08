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

1. For every GET request, a random token is generated and stored in the session
2. The token is also set as an `XSRF-TOKEN` cookie
3. For state-changing requests (POST, PUT, PATCH, DELETE), the middleware compares the token from the request with the one in the session
4. Comparison uses constant-time comparison to prevent timing attacks
5. On successful validation, the token is rotated (new token generated)

## CSRF Token Sources

The middleware checks for the token in this order:
1. `X-XSRF-TOKEN` header
2. `_token` POST form value
3. `_token` query parameter
4. JSON body `_token` field

## Configuration

```go
middleware.VerifyCSRF(&middleware.CSRFOpts{
    ExcludePatterns: []string{"/api/.*", "/webhook"},
})
```

Excluded patterns are evaluated as regular expressions. Requests matching any pattern skip CSRF verification entirely.

## In Templates

### Go Templates

The `_token` is available in templates via session data:

```html
<form method="POST" action="/tasks">
    <input type="hidden" name="_token" value="{{ .csrf_token }}">
</form>
```

### Templ

A helper component is provided:

```go
templ CsrfField() {
    <input type="hidden" name="_token" value={ templ.Raw(csrf.Token) }/>
}
```

Usage:

```go
<form method="POST" action="/tasks">
    @CsrfField()
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

- Tokens are generated using `crypto/rand` for cryptographic security
- Token comparison uses `subtle.ConstantTimeCompare` to prevent timing side-channels
- Tokens are rotated after each successful validation (prevents token reuse)
- The session token is separate from the cookie token for defense in depth
