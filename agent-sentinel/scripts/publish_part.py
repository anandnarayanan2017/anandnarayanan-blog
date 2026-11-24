#!/usr/bin/env python3
"""Publish one drafted Agent Sentinel part, on its release day.

    python agent-sentinel/scripts/publish_part.py 3            # from the repository root
    python agent-sentinel/scripts/publish_part.py 3 --dry-run  # show what would change

The site shows a part as soon as it is deployed and does not hold back future
dates, so run this on the day itself. For part N it:

  1. checks parts 1..N-1 are published, part N is drafted and not yet
     published, part N isn't dated after today and the hero image exists,
     then dates part N today in series.json if it has no date yet;
  2. moves the write-up and LinkedIn post out of docs/blog/drafts/ (git mv)
     and removes the leading DRAFT comment;
  3. fixes relative links for the new folder depth, and turns links to parts
     that are not published yet into plain text;
  4. turns "Next: Part N — <title>." in part N-1 into a link;
  5. adds part N's rows to docs/blog/TRACEABILITY.md and to the README's
     "Try each part locally" table, from drafts/traceability-rows.json and
     drafts/try-rows.json;
  6. runs scripts/check_links.py.

It never commits or pushes. Review the diff, run `npm run build` and the
folder's tests, then open the pull request.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

FOLDER = Path(__file__).resolve().parents[1]  # agent-sentinel/
BLOG = FOLDER / "docs" / "blog"
DRAFTS = BLOG / "drafts"
LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")
ANY_LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)")
TRY_HEADING = "## Try each part locally"


def fail(msg: str) -> None:
    sys.exit(f"publish_part: {msg}")


def one(pattern: str, where: Path) -> Path | None:
    hits = sorted(where.glob(pattern))
    if len(hits) > 1:
        fail(f"more than one match for {pattern} in {where}")
    return hits[0] if hits else None


def published(n: int) -> Path | None:
    return one(f"{n:02d}-*.md", BLOG / "technical-details")


def shallower(text: str) -> str:
    """One folder up (drafts/X/ -> X/): every link that climbs two or more levels loses one."""

    def fix(m: re.Match[str]) -> str:
        bang, label, url = m.groups()
        if url.startswith("../../"):
            url = url[3:]
        return f"{bang}[{label}]({url})"

    return ANY_LINK.sub(fix, text)


def unlink_unpublished(text: str, here: Path) -> str:
    """Links to a part's write-up or post that does not exist yet become plain text."""

    def fix(m: re.Match[str]) -> str:
        label, url = m.groups()
        path = url.split("#", 1)[0]
        if not re.search(r"(^|/)\d{2}-[^/]*\.md$", path):
            return m.group(0)
        return m.group(0) if (here.parent / path).resolve().exists() else label

    return LINK.sub(fix, text)


def strip_draft_comment(text: str) -> str:
    return re.sub(r"\n<!--\s*\nDRAFT[\s\S]*?-->\n", "\n", text, count=1)


