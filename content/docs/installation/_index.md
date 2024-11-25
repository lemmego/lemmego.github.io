---
title: Installation
type: docs
prev: /docs
next: docs/quick-start/
weight: 1
---

To get started let's install the `lemmego` cli first by running the following shell command in your favorite terminal:

{{< tabs items="Linux,macOS,Windows" >}}

{{< tab >}}

```shell
curl -fsSL https://raw.githubusercontent.com/lemmego/cli/refs/heads/main/installer.sh | sudo sh
```

{{</tab>}}
{{< tab >}}

```shell
curl -fsSL https://raw.githubusercontent.com/lemmego/cli/refs/heads/main/installer.sh | sudo sh
```

{{</tab>}}
{{< tab >}} TBA {{</tab>}}

{{< /tabs >}}

## Confirm Installation

Run the following command to make sure that the binary has been installed and is available system-wide:

```shell
lemmego --version
```

It should output something like this:

> version [x.x.x]

Congratulations! You have successfully installed the `lemmego` cli. In the next section, we will use this to create a new project.
