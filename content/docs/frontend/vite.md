---
title: Vite Integration
type: docs
prev: docs/frontend/inertia
sidebar:
  open: true
weight: 39
---

## Overview

Lemmego uses [Vite](https://vitejs.dev/) as the frontend build tool, integrated through the Inertia adapter. It provides hot module replacement (HMR) during development and optimized production builds.

## Configuration

The generated project includes a `vite.config.js`:

```js
import { defineConfig } from 'vite';
import laravel from 'laravel-vite-plugin';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    laravel({
      input: ['resources/js/app.tsx'],
      refresh: true,
    }),
    react(),
    tailwindcss(),
  ],
});
```

### Entry Points

The main entry point is `resources/js/app.tsx` (React) or `resources/js/app.js` (Vue).

## Development

Run the dev server:

```shell
npm run dev
```

This starts Vite's dev server. The `lemmego dev` command automatically detects `package.json` and starts Vite alongside air and templ.

### Hot Module Replacement

Changes to `resources/js/` and `resources/css/` files are instantly reflected in the browser without a full page reload.

## Production Build

Build assets for production:

```shell
lemmego build
```

Or run Vite directly:

```shell
npm run build
```

The built assets are output to `public/build/` with a `manifest.json`:

```json
{
  "resources/js/app.tsx": {
    "file": "assets/app-abc123.js",
    "isEntry": true,
    "src": "resources/js/app.tsx"
  },
  "resources/css/app.css": {
    "file": "assets/app-xyz789.css",
    "src": "resources/css/app.css"
  }
}
```

## Root Layout

The Inertia root layout is in `resources/views/root.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title inertia>{{ .appName }}</title>
    {{ .inertiaHead }}
</head>
<body>
    {{ .inertia }}
    @vite('resources/js/app.tsx')
</body>
</html>
```

## Tailwind CSS

The generated project includes Tailwind CSS v4 configured via the Vite plugin. Styles are in `resources/css/app.css`:

```css
@import "tailwindcss";

.input { @apply border rounded px-3 py-2; }
.btn-primary { @apply bg-blue-500 text-white px-4 py-2 rounded; }
```

## Package Manager

The project uses `pnpm` by default with a `pnpm-workspace.yaml` for monorepo support. You can use `npm` or `yarn` as alternatives.
