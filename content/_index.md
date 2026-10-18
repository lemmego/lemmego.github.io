---
title: Lemmego
layout: home
toc: false

headline: The Go framework that ships batteries included
subtitle: >-
  Routing, an ORM, migrations, auth, queues, mail, realtime and a frontend —
  wired together, type-safe, and yours to replace one piece at a time.
install: go install github.com/lemmego/cli/cmd/lemmego@latest
actions:
  - text: Get started
    link: /docs/quick-start
    primary: true
  - text: Read the docs
    link: /docs/prologue
  - text: GitHub
    link: https://github.com/lemmego
---

{{< hextra/feature-grid cols="3" >}}
  {{< hextra/feature-card
    icon="server"
    title="A real HTTP layer"
    subtitle="Pattern routing, groups, handler-chained middleware, typed errors that negotiate JSON or HTML, and validation that reads like a sentence."
  >}}
  {{< hextra/feature-card
    icon="database"
    title="An ORM, or yours"
    subtitle="Generic queries over database/sql — no casting, no interface{}. Prefer GORM, Bun, Mongo or Redis? Swap the GPA provider and keep the same shape."
  >}}
  {{< hextra/feature-card
    icon="table"
    title="Migrations that travel"
    subtitle="One declaration renders per dialect. PostgreSQL, MySQL and SQLite each get the right unsigned integer, timestamp and index form."
  >}}
  {{< hextra/feature-card
    icon="lightning-bolt"
    title="Background work"
    subtitle="A queue over a cron scheduler, with a dashboard that stays closed until you name who may retry and cancel jobs."
  >}}
  {{< hextra/feature-card
    icon="desktop-computer"
    title="Pick your frontend"
    subtitle="Inertia with React or Vue and server-side rendering, type-safe Templ components, or plain Go templates."
  >}}
  {{< hextra/feature-card
    icon="puzzle"
    title="Everything is a provider"
    subtitle="Each capability is its own module behind an interface. Add one, replace one, or write your own against the same seam."
  >}}
{{< /hextra/feature-grid >}}

## What it looks like

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
        &logger.Provider{},
        &session.Provider{},
        &ormconnector.Provider{},
        &inertia.Provider{},
        &queue.Provider{DashboardAuth: mayUseTheDashboard},
        &auth.Provider{Opts: &auth.Opts{UserLoader: loadUser}},
    }
}
```

Two of those take a rule you own. `UserLoader` turns the id a credential
carries into your user; `DashboardAuth` decides who may retry and cancel
jobs. The scaffold writes both.

{{< /tab >}}
{{< tab name="Routing" >}}

```go
// internal/routes/web.go
func WebRoutes(a app.App) {
    r := a.Router()

    r.Get("/articles", handlers.ArticleIndex)
    r.Get("/articles/{id}", handlers.ArticleShow)

    admin := r.Group("/admin")
    admin.UseBefore(auth.Protected)
    admin.Get("/articles/new", handlers.ArticleCreate)
    admin.Post("/articles", handlers.ArticleStore)
}
```

Middleware on a route is an ordinary handler — `auth.Protected` is
`func(app.Context) error`, like the one that answers. A `{id}` segment is read
with `c.Param("id")`.

{{< /tab >}}
{{< tab name="Handler" >}}

```go
// internal/inputs/article_input.go
type CreateArticleInput struct {
    ctx   app.Context
    Title string `json:"title" form:"title"`
    Body  string `json:"body"  form:"body"`
}

func NewCreateArticleInput(c app.Context) (*CreateArticleInput, error) {
    input := &CreateArticleInput{ctx: c}
    if err := c.ParseInput(input); err != nil {
        return nil, err
    }
    return input, input.Validate()
}

func (i *CreateArticleInput) Validate() error {
    v := i.ctx.Validator()
    v.Field("title", i.Title).Required().Max(255)
    v.Field("body", i.Body).Required()
    return v.Validate()
}
```

```go
// internal/handlers/article_handler.go
func ArticleStore(c app.Context) error {
    input, err := inputs.NewCreateArticleInput(c)
    if err != nil {
        return err
    }

    article := &models.Article{Title: input.Title, Body: input.Body}
    if _, err := ormconnector.Get(c.App()).
        Model[models.Article]().
        Create(c.RequestContext(), article); err != nil {
        return err
    }

    inertia.Redirect(c, "/articles")
    return nil
}
```

The decode and the validation live together, beside the input type, so a
handler gets one call and one error.

{{< /tab >}}
{{< tab name="Migrations" >}}

```go
// internal/migrations/20250706000001_create_articles_table.go
func mig_up(tx *sql.Tx) error {
    schema := migration.Create("articles", func(t *migration.Table) {
        t.BigIncrements("id").Primary()
        t.UnsignedBigInt("author_id")
        t.String("title", 255)
        t.Text("body").Default("")
        t.String("status", 16).Default("draft")
        t.TimestampTz("created_at", 0).Default(migration.Expr("now()"))
        t.TimestampTz("deleted_at", 0).Nullable()

        t.Foreign("author_id").References("id").On("users").OnDelete("CASCADE")
        t.Check("articles_status_valid", "status IN ('draft','published')")
        t.Index("status", "created_at").Name("articles_feed_idx")
    }).Build()

    _, err := tx.Exec(schema)
    return err
}
```

The same declaration becomes `BIGINT UNSIGNED` on MySQL and `BIGINT` on
PostgreSQL, an inline `INDEX` clause on one and a `CREATE INDEX` on the
others. Run it with `lemmego run migrate up`.

{{< /tab >}}
{{< tab name="Persistence" >}}

```go
// internal/models/article.go
type Article struct {
    ID        uint       `orm:"primaryKey;autoIncrement"`
    Title     string
    Status    string
    AuthorID  uint
    Author    *User      `orm:"belongsTo:AuthorID"`
    Comments  []Comment  `orm:"hasMany:ArticleID"`
    CreatedAt time.Time
    UpdatedAt time.Time
    DeletedAt *time.Time
}

