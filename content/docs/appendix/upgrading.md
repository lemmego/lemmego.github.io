---
title: Upgrade notes
type: docs
prev: docs/appendix/
next: docs/appendix/faq
weight: 142
sidebar:
  open: true
---

Everything on the rest of the site describes the current release. This page is
the exception: it collects the changes that need action when you move an
existing project forward, so you can read it once after an upgrade and ignore
it the rest of the time.

Modules are versioned independently. Only the ones listed here have changes
that affect code you have already written.

## Breaking changes

### `oauth2` v0.2.0 — one user loader

`Provider.UserResolver` and the `oauth2.UserResolver` type were removed.
Resolving a user from a token is now configured in one place, alongside every
other credential:

```go
// Before — oauth2 resolved its own user
&oauth2.Provider{
    UserResolver: func(ctx context.Context, id string) (any, error) { … },
}

// Now — auth resolves users for every credential type
auth.Opts{
    UserLoader: func(ctx context.Context, id string) (any, error) { … },
}
```

If you read the authenticated user inside a route protected by
`oauth2.Protect`, check what you assert it to. The old `Protect` stored an
`*oauth2.Principal` under auth's user key, so a handler written against your
own user type would have failed the assertion. It stores whatever
`UserLoader` returns, so one handler now works behind either credential.

See [Protecting routes](/docs/oauth2/protecting-routes) for the current setup.

### `migration` v0.1.24 — `--step` counts migrations

`migrate down --step N` reverts the last N *migrations*. It previously
reverted the last N *batches*, where a batch is everything applied by one
`migrate up` run.

The two readings agree only when each batch holds a single migration. On a
project whose schema went up in one command — which is every project on its
first deploy — the newest batch is the entire schema, so `down --step 1`
reverted all of it.

**If you are pinned below v0.1.24, do not use `down --step`.** Upgrade, or
roll back deliberately with an explicit count you have checked against
`schema_migrations`.

## New behaviour worth adopting

### `migration` v0.5.1 — pooled URLs are skipped automatically

`migrate` reads `DATABASE_URL_UNPOOLED` ahead of `DATABASE_URL`, so a managed
Postgres provider that publishes both endpoints gets migrated over the direct
one. Set both variables and nothing further is needed.

Migrating through a transaction pooler fails intermittently and can leave a
schema half-changed. If your provider gives you only a pooled URL, see
[Never migrate through a connection pooler](/docs/migrations/running-migrations#never-migrate-through-a-connection-pooler)
for what to set instead.

### `cli` v0.5.5 — `lemmego run` forwards stdin

A command run through `lemmego run` can read standard input, so it can prompt,
accept a pipe, or speak a protocol over stdio. Below this version stdin was
not forwarded and any read returned EOF immediately, which is why
`lemmego run mcp` needs v0.5.5 or later.

## Minimum versions

Features added after a module's first release. Nothing here is a breaking
change; the feature is simply absent below the version given.

| Feature | Needs |
|---|---|
| [`database` session driver](/docs/session#database) | `api` v0.6.5 |
| [MCP server over stdio](/docs/mcp) | `cli` v0.5.5 |
| [Named keys and constraints](/docs/migrations/schema-builder#keys-and-constraints) | `migration` v0.5.0 |
| [Unpooled DSN preference](/docs/migrations/running-migrations#which-database-migrate-connects-to) | `migration` v0.5.1 |

## Upgrading a project

Modules share no release train, so bump the ones you use and let the module
graph settle the rest:

```shell
go get -u github.com/lemmego/api@latest
go mod tidy
go build ./...
```

Then run the test suite. If you do not have one, [Testing](/docs/testing)
starts a real application against a scratch database in about twenty lines.
