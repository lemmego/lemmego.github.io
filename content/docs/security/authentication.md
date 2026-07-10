---
title: Authentication
type: docs
prev: docs/security/
next: docs/security/csrf
sidebar:
  open: true
weight: 43
---

## Overview

The `auth` package provides dual authentication support: session-based and JWT-based. These can work independently or together.

## Setup

Register the auth provider in `bootstrap/providers.go`:

```go
func LoadProviders() []app.Provider {
    return []app.Provider{
        &auth.Provider{
            Opts: &auth.Opts{
                DisableSession: false,
                JwtSecret:      config.MustEnv("JWT_SECRET", "your-secret-key"),
                HomeRoute:      "/dashboard",
            },
        },
    }
}
```

## User Model

Your user model must implement the `UserProvider` interface:

```go
type UserProvider interface {
    GetID() any
    GetUsername() string
    GetPassword() string
}
```

The generated project includes a default `User` model that satisfies this interface:

```go
type User struct {
    ID        uint
    Name      string
    Email     string
    Password  string
    CreatedAt time.Time
    UpdatedAt time.Time
}

func (u *User) GetID() any     { return u.ID }
func (u *User) GetUsername() string { return u.Email }
func (u *User) GetPassword() string { return u.Password }
```

## Login

```go
func login(c app.Context) error {
    result := auth.Login(c, user, username, password)
    if result.Err != nil {
        return c.BadRequest(result.Err)
    }
    // result.JwtToken is available if JWT is enabled
    // result.Cookie contains the session/JWT cookie
    return c.JSON(app.M{"token": result.JwtToken})
}
```

## Auth Middleware

### Protected Routes

Blocks unauthenticated users (returns 401):

```go
r.Get("/dashboard", auth.Protected, handlers.Dashboard)
```

### Guest Routes

Allows only unauthenticated users (redirects to home):

```go
r.Get("/login", auth.Guest, handlers.LoginForm)
```

### Optional Auth

Silently populates the user if authenticated, never blocks:

```go
r.Get("/profile", auth.OptionalAuth, handlers.Profile)
```

## Accessing the Current User

```go
func MyHandler(c app.Context) error {
    user, ok := c.Get(auth.UserKey).(*auth.User)
    if !ok {
        return c.Unauthorized()
    }
    return c.JSON(app.M{"user": user})
}
```

## Logout

```go
func logout(c app.Context) error {
    auth.Logout(c)
    return c.Redirect("/")
}
```

Or via package-level helper:

```go
auth.Get(a).Logout(c)
```

## JWT Flow

1. On login, the auth package creates a JWT token signed with HMAC-SHA256
2. The token is stored in a `jwt` cookie (configurable) or returned in the response body
3. On subsequent requests, the token is read from the `jwt` cookie first, then `Authorization: Bearer <token>` header
4. The `user` claim contains the JSON-encoded user data
5. Custom claims can be merged via `Opts.JwtClaims`

## Session-Only Auth

Disable JWT:

```go
&auth.Opts{
    DisableSession: false,
    JwtSecret:      "", // JWT disabled when empty
}
```

## JWT-Only Auth

Disable session:

```go
&auth.Opts{
    DisableSession: true,
    JwtSecret:      "your-secret-key",
}
```
