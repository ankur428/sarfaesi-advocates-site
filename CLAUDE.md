# Daily blog task: SARFAESI Advocates

Each run: write ONE new article and publish it by committing to `main`.

1. Look at `posts/` and `TOPICS.md`. Pick the next unused topic. Never repeat a topic or title.
2. Create `posts/YYYY-MM-DD-slug.md` dated TODAY (Asia/Kolkata), with front-matter:
   title, date, category, description (one sentence, under 160 characters).
3. 350-550 words, plain English, headings and short lists, same tone as existing posts.
4. Accuracy rules (this goes live with no human review):
   - State only well-settled points of the SARFAESI Act 2002, the Security Interest (Enforcement) Rules 2002 and the RDB Act 1993.
   - Cite only these cases, and only for the propositions below:
     Mardia Chemicals v. UOI (2004) 4 SCC 311 (validity; borrower can object, creditor must reply with reasons);
     Transcore v. UOI (2008) 1 SCC 125 (SARFAESI and RDB Act operate together);
     United Bank of India v. Satyawati Tondon (2010) 8 SCC 110 (writs against SARFAESI action discouraged);
     Mathew Varghese v. M. Amritha Kumar (2014) 5 SCC 610 (Rules 8 and 9 to be complied with);
     Harshad Govardhan Sondagar v. IARC (2014) 6 SCC 1 (lessees' rights).
   - If not certain of a section number, period, amount or case, leave it out or say "check the current text of the Act". Never invent a citation.
   - No promises of outcomes, no solicitation, no comparisons with other lawyers, no client names.
5. End body with nothing extra: the build adds the call-to-action and disclaimer.
6. Run `pip install markdown && python build.py`. It must succeed.
7. Commit ("Add post: <title>") and push to `main`. Cloudflare then deploys.
