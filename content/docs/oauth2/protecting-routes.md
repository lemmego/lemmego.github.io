---
title: Protecting routes
type: docs
prev: docs/oauth2/grants
next: docs/oauth2/consent-screen
sidebar:
  open: true
weight: 5
---

## Requiring a token

```go
provider := &oauth2.Provider{}

api := r.Group("/api")
api.UseBefore(provider.Protect())
{
    api.Get("/me", handlers.Me)
}
```

## Requiring scopes

```go
orders := r.Group("/api/orders")
orders.UseBefore(provider.Protect("orders:read"))
```

A token without every named scope gets `403` with
`{"error": "insufficient_scope"}` — not `401`. The distinction matters to a
client: the token is valid and re-authenticating will not help, so it needs a
*different* token rather than a fresh one. RFC 6750 §3.1.

{{< callout type="warning" >}}
Register middleware on a group **before** its routes. A group snapshots its
middleware into each route as the route is added, so a `UseBefore` that comes
after a `Get` silently does nothing.
{{< /callout >}}

## Reading the token

```go
func Me(c app.Context) error {
    principal, ok := oauth2.PrincipalFrom(c)
    if !ok {
        return c.Unauthorized(errors.New("no token"))
    }

    return c.JSON(app.M{
        "user":   principal.UserID,     // empty for client credentials
        "client": principal.ClientID,
        "scopes": principal.Scopes,
    })
}
```

| Method | |
|---|---|
| `HasScope("x")` | One scope |
| `HasAllScopes("x", "y")` | Every one |
| `HasAnyScope("x", "y")` | At least one |
| `IsClientCredentials()` | No user is involved |

Use `IsClientCredentials()` rather than checking `sub` against `client_id`
yourself. For a machine token the two are equal by design, and reading the
claim invites treating a client id as a user id.

## Working with the auth package

`Protect` also sets the key `auth` uses, so a handler already written against
`auth.AuthUser(c)` works with a bearer token without being changed:

```go
user := auth.AuthUser(c)   // the *Principal, or a real user — see below
```

With no resolver configured this is the `*oauth2.Principal`. To hand handlers
a real user row, supply one:

```go
&oauth2.Provider{
    UserResolver: func(ctx context.Context, userID string) (any, error) {
        return repos.User(a).FindByID(ctx, userID)
    },
}
```

This module cannot do that lookup itself: `auth.UserProvider` is three getters
with no lookup method, and `oauth2` has no opinion about what a user is or
where it lives.

{{< callout type="info" >}}
The dependency only ever points one way. `oauth2` imports `auth` for the
context key; `auth` knows nothing about OAuth2. What makes that work is that
`auth.Check` treats a user another middleware has already established as
authenticated, so `auth.Protected` and `oauth2.Protect` compose in either
order.
{{< /callout >}}

## Combining with session authentication

A route can accept either a session cookie or a bearer token:

```go
api.UseBefore(provider.Protect(), auth.Protected)
```

`Protect` populates the user from a token when one is present; `auth.Protected`
then accepts it, or falls back to the session.

## Checking a token from elsewhere

Another service can verify a token without calling this one, using the
published keys:

```text
GET /.well-known/jwks.json
```

Verify RS256 against the key matching the token's `kid`, and check `iss`,
`aud` and `exp`.

{{< callout type="warning" >}}
Offline verification cannot see revocation. A token revoked a second ago still
verifies until it expires, because nothing about the signature changes. Where
that matters, call the introspection endpoint instead — it reads the
revocation row:

```bash
curl -u "$CLIENT_ID:$CLIENT_SECRET" \
  -d token="$ACCESS_TOKEN" \
  https://auth.example.com/oauth/introspect
```

Introspection is limited to confidential clients, so a browser cannot use it
to probe tokens it was never issued.
{{< /callout >}}
