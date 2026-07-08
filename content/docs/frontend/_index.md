---
title: Frontend
type: docs
prev: docs/migrations/running-migrations
next: docs/frontend/go-templates
sidebar:
  open: true
weight: 35
---

## Overview

Lemmego supports multiple frontend rendering approaches, from server-rendered HTML to modern SPAs. You can choose the approach that best fits your project, or combine them.

### Available Options

| Approach | Description | Best For |
|----------|-------------|----------|
| **Go Templates** | Native `html/template` with layouts, partials, and caching | Traditional server-rendered apps |
| **Templ** | Type-safe Go templates with compile-time checking | Go developers who want type safety in templates |
| **Inertia.js** | SPA-like experience with React or Vue, server-side routing | Modern single-page applications with rich interactivity |

### Asset Pipeline

All frontend approaches work with the Vite asset pipeline for bundling JavaScript, CSS, and hot module replacement during development.

{{< cards >}}
{{< card link="go-templates" title="Go Templates" subtitle="Server-rendered HTML with layouts and partials" >}}
{{< card link="templ" title="Templ" subtitle="Type-safe Go templates" >}}
{{< card link="inertia" title="Inertia.js" subtitle="Modern SPA with React or Vue" >}}
{{< card link="vite" title="Vite Integration" subtitle="Asset pipeline and HMR" >}}
{{< /cards >}}
