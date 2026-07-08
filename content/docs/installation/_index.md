---
title: Installation
type: docs
prev: /docs
next: docs/quick-start/
weight: 1
---

## Prerequisites

Lemmego is a Go framework. You should have basic familiarity with Go and have the following installed:

- [Go 1.24+](https://go.dev/dl/)
- [Node.js](https://nodejs.org/en/download/package-manager) (for frontend tooling)
- [Air](https://github.com/air-verse/air) (for hot reloading)
- [Templ](https://templ.guide/quick-start/installation) (optional, for type-safe Go templates)

## Installation

Once you have all the prerequisites installed, install the Lemmego CLI using this command:

{{< tabs >}}
{{< tab name="Linux" >}}

```shell
curl -fsSL https://raw.githubusercontent.com/lemmego/cli/refs/heads/main/installer.sh | sudo sh
```

{{< /tab >}}
{{< tab name="macOS" >}}

```shell
curl -fsSL https://raw.githubusercontent.com/lemmego/cli/refs/heads/main/installer.sh | sudo sh
```

Or with Homebrew (if available):

```shell
brew install lemmego/tap/lemmego
```

{{< /tab >}}
{{< tab name="Windows" >}} TBA {{< /tab >}}
{{< /tabs >}}

### Install via Go

If you have Go installed, you can also install the CLI directly:

```shell
go install github.com/lemmego/cli/cmd/lemmego@latest
```

Make sure `$GOPATH/bin` is in your `PATH`.

## Verify Installation

Run the following to confirm the CLI is installed:

```shell
lemmego --version
```

Expected output:

```
version [x.x.x]
```

## Next Steps

Now that the CLI is installed, proceed to the [Quick Start](/docs/quick-start/) guide to create your first project.
