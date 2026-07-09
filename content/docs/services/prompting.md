---
title: CLI Prompting
type: docs
prev: docs/services/queue
sidebar:
  open: true
weight: 55
---

## Overview

The `cmder` package provides fluent CLI prompting utilities for building interactive command-line interfaces. It wraps `github.com/manifoldco/promptui` for terminal UI.

## Basic Prompts

### Ask

```go
import "github.com/lemmego/api/cmder"

name := cmder.Ask("What is your name?", nil).Result
```

With validation:

```go
name := cmder.Ask("Enter your email", func(input string) error {
    if !strings.Contains(input, "@") {
        return fmt.Errorf("invalid email")
    }
    return nil
}).Result
```

### Confirm

```go
confirmed := cmder.Confirm("Continue?", 'y')
if confirmed.Confirmed {
    // proceed
}
```

### Select

```go
selected := cmder.Select("Choose a color", []cmder.Item{
    {Label: "Red"},
    {Label: "Green"},
    {Label: "Blue"},
})
```

### MultiSelect

```go
selected := cmder.MultiSelect("Select toppings", []cmder.Item{
    {Label: "Cheese", IsSelected: true},
    {Label: "Pepperoni"},
    {Label: "Mushrooms"},
}, 0) // 0 = position of "Done" item
```

## Chaining Prompts

Prompts can be chained with conditional execution:

```go
result := cmder.
    Ask("Project name?", nil).
    Confirm("Include Redis?", 'y').
    When(true, cmder.Ask("Redis host:", nil))
```

## Use in CLI Commands

The prompting utilities are used extensively in the CLI's code generators:

```go
// From the interactive model generator
name := cmder.Ask("Field name (snake_case):", validateSnakeCase).Result
fieldType := cmder.Select("Field type:", fieldTypes)
```

## Result Types

```go
type PromptResult struct {
    Result    string
    Confirmed bool
    Items     []Item
}
```

## Interrupt Handling

All prompts handle Ctrl+C gracefully, exiting the application cleanly.
