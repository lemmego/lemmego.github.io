---
title: Installation
type: docs
prev: docs/prologue
next: docs/quick-start/
weight: 11
sidebar:
  open: true
---

## Prerequisites

Lemmego is a Go framework. You should have basic familiarity with Go and have the following installed:

- [Go 1.27+](https://go.dev/dl/) — the ORM uses generic methods, which need 1.27
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

{{< /tab >}}
{{< tab name="Windows" >}}

In an elevated PowerShell prompt:

```powershell
irm https://raw.githubusercontent.com/lemmego/cli/refs/heads/main/installer.ps1 | iex
```

{{< /tab >}}
{{< /tabs >}}

### Install from source

If you have Go installed, you can build the CLI yourself:

```shell
go install github.com/lemmego/cli/cmd@latest
```

{{< callout type="warning" >}}
This installs a binary called **`cmd`**, after the package's directory name.
Rename it to `lemmego` before using the rest of these docs:

```shell
mv "$(go env GOPATH)/bin/cmd" "$(go env GOPATH)/bin/lemmego"
```
{{< /callout >}}

Make sure `$GOPATH/bin` is in your `PATH`.

A binary installed this way reports its module version; one built from a
checkout reports `dev+<commit>`.

### Installer options

Both installers resolve the latest release automatically and verify the download
checksum. Two environment variables override that:

| Variable | Effect |
|----------|--------|
| `LEMMEGO_VERSION` | Install a specific tag instead of the latest, e.g. `v0.4.1` |
| `LEMMEGO_INSTALL_DIR` | Install somewhere other than `/usr/local/bin` (`C:\Windows\System32` on Windows) |

```shell
# Pin a version, and install without sudo
LEMMEGO_VERSION=v0.4.1 LEMMEGO_INSTALL_DIR=$HOME/.local/bin \
  curl -fsSL https://raw.githubusercontent.com/lemmego/cli/refs/heads/main/installer.sh | sh
```

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
