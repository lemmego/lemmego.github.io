#!/usr/bin/env python3
"""Own the documentation's reading order.

The sidebar, the prev/next footer links and the order a reader meets topics in
are all one decision. Keeping that decision in ninety front-matter blocks is
how it drifted: duplicate weights, fractional weights wedged in to avoid
renumbering, chains that dead-ended mid-section, and a prev pointing at a page
that does not exist.

So ORDER below is the single source of truth. Run this after adding a page:

    python3 scripts/spine.py          # rewrite front matter
    python3 scripts/spine.py --check  # verify, touch nothing (for CI)

Sections are spaced ten apart so inserting a page never needs a fraction.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "content" / "docs"

# (section label, [page paths in reading order]). The label is a comment for
# whoever edits this list; it is not emitted anywhere.
ORDER: list[tuple[str, list[str]]] = [
    ("Getting started", [
        "prologue.md",
        "installation/_index.md",
        "quick-start/_index.md",
        "project-structure.md",
        "configuration.md",
    ]),
    ("The HTTP layer", [
        "http/_index.md",
        "http/routing.md",
        "http/middleware.md",
        "http/request-handling.md",
        "http/response-handling.md",
        "http/error-handling.md",
        "http/context.md",
    ]),
    ("Frontend", [
        "frontend/_index.md",
        "frontend/go-templates.md",
        "frontend/templ.md",
        "frontend/inertia.md",
        "frontend/vite.md",
    ]),
    ("The ORM", [
        "orm/_index.md",
        "orm/queries.md",
        "orm/writes.md",
        "orm/relationships.md",
        "orm/field-descriptors.md",
        "orm/gpa-adapter.md",
    ]),
    ("GPA and providers", [
        "database/_index.md",
        "database/provider-registry.md",
        "database/connection-seam.md",
        "database/generic-repository.md",
        "database/query-system.md",
        "database/entity-hooks.md",
        "database/transactions.md",
        "database/raw-sql-and-ddl.md",
        "database/providers/gorm.md",
        "database/providers/bun.md",
        "database/providers/mongodb.md",
        "database/providers/redis.md",
        "database/gormconnector.md",
        "database/bunconnector.md",
    ]),
    ("Migrations", [
        "migrations/_index.md",
        "migrations/schema-builder.md",
        "migrations/column-types.md",
        "migrations/writing-migrations.md",
        "migrations/running-migrations.md",
    ]),
    ("How the framework fits together", [
        "core-concepts/_index.md",
        "core-concepts/application-bootstrap.md",
        "core-concepts/service-container.md",
        "core-concepts/provider-plugin-system.md",
        "core-concepts/dependency-injection.md",
        "core-concepts/event-system.md",
        "logging.md",
    ]),
    ("Security", [
        "security/_index.md",
        "security/authentication.md",
        "security/current-user.md",
        "security/csrf.md",
        "security/encryption.md",
        "session.md",
        "authz/_index.md",
        "ratelimit/_index.md",
    ]),
    ("Modules", [
        "cache/_index.md",
        "cache/drivers.md",
        "cache/typed-access.md",
        "cache/locks.md",
        "cache/tags.md",
        "cache/events.md",
        "queue.md",
        "mail/_index.md",
        "notifications/_index.md",
        "broadcast/_index.md",
        "filesystem/_index.md",
        "media/_index.md",
        "search/_index.md",
        "seo/_index.md",
        "payments/_index.md",
    ]),
    ("OAuth2 server", [
        "oauth2/_index.md",
        "oauth2/installation.md",
        "oauth2/configuration.md",
        "oauth2/clients.md",
        "oauth2/grants.md",
        "oauth2/protecting-routes.md",
        "oauth2/consent-screen.md",
        "oauth2/tokens-and-keys.md",
    ]),
    ("Tooling and shipping", [
        "cli/_index.md",
        "testing/_index.md",
        "deployment/_index.md",
        "mcp.md",
        "prompting.md",
    ]),
    ("Reference", [
        "architecture/_index.md",
        "appendix/_index.md",
        "appendix/upgrading.md",
        "appendix/faq.md",
    ]),
]

SECTION_GAP = 10


def url_for(rel: str) -> str:
    """The route Hugo serves a content path at."""
    if rel.endswith("/_index.md"):
        return "docs/" + rel[: -len("/_index.md")] + "/"
    return "docs/" + rel[:-3]


def planned() -> list[tuple[str, int, str, str]]:
    """(path, weight, prev, next) for every page, in reading order."""
    flat: list[str] = []
    weights: dict[str, int] = {}
    weight = SECTION_GAP
    for _, pages in ORDER:
        for i, rel in enumerate(pages):
            flat.append(rel)
            weights[rel] = weight + i
        # Round up to the next multiple of SECTION_GAP, leaving room inside.
        weight = ((weight + len(pages)) // SECTION_GAP + 1) * SECTION_GAP

    out = []
    for i, rel in enumerate(flat):
        prev = url_for(flat[i - 1]) if i else "/docs"
        nxt = url_for(flat[i + 1]) if i + 1 < len(flat) else ""
        out.append((rel, weights[rel], prev, nxt))
    return out


FIELDS = ("weight", "prev", "next")


def rewrite(text: str, weight: int, prev: str, nxt: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SystemExit("page has no front matter")
    fm, body = m.group(1), text[m.end():]

    # Drop the fields we own, and the sidebar block we re-add uniformly.
    lines = [l for l in fm.splitlines()
             if not re.match(r"^(weight|prev|next):", l)]
    kept, skip = [], False
    for l in lines:
        if re.match(r"^sidebar:\s*$", l):
            skip = True
            continue
        if skip:
            if re.match(r"^\s+\S", l):
                continue
            skip = False
        kept.append(l)

    ordered = [l for l in kept if re.match(r"^(title|type):", l)]
    rest = [l for l in kept if l not in ordered]

    fm_out = ordered + [f"prev: {prev}"]
    if nxt:
        fm_out.append(f"next: {nxt}")
    fm_out += [f"weight: {weight}", "sidebar:", "  open: true"] + rest
    return "---\n" + "\n".join(fm_out) + "\n---\n" + body


def main() -> int:
    check = "--check" in sys.argv
    plan = planned()

    on_disk = {
        str(p.relative_to(DOCS))
        for p in DOCS.rglob("*.md")
        if p.name != "_index.md" or p.parent != DOCS
    }
    listed = {rel for rel, _, _, _ in plan}

    problems = []
    for rel in sorted(listed - on_disk):
        problems.append(f"listed in ORDER but missing on disk: {rel}")
    for rel in sorted(on_disk - listed):
        problems.append(f"on disk but absent from ORDER: {rel}")
    if problems:
        print("\n".join(problems))
        return 1

    changed = 0
    for rel, weight, prev, nxt in plan:
        path = DOCS / rel
        before = path.read_text(encoding="utf-8")
        after = rewrite(before, weight, prev, nxt)
        if before != after:
            changed += 1
            if not check:
                path.write_text(after, encoding="utf-8")
            else:
                print(f"would rewrite {rel}")

    print(f"{len(plan)} pages, {changed} {'to change' if check else 'rewritten'}")
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