// internal/handlers/article_handler.go
func ArticleIndex(c app.Context) error {
    db := ormconnector.Get(c.App())

    articles, err := db.Model[models.Article]().
        Where(orm.Eq("status", "published")).
        With("Author", "Comments").
        OrderBy(orm.Desc("created_at")).
        Limit(20).
        All(c.RequestContext())
    if err != nil {
        return err
    }
    return c.JSON(app.M{"articles": articles})
}
```

`db.Model[Article]()` returns `[]Article` — generic methods on a concrete
type, so there is nothing to cast. `With` eager-loads at one query per
relation level, and a nullable `DeletedAt` opts the model into soft deletes.

{{< /tab >}}
{{< tab name="Queues" >}}

```go
// internal/jobs/send_email.go
type SendEmail struct {
    Email  string `json:"email"`
    UserID int    `json:"user_id"`
}

func (j *SendEmail) Handle(ctx context.Context) error {
    return mail.Send(ctx, welcome(j.Email))
}

func init() {
    queue.RegisterJob("*jobs.SendEmail", func() tasker.Job { return &SendEmail{} })
}
```

```go
// from any handler
if _, err := queue.Dispatch(c.RequestContext(), &jobs.SendEmail{
    Email: user.Email, UserID: user.ID,
}); err != nil {
    return err
}
```

Workers claim jobs with `lemmego run tasker:work`, and the scheduler runs as
one process with `lemmego run tasker:schedule`.

{{< /tab >}}
{{< /tabs >}}

## Start here

{{< cards >}}
  {{< card link="docs/installation" title="Installation" icon="terminal" subtitle="Install the CLI" >}}
  {{< card link="docs/quick-start" title="Quick Start" icon="fire" subtitle="A running project in minutes" >}}
  {{< card link="docs/prologue" title="Prologue" icon="book-open" subtitle="The framework from the ground up" >}}
{{< /cards >}}

## The modules

Each is its own Go module and its own repository. A project takes the ones it
needs and nothing else.

| | |
|---|---|
| **Core** | [`api`](/docs/http/) routing, middleware, DI, sessions, config, validation · [`cli`](/docs/cli/) scaffolding and generators · [`log`](/docs/logging) rotating files and a terminal-aware console |
| **Data** | [`orm`](/docs/orm/) generic SQL persistence · [`gpa`](/docs/database/) the multi-provider abstraction · [`migration`](/docs/migrations/) dialect-aware schema evolution · [`search`](/docs/search/) full-text over `tsvector` |
| **Identity** | [`auth`](/docs/security/authentication) credentials, sessions, JWT and social sign-in · [`authz`](/docs/authz/) policies, ownership and a route gate · [`oauth2`](/docs/oauth2/) an authorization server |
| **Delivery** | [`mail`](/docs/mail/) SMTP with queued sending · [`notify`](/docs/notifications/) one notification over many channels · [`broadcast`](/docs/broadcast/) SSE and WebSocket behind one contract |
| **Frontend** | [`inertia`](/docs/frontend/inertia) React or Vue with SSR · [`templ`](/docs/frontend/templ) type-safe Go components · [`seo`](/docs/seo/) meta, JSON-LD, sitemaps and slugs |
| **Infrastructure** | [`queue`](/docs/queue) background jobs and a cron scheduler · [`cache`](/docs/cache/) memory, file and redis stores · [`fsys`](/docs/filesystem/) local, S3 and GCS · [`media`](/docs/media/) image ingest with no CGO · [`ratelimit`](/docs/ratelimit/) middleware over the cache |
| **Commerce** | [`pay`](/docs/payments/) one hosted checkout and one webhook |
| **Testing** | [`apptest`](/docs/testing/) boots the real application against a scratch database |
