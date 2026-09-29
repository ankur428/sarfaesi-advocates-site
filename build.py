#!/usr/bin/env python3
"""Static site builder for SARFAESI Advocates.

Usage:  python3 build.py            # builds ./dist
Blog posts live in ./posts/*.md with a small front-matter header:

    ---
    title: ...
    date: 2026-09-30        (posts dated in the future are NOT published until that date)
    category: ...
    description: ...
    ---
    Markdown body...

Re-running the build each day publishes any post whose date has arrived.
"""
import datetime as dt
import html
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SITE_URL = "https://www.sarfaesiadvocates.com"   # change to the final domain
NAME = "SARFAESI Advocates"
PHONE = "08048067040"
PHONE_TEL = "08048067040"
EMAIL = "sarfaesiadvocates@gmail.com"
ADDRESS = "No. 76, Kasturi Complex, 2nd Floor, Mission Road, Bengaluru 560027"
from zoneinfo import ZoneInfo
TODAY = dt.datetime.now(ZoneInfo('Asia/Kolkata')).date()

NAV = [("index.html", "Home"), ("about.html", "About"), ("services.html", "Services"),
       ("faq.html", "FAQs"), ("blog/index.html", "Blog"), ("contact.html", "Contact")]


def rel(depth):
    return "../" * depth


def layout(title, desc, body, path, depth=0, extra_head=""):
    r = rel(depth)
    nav = "".join(
        f'<a href="{r}{href}"{" class=active" if href == path else ""}>{label}</a>'
        for href, label in NAV)
    canonical = f"{SITE_URL}/{path}" if path != "index.html" else SITE_URL + "/"
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="{r}assets/style.css">
{extra_head}
</head><body>
<header class="site-header"><div class="wrap bar">
<a class="brand" href="{r}index.html"><span class="mark">§</span><span>SARFAESI<br><small>Advocates</small></span></a>
<button class="menu-btn" aria-label="Menu" onclick="document.body.classList.toggle('nav-open')">☰</button>
<nav>{nav}</nav>
</div></header>
<main>{body}</main>
<footer class="site-footer"><div class="wrap cols">
<div><h4>{NAME}</h4><p>Litigation, liaisoning and advisory under the SARFAESI Act, 2002, DRT/DRAT proceedings and secured-asset auctions.</p></div>
<div><h4>Contact</h4><p>{ADDRESS}<br><a href="tel:{PHONE_TEL}">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
<div><h4>Explore</h4><p><a href="{r}services.html">Services</a><br><a href="{r}blog/index.html">Blog</a><br><a href="{r}faq.html">FAQs</a><br><a href="{r}disclaimer.html">Disclaimer</a></p></div>
</div>
<div class="wrap legal">© {TODAY.year} {NAME}. Content on this website is for general information only and is not legal advice. As per the rules of the Bar Council of India, this site is not advertising or solicitation.</div>
</footer>
<div id="bci" class="modal" hidden><div class="modal-box">
<h3>Disclaimer</h3>
<p>The Bar Council of India does not permit advertisement or solicitation by advocates in any form or manner. By clicking “I Agree”, you acknowledge that you are seeking information about {NAME} of your own accord, that there has been no advertisement, personal communication, solicitation, invitation or inducement of any sort from us, and that the information on this website is for general information only and does not constitute legal advice or create an advocate-client relationship.</p>
<button id="bci-agree">I Agree</button></div></div>
<script src="{r}assets/site.js"></script>
</body></html>"""


def cta():
    return f"""<section class="cta"><div class="wrap"><h2>Received a SARFAESI notice or an auction notice?</h2>
<p>Deadlines under the Act are short. Speak to us early so that your options stay open.</p>
<a class="btn" href="contact.html">Request a consultation</a></div></section>"""


def page_index():
    body = f"""
<section class="hero"><div class="wrap">
<p class="eyebrow">Bengaluru · Karnataka High Court · DRT · DRAT</p>
<h1>Focused counsel for SARFAESI disputes and secured-asset auctions.</h1>
<p class="lead">We act for borrowers, guarantors, auction purchasers, financial creditors and asset reconstruction companies in proceedings under the SARFAESI Act, 2002 and the Recovery of Debts Act, 1993.</p>
<p><a class="btn" href="contact.html">Request a consultation</a> <a class="btn ghost" href="services.html">Our services</a></p>
</div></section>
<section class="wrap grid3 pad">
<div class="card"><h3>Litigation</h3><p>Section 17 applications before the Debts Recovery Tribunal, Section 18 appeals before the DRAT, writ petitions before the High Court and challenges to Section 14 orders.</p></div>
<div class="card"><h3>Liaisoning</h3><p>Structured engagement with banks, authorised officers, asset reconstruction companies, DRT registries and court commissioners so that matters move without avoidable delay.</p></div>
<div class="card"><h3>Advisory</h3><p>Pre-notice planning, response to Section 13(2) demand notices, one-time settlements, redemption and diligence for auction purchasers.</p></div>
</section>
<section class="band"><div class="wrap grid2">
<div><h2>Why a specialist practice?</h2>
<p>SARFAESI matters are governed by short limitation periods, mandatory pre-deposits, strict procedural rules for notices and sale, and a fast-moving body of case law. A missed date or a defective challenge can be fatal to the case.</p></div>
<ul class="ticks"><li>Section 13(2) notice replies and 13(3A) objections</li><li>Section 17 applications and interim protection</li><li>Section 14 possession orders and resistance</li><li>Auction notices, reserve price and e-auction irregularities</li><li>Pre-deposit and Section 18 appeals</li><li>Purchaser due diligence and title protection</li></ul>
</div></section>
<section class="wrap pad"><h2>From the blog</h2><div class="grid3">{{latest}}</div>
<p><a href="blog/index.html">All articles →</a></p></section>
{cta()}"""
    return body


def page_about():
    return f"""<section class="page-head"><div class="wrap"><h1>About the firm</h1></div></section>
<section class="wrap prose pad">
<p>{NAME} is a Bengaluru-based practice devoted to secured-asset enforcement law. Our work is concentrated on the SARFAESI Act, 2002, the Security Interest (Enforcement) Rules, 2002 and proceedings before the Debts Recovery Tribunals, Debts Recovery Appellate Tribunals and the High Court of Karnataka.</p>
<p>Because the practice is narrow, our advice is specific. We understand how authorised officers issue notices, how auctions are conducted and where the procedural weak points usually lie, on either side of the table.</p>
<h2>How we work</h2>
<ul><li><b>Deadline first.</b> Every engagement begins with a limitation and remedies map.</li>
<li><b>Litigation-led advice.</b> We plan the pre-litigation stage with the eventual hearing in mind.</li>
<li><b>Plain communication.</b> Clients receive clear options, costs and risks in writing.</li></ul>
<h2>Who we act for</h2>
<ul><li>Borrowers, promoters and guarantors facing enforcement</li><li>Successful auction purchasers and bidders</li><li>Banks, NBFCs and asset reconstruction companies</li><li>Residents, tenants and third parties affected by possession</li></ul>
</section>{cta()}"""


def page_services():
    items = [
        ("Response to Section 13(2) demand notices", "Reviewing the notice, account classification and security documents, and preparing a reasoned reply and representation within the sixty-day period."),
        ("Section 17 applications before the DRT", "Drafting and arguing applications against measures taken under Section 13(4), including interim stay of possession and sale, within the forty-five day limit."),
        ("Section 18 appeals before the DRAT", "Appeals against DRT orders, including advice on the statutory pre-deposit and applications for its reduction."),
        ("Section 14 possession proceedings", "Appearing before the Chief Metropolitan Magistrate or District Magistrate, and challenging or resisting orders where the law permits."),
        ("Auction disputes", "Challenges to defective sale notices, undervaluation, reserve price and conduct of e-auctions, and enforcement of rights by auction purchasers, including sale confirmation and delivery of possession."),
        ("Writ jurisdiction of the High Court", "Writ petitions in the limited situations where the High Court entertains challenges despite the alternative remedy before the DRT."),
        ("Settlements, OTS and redemption", "Negotiating one-time settlements and restructuring, and advising on the borrower's right of redemption."),
        ("Purchaser and lender advisory", "Due diligence before bidding, title and encumbrance checks, and enforcement strategy and compliance for lenders."),
    ]
    cards = "".join(f'<div class="card"><h3>{t}</h3><p>{d}</p></div>' for t, d in items)
    return f"""<section class="page-head"><div class="wrap"><h1>Services</h1><p>Litigation, liaisoning and advisory across the SARFAESI enforcement cycle.</p></div></section>
<section class="wrap grid2 pad">{cards}</section>{cta()}"""


FAQS = [
    ("What is the time limit to challenge SARFAESI action?", "An application under Section 17 before the Debts Recovery Tribunal must ordinarily be filed within forty-five days from the date on which any measure under Section 13(4) is taken. Act early; delay can close the door."),
    ("How long do I have to respond to a Section 13(2) notice?", "The borrower is given sixty days from the notice to discharge the liability. Written objections to the notice should be made within that period, and the secured creditor must reply to them with reasons."),
    ("Can I stop an auction?", "That depends on the facts. Courts and tribunals look at compliance with the notice and sale rules, the valuation and reserve price, and whether payment or settlement is offered. Interim relief is discretionary and often conditional on a deposit."),
    ("Is a pre-deposit required to appeal?", "For an appeal before the Debts Recovery Appellate Tribunal under Section 18, the borrower must deposit fifty per cent of the debt due as claimed by the secured creditor or determined by the Tribunal, whichever is less. The Appellate Tribunal may reduce this to not less than twenty-five per cent, with reasons recorded."),
    ("Can I go directly to the High Court?", "The High Court has writ jurisdiction, but it generally expects borrowers to use the statutory remedy before the DRT. Writs are entertained only in limited situations, such as a manifest lack of jurisdiction or violation of fundamental rights."),
    ("I bought a property in a bank auction. What are my risks?", "Purchasers should verify the sale notice and its publication, the reserve price, encumbrances and any pending challenge before bidding, and must observe the payment timelines under the Rules. We advise on diligence and on securing possession afterwards."),
    ("Are all loans covered by the SARFAESI Act?", "No. The Act does not apply to certain categories, such as unsecured loans, security over agricultural land and some small-value dues. Whether it applies to your loan should be checked against the Act and the documents."),
]


def page_faq():
    qa = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQS)
    import json
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQS]})
    return (f"""<section class="page-head"><div class="wrap"><h1>Frequently asked questions</h1><p>General information only. Every case turns on its own facts and documents.</p></div></section>
<section class="wrap prose pad">{qa}</section>{cta()}""",
            f'<script type="application/ld+json">{ld}</script>')


def page_contact():
    return f"""<section class="page-head"><div class="wrap"><h1>Contact</h1></div></section>
<section class="wrap grid2 pad">
<div class="prose"><h2>Office</h2><p>{NAME}<br>{ADDRESS}</p>
<p>Phone: <a href="tel:{PHONE_TEL}">{PHONE}</a><br>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p>If you have a notice or order, please send a copy with your message. Do not send confidential documents until an engagement is confirmed.</p></div>
<form class="card" action="https://formsubmit.co/{EMAIL}" method="POST" id="contact-form">
<input type="hidden" name="_subject" value="New enquiry from sarfaesiadvocates.com">
<input type="hidden" name="_next" value="{SITE_URL}/thanks.html">
<input type="hidden" name="_template" value="table">
<input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
<label>Name<input name="name" required></label>
<label>Email<input type="email" name="email" required></label>
<label>Phone (optional)<input name="phone"></label>
<label>Message<textarea name="message" rows="5" required></textarea></label>
<button class="btn" type="submit">Send message</button>
<p class="note">Please do not include confidential documents or details in this form. We will get back to you on the details you provide.</p>
</form></section>"""


def page_thanks():
    return f"""<section class="page-head"><div class="wrap"><h1>Thank you</h1></div></section>
<section class="wrap prose pad"><p>Your message has been sent. For anything urgent, please call <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
<p><a href="index.html">Back to home</a></p></section>"""


def page_disclaimer():
    return f"""<section class="page-head"><div class="wrap"><h1>Disclaimer</h1></div></section>
<section class="wrap prose pad">
<p>The rules of the Bar Council of India prohibit advocates from soliciting work or advertising. This website is intended solely to provide information about {NAME} and about the law. It is not advertising, and nothing on it is an offer or invitation for legal work.</p>
<p>Articles and answers are general information as at their publication dates. They are not legal advice, may not reflect later amendments or decisions, and should not be relied upon without consulting an advocate on your specific facts. Use of the website or receipt of its content does not create an advocate-client relationship.</p>
<p>Links to third-party sites are provided for convenience, and we are not responsible for their content.</p>
</section>"""


def parse_post(p):
    txt = p.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", txt, re.S)
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    meta["date"] = dt.date.fromisoformat(meta["date"])
    meta["slug"] = p.stem
    meta["html"] = markdown.markdown(m.group(2), extensions=["extra", "sane_lists"])
    return meta


def card(post, r=""):
    return (f'<article class="card"><p class="meta">{post["category"]} · {post["date"].strftime("%d %b %Y")}</p>'
            f'<h3><a href="{r}blog/{post["slug"]}.html">{html.escape(post["title"])}</a></h3>'
            f'<p>{html.escape(post["description"])}</p></article>')


def write(path, content):
    f = DIST / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "assets", DIST / "assets")
    posts = [parse_post(p) for p in sorted((ROOT / "posts").glob("*.md"))]
    live = sorted([p for p in posts if p["date"] <= TODAY], key=lambda p: p["date"], reverse=True)
    queued = [p for p in posts if p["date"] > TODAY]

    latest = "".join(card(p) for p in live[:3])
    write("index.html", layout(f"{NAME} | SARFAESI Act litigation, auctions and advisory in Bengaluru",
          "Specialist advocates for SARFAESI Act proceedings, DRT and DRAT litigation, Section 13(2) notices and auction disputes.",
          page_index().replace("{latest}", latest), "index.html"))
    write("about.html", layout(f"About | {NAME}", "About SARFAESI Advocates, a Bengaluru practice focused on secured-asset enforcement law.", page_about(), "about.html"))
    write("services.html", layout(f"Services | {NAME}", "SARFAESI notices, Section 17 applications, DRAT appeals, Section 14 possession and auction disputes.", page_services(), "services.html"))
    faq_body, faq_head = page_faq()
    write("faq.html", layout(f"FAQs | {NAME}", "Answers on SARFAESI limitation, pre-deposit, auctions and remedies.", faq_body, "faq.html", extra_head=faq_head))
    write("contact.html", layout(f"Contact | {NAME}", "Contact SARFAESI Advocates, Mission Road, Bengaluru.", page_contact(), "contact.html"))
    write("thanks.html", layout(f"Thank you | {NAME}", "Message sent.", page_thanks(), "thanks.html"))
    write("disclaimer.html", layout(f"Disclaimer | {NAME}", "Bar Council of India disclaimer.", page_disclaimer(), "disclaimer.html"))

    cards = "".join(card(p, "../").replace('href="../blog/', 'href="') for p in live)
    write("blog/index.html", layout(f"Blog | {NAME}", "Articles on the SARFAESI Act, DRT and DRAT practice, and auction law.",
          f'<section class="page-head"><div class="wrap"><h1>Blog</h1><p>Practical notes on SARFAESI law and practice.</p></div></section><section class="wrap grid2 pad">{cards}</section>',
          "blog/index.html", depth=1))
    for p in live:
        body = (f'<section class="page-head"><div class="wrap"><p class="meta">{p["category"]} · {p["date"].strftime("%d %B %Y")}</p>'
                f'<h1>{html.escape(p["title"])}</h1></div></section>'
                f'<article class="wrap prose pad">{p["html"]}'
                f'<div class="callbox"><b>Have a query on this topic?</b> Call <a href="tel:{PHONE_TEL}">{PHONE}</a> '
                f'or write to <a href="mailto:{EMAIL}">{EMAIL}</a>.</div><p class="note">General information only, not legal advice. Law may have changed after the date of publication.</p>'
                f'<p><a href="index.html">← All articles</a></p></article>')
        import json
        ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": p["title"],
                         "datePublished": p["date"].isoformat(), "author": {"@type": "Organization", "name": NAME},
                         "description": p["description"]})
        write(f"blog/{p['slug']}.html", layout(f"{p['title']} | {NAME}", p["description"], body,
              f"blog/{p['slug']}.html", depth=1, extra_head=f'<script type="application/ld+json">{ld}</script>'))

    # feed, sitemap, robots
    urls = ["", "about.html", "services.html", "faq.html", "contact.html", "disclaimer.html", "blog/index.html"] + [f"blog/{p['slug']}.html" for p in live]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
          "".join(f"<url><loc>{SITE_URL}/{u}</loc></url>" for u in urls) + "</urlset>")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    items = "".join(f"<item><title>{html.escape(p['title'])}</title><link>{SITE_URL}/blog/{p['slug']}.html</link>"
                    f"<pubDate>{p['date'].strftime('%a, %d %b %Y')} 06:00:00 +0530</pubDate><description>{html.escape(p['description'])}</description></item>" for p in live[:20])
    write("blog/feed.xml", f'<?xml version="1.0"?><rss version="2.0"><channel><title>{NAME}</title><link>{SITE_URL}</link><description>SARFAESI law and practice</description>{items}</channel></rss>')
    write("404.html", layout(f"Not found | {NAME}", "Page not found.", '<section class="page-head"><div class="wrap"><h1>Page not found</h1><p><a href="/index.html">Return home</a></p></div></section>', "404.html"))
    print(f"Built {len(live)} live posts, {len(queued)} queued (dates: {[str(p['date']) for p in sorted(queued, key=lambda p: p['date'])]})")


if __name__ == "__main__":
    main()
