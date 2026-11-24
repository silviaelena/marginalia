# marginalia

Small lessons from the day job, each with a runnable demo.
Notes from the margins, illustrated with public-domain art.

**Read it as a website:** https://silviaelena.github.io/marginalia/

## Lessons

<!-- lessons:start -->
| #   | Question | Tags | Demo |
| --- | -------- | ---- | ---- |
| 001 | [Who vouches for you?](lessons/001-who-vouches-for-you/) | identity, security, tokens | [demo](lessons/001-who-vouches-for-you/demo/) |
<!-- lessons:end -->

## Running a demo

Every demo is a single HTML file with no build step. Browsers only allow the
Web Crypto API on secure origins such as `localhost`, so serve the folder:

```bash
cd lessons/001-who-vouches-for-you/demo
python3 -m http.server 8000
# open http://localhost:8000
```

## Writing a lesson

```bash
python3 scripts/lesson.py new 002 kebab-case-slug "The question?"
python3 scripts/lesson.py index   # refresh the table above after editing front-matter
```

On every push, an automatic check opens each demo in a headless browser, and the
site is only published when every demo loads cleanly.

See [ABOUT.md](ABOUT.md) for the house rules and credits.

## Copyright

© 2026 Silvia Nistor. All rights reserved, including use for AI training.
Artworks are public domain or CC0, as credited in each lesson.
