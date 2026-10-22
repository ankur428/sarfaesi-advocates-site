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
import json
import re
import shutil
from pathlib import Path

import markdown

from service_pages import SERVICE_BY_SLUG, SERVICE_KEYS, SERVICE_PAGES

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SITE_URL = "https://sarfaesiadvocates.com"
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


def clean(path):
    """Map a built file path to the URL path the host actually serves (Cloudflare strips .html
    and serves directory indexes at 'dir/'). 'index.html' -> '', 'blog/index.html' -> 'blog/',
    'about.html' -> 'about'."""
    if path == "index.html":
        return ""
    if path.endswith("/index.html"):
        return path[: -len("index.html")]
    if path.endswith(".html"):
        return path[: -len(".html")]
    return path


def full_url(path):
    return f"{SITE_URL}/{clean(path)}"


def clean_internal_links(page_html, page_path):
    """Rewrite internal href="...html" links to the clean, root-absolute URLs the host serves,
    so visitors and crawlers do not hit a redirect on every internal link."""
    import posixpath
    base = posixpath.dirname(page_path)

    def fix(m):
        href = m.group(1)
        if re.match(r"(https?:|mailto:|tel:|#|//)", href):
            return m.group(0)
        target, _, frag = href.partition("#")
        if not target:
            return m.group(0)
        resolved = posixpath.normpath(posixpath.join(base, target)) if not target.startswith("/") else target.lstrip("/")
        if not (resolved.endswith(".html") or resolved.endswith("/index.html")):
            return m.group(0)
        url = "/" + clean(resolved.lstrip("/"))
        return f'href="{url}{"#" + frag if frag else ""}"'

    return re.sub(r'href="([^"]*)"', fix, page_html)


def jsonld(data):
    """Serialise a schema.org object as a JSON-LD script tag (safe against </script>)."""
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def breadcrumbs(trail):
    """trail: list of (name, path) from Home down to the current page."""
    return jsonld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name,
         "item": full_url(path)}
        for i, (name, path) in enumerate(trail)]})