def insert_row(text: str, row: str, n: int, after_heading: str | None = None) -> str:
    """Put `row` after the table row for the highest part number below n."""
    if f"\n| {n} |" in text:
        fail(f"a row for part {n} is already there")
    lines = text.split("\n")
    start = lines.index(after_heading) if after_heading else 0
    last = None
    for i in range(start, len(lines)):
        m = re.match(r"\| (\d+) \|", lines[i])
        if m and int(m.group(1)) < n:
            last = i
        elif last is not None and not lines[i].startswith("|"):
            break
    if last is None:
        fail(f"no table row for an earlier part to insert part {n} after")
    lines.insert(last + 1, row)
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("part", type=int)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    n, dry = args.part, args.dry_run

    for k in range(1, n):
        if not published(k):
            fail(f"part {k} is not published yet; publish parts in order")
    if published(n):
        fail(f"part {n} is already published")
    draft = one(f"{n:02d}-*.md", DRAFTS / "technical-details")
    post = one(f"{n:02d}-*.md", DRAFTS / "linkedin")
    if not draft or not post:
        fail(f"part {n} needs drafts/technical-details/ and drafts/linkedin/ files")
    if draft.name != post.name:
        fail(f"file names differ: {draft.name} and {post.name}")
    # A part is dated the day it goes live, never ahead of it: the site shows
    # every deployed part, so a future date would claim a release that hasn't
    # happened. The site build refuses one too (scripts/sync-series.mjs).
    today = datetime.now(UTC).date().isoformat()
    series_path = BLOG / "series.json"
    series = json.loads(series_path.read_text(encoding="utf-8"))
    dates = series["dates"]
    if dates.get(str(n), today) > today:
        fail(f'"{n}" is dated {dates[str(n)]} in docs/blog/series.json, after today ({today})')
    hero = BLOG / "images" / f"{draft.stem}-1.png"
    if not hero.exists():
        fail(f"hero image missing: {hero.relative_to(FOLDER)}")
    trace_rows = json.loads((DRAFTS / "traceability-rows.json").read_text())
    try_rows = json.loads((DRAFTS / "try-rows.json").read_text())
    if str(n) not in trace_rows:
        fail(f'no row for "{n}" in drafts/traceability-rows.json')

    date = dates.get(str(n), today)
    print(f"Publishing part {n} ({draft.stem}), dated {date}")
    if dry:
        print("dry run: nothing changed")
        return

    # 1b. Date the part today, if it has no date yet. Edited as text so the
    # rest of series.json keeps its formatting.
    if str(n) not in dates:
        text = series_path.read_text(encoding="utf-8")
        block = re.search(r'("dates": \{)(.*?)(\n  \})', text, re.DOTALL)
        if not block:
            fail('no "dates" block found in docs/blog/series.json')
        entry = f'\n    "{n}": "{today}"'
        body = block.group(2) + ("," if block.group(2).strip() else "") + entry
        series_path.write_text(
            text[: block.start(2)] + body + text[block.end(2) :], encoding="utf-8"
        )

    # 2-3. Move, then fix links for the new depth.
    for src, dest_dir in ((draft, "technical-details"), (post, "linkedin")):
        dest = BLOG / dest_dir / src.name
        subprocess.run(["git", "mv", str(src), str(dest)], check=True)
        text = shallower(strip_draft_comment(dest.read_text(encoding="utf-8")))
        dest.write_text(unlink_unpublished(text, dest), encoding="utf-8")

    # 4. Link "Next: Part n — Title." in the previous part.
    if n > 1:
        prev = published(n - 1)
        assert prev is not None
        text = prev.read_text(encoding="utf-8")
        new = re.sub(
            rf"^Next: (Part {n} — [^\n]+?)\.$",
            lambda m: f"Next: [{m.group(1)}]({draft.name}).",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        if new == text:
            print(f"note: no plain 'Next: Part {n} — ...' line in {prev.name}; check it by hand")
        prev.write_text(new, encoding="utf-8")

    # 5. Tables.
    trace = BLOG / "TRACEABILITY.md"
    trace.write_text(insert_row(trace.read_text(encoding="utf-8"), trace_rows.pop(str(n)), n))
    (DRAFTS / "traceability-rows.json").write_text(
        json.dumps(trace_rows, indent=2, ensure_ascii=False) + "\n"
    )
    if str(n) in try_rows:
        readme = FOLDER / "README.md"
        readme.write_text(
            insert_row(readme.read_text(encoding="utf-8"), try_rows.pop(str(n)), n, TRY_HEADING)
        )
        (DRAFTS / "try-rows.json").write_text(
            json.dumps(try_rows, indent=2, ensure_ascii=False) + "\n"
        )

    # 6. Links.
    subprocess.run([sys.executable, "scripts/check_links.py"], cwd=FOLDER, check=True)
    print(
        f"Done. Next: review `git diff`, run `npm run build`, then open the pull request for part {n}."
    )


if __name__ == "__main__":
    main()
