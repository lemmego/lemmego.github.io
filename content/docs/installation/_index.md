---
title: Installation
type: docs
prev: /docs
next: docs/quick-start/
weight: 1
---

To get started, install the `lemmego` CLI.

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
