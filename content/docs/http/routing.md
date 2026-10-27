---
title: Routing
type: docs
prev: docs/http/
next: docs/http/middleware
weight: 21
sidebar:
  open: true
---

## What a route is

When somebody opens a page, their browser sends your server a short message.
Stripped of everything else, it amounts to two pieces of information:

```text
GET /users/42
```

A **method** — `GET` — saying what kind of action this is, and a **path** —
`/users/42` — saying what it concerns. That is almost all your program is
given, and from it alone it must decide which of your Go functions should
answer.

A **route** is one line in that decision. It pairs a method and a path with a
function to run:

> `GET` + `/hello` → run this function

Nothing more. A web application is, at bottom, a list of such pairings, and
the **router** is the thing that holds the list and looks up the right one
when a request arrives. The function it picks is called a **handler**, because
it handles the request.

If no route matches, there is nothing to run, and the server answers `404 Not
Found` — which is not an error in your code, just the absence of a matching
line.

### Methods

The method is a verb describing intent, and the convention is near-universal:

| Method | Means | Typically |
|---|---|---|
| `GET` | fetch something, change nothing | viewing a page |
| `POST` | create something | submitting a form |
| `PUT` | replace something | saving a whole record |
| `PATCH` | change part of something | editing one field |
| `DELETE` | remove something | deleting a record |

Nothing in HTTP enforces this; a `GET` route *could* delete a record. It is a
promise, and browsers, caches and crawlers rely on it — which is why a `GET`
should never change data.

## Writing routes

Routes live in `internal/routes/`. Each method on the router registers one:

```go
// internal/routes/web.go
package routes

func WebRoutes(a app.App) {
    r := a.Router()

    r.Get("/hello", func(c app.Context) error {
        return c.Text([]byte("World"))
    })

    r.Post("/submit", func(c app.Context) error {
        return c.JSON(app.M{"status": "ok"})
    })
}
```

Read the first one as: *when a `GET` arrives for `/hello`, run this function.*

The handler takes one argument, `c app.Context`, and returns an `error`. That
argument carries everything about the request and is also how you reply —
`c.Text` sends plain text, `c.JSON` sends JSON. Returning `nil` means the
request was answered; returning an error hands it to the framework to turn
into an error page or a JSON error.

`app.M` is shorthand for `map[string]any`, so that second handler sends
`{"status":"ok"}`.

The router has a method for every HTTP method: `Get`, `Post`, `Put`, `Patch`,
`Delete`, `Head`, `Options`, `Connect` and `Trace`.

## Route parameters

Most addresses are not fixed. `/users/42` and `/users/43` are different pages,
and you cannot register a route per user — you do not know their ids, and
there may be millions.

So a path pattern can contain a **hole** with a name on it:

```text
/users/{id}
```

This matches `/users/42`, `/users/43` and `/users/anything-without-a-slash`.
The part that fell into the hole — `42` — is the **route parameter**, and the
router keeps it for you under the name you gave it. `c.Param("id")` reads it
back:

```go
r.Get("/users/{id}", func(c app.Context) error {
    id := c.Param("id")
    return c.Text([]byte("User: " + id))
})
```

So one route serves every user, and the parameter tells the handler which one
was asked for.

Two things to know about the value:

- **It is always a string**, because a URL is text. `/users/42` gives you
  `"42"`, and turning it into a number is yours to do — with
  `strconv.Atoi`, which also tells you when somebody asked for
  `/users/banana`.
- **It is typed by a stranger.** Anyone can request `/users/999999` or
  `/users/'%20OR%201=1`. Treat it as input to be checked, never as a fact.

A pattern can have several parameters, and a parameter fills exactly one path
segment — it stops at the next `/`:

```go
r.Get("/launch/{slug}/comments/{commentID}", handlers.ShowComment)
```

{{< callout type="info" >}}
**A hole must be a whole segment.** `/users/{id}` is valid; `/user-{id}` and
`/@{handle}` are not, because there the fixed text and the hole share one
segment, and Go's router cannot split a segment in two.

A URL of that shape — `/@alice`, say — is therefore built by rewriting the
path in [HTTP middleware](/docs/http/middleware) before matching happens:
the request arrives for `/@alice`, the middleware turns it into `/u/alice`,
and an ordinary `/u/{handle}` route answers it.
{{< /callout >}}

