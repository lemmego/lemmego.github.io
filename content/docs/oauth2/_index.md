---
title: OAuth2 Server
type: docs
prev: docs/security/encryption
next: docs/oauth2/installation
sidebar:
  open: true
weight: 44
---

## Overview

The `oauth2` module turns your application into an OAuth 2.0 **authorization
server**: it issues and revokes the tokens other applications use to call your
API, manages the clients that may ask for them, and runs the screen where a
user approves or refuses.

This is the server side — the equivalent of Laravel Passport. Signing your
users *in* to somebody else's provider, "log in with GitHub", is the client
side and is a different, much smaller thing this module does not do.

```go
// bootstrap/providers.go — below the database connector
&ormconnector.Provider{},
&oauth2.Provider{},
```

{{< cards >}}
{{< card link="installation" title="Installation" subtitle="Set it up in an existing project" >}}
{{< card link="configuration" title="Configuration" subtitle="Every key and environment variable" >}}
{{< card link="clients" title="Clients" subtitle="The five kinds, and how to register them" >}}
{{< card link="grants" title="Grants" subtitle="Authorization code, refresh, device and the rest" >}}
{{< card link="protecting-routes" title="Protecting routes" subtitle="Bearer tokens and scopes" >}}
{{< card link="consent-screen" title="Consent screen" subtitle="The default, and how to replace it" >}}
{{< card link="tokens-and-keys" title="Tokens and keys" subtitle="JWTs, JWKS, rotation, revocation" >}}
{{< /cards >}}

## What it supports

| Grant | Use |
|---|---|
| Authorization code + PKCE | A third-party web, mobile or single-page application acting for a user |
| Refresh token | Renewing access without asking the user again |
| Client credentials | A machine calling your API as itself, with no user involved |
| Device authorization | A CLI, a TV app, anything that cannot open a browser |
| Personal access tokens | A token a user creates for themselves, like an API key |

## What it deliberately does not support

**The implicit grant** returned tokens directly in a redirect, where they
landed in browser history and referrer headers. It is obsolete; the
authorization code grant with PKCE replaces it.

**The password grant** required the client application to handle your users'
passwords directly, which defeats the point of delegated authorization. RFC
9700 deprecates it.

Neither is disabled by a setting you could switch back on — they are not
implemented. The token endpoint names them in its error message so a client
that tries gets an answer rather than a puzzle:

```json
{
  "error": "unsupported_grant_type",
  "error_description": "the password grant is not supported; use the authorization code grant with PKCE"
}
```

Passport dropped both as well.

## Standards

The implementation follows RFC 6749 (the core framework), RFC 6750 (bearer
token usage), RFC 7636 (PKCE), RFC 7009 (revocation), RFC 7638 (JWK
thumbprints), RFC 7662 (introspection), RFC 8414 (server metadata), RFC 8628
(the device grant), RFC 9068 (the JWT profile for access tokens), and the
current best practice in RFC 9700.

## Requirements

A database. Clients, authorization codes, refresh tokens and the revocation
list are all persisted, so a project scaffolded with `--database none` cannot
run the server — the provider says so at boot rather than failing later:

```text
oauth2: this application has no database, and an OAuth2 server cannot run without one.
```

It works with any SQL connector — the Lemmego ORM, GORM or Bun, with or
without GPA — because it resolves the connection through
[`api/db`](/docs/database/connection-seam) rather than through an ORM.

## A word on hand-rolled protocol code

This is a hand-written implementation, not a wrapper around an audited library
such as `ory/fosite`. That is a deliberate trade: the API stays
Lemmego-shaped, and there is no second framework's vocabulary leaking through.

The cost is that protocol mistakes here are security bugs. The module carries
an adversarial test suite covering code replay, code and redirect
substitution, PKCE downgrade and stripping, refresh reuse, scope elevation,
`alg:none`, algorithm confusion, `kid` injection, `typ` confusion and a forged
`jti`. That suite proves those specific attacks are blocked. It does not prove
the absence of attacks, and it would be wrong to read it as doing so.
