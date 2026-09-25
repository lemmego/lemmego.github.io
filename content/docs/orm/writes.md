---
title: Writes and Transactions
type: docs
prev: docs/orm/relationships
next: docs/orm/field-descriptors
sidebar:
  open: true
weight: 17.3
---

## Creating and updating

```go
user := &User{Email: "ada@example.com"}
_, err := db.Model[User]().Create(ctx, user)
// user.ID is now populated

_, err = db.Model[User]().CreateBatch(ctx, []*User{a, b, c})

user.Email = "ada@lovelace.example"
_, err = db.Model[User]().Update(ctx, user)
```

A generated key is written back onto the entity after insert, using `RETURNING` where the dialect supports it and `LastInsertId` where it does not.

### Bulk writes

```go
_, err := db.Model[User]().
    Where(orm.Lt("last_seen", cutoff)).
    UpdateAll(ctx, map[string]any{"active": false})

_, err = db.Model[Session]().Where(orm.Lt("expires_at", now)).DeleteAll(ctx)
```

Both **refuse to run without a predicate**, returning `orm.ErrUnsafeMutation`. An unfiltered `UPDATE` is almost always a mistake, so it has to be an explicit opt-in rather than a silent table rewrite.

## Upserts

```go
// Insert, or update the named columns when the row already exists
_, err := db.Model[User]().Upsert(ctx, user, []string{"email"}, "name", "updated_at")

// Insert, or leave the existing row alone
_, err = db.Model[User]().InsertIgnore(ctx, user, "email")
```

With no update columns named, every mapped column except the conflict columns and the generated key is overwritten.

The three databases spell this differently and the dialect hides it: `ON CONFLICT (...) DO UPDATE` on PostgreSQL and SQLite, `ON DUPLICATE KEY UPDATE` on MySQL. Two MySQL differences are worth knowing — it keys the conflict off *any* unique index rather than the columns you name, and it has no `DO NOTHING`, so `InsertIgnore` compiles to the conventional self-assignment no-op.

An upsert does not write a generated key back: the statement may update an existing row rather than insert one, so there is no new key to report.

## Soft deletes

A model is soft-deletable when it has a nullable timestamp named `DeletedAt`, or any nullable timestamp tagged `orm:"softDelete"`:

```go
type Post struct {
    ID        int        `orm:"primaryKey;autoIncrement"`
    Title     string
    DeletedAt *time.Time            // or sql.NullTime
}
```

The column **must** be `*time.Time` or `sql.NullTime`. A bare `time.Time` is rejected at metadata time, because its zero value still writes a real timestamp and `deleted_at IS NULL` would then match no row at all — the failure mode would be an empty table rather than an error.

Reads exclude trashed rows by default, and so do `Count`, `Exists`, `Paginate`, `UpdateAll` and `DeleteAll`:

```go
db.Model[Post]().All(ctx)                 // visible rows only
db.Model[Post]().WithTrashed().All(ctx)   // everything
db.Model[Post]().OnlyTrashed().All(ctx)   // just the trashed

db.Model[Post]().Delete(ctx, &post)       // marks deleted_at
db.Model[Post]().Restore(ctx, &post)      // clears it
db.Model[Post]().ForceDelete(ctx, &post)  // really removes the row
```

`DeleteAll` soft-deletes. `ForceDeleteAll` removes rows, but still honours the default scope — combine it with `WithTrashed()` to purge everything.

Soft-deleted rows are also excluded from [relationships](/docs/orm/relationships), so "deleted" does not depend on how you reach the row.

## Automatic timestamps

Fields named `CreatedAt` and `UpdatedAt` of a time type are maintained automatically, as is any field tagged `autoCreateTime` or `autoUpdateTime`. `CreatedAt` is only filled when unset, so a value you assign yourself — or one a `BeforeCreate` hook sets — survives. `UpdatedAt` is always refreshed on update.

