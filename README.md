# SARFAESI Advocates website

- Build: `pip install markdown && python build.py` -> `dist/`
- Cloudflare (Git integration): build command `pip install markdown && python build.py`, output directory `dist`
- Posts: `posts/YYYY-MM-DD-slug.md`. Future-dated posts stay hidden until their date.
- Practice-area pages live in `service_pages.py` and are built to the site root (for example `/section-17-drt-application`).
- URLs: the host serves clean URLs (no `.html`). The build writes canonicals, the sitemap, schema, the RSS feed and internal links in that form.
- Daily blog: a scheduled Claude task adds one post at 08:45 IST, following `CLAUDE.md` and the backlog in `TOPICS.md`. The push triggers a Cloudflare build, and posts dated today go live.
- Quality gate: for posts dated 2026-11-09 or later, `build.py` checks title and description length, word count, headings, allowed case citations, promotional wording and internal links. Errors stop a local build. On Cloudflare's own build they are shown as warnings so a lint problem can never stop the site deploying.
- Each post links automatically to its practice-area page(s) and to related articles, using keywords in the file name (see `SERVICE_KEYS` in `service_pages.py`). A `## Frequently asked questions` section with `###` questions becomes FAQ structured data.
- Testing: `BUILD_DATE=YYYY-MM-DD python build.py` builds as if it were that date.
