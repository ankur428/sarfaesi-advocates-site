# SARFAESI Advocates website

- Build: `pip install markdown && python build.py` -> `dist/`
- Cloudflare Pages (Git integration): build command `pip install markdown && python build.py`, output directory `dist`
- Posts: `posts/YYYY-MM-DD-slug.md`. Future-dated posts stay hidden until their date.
- Daily: a scheduled Claude task adds one post at 08:45 IST (see CLAUDE.md, TOPICS.md). The push triggers a Cloudflare build, and posts dated today go live.