Stamps are taken in **UTC**. A naive column stores no offset, so writing local time and reading it back returns a value shifted by the machine's zone offset.

The type check is deliberate: a model carrying its own `CreatedAt int64` keeps full manual control rather than having the ORM overwrite it.

## Hooks

Implement any of these on a model and the ORM calls them:

```go
func (u *User) BeforeCreate(ctx context.Context) error {
    hashed, err := utils.Bcrypt(u.Password)
    if err != nil {
        return err
    }
    u.Password = hashed
    return nil
}
```

`BeforeCreate`, `AfterCreate`, `BeforeUpdate`, `AfterUpdate`, `BeforeDelete`, `AfterDelete`. The order is:

```
BeforeCreate / BeforeUpdate / BeforeDelete
SQL statement
AfterCreate / AfterUpdate / AfterDelete
transaction commit
AfterCommit callbacks
```

An after-statement hook error is returned to the caller, and rolls back when inside `DB.Transaction`. After-commit callbacks run only once the commit has succeeded and cannot roll it back.

## Transactions

```go
err := db.Transaction(ctx, func(tx *orm.Tx) error {
    if _, err := tx.Model[User]().Create(ctx, user); err != nil {
        return err
    }
    if _, err := tx.Model[Post]().Create(ctx, post); err != nil {
        return err   // rolls back
    }
    return tx.AfterCommit(func(context.Context) error {
        return mailer.Send(user.Email)
    })
})
```

It commits when the callback returns nil, rolls back on error, and recovers from a panic by rolling back before re-panicking.

A transaction is deliberately **not** bound to one entity type, so a single unit of work spans as many models as it needs.

`DB.Begin` (and `DB.BeginTx` for isolation levels) returns a `*Tx` the caller must finish itself, for code that has to hand the handle around.

### Savepoints

```go
err := db.Transaction(ctx, func(tx *orm.Tx) error {
    if _, err := tx.Model[Order]().Create(ctx, order); err != nil {
        return err
    }
    if err := tx.Savepoint(ctx, "after_order"); err != nil {
        return err
    }
    if _, err := tx.Model[Shipment]().Create(ctx, shipment); err != nil {
        return tx.RollbackTo(ctx, "after_order")   // keep the order
    }
    return tx.ReleaseSavepoint(ctx, "after_order")
})
```

Savepoint names cannot be bound as parameters, so they are validated as plain identifiers; anything else returns `orm.ErrInvalidIdentifier`.

## Errors

Driver errors are normalised into typed constraint errors:

```go
if orm.IsUniqueViolation(err) {
    return c.ValidationError(shared.ValidationErrors{"email": {"Already taken"}})
}

var constraint *orm.ConstraintError
if errors.As(err, &constraint) {
    log.Println(constraint.Kind, constraint.Table, constraint.Columns)
}
```

`IsUniqueViolation`, `IsForeignKeyViolation`, `IsNotNullViolation`, `IsCheckViolation`. The original driver error stays reachable through `errors.As`.

Sentinels: `ErrNotFound`, `ErrClosed`, `ErrUnsafeMutation`, `ErrUnsupported`, `ErrNoRowsAffected`, `ErrConstraint`, `ErrInvalidIdentifier`.

## Query logging

```go
db := orm.Open(sqlDB, orm.Postgres(), orm.WithSlogLogger(slog.Default()))

// or handle the events yourself
db = orm.Open(sqlDB, orm.Postgres(), orm.WithLogger(
    func(ctx context.Context, e orm.QueryEvent) {
        if e.Duration > 100*time.Millisecond {
            log.Printf("slow: %s", e)
        }
    }))
```

Every statement is reported, including the extra queries eager loading issues — usually the ones worth seeing. `QueryEvent` carries the SQL, bound arguments, duration, error, and rows affected; the last is `-1` for a read, since rows are counted as they are scanned.

The logger is called synchronously on the query path, so hand off to a channel if the work is expensive. With no logger installed nothing is wrapped.
