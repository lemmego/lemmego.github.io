# lemmego.org

The source of the [Lemmego documentation site](https://lemmego.org), built with
[Hugo](https://gohugo.io) and the [Hextra](https://github.com/imfing/hextra)
theme, and published to GitHub Pages by
[`.github/workflows/pages.yaml`](./.github/workflows/pages.yaml) on every push
to `main`.

## Before you write anything

Read **[STYLE.md](./STYLE.md)**. It is the voice contract for every page: who
the reader is, how to address them, how to define a term the first time it
appears, and what does not belong on a page — version archaeology, development
history, war stories.

## Local development

You need [Hugo](https://gohugo.io/getting-started/installing/) (extended),
[Go](https://go.dev/doc/install) and Git.

```shell
hugo mod tidy
hugo server --disableFastRender -p 1313
```

Then open <http://localhost:1313>.

## Adding a page

The sidebar order, and the `prev`/`next` links at the foot of every page, are
**generated**. Do not hand-edit `weight`, `prev` or `next` in a page's front
matter — the script overwrites them.

1. Write the page under `content/docs/`.
2. Add it to the `ORDER` list in [`scripts/spine.py`](./scripts/spine.py), in
   the position a reader should meet it.
3. Run the script:

```shell
python3 scripts/spine.py          # rewrite the front matter
python3 scripts/spine.py --check  # what CI runs
```

`--check` fails when a page exists on disk but not in `ORDER`, or the other
way round, so a new page cannot quietly fall out of the reading order. The
build runs it before Hugo, so a forgotten entry fails the deploy rather than
shipping a dangling page.

Sections are spaced ten apart, so a new page never needs a fractional weight.

## Writing code samples

**Compile every Go sample against the module it documents** rather than
writing it from memory. `go doc` on the pinned version is the fastest check,
and the MCP server's `module-api` tool answers the same question from inside
an editor. A sample that calls a function which does not exist reads exactly
like one that works.

Terms used across many pages belong in
[the glossary](./content/docs/glossary.md), linked on first use. A term a page
is *about* is defined on that page.

A breaking change a reader has to act on goes in
[Upgrade notes](./content/docs/appendix/upgrading.md), with the version in the
heading — one page, so it can be read once and skipped forever. Nowhere else.

## Updating the theme

```shell
hugo mod get -u
hugo mod tidy
```

## License

[MIT](./LICENSE)
