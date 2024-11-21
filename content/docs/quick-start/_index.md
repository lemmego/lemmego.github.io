---
title: Quick Start
type: docs
prev: docs/installation/
---

Now that you have installed the `lemmego` cli, you can use it to create a new project running the following command:

```shell
lemmego new my-project
```

This command will ask you to provide the module name (for the `go.mod` file) of your project and create a new project in the `my-project` directory.

Once the project has been created, you can navigate into your project directory:

```shell
cd my-project
```

...and run your application:

```shell
go run ./cmd/app
```

In development, you might want to [use the air package](https://github.com/air-verse/air) for live-reloading of your application upon changes.
Follow the instructions in the air documentation to get started.

If no other application has occupied the `8080` port, your app should be running. Open your browser and visit `http://locahost:8080` and you should see a minimal homepage.

To learn more about the `lemmego` CLI, visit [https://github.com/lemmego/cli](https://github.com/lemmego/cli).
