---
title: Lemmego — The full-stack Go web framework
layout: home
toc: false
---

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
        &queue.Provider{},
        &auth.Provider{},
    }
}
```

{{< /tab >}}
{{< tab name="Routing" >}}

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

```go
// bootstrap/middleware.go
func LoadMiddlewares() []app.Handler {
    return []app.Handler{
        middleware.VerifyCSRF(&middleware.CSRFOpts{
            ExcludePatterns: []string{"/api/.*"},
        }),
    }
}
```

Route parameters like `{id}` are accessed via `c.Param("id")`. HTTP middleware wraps the router while app middleware runs at the handler level — both compose into a flexible pipeline.

{{< /tab >}}
{{< tab name="Handler" >}}

```go
// internal/inputs/article_input.go
type CreateArticleInput struct {
    Title string `json:"title"`
    Body  string `json:"body"`
}

func (i *CreateArticleInput) Validate() error {
    v := app.NewValidator()
    v.Field("title", i.Title).Required().Max(255)
    v.Field("body", i.Body).Required()
    return v.Validate()
}
```

```go
// internal/handlers/article_handler.go
func ArticleStore(c app.Context) error {
    input, err := c.Input(&CreateArticleInput{}).(*CreateArticleInput)
    if err != nil {
        return c.UnprocessableEntity(err)
    }
    article := &models.Article{
        Title: input.Title,
        Body:  input.Body,
    }
    Article().Create(c.RequestContext(), article)
    return inertia.Redirect(c, "/articles")
}
```

Input structs define validation rules inline. The handler binds, validates, persists, and redirects — all in a few lines of type-safe Go.

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
{{< tab name="Queues" >}}

```go
type SendEmail struct {
    Email string `json:"email"`
    UserID int   `json:"user_id"`
}

func (j *SendEmail) Handle(ctx context.Context) error {
    fmt.Printf("Sending email to %s\n", j.Email)
    return nil
}

func init() {
    queue.RegisterJob("*jobs.SendEmail", func() queue.Job {
        return &SendEmail{}
    })
}
```

```go
// Dispatched from any handler
queue.Dispatch(ctx, &SendEmail{
    Email: "user@test.com", UserID: 42,
})

// Workers claim and process jobs
// $ lemmego run tasker:work --queue=default --workers=3
```

Monitor jobs in real-time at `http://localhost:8080/tasker/` with the built-in web dashboard.

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

{{< /tab >}}
{{< /tabs >}}

## Features

- **Full-featured HTTP layer** — Param-based routing, route grouping, flexible middleware, input validation, typed errors
- **Type-safe database layer** — GPA provides compile-time type safety across SQL, NoSQL, and KV stores with generic `Repository[T]`
- **Plugin architecture** — Extend the framework through providers without modifying core code
- **Multiple frontends** — Go Templates, Templ, or Inertia.js with React/Vue
- **File storage** — Unified abstraction for local, S3, and GCS
- **CLI tools** — Project scaffolding, code generators, migration management
- **Background jobs** — Distributed queue system with web dashboard

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
| **Queue** | Distributed background job system with web dashboard |
| **CLI** | Project scaffolding and code generation |
| **Inertia** | Server-side adapter for Inertia.js SPAs |
| **Templ** | Bridge for type-safe Go templates |
| **Auth** | Session + JWT authentication with middleware |
| **Migrations** | Bidirectional database schema management |
| **File System** | Cloud-agnostic storage (local, S3, GCS) |
