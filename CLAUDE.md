# Daily blog task: SARFAESI Advocates (SEO-led)

Each run: write ONE new article and publish it by committing to `main`. The goal is a useful, accurate article that answers one specific question a borrower, guarantor, bidder, occupant or lender would type into Google, and that leads the reader to the matching practice-area page. This goes live with no human review, so accuracy and the build's quality checks matter more than speed.

## 1. Choose the topic
- Open `TOPICS.md` and take the FIRST unused line under "Backlog". Run `ls posts/` and make sure no existing post already covers the same question or primary search phrase. Never repeat a topic, title or primary keyword.
- If fewer than 10 unused topics remain, add 20 new ones in the same format in the same commit (distinct questions, real search phrases, only topics where well-settled points can be stated).

## 2. Create the file
`posts/YYYY-MM-DD-slug.md`.
- Date: the day after the LATEST date already in `posts/` (or today in Asia/Kolkata, whichever is later), so there is exactly one post per day and the queue never runs dry.
- Slug: the date, then the topic's "slug must contain" fragment from `TOPICS.md`, lower case, hyphens only. The fragment makes the build link the post to the right practice-area page automatically.
- Front-matter, exactly these four keys:
  - `title`: 25-65 characters, primary keyword near the start, plain and specific, no clickbait, no year.
  - `date`: YYYY-MM-DD.
  - `category`: one of Basics, Notices, Litigation, Possession, Auctions, Borrower Guidance, Lender Guidance, Case Law, Settlement, Recovery Routes.
  - `description`: one sentence, 70-160 characters, contains the primary keyword, says what the reader will learn. No quotation marks.

## 3. Write the article (500-750 words, plain English)
Structure:
1. An opening paragraph of two or three sentences that answers the question directly and uses the primary keyword.
2. Three to five `##` sections with clear headings (questions or plain topic phrases, using natural keyword variations). Use short paragraphs, and at least one short bullet or numbered list.
3. A closing `## Frequently asked questions` section with two or three `###` questions, each answered in one to three sentences. Phrase the questions the way a reader would ask them.
Do not add a conclusion, call to action or disclaimer. The build adds the call to action, related links, structured data and the disclaimer.

Internal links (required, 2-4 in total, natural anchor text, markdown format):
- At least one link to the topic's practice-area page, written as a clean path, e.g. `[Section 17 applications](/section-17-drt-application)`.
- At least one link to an EARLIER article, e.g. `[title or phrase](/blog/2026-10-02-section-17-application-drt)`. Only link to posts that exist in `posts/` and are dated on or before this post's date.
- Practice-area pages: `/section-13-2-notice-reply`, `/section-17-drt-application`, `/section-18-drat-appeal`, `/section-14-possession-order`, `/sarfaesi-auction-disputes`, `/one-time-settlement-redemption`, `/guarantors-sarfaesi-enforcement`, `/high-court-writ-sarfaesi`, `/lender-arc-enforcement-advisory`, `/sarfaesi-and-rdb-act-recovery-routes`, `/tenants-occupants-sarfaesi-possession`.
- Never use `.html` in links. No external links, images or tables.

Keywords: use the primary phrase in the title, the first paragraph, one heading and the description, and related wording naturally elsewhere. Never repeat a phrase just to rank. Write for the reader first.

## 4. Accuracy rules (non-negotiable)
- State only well-settled points of the SARFAESI Act 2002, the Security Interest (Enforcement) Rules 2002 and the RDB Act 1993 (plus the Contract Act and IBC points already used on the practice pages).
- Cite only these cases, in this exact form, and only for the propositions below:
  - Mardia Chemicals v. UOI (2004) 4 SCC 311 (validity; borrower can object, creditor must reply with reasons)
  - Transcore v. UOI (2008) 1 SCC 125 (SARFAESI and RDB Act operate together)
  - United Bank of India v. Satyawati Tondon (2010) 8 SCC 110 (writs against SARFAESI action discouraged)
  - Mathew Varghese v. M. Amritha Kumar (2014) 5 SCC 610 (Rules 8 and 9 to be complied with)
  - Harshad Govardhan Sondagar v. IARC (2014) 6 SCC 1 (lessees' rights)
- If you are not certain of a section number, period, percentage, amount, form number or case, leave it out or say "check the current text of the Act". For anything that changes over time (monetary thresholds, notified limits, RBI circulars), say "check the current notification" and give no figure.
- Never invent or guess a citation, quotation or statistic. No outcome predictions.
- Bar Council of India rules: information only. No promises of outcomes, no solicitation, no "best" or "top" claims, no comparisons with other lawyers, no client names or case stories, no "contact us" language.

## 5. Build and quality gate
Run `pip install markdown && python build.py`. It must finish without errors. The build checks title and description length, word count, headings, allowed citations, banned promotional wording, and that every internal link exists and is live. If it prints `LINT ERROR`, fix the post and run it again. Do not edit `build.py`, `service_pages.py` or `assets/` to get past a check. If you cannot make the post pass, do not publish it.

## 6. Publish
1. In `TOPICS.md`, move the used line to the "Done" section with the post date.
2. Commit with the message `Add post: <title>` and push to `main`. Cloudflare then deploys.
3. Change nothing else in the repository.
