---
title: Lemmego — The full-stack Go web framework
toc: false
---

Lemmego is a modern, full-stack web framework for Go that combines the productivity of Laravel/Rails with the type safety and performance of Go.

## Batteries

Lemmego is a batteries-included framework.

{{< tabs >}}
{{< tab name="Bootstrap" >}}

```go
// cmd/app/main.go
func main() {
    app.Configure().
        WithProviders(bootstrap.LoadProviders()).
        WithRoutes(bootstrap.LoadRoutes()).
        WithMiddlewares(bootstrap.LoadMiddlewares()).
    Run()
}
```

```go
// bootstrap/providers.go
func LoadProviders() []app.Provider {
    return []app.Provider{
        &session.Provider{},
        &gormconnector.Provider{UseGPA: true},
        &inertia.Provider{},
        &auth.Provider{},
    }
}
```

{{< /tab >}}
{{< tab name="Route" >}}

```go
// internal/routes/web.go
func WebRoutes(a app.App) {
    r := a.Router()

    r.Get("/articles", handlers.ArticleIndex)
    r.Get("/articles/{id}", handlers.ArticleShow)

    admin := r.Group("/admin")
    admin.UseBefore(middleware.AdminAuth)
    admin.Get("/articles/new", handlers.ArticleCreate)
    admin.Post("/articles", handlers.ArticleStore)
}
```

Route parameters like `{id}` are accessed via `c.Param("id")`. Groups share common prefixes and middleware.

{{< /tab >}}
{{< tab name="Middleware" >}}

```go
// bootstrap/http_middleware.go
func LoadHTTPMiddlewares() []app.HTTPMiddleware {
    return []app.HTTPMiddleware{
        middleware.Recoverer(),     // Panic recovery
        middleware.RequestLogger(), // Request logging
        middleware.MethodOverride,  // PUT/DELETE via _method
    }
}

// bootstrap/middleware.go
func LoadMiddlewares() []app.Handler {
    return []app.Handler{
        middleware.VerifyCSRF(&middleware.CSRFOpts{
            ExcludePatterns: []string{"/api/.*"},
        }),
    }
}
```

HTTP middleware wraps the entire router. App middleware runs at the handler level — both compose into a flexible pipeline.

{{< /tab >}}
{{< tab name="Migrations" >}}

```go
// internal/migrations/20250706000001_create_articles_table.go
func init() {
    migration.GetMigrator().AddMigration(&migration.Migration{
        Version: "20250706000001",
        Up:      mig_up, Down: mig_down,
    })
}

func mig_up(tx *sql.Tx) error {
    schema := migration.Create("articles", func(t *migration.Table) {
        t.BigIncrements("id")
        t.String("title").NotNull()
        t.Text("body")
        t.String("status").Default("'draft'")
        t.ForeignID("author_id").Constrained()
        t.Timestamps()
    }).Build()
    _, err := tx.Exec(schema)
    return err
}
```

Run with: `lemmego run migrate up`

{{< /tab >}}
{{< tab name="Persistence" >}}

```go
// internal/repos/article_repo.go
type ArticleRepository struct {
    gpa.MigratableRepository[models.Article]
}

func Article() *ArticleRepository {
    return &ArticleRepository{
        gpagorm.GetRepository[models.Article](),
    }
}

// internal/handlers/article_handler.go
func ArticleIndex(c app.Context) error {
    articles, _ := Article().FindAll(c.RequestContext(),
        gpa.Where("status", gpa.OpEqual, "published"),
        gpa.OrderBy("created_at", gpa.OrderDesc),
        gpa.Preload("Author"),
    )
    return c.JSON(app.M{"articles": articles})
}
```

Type-safe, generic repositories — no `interface{}` casting, no runtime reflection.

{{< /tab >}}
{{< tab name="Plugins" >}}

```go
// plugins/cms/provider.go
type CMSProvider struct{}

func (p *CMSProvider) Provide(a app.App) error {
    a.AddService(NewCMS(a.Config()))
    a.Router().Get("/sitemap.xml", p.Sitemap)
    return nil
}

func (p *CMSProvider) Sitemap(c app.Context) error {
    articles, _ := Article().FindAll(c.RequestContext(),
        gpa.Where("status", gpa.OpEqual, "published"),
    )
    return c.XML(app.M{"sitemap": buildSitemap(articles)})
}
```

```go
// bootstrap/providers.go
func LoadProviders() []app.Provider {
    return []app.Provider{
        // ...framework providers...
        &plugins.CMSProvider{},
    }
}
```

Providers implement `app.Provider` — they register services, routes, and middleware with full access to the application instance.

{{< /tab >}}
{{< tab name="Frontend" >}}

```go
// internal/handlers/article_handler.go
func ArticleIndex(c app.Context) error {
    articles, _ := Article().FindAll(c.RequestContext(),
        gpa.Where("status", gpa.OpEqual, "published"),
        gpa.Preload("Author"),
    )
    return inertia.Respond(c, "Articles/Index", map[string]any{
        "articles": articles,
    })
}
```

```tsx
// resources/js/Pages/Articles/Index.tsx
export default function Index({ articles }: PageProps) {
    return (
        <div>
            {articles.map(article => (
                <ArticleCard key={article.id} article={article} />
            ))}
        </div>
    );
}
```

Choose from Inertia.js with React/Vue, server-rendered Go Templates, or type-safe Templ components.

{{< /tab >}}
{{< /tabs >}}

## Features

- **Full-featured HTTP layer** — Param-based routing, route grouping, flexible middleware, input validation, typed errors
- **Type-safe database layer** — GPA provides compile-time type safety across SQL, NoSQL, and KV stores with generic `Repository[T]`
- **Plugin architecture** — Extend the framework through providers without modifying core code
- **Multiple frontends** — Go Templates, Templ, or Inertia.js with React/Vue
- **File storage** — Unified abstraction for local, S3, and GCS
- **CLI tools** — Project scaffolding, code generators, migration management

## Get Started

{{< cards >}}
{{< card link="docs/prologue" title="Prologue" icon="book-open" subtitle="Learn the framework from the ground up" >}}
{{< card link="docs/installation" title="Installation" icon="terminal" subtitle="Install the lemmego CLI" >}}
{{< card link="docs/quick-start" title="Quick Start" icon="fire" subtitle="Create your first project in minutes" >}}
{{< /cards >}}

## What's Included

| Module | Description |
|--------|-------------|
| **API** | Core framework: routing, middleware, DI, sessions, config, validation |
| **GPA** | Type-safe database abstraction with multi-provider support |
| **CLI** | Project scaffolding and code generation |
| **Inertia** | Server-side adapter for Inertia.js SPAs |
| **Templ** | Bridge for type-safe Go templates |
| **Auth** | Session + JWT authentication with middleware |
| **Migrations** | Bidirectional database schema management |
| **File System** | Cloud-agnostic storage (local, S3, GCS) |