def crumbs_html(trail, depth=0):
    r = rel(depth)
    parts = [f'<a href="{r}{path}">{html.escape(name)}</a>' for name, path in trail[:-1]]
    parts.append(f'<span>{html.escape(trail[-1][0])}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap">' + " › ".join(parts) + "</div></nav>"


def post_services(slug):
    """Service pages a post relates to, best match first (max 2)."""
    scored = []
    for svc_slug, keys in SERVICE_KEYS.items():
        score = sum(1 for k in keys if k in slug)
        if score:
            scored.append((score, svc_slug))
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [s for _, s in scored[:2]]


def layout(title, desc, body, path, depth=0, extra_head=""):
    r = rel(depth)
    nav = "".join(
        f'<a href="{r}{href}"{" class=active" if href == path else ""}>{label}</a>'
        for href, label in NAV)
    canonical = full_url(path)
    return f"""<!doctype html>
<html lang="en-IN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/rss+xml" title="{NAME} blog" href="{SITE_URL}/blog/feed.xml">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="{NAME}"><meta property="og:locale" content="en_IN">
<meta name="twitter:card" content="summary">
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
<div><h4>Practice areas</h4><p>{"<br>".join(f'<a href="{r}{s["slug"]}.html">{html.escape(s["nav"])}</a>' for s in SERVICE_PAGES)}</p></div>
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
<ul class="ticks"><li><a href="section-13-2-notice-reply.html">Section 13(2) notice replies and 13(3A) objections</a></li><li><a href="section-17-drt-application.html">Section 17 applications and interim protection</a></li><li><a href="section-14-possession-order.html">Section 14 possession orders and resistance</a></li><li><a href="sarfaesi-auction-disputes.html">Auction notices, reserve price and e-auction irregularities</a></li><li><a href="section-18-drat-appeal.html">Pre-deposit and Section 18 appeals</a></li><li><a href="sarfaesi-auction-disputes.html">Purchaser due diligence and title protection</a></li><li><a href="one-time-settlement-redemption.html">One-time settlement and redemption</a></li></ul>
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
        ("Guarantors and third-party mortgagors", "Notices, objections and remedies for persons who gave a guarantee or mortgaged property for another's loan."),
        ("Tenants and occupants", "Advice to tenants, lessees and other occupants affected by a possession under the Act."),
        ("SARFAESI and the RDB Act", "How enforcement under the SARFAESI Act and recovery applications before the DRT operate together."),
    ]
    # Cards that have a dedicated page link to it (matched by position in the list above).
    page_for = {0: "section-13-2-notice-reply", 1: "section-17-drt-application", 2: "section-18-drat-appeal",
                3: "section-14-possession-order", 4: "sarfaesi-auction-disputes", 5: "high-court-writ-sarfaesi",
                6: "one-time-settlement-redemption", 7: "lender-arc-enforcement-advisory",
                8: "guarantors-sarfaesi-enforcement", 9: "tenants-occupants-sarfaesi-possession",
                10: "sarfaesi-and-rdb-act-recovery-routes"}
    cards = "".join(
        f'<div class="card"><h3>{t}</h3><p>{d}</p>'
        + (f'<p><a href="{page_for[i]}.html">Read more →</a></p>' if i in page_for else "")
        + '</div>'
        for i, (t, d) in enumerate(items))
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
<form class="card" action="https://api.web3forms.com/submit" method="POST" id="contact-form">
<input type="hidden" name="access_key" value="4397b2f2-ada9-4ef1-beb5-f6aedae4147f">
<input type="hidden" name="subject" value="New enquiry from sarfaesiadvocates.com">
<input type="hidden" name="from_name" value="SARFAESI Advocates website">
<input type="hidden" name="redirect" value="{SITE_URL}/thanks">
<input type="checkbox" name="botcheck" style="display:none" tabindex="-1" autocomplete="off">
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
    if path.endswith(".html"):
        content = clean_internal_links(content, path)
    f.write_text(content, encoding="utf-8")


def legal_service_ld():
    return jsonld({
        "@context": "https://schema.org", "@type": "LegalService", "@id": SITE_URL + "/#firm",
        "name": NAME, "url": SITE_URL + "/",
        "description": "Advocates for SARFAESI Act proceedings, DRT and DRAT litigation, Section 13(2) notices, possession orders and secured-asset auction disputes.",
        "telephone": "+918048067040", "email": EMAIL,
        "address": {"@type": "PostalAddress", "streetAddress": "No. 76, Kasturi Complex, 2nd Floor, Mission Road",
                    "addressLocality": "Bengaluru", "addressRegion": "Karnataka", "postalCode": "560027", "addressCountry": "IN"},
        "areaServed": [{"@type": "City", "name": "Bengaluru"}, {"@type": "State", "name": "Karnataka"}],
        "knowsAbout": ["SARFAESI Act, 2002", "Debts Recovery Tribunal proceedings", "Secured-asset auctions"],
    })


def render_service(svc, live):
    """Build one service landing page. Returns (body_html, extra_head)."""
    slug = svc["slug"]
    related = [p for p in live if slug in post_services(p["slug"])][:8]
    others = [s for s in SERVICE_PAGES if s["slug"] != slug]
    qa = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in svc["faqs"])
    rel_posts = "".join(
        f'<li><a href="blog/{p["slug"]}.html">{html.escape(p["title"])}</a></li>' for p in related)
    rel_block = f'<h2>Related articles</h2><ul class="related">{rel_posts}</ul>' if related else ""
    more = "".join(f'<li><a href="{s["slug"]}.html">{html.escape(s["nav"])}</a></li>' for s in others)
    trail = [("Home", "index.html"), ("Services", "services.html"), (svc["nav"], f"{slug}.html")]
    body = (f'{crumbs_html(trail)}'
            f'<section class="page-head"><div class="wrap"><h1>{html.escape(svc["h1"])}</h1><p>{html.escape(svc["lead"])}</p></div></section>'
            f'<section class="wrap prose pad">{svc["body"]}'
            f'<h2>Frequently asked questions</h2>{qa}'
            f'{rel_block}'
            f'<h2>Other practice areas</h2><ul class="related">{more}</ul>'
            f'<p class="note">General information only, not legal advice. Please check the current text of the Act and Rules, which may have been amended.</p>'
            f'</section>{cta()}')
    faq_ld = jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": re.sub(r"<[^>]+>", "", q),
         "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in svc["faqs"]]})
    return body, breadcrumbs(trail) + faq_ld


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
          page_index().replace("{latest}", latest), "index.html", extra_head=legal_service_ld()))
    write("about.html", layout(f"About | {NAME}", "About SARFAESI Advocates, a Bengaluru practice focused on secured-asset enforcement law.", page_about(), "about.html",
          extra_head=breadcrumbs([("Home", "index.html"), ("About", "about.html")])))
    write("services.html", layout(f"Services | {NAME}", "SARFAESI notices, Section 17 applications, DRAT appeals, Section 14 possession and auction disputes.", page_services(), "services.html",
          extra_head=breadcrumbs([("Home", "index.html"), ("Services", "services.html")])))
    for svc in SERVICE_PAGES:
        svc_body, svc_head = render_service(svc, live)
        write(f"{svc['slug']}.html", layout(f"{svc['title']} | {NAME}", svc["desc"], svc_body, f"{svc['slug']}.html", extra_head=svc_head))
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
        svcs = post_services(p["slug"])
        # Link each article to its practice-area page(s) and to a few sibling articles.
        svc_links = "".join(
            f'<li><a href="../{s}.html">{html.escape(SERVICE_BY_SLUG[s]["nav"])}</a></li>' for s in svcs)
        sibs = [q for q in live if q["slug"] != p["slug"] and set(svcs) & set(post_services(q["slug"]))][:3]
        sib_links = "".join(f'<li><a href="{q["slug"]}.html">{html.escape(q["title"])}</a></li>' for q in sibs)
        related_box = ""
        if svc_links:
            related_box += f'<div class="related-box"><h2>Related practice areas</h2><ul class="related">{svc_links}</ul></div>'
        if sib_links:
            related_box += f'<div class="related-box"><h2>Related articles</h2><ul class="related">{sib_links}</ul></div>'
        trail = [("Home", "index.html"), ("Blog", "blog/index.html"), (p["title"], f"blog/{p['slug']}.html")]
        body = (f'{crumbs_html(trail, depth=1)}'
                f'<section class="page-head"><div class="wrap"><p class="meta">{p["category"]} · {p["date"].strftime("%d %B %Y")}</p>'
                f'<h1>{html.escape(p["title"])}</h1></div></section>'
                f'<article class="wrap prose pad">{p["html"]}{related_box}'
                f'<div class="callbox"><b>Have a query on this topic?</b> Call <a href="tel:{PHONE_TEL}">{PHONE}</a> '
                f'or write to <a href="mailto:{EMAIL}">{EMAIL}</a>.</div><p class="note">General information only, not legal advice. Law may have changed after the date of publication.</p>'
                f'<p><a href="index.html">← All articles</a></p></article>')
        page_url = full_url(f"blog/{p['slug']}.html")
        ld = jsonld({"@context": "https://schema.org", "@type": "Article", "headline": p["title"],
                     "datePublished": p["date"].isoformat(), "dateModified": p["date"].isoformat(),
                     "author": {"@type": "Organization", "name": NAME},
                     "publisher": {"@type": "Organization", "name": NAME, "url": SITE_URL + "/"},
                     "mainEntityOfPage": page_url, "inLanguage": "en-IN",
                     "description": p["description"]})
        # Long article titles are truncated in search results; skip the brand suffix when it would push past ~65 chars.
        page_title = p["title"] if len(p["title"]) + len(NAME) + 3 > 65 else f"{p['title']} | {NAME}"
        write(f"blog/{p['slug']}.html", layout(page_title, p["description"], body,
              f"blog/{p['slug']}.html", depth=1, extra_head=ld + breadcrumbs(trail)))

    # feed, sitemap, robots
    urls = [("", None), ("about.html", None), ("services.html", None)]
    urls += [(f"{s['slug']}.html", None) for s in SERVICE_PAGES]
    urls += [("faq.html", None), ("contact.html", None), ("disclaimer.html", None),
             ("blog/index.html", live[0]["date"] if live else None)]
    urls += [(f"blog/{p['slug']}.html", p["date"]) for p in live]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
          "".join(f"<url><loc>{full_url(u) if u else SITE_URL + '/'}</loc>" + (f"<lastmod>{d.isoformat()}</lastmod>" if d else "") + "</url>"
                  for u, d in urls) + "</urlset>")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    items = "".join(f"<item><title>{html.escape(p['title'])}</title><link>{full_url('blog/' + p['slug'] + '.html')}</link>"
                    f"<pubDate>{p['date'].strftime('%a, %d %b %Y')} 06:00:00 +0530</pubDate><description>{html.escape(p['description'])}</description></item>" for p in live[:20])
    write("blog/feed.xml", f'<?xml version="1.0"?><rss version="2.0"><channel><title>{NAME}</title><link>{SITE_URL}</link><description>SARFAESI law and practice</description>{items}</channel></rss>')
    write("404.html", layout(f"Not found | {NAME}", "Page not found.", '<section class="page-head"><div class="wrap"><h1>Page not found</h1><p><a href="/index.html">Return home</a></p></div></section>', "404.html"))
    print(f"Built {len(live)} live posts, {len(queued)} queued (dates: {[str(p['date']) for p in sorted(queued, key=lambda p: p['date'])]})")


if __name__ == "__main__":
    main()
