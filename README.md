# SARFAESI Advocates website

- Build: `pip install markdown && python build.py` -> `dist/`
- Cloudflare Pages (Git integration): build command `pip install markdown && python build.py`, output directory `dist`
- Daily: GitHub Action calls the Pages deploy hook at 09:00 IST (secret CF_DEPLOY_HOOK). A daily Claude task adds one post (see CLAUDE.md, TOPICS.md).
- Posts: `posts/YYYY-MM-DD-slug.md`. Future-dated posts stay hidden until their date.
