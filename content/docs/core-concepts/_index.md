---
title: Core Concepts
type: docs
prev: docs/migrations/running-migrations
next: docs/core-concepts/application-bootstrap
weight: 80
sidebar:
  open: true
---

By this point you have written handlers, rendered a page and queried a
database. This section covers the wiring underneath all three: how an
application boots, how services find each other, and how a module adds itself
to your project.

Read it before you add your first module from the next section — every one of
them arrives as a provider, and the pages here are what a provider is.

{{< cards >}}
{{< card link="application-bootstrap" title="Application Bootstrap" subtitle="The app lifecycle and bootstrapping pipeline" >}}
{{< card link="service-container" title="Service Container" subtitle="Service registration and resolution" >}}
{{< card link="provider-plugin-system" title="Provider & Plugin System" subtitle="Extending the framework through providers" >}}
{{< card link="dependency-injection" title="Dependency Injection" subtitle="Type-safe DI with three lifetimes" >}}
{{< card link="event-system" title="Event System" subtitle="Lifecycle events and pub/sub communication" >}}
{{< /cards >}}
