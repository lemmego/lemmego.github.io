# Writing for these docs

The site is read by someone trying to get something working. Every page is
judged on one question: can a reader who arrives cold do the thing the page is
about?

## The reader

Assume a competent Go developer who has not used this framework. They arrived
from a search engine or the sidebar, they have a task in mind, and they will
leave the moment the page starts talking about itself instead of about their
task.

They are not interested in the framework's history, the author's reasoning, or
what changed between two releases.

## Voice

Write to the reader, in the present tense, in the second person. The subject
of most sentences is **you** — not "the application", "a caller", "somebody"
or "the developer".

- **Say what to do, then show it.** A sentence of context, then code.
- **Lead with the common case.** The edge case goes after it, or in a callout.
- **One idea per heading.** A heading is a task or a thing, not an argument.

### Speak to the person reading

Anticipate the situation they are in and name it. Reassure them where the
framework has already done the work. These are the moves:

| Instead of | Write |
|---|---|
| "A caller that needs a strict rate must…" | "If you need a strict rate, you can…" |
| "The application resolves the user through…" | "Your handler receives the user, resolved through…" |
| "A session is created on first write." | "Don't worry about creating a session — one is created for you on the first write." |
| "It is possible to override the directory." | "Sometimes you'll want the templates somewhere else. Override it with…" |
| "Two copies of a price eventually disagree." | "Keep one copy of the price. Two will disagree eventually, and then…" |
| "Configuration is read from `internal/configs/`." | "You'll find your configuration in `internal/configs/`." |

Use "we" only for walking through something together — "let's add a route" —
never for the framework's authors or the project.

### Define a term the first time you use it

Assume the reader has never used a web framework. A page that opens "Routes
are defined in `internal/routes/` using the application's `Router` interface"
teaches only somebody who already knows what a route is.

So before the syntax, say what the thing **is**, in terms the reader already
has, and why it exists at all:

> When someone visits your site, their browser sends your application a short
> message: a method, like `GET`, and a path, like `/users/42`. From those two
> things your application has to pick the Go function that answers. A route is
> one line in that decision — `GET` + `/hello` → run this function.

Then the code. Keep the definition concrete: a browser sending bytes, a row in
a table, a file on disk. Avoid defining one unfamiliar word with three others.

Terms used across many pages live in
[the glossary](content/docs/glossary.md) and are linked on first use rather
than redefined. A term a page is *about* is defined on that page.

### Headings are labels, not opinions

A reader scans headings to find their task. A heading that states a position
cannot be scanned for.

| Instead of | Write |
|---|---|
| `## Read this before you deploy it` | `## Scope and limits` |
| `## Why the route is in the key` | `## How keys are built` |
| `## A cache failure allows the request` | `## Behaviour when the cache is down` |
| `## Deliberate omissions` | `## Limitations` |
| `## Both transports, and why that is not indulgence` | `## Choosing a transport` |
| `## The problem it solves` | `## When to use it` |
| `## Scale, honestly` | `## Capacity planning` |

## What does not belong on a page

**Version archaeology.** No "fixed in v0.1.24", no "before v0.5.5 this did
something else", no "available since v0.6.5". Document what the current
version does. A reader on an old version reads that version's docs or the
release notes.

The one exception is a breaking change a reader must act on, and that goes in
[Upgrade notes](content/docs/appendix/upgrading.md) with the version in the
heading — one page, so it can be read once and skipped forever.

**Development history.** No "this was not the case until", no "the gap was
expensive", no "found in an application where". The reader does not need to
know how a behaviour came to be in order to rely on it.

**Self-defence.** No "that is not a bug", "this is a decision, not an
oversight", "honestly", "deliberately". If a limit needs explaining, explain
the limit and what to do about it:

> A fixed window allows up to twice the limit across a window boundary. If you
> need a strict rate, put the limiter behind something that enforces one.

not:

> That is not a bug to be fixed later; it is the honest consequence of where
> the counters live.

**War stories.** A concrete failure is useful as a worked example, with the
details that let a reader recognise it in their own code. It is not useful as
an anecdote about another codebase.

## What does belong

- **A runnable example.** Imports included where they are not obvious.
- **Defaults, stated.** A reader needs to know what happens if they configure
  nothing.
- **Failure behaviour.** What happens when the dependency is down, the input
  is wrong, the table is missing.
- **Limits.** Said plainly, with the alternative if there is one.
- **Links forward and back.** Every page names what to read next.

## Page shape

Pages follow this order. Omit what does not apply; do not reorder.

1. **One paragraph** saying what the thing is and when you would reach for it.
2. **Install / register**, if anything is needed.
3. **The common case** — the smallest useful working example.
4. **The options**, grouped by task.
5. **Behaviour and limits** — defaults, failure modes, what it does not do.
6. **Next steps** — two or three links.

Do not open a page with `## Overview`. The first paragraph is the overview and
needs no heading; a heading there just pushes the content down.

## Continuity

The docs are an ordered path, not a pile. Every page carries `weight`, `prev`
and `next` in its front matter, and they are generated — see
[`scripts/spine.py`](scripts/spine.py), which owns the order and rewrites the
front matter of every page.

Add a page by adding it to the list in that script and running it. Never hand
-edit `weight`, `prev` or `next`; the script will overwrite it.

Sections are spaced ten apart so a new page never needs a fractional weight.