## Route groups

A **group** is not a thing that exists when your program runs. It is a way of
writing: a small object holding a path prefix and a list of middleware, which
it attaches to every route you register through it. Register
`api.Get("/users", …)` on a group whose prefix is `/api`, and what lands in
the router is an ordinary route for `/api/users`. Afterwards there is no group
left — only routes, exactly as if you had typed them out in full.

So a group buys you nothing at runtime. What it buys is that the prefix and
the rule are written **once**:

```go
api := r.Group("/api")
api.Get("/users", handlers.UserIndex)    // → /api/users
api.Post("/users", handlers.UserStore)   // → /api/users

admin := r.Group("/admin")
admin.UseBefore(auth.Protected)          // applies to every route below
admin.Get("/dashboard", handlers.AdminDashboard)
```

Every route in the `admin` group now requires a signed-in user, because
`UseBefore` attaches that check to the group rather than to each route.

This is the real reason to reach for one. Repeating `auth.Protected` on thirty
admin routes works right up until somebody adds the thirty-first and forgets,
and that single unprotected route looks exactly like the others in the file.
Stated on the group, it cannot be forgotten by a route that did not mention
it.

Groups nest, and the prefixes join:

```go
v1 := api.Group("/v1")
v1.Get("/products", handlers.ProductIndex)   // → /api/v1/products
```

## Middleware on a route

**Middleware** is a function that runs *before* the handler and can decide
whether the handler runs at all — a checkpoint on the way in. Authentication
is the usual example: look at the request, and either let it through or answer
it yourself with a redirect to the sign-in page.

In Lemmego, middleware is not a special type. It is an ordinary handler listed
before the one that answers:

```go
r.Get("/search", auth.OptionalAuth, handlers.SearchIndex)
r.Post("/posts", auth.Protected, handlers.PostStore)
```

Each runs in turn. A handler passes control onward by calling `c.Next()`, and
simply returning without calling it stops the chain there — which is how
`auth.Protected` refuses an anonymous request.

`auth.Protected` is `func(c app.Context) error`, exactly like your own
handlers. That is the whole contract, and there is no separate middleware
interface to satisfy.

[Middleware](/docs/http/middleware) covers writing your own, and the second
kind that wraps the entire router.

## Registering your route files

Writing a function full of routes does not run it. `bootstrap/routes.go` lists
the functions the application should call at startup:

```go
// bootstrap/routes.go
package bootstrap

func LoadRoutes() []app.RouteCallback {
    return []app.RouteCallback{
        routes.WebRoutes,
        routes.ApiRoutes,
    }
}
```

A `RouteCallback` is just `func(a app.App)` — a function handed the running
application, which it uses to reach `a.Router()` and register. A new route
file is a new function in this list.

## Router reference

```go
type Router interface {
    Group(prefix string) *routeGroup
    UseBefore(handlers ...Handler)
    UseAfter(handlers ...Handler)
    Get(pattern string, handlers ...Handler) *route
    Post(pattern string, handlers ...Handler) *route
    Put(pattern string, handlers ...Handler) *route
    Patch(pattern string, handlers ...Handler) *route
    Delete(pattern string, handlers ...Handler) *route
    Head(pattern string, handlers ...Handler) *route
    Options(pattern string, handlers ...Handler) *route
    Connect(pattern string, handlers ...Handler) *route
    Trace(pattern string, handlers ...Handler) *route
    Use(middlewares ...HTTPMiddleware)
    HasRoute(method string, pattern string) bool
    Handle(pattern string, handler http.Handler)
    HandleFunc(pattern string, handler func(http.ResponseWriter, *http.Request))
}
```

`Handle` and `HandleFunc` mount a plain `net/http` handler, for reusing code
written against the standard library.

To see every route your application actually registered, including the ones
modules added for you, use the `list-routes` tool on the
[MCP server](/docs/mcp) — it reports each route's method, resolved path and
handler from the running application.

## Next steps

- [Middleware](/docs/http/middleware) — writing your own checkpoints.
- [Request handling](/docs/http/request-handling) — reading form and JSON
  bodies, and validating them.
- [Context](/docs/http/context) — the full API of the `c` every handler
  receives.
