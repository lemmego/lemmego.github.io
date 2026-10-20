---
title: Session
type: docs
prev: docs/deployment/
next: docs/logging
sidebar:
  open: true
weight: 49
---

## Overview

Session management is handled by the `session` package. It supports multiple storage backends and integrates with the framework's CSRF protection.

## Configuration

Session settings are in `internal/configs/session.go`:

```go
config.Set("session", config.M{
    "driver":   config.MustEnv("SESSION_DRIVER", "file"),
    "lifetime": config.MustEnv("SESSION_LIFETIME", 120),
    "cookie":   config.MustEnv("SESSION_COOKIE", "lemmego_session"),
    "domain":   config.MustEnv("SESSION_DOMAIN", ""),
    "path":     "/",
    "secure":   config.MustEnv("SESSION_SECURE", false),
    "http_only": true,
    "same_site": "lax",
})
```

## Storage Backends

### Memory

```go
config.Set("session", config.M{"driver": "memory"})
```

Sessions are stored in memory. Best for development or single-server deployments.

### File

```go
config.Set("session", config.M{"driver": "file"})
```

Sessions are persisted to disk (default: `storage/session/`). Includes automatic expiry cleanup.

### Redis

```go
config.Set("session", config.M{"driver": "redis"})
config.Set("keyvalue", config.M{
    "connections": config.M{"redis": config.M{
        "host": config.MustEnv("REDIS_HOST", "127.0.0.1"),
        "port": 6379,
    }},
})
```

Best for multi-server deployments where you already run Redis.

### Database

```go
config.Set("session", config.M{"driver": "database"})
```

Sessions live in your own SQL database, in a `sessions` table. Available since
`api` v0.6.5.

It is the only durable store that costs a deployment nothing extra. `file`
needs a writable volume that outlives the container, and `redis` needs a
service — so on a container platform with neither, the remaining choice is
`memory`, **which signs everybody out on every deploy**. If you already run a
database, this is the one to use.

The driver is named for the capability, not a product: it takes the dialect
from the connection your SQL connector registered, so the same value works on
**Postgres, MySQL and SQLite**.

#### Two requirements

**1. The provider must come after the database connector.** The driver
resolves the connection through `db.Resolve`, and `Provide` runs in
`LoadProviders` order — so a session provider listed first finds nothing:

```go
func LoadProviders() []app.Provider {
    return []app.Provider{
        &ormconnector.Provider{},   // registers db.Connection
        &session.Provider{},        // ...so this must come after it
    }
}
```

It refuses to boot in that case rather than falling back, naming the fix. The
fallback would be an application that looks healthy and signs everybody out,
which is indistinguishable from a cookie problem.

**2. The table is yours to migrate.** Each dialect has its own store writing
its own SQL, so there is no portable definition — `expiry` in particular is
read differently by each:

{{< tabs >}}
{{< tab name="Postgres" >}}
```sql
CREATE TABLE sessions (
    token  TEXT        NOT NULL PRIMARY KEY,
    data   BYTEA       NOT NULL,
    expiry TIMESTAMPTZ NOT NULL
);
CREATE INDEX sessions_expiry_idx ON sessions (expiry);
```
{{< /tab >}}
{{< tab name="MySQL" >}}
```sql
CREATE TABLE sessions (
    token  CHAR(43) COLLATE utf8mb4_bin NOT NULL PRIMARY KEY,
    data   BLOB         NOT NULL,
    expiry TIMESTAMP(6) NOT NULL
);
CREATE INDEX sessions_expiry_idx ON sessions (expiry);
```
{{< /tab >}}
{{< tab name="SQLite" >}}
```sql
CREATE TABLE sessions (
    token  TEXT NOT NULL PRIMARY KEY,
    data   BLOB NOT NULL,
    expiry REAL NOT NULL
);
CREATE INDEX sessions_expiry_idx ON sessions (expiry);
```
{{< /tab >}}
{{< /tabs >}}

`lemmego new --session database` writes this migration for you, for the
database you picked. The index keeps the periodic sweep of expired rows cheap;
without it every sweep scans the table.

Write it as raw `tx.Exec` rather than through the schema builder. The schema
belongs to the store, not to your project: the builder would add an `id` and
timestamps, and produce a table the store cannot query.

## Provider Registration

The session provider is registered in `bootstrap/providers.go`:

```go
func LoadProviders() []app.Provider {
    return []app.Provider{
        &session.Provider{},
    }
}
```

With the `database` driver this must be listed **after** your SQL connector —
see [Database](#database) above.

## Using Sessions

### In Request Context

```go
// Read
val := c.Session("key")
str := c.SessionString("key")

// Write
c.PutSession("key", value)

// Read and remove
val := c.PopSession("key")
str := c.PopSessionString("key")
```

### Via the Session Manager

```go
sess := app.Get[*session.Session](a)

// Standard scs.SessionManager API
err := sess.RenewToken(ctx)
err := sess.Destroy(ctx)
userID := sess.GetString(ctx, "user_id")
sess.Put(ctx, "last_activity", time.Now())
```

## Session & CSRF

The CSRF middleware keeps its token in the session, under `_token`. It is generated
once — on the first request of a session — and reused for as long as that session
lives, rather than being rotated per request; [CSRF Protection](/docs/security/csrf)
explains why. Destroying or regenerating the session therefore also invalidates the
CSRF token, and the next request issues a fresh one.

Logging in rotates the session id (see [Session fixation](#session-fixation)),
but carries the data across, so the CSRF token survives and the request right
after a login is not rejected as expired. Logging out destroys the session, so
the next page load issues a new token.

## Session Fixation

`auth.Login` rotates the session id before writing the user into the session,
and `auth.Logout` destroys the session rather than only removing the user.
Without the rotation, an attacker who can plant a session cookie in a victim's
browser before they log in still holds a valid id afterwards, authenticated as
them.

Both are handled for you; there is nothing to call. If you manage sessions
yourself, do the same at your own login boundary:

```go
sess := app.Get[*session.Session](a)

if err := sess.RenewToken(ctx); err != nil {   // before storing the identity
    return err
}
sess.Put(ctx, "user_id", user.ID)

// ...and on the way out
err := sess.Destroy(ctx)
```

Applications configured with `DisableSession: true` authenticate with JWT and
have no session to fixate — but note that they also have nothing to revoke:
`auth.Logout` clears the cookie and a copy of the token taken beforehand stays
valid until it expires. The fixation defence above and server-side logout are
the same feature seen from two sides, and both are off together.

## Lifecycle

Session data is automatically loaded on request start and committed on response completion. You don't need to manually save session changes.

## When a session cannot be read

A stored record sometimes cannot be decoded: the file is corrupt, or the
record holds a `gob`-encoded type that the binary now running no longer
registers — which is the ordinary case after a deploy that removed one.

Such a session is treated as **an absent session**, not a server error. The
framework logs a warning, drops the cookie and serves the request anonymously,
so the visitor is signed out and can sign back in.

This is worth knowing because the underlying library does the opposite. `scs`
calls its error handler and returns *without invoking your handler at all*;
with no handler configured that is a bare `500`. The visitor would get a blank
error page on every URL — **including `/login`** — for as long as the cookie
lived, with nothing they could do about it. `api` v0.1.40 and later wrap the
middleware to prevent that.
