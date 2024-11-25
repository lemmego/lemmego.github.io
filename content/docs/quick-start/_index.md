---
title: Quick Start
type: docs
prev: docs/installation/
next: docs/http/routing/
sidebar:
  open: true
weight: 2
---

## Creating an application

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

## Running an application:

If no other application has occupied the `8080` port, your app should be running now. Open your browser and visit `http://locahost:8080` and you should see a minimal homepage.

The `go run ./cmd/app` is the very basic command to run your application. If you run `lemmego run` from your project root,
the result will be the same.

If you use either of these commands to run your application, whenever you make any changes to your source code, you will
have to restart your server by pressing `Ctrl+C` from your terminal and re-running the command.

During development, you might want to [use the air package](https://github.com/air-verse/air) for live-reloading of your application upon changes.
Follow the instructions in the air documentation to get started.

If you have air installed, and the `air` command is available in your terminal, run the `air` command from the project root
to run the application with live-reloading enabled. Your project already has an `air.toml` file which will be detected
by the `air` command.

## Frontend watching:

Lemmego comes with a few frontend options:

* [Go Templates](https://pkg.go.dev/text/template)
  * If you want to use Go Templates for your frontend, you can run the `make watch` command which will use the port 1773
    and reload the browser if any `.gohtml` file is modified.
* [Templ](https://templ.guide/)
  * If you want to use Templ for your frontend, you can run the `make watch` command which will use the port 1773
        and reload the browser if any `.templ` file is modified.
* [Inertia](https://inertiajs.com/) (with React and Vue)
  * If you want to use Inertia for your frontend, you can run the `npm run dev` command which will take care of reloading
    your React (`.tsx/.jsx`) or Vue (`.vue`) components.


  