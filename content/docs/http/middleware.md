---
title: Middleware
type: docs
prev: docs/http/
sidebar:
  open: true
weight: 5
---

When an HTTP request enters into your application, depending on how you've configured the application,
it will go through a set of:

* Global middleware (executed during each request), and
* Route-scoped middleware (executed for a specific route)
