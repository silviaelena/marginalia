#!/usr/bin/env python3
"""Lesson helper.

  python3 scripts/lesson.py new 002 slug "Question?"   create a lesson from the template
  python3 scripts/lesson.py index                      rewrite the lesson table in README.md
  python3 scripts/lesson.py index --check              fail if the table is out of date
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LESSONS = ROOT / "lessons"
README = ROOT / "README.md"
START, END = "<!-- lessons:start -->", "<!-- lessons:end -->"

LESSON_TEMPLATE = """---
layout: lesson
number: "{number}"
title: {title}
summary: TODO one sentence.
date: {today}
last_verified: {today}
tags: []
takeaways:
  - TODO three or four one-line points, shown as "In short".
---

# {number} · {title}

![Artwork: to be chosen, see art/CREDIT.md](art/art.jpg)

> *Epigraph.*
>
> Author, *Work*

## The question

## The lesson

## The demo

<figure class="demo">
  <iframe src="demo/" title="Demo: TODO" loading="lazy"></iframe>
  <figcaption><a href="demo/">Open the demo full screen</a>, or run it locally:
  <code>cd demo &amp;&amp; python3 -m http.server 8000</code></figcaption>
</figure>

What to try:

1.

## Under AI

<div class="card now" markdown="1">

### Now (facts, with sources)

</div>

<div class="card next" markdown="1">

### Next (my opinion)

</div>

## Sources

**Art:** see [art/CREDIT.md](art/CREDIT.md).
"""

DEMO_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noai, noimageai">
<title>{number} · {title}</title>
</head>
<body>
<main>
  <h1>{title}</h1>
</main>
<script>
</script>
</body>
</html>
"""

CREDIT_TEMPLATE = """# Art credit

| Field       | Value |
| ----------- | ----- |
| Title       |       |
| Artist      |       |
| Date        |       |
| Institution |       |
| Source URL  |       |
| Licence     | CC0 / public domain |
"""


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        sys.exit(f"{path}: missing front-matter")
    data = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith(" "):
            data[key.strip()] = value.strip().strip('"')
    return data


def lessons():
    for folder in sorted(p for p in LESSONS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        yield folder, front_matter(folder / "README.md")


def table():
    rows = ["| #   | Question | Tags | Demo |", "| --- | -------- | ---- | ---- |"]
    for folder, fm in lessons():
        link = f"lessons/{folder.name}/"
        tags = ", ".join(t.strip() for t in fm.get("tags", "").strip("[]").split(",") if t.strip())
        rows.append(f"| {fm['number']} | [{fm['title']}]({link}) | {tags} | [demo]({link}demo/) |")
    return "\n".join(rows)


def index(check):
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit(f"README.md: markers {START} / {END} not found")
    updated = pattern.sub(f"{START}\n{table()}\n{END}", text)
    if check:
        if updated != text:
            sys.exit("README.md lesson table is out of date: run python3 scripts/lesson.py index")
        print("README.md lesson table is up to date")
    elif updated != text:
        README.write_text(updated, encoding="utf-8")
        print("README.md lesson table updated")


def new(number, slug, title):
    if not re.fullmatch(r"\d{3}", number) or not re.fullmatch(r"[a-z0-9-]+", slug):
        sys.exit("usage: lesson.py new 002 kebab-case-slug \"Question?\"")
    folder = LESSONS / f"{number}-{slug}"
    if folder.exists() or any(p.name.startswith(number + "-") for p in LESSONS.iterdir()):
        sys.exit(f"lesson {number} already exists")
    values = {"number": number, "title": title, "today": datetime.date.today().isoformat()}
    (folder / "demo").mkdir(parents=True)
    (folder / "art").mkdir()
    (folder / "README.md").write_text(LESSON_TEMPLATE.format(**values), encoding="utf-8")
    (folder / "demo" / "index.html").write_text(DEMO_TEMPLATE.format(**values), encoding="utf-8")
    (folder / "art" / "CREDIT.md").write_text(CREDIT_TEMPLATE, encoding="utf-8")
    print(f"created {folder.relative_to(ROOT)}")
    index(check=False)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["new"] and len(args) == 4:
        new(*args[1:])
    elif args[:1] == ["index"]:
        index(check="--check" in args)
    else:
        sys.exit(__doc__)
