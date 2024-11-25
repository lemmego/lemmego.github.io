---
title: Routing
type: docs
prev: docs/quick-start/
sidebar:
  open: true
weight: 4
---

Routing is how we want our application to respond to an HTTP request when a given URL segment, for example,
the `/api/v1/user` part in the `https://example.com/api/v1/user` and the HTTP verb (e.g. `GET`, `POST`, `PATCH` etc.) are
matched with our defined ones after submitting the request from the browser, or any other HTTP client such as Postman.

### Route Definitions

Routes are defined inside the `./internal/routes` directory. By default, there are two files containing some example
routes: the `web.go` and the `api.go` files.

* The `web.go` file contains the routes which are typically requested from
a browser that return HTML (e.g. `content-type: text/html`) responses.

* The `api.go` file contains the routes which typically return non-HTML (e.g. `content-type: application/json`) responses.

Feel free to define your routes in these files, or create your own route files (e.g. `products.go`, `orders.go`) if you
need. Let's create an example route in the `web.go` file:

```go {filename="web.go"}
r.Get("/hello", func(c *app.Context) error {
    return c.Text([]byte(`World`))
})
```

Keep your server running and open the `http://localhost:8080/hello` URL in your browser and
you should see the `text/plain` response:

> World