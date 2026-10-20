#!/usr/bin/env python3
"""Builds accounts-101/index.html (single file, inline SVG, no images).

Part 1 teaches accounting through one running example (Rahim Mobile).
Part 2 maps the ideas to what Dokani does today.
Every number in the example is derived below, so the statements always agree.
Run:  python3 build.py
"""
from pathlib import Path

DIG = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def bn(n, sign=False):
    """Bangla digits with lakh grouping: 100000 -> ১,০০,০০০"""
    neg = n < 0
    s = f"{abs(int(round(n))):d}"
    if len(s) > 3:
        head, tail, parts = s[:-3], s[-3:], []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    s = s.translate(DIG)
    return ("−" if neg else ("+" if sign else "")) + s


def tk(n, sign=False):
    return "৳" + bn(n, sign)


def pct(x):
    return str(round(x)).translate(DIG) + "%"


# ------------------------------------------------------------------ the example
OPEN_CASH, OPEN_STOCK = 50000, 150000
OPEN_CAPITAL = OPEN_CASH + OPEN_STOCK
PURCHASE, PURCHASE_PAID = 100000, 70000
PURCHASE_CREDIT = PURCHASE - PURCHASE_PAID
SALES, SALES_CASH = 100000, 85000
SALES_CREDIT = SALES - SALES_CASH
COGS = 80000
RENT, SALARY, NET_EXP = 3000, 4000, 1000
EXPENSES = RENT + SALARY + NET_EXP
EXP_UNPAID = RENT
EXP_PAID = EXPENSES - EXP_UNPAID
DRAW = 5000
GROSS = SALES - COGS
NET = GROSS - EXPENSES
CLOSE_CASH = OPEN_CASH + SALES_CASH - PURCHASE_PAID - EXP_PAID - DRAW
CLOSE_STOCK = OPEN_STOCK + PURCHASE - COGS
RECEIVABLE = SALES_CREDIT
PAYABLE = PURCHASE_CREDIT + EXP_UNPAID
ASSETS = CLOSE_CASH + CLOSE_STOCK + RECEIVABLE
EQUITY = OPEN_CAPITAL + NET - DRAW
assert ASSETS == PAYABLE + EQUITY, (ASSETS, PAYABLE, EQUITY)
assert CLOSE_CASH - OPEN_CASH == NET - (CLOSE_STOCK - OPEN_STOCK) - RECEIVABLE + PAYABLE - DRAW
OP_CASH = SALES_CASH - PURCHASE_PAID - EXP_PAID

# ------------------------------------------------------------------ svg helpers
def svg(inner, w=900, h=340, label=""):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}" class="fig">'
            f'{inner}</svg>')


def txt(x, y, s, cls="t", size=18, anchor="middle", weight=600):
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{s}</text>')


def waterfall(items, w=900, h=360, unit=1000):
    """items: (label, value, kind) kind in total|delta. Handles negative running totals."""
    left, right, top, bottom = 30, 30, 50, 70
    run, spans = 0, []
    for label, value, kind in items:
        if kind == "total":
            a, b = 0, value
            run = value
        else:
            a, b = run, run + value
            run = b
        spans.append((label, value, kind, a, b))
    lo = min(0, min(min(s[3], s[4]) for s in spans))
    hi = max(0, max(max(s[3], s[4]) for s in spans))
    ph = h - top - bottom
    sc = ph / (hi - lo)
    y = lambda v: top + (hi - v) * sc
    n = len(spans)
    slot = (w - left - right) / n
    bw = slot * 0.62
    out = [f'<line x1="{left}" x2="{w-right}" y1="{y(0)}" y2="{y(0)}" class="axis"/>']
    for i, (label, value, kind, a, b) in enumerate(spans):
        x = left + i * slot + (slot - bw) / 2
        top_v, bot_v = max(a, b), min(a, b)
        color = "bar-total" if kind == "total" else ("bar-up" if value >= 0 else "bar-down")
        out.append(f'<rect x="{x:.1f}" y="{y(top_v):.1f}" width="{bw:.1f}" height="{max(2,(top_v-bot_v)*sc):.1f}" rx="5" class="{color}"/>')
        ty = y(top_v) - 8
        out.append(txt(x + bw / 2, f"{ty:.1f}", bn(value, sign=(kind == 'delta' and value > 0)), "t", 17, weight=800))
        out.append(txt(x + bw / 2, h - bottom + 26, label, "m", 15, weight=600))
    return svg("".join(out), w, h, "Waterfall chart")


def bars(rows, w=900, h=300, maxv=None):
    """Horizontal bars: (label, value, cls)."""
    maxv = maxv or max(v for _, v, _ in rows)
    lw, gap = 230, 14
    bh = (h - gap * (len(rows) + 1)) / len(rows)
    out = []
    for i, (label, v, cls) in enumerate(rows):
        yy = gap + i * (bh + gap)
        out.append(txt(lw - 12, yy + bh / 2 + 6, label, "t", 17, "end"))
        wd = (w - lw - 130) * v / maxv
        out.append(f'<rect x="{lw}" y="{yy:.1f}" width="{wd:.1f}" height="{bh:.1f}" rx="6" class="{cls}"/>')
        out.append(txt(lw + wd + 10, yy + bh / 2 + 6, bn(v), "t", 17, "start", 800))
    return svg("".join(out), w, h, "Bar chart")


def equation(a, l, e, w=900, h=330, title=""):
    """Balance-scale style: Assets block = Liabilities + Equity stacked, proportional."""
    top, base = 50, h - 60
    ph = base - top
    scale = ph / max(a, l + e)
    ah, lh, eh = a * scale, l * scale, e * scale
    out = []
    ax, bx = 90, 520
    bw = 250
    out.append(f'<rect x="{ax}" y="{base-ah:.1f}" width="{bw}" height="{ah:.1f}" rx="8" class="bar-total"/>')
    out.append(txt(ax + bw / 2, base - ah / 2 + 6, f"Assets {tk(a)}", "wt", 20, weight=800))
    out.append(txt(ax + bw + 70, base - ah / 2 + 10, "=", "t", 44, weight=800))
    if l > 0:
        out.append(f'<rect x="{bx}" y="{base-lh:.1f}" width="{bw}" height="{lh:.1f}" rx="8" class="bar-down"/>')
        out.append(txt(bx + bw / 2, base - lh / 2 + 6, f"Liabilities {tk(l)}", "wt", 18, weight=800))
    out.append(f'<rect x="{bx}" y="{base-lh-eh:.1f}" width="{bw}" height="{eh:.1f}" rx="8" class="bar-up"/>')
    out.append(txt(bx + bw / 2, base - lh - eh / 2 + 6, f"Equity {tk(e)}", "wt", 20, weight=800))
    out.append(f'<line x1="40" x2="{w-40}" y1="{base}" y2="{base}" class="axis"/>')
    if title:
        out.append(txt(w / 2, 30, title, "m", 17))
    return svg("".join(out), w, h, "Accounting equation")


# ------------------------------------------------------------------ html helpers
def table(head, rows, num_cols=(), total_rows=(), neg_rows=()):
    h = "".join(f'<th class="{"n" if i in num_cols else ""}">{c}</th>' for i, c in enumerate(head))
    body = ""
    for ri, r in enumerate(rows):
        cls = ("total " if ri in total_rows else "") + ("neg " if ri in neg_rows else "")
        body += f'<tr class="{cls.strip()}">' + "".join(
            f'<td class="{"n" if i in num_cols else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>"
    return f"<table><tr>{h}</tr>{body}</table>"


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def callout(t, kind=""):
    return f'<div class="callout {kind}">{t}</div>'


def tiles(items, cols=3):
    cls = {2: " c2", 3: "", 4: " c4"}[cols]
    out = f'<div class="tiles{cls}">'
    for it in items:
        k = it.get("k", "")
        out += (f'<div class="tile {k}"><b>{it["b"]}</b>'
                + (f'<em>{it["em"]}</em>' if it.get("em") else "")
                + f'<span>{it["s"]}</span></div>')
    return out + "</div>"


def steps(items):
    out = '<div class="check">'
    for i, t in enumerate(items, 1):
        out += f"<div><i>{str(i).translate(DIG)}</i><span>{t}</span></div>"
    return out + "</div>"


def cols(a, b):
    return f'<div class="cols"><div>{a}</div><div>{b}</div></div>'


def flow(items):
    out = '<div class="flow">'
    for i, (b, s) in enumerate(items):
        if i:
            out += '<div class="arrow">→</div>'
        out += f'<div class="step"><b>{b}</b><span>{s}</span></div>'
    return out + "</div>"


SLIDES = []


def slide(part, title, body, tag="", notes="", hero=False, soon=False):
    SLIDES.append(dict(part=part, title=title, body=body, tag=tag, notes=notes, hero=hero, soon=soon))


P1, P2 = "Part 1 · হিসাবের মূল ধারণা", "Part 2 · Dokani-তে হিসাব"

# ================================================================== PART 1
slide(P1, "Accounts 101", f"""
<span class="tag">Accounts 101</span>
<h1>হিসাব শেখা, Dokani-র সাথে</h1>
<p class="lead">প্রথমে হিসাবের মূল ধারণা, একটা ছোট দোকানের উদাহরণ দিয়ে। তারপর দেখব Dokani-তে সেগুলো কোথায় আছে।</p>
""", hero=True, notes="Two parts. Part 1 teaches accounting from zero with one running example. Part 2 shows exactly what Dokani does today and where it differs from textbook accounting.")

slide(P1, "এই ডেক কীভাবে পড়বেন", f"""
<span class="tag">শুরুর আগে</span>
<h2>এই ডেক কীভাবে পড়বেন</h2>
{cols(ul([
    "<b>Part 1</b> (স্লাইড ১–৩৪): হিসাবের মূল ধারণা, কোনো আগের জ্ঞান ছাড়া",
    "<b>Part 2</b>: Dokani-তে এগুলো কোথায় আছে, কী আছে, কী নেই",
    "পুরো সময় একটাই উদাহরণ: <b>Rahim Mobile</b>, এক মাসের হিসাব",
    "সংখ্যাগুলো সব মিলে যায়: বিক্রি, লাভ, ক্যাশ, দেনা, সব",
]), steps([
    "ডান বা বাম তীর: স্লাইড বদলান",
    "<b>M</b>: সব স্লাইডের তালিকা, <b>N</b>: ব্যাখ্যার নোট",
    "<b>D</b>: dark mode, <b>F</b>: fullscreen",
]))}
""")

slide(P1, "Rahim Mobile", f"""
<span class="tag">উদাহরণ</span>
<h2>পরিচয়: Rahim Mobile</h2>
{cols(ul([
    "রহিম ভাইয়ের একটা মোবাইল শপ। এক মাসের হিসাব দেখব",
    f"মাসের শুরুতে হাতে ক্যাশ <b>{tk(OPEN_CASH)}</b> আর দোকানে ফোনের স্টক <b>{tk(OPEN_STOCK)}</b> (কেনা দামে)",
    f"মোট <b>{tk(OPEN_CAPITAL)}</b> ব্যবসায় লাগানো, কারও কাছে ধার নেই",
    "এই মাসে তিনি স্টক কিনবেন, বিক্রি করবেন, খরচ করবেন, আর নিজের জন্য কিছু টাকা তুলবেন",
]), svg(f'''
<rect x="60" y="150" width="780" height="150" rx="14" class="card-s"/>
<polygon points="40,150 450,60 860,150" class="bar-total"/>
{txt(450,125,"Rahim Mobile","wt",26,weight=800)}
<rect x="100" y="190" width="200" height="90" rx="10" class="bar-up"/>
{txt(200,225,"ক্যাশ","wt",18)}{txt(200,258,tk(OPEN_CASH),"wt",24,weight=800)}
<rect x="350" y="190" width="200" height="90" rx="10" class="bar-total"/>
{txt(450,225,"ফোনের স্টক","wt",18)}{txt(450,258,tk(OPEN_STOCK),"wt",24,weight=800)}
<rect x="600" y="190" width="200" height="90" rx="10" class="card-s2"/>
{txt(700,225,"ধার","t",18)}{txt(700,258,tk(0),"t",24,weight=800)}
''', 900, 330, "Shop"))}
""", notes="Opening position: cash 50,000, stock 150,000, owner capital 200,000, no loans or payables. This same shop is used in every Part 1 slide.")

slide(P1, "হিসাব কী", f"""
<span class="tag">মূল ধারণা</span>
<h2>হিসাব রাখা মানে কী</h2>
{svg(f'''
{"".join(f'<rect x="{30+i*215}" y="70" width="190" height="130" rx="16" class="card-s"/>' for i in range(4))}
{"".join(txt(125+i*215,115,t,"t",22,weight=800) for i,t in enumerate(["১. লেখা","২. ভাগ করা","৩. সারাংশ","৪. সিদ্ধান্ত"]))}
{"".join(txt(125+i*215,152,t,"m",16) for i,t in enumerate(["প্রতিটি লেনদেন","বিক্রি, খরচ, কেনা","মাসের তিনটি রিপোর্ট","দাম, স্টক, খরচ"]))}
{"".join(f'<text x="{222+i*215}" y="142" class="arrowt" font-size="34" text-anchor="middle">→</text>' for i in range(3))}
''',900,260,"Accounting steps")}
{callout("হিসাব মানে শুধু খাতা ভরা নয়। উদ্দেশ্য একটাই: <b>ভালো সিদ্ধান্ত নেওয়া।</b> কত দামে বেচব, কত স্টক রাখব, ধার দেব কিনা, কাকে বেতন বাড়াব।")}
""", notes="Record, classify, summarize, decide. Dokani automates the first two for sales and expenses.")

slide(P1, "তিনটি প্রশ্ন, তিনটি রিপোর্ট", f"""
<span class="tag">মূল ধারণা</span>
<h2>তিনটি প্রশ্ন, তিনটি রিপোর্ট</h2>
{svg(f'''
{"".join(f'<rect x="{25+i*300}" y="30" width="270" height="230" rx="18" class="card-s"/>' for i in range(3))}
{"".join(f'<rect x="{25+i*300}" y="30" width="270" height="48" rx="18" class="{c}"/>' for i,c in enumerate(["bar-up","bar-total","bar-down"]))}
{"".join(txt(160+i*300,62,t,"wt",19,weight=800) for i,t in enumerate(["Income statement","Balance sheet","Cash flow"]))}
{"".join(txt(160+i*300,125,t,"t",21,weight=800) for i,t in enumerate(["এই মাসে লাভ হলো?","আজ আমার কী আছে,","টাকা কোথা থেকে এলো,"]))}
{"".join(txt(160+i*300,155,t,"t",21,weight=800) for i,t in enumerate(["","কী দেনা আছে?","কোথায় গেল?"]))}
{"".join(txt(160+i*300,205,t,"m",16) for i,t in enumerate(["একটা সময়ের হিসাব","একটা দিনের ছবি","একটা সময়ের নড়াচড়া"]))}
''',900,290,"Three statements")}
{callout("এই তিনটি রিপোর্টে হিসাবের প্রায় সবকিছু ধরা পড়ে। এরপরের স্লাইডগুলোতে একটা একটা করে শিখব।")}
""", notes="Income statement covers a period. Balance sheet is a snapshot on a date. Cash flow explains movement of cash over a period.")

slide(P1, "Cash বনাম Accrual", f"""
<span class="tag">মূল ধারণা</span>
<h2>কখন ধরব: টাকা হাতে এলে, নাকি কাজ হলে?</h2>
{svg(f'''
<line x1="60" x2="840" y1="150" y2="150" class="axis" stroke-width="4"/>
<line x1="450" x2="450" y1="90" y2="210" class="dash"/>
{txt(250,80,"অক্টোবর","t",22,weight=800)}{txt(650,80,"নভেম্বর","t",22,weight=800)}
<circle cx="300" cy="150" r="13" class="dot-a"/>{txt(300,192,"২৮ অক্টোবর","m",16)}{txt(300,214,"৳১২,০০০-এর ফোন বেচা","m",16)}
<circle cx="600" cy="150" r="13" class="dot-b"/>{txt(600,192,"৫ নভেম্বর","m",16)}{txt(600,214,"গ্রাহক টাকা দিলেন","m",16)}
{txt(300,118,"Accrual: আয় এখানে","t",17,weight=800)}
{txt(600,118,"Cash basis: আয় এখানে","t",17,weight=800)}
''',900,250,"Timeline")}
{cols(ul(["<b>Cash basis:</b> টাকা হাতে এলে বা বেরোলে তখন ধরা","<b>Accrual basis:</b> কাজ বা বিক্রি যে মাসে হলো, সেই মাসে ধরা"]),
      ul(["Accrual-এ মাসের লাভ বেশি সঠিক, কারণ আয় ও খরচ একই মাসে মিলে যায়","Cash-এ জানা যায় হাতে আসলে কত টাকা আছে। দুটোই দরকার"]))}
{callout("মনে রাখুন: <b>লাভ</b> accrual-এ মাপা হয়, <b>cash flow</b> cash basis-এ। তাই লাভ ১২,০০০ হলেও ক্যাশ ১২,০০০ বাড়তে হবে না। এটা পরে বিস্তারিত দেখব।", "warn")}
""", notes="Dokani's profit side follows the sale/expense date (accrual-like). Its cash flow follows payment dates. Paid/unpaid on expenses exists precisely to separate these two.")

slide(P1, "Revenue", f"""
<span class="tag">Income statement</span>
<h2>Revenue: যা বিক্রি করে আয় হলো</h2>
{cols(ul([
    "ব্যবসার মূল কাজ থেকে আসা মোট বিক্রি",
    f"Rahim Mobile: এই মাসে মোট বিক্রি <b>{tk(SALES)}</b>",
    f"এর মধ্যে ক্যাশে পেয়েছেন {tk(SALES_CASH)}, বাকিতে দিয়েছেন {tk(SALES_CREDIT)}",
    "বাকিতে বেচলেও বিক্রি হয়ে গেছে, তাই Revenue-তে ধরা হয়",
]), steps(["<b>Revenue নয়:</b> ব্যাংক থেকে ঋণ নেওয়া টাকা","<b>Revenue নয়:</b> মালিক নিজের পকেট থেকে ব্যবসায় দেওয়া টাকা","<b>Revenue নয়:</b> মেরামতের জন্য নেওয়া Advance, ডেলিভারির আগে"]))}
{callout("প্রশ্ন করুন: এই টাকা কি গ্রাহকের কাছে পণ্য বা সেবা দিয়ে আয় হয়েছে? উত্তর না হলে এটা Revenue নয়।")}
""")

slide(P1, "COGS", f"""
<span class="tag">Income statement</span>
<h2>COGS: যা বিক্রি হয়েছে, শুধু তার কেনা দাম</h2>
{svg(f'''
{"".join(f'<rect x="{40+i*82}" y="40" width="64" height="100" rx="8" class="{"bar-down" if i<8 else "ghost"}"/>' for i in range(10))}
{"".join(txt(72+i*82,98,"ফোন","wt" if i<8 else "t",16) for i in range(10))}
<line x1="40" x2="{40+8*82-18}" y1="160" y2="160" class="line-r" stroke-width="5"/>
{txt(40+4*82-9,192,f"বিক্রি হলো ৮টি = COGS {tk(80000)}","t",20,weight=800)}
<line x1="{40+8*82}" x2="{40+10*82-18}" y1="160" y2="160" class="line-g" stroke-width="5"/>
{txt(40+9*82-9,192,f"স্টকে {tk(20000)}","t",20,weight=800)}
{txt(450,240,"প্রতিটি ফোনের কেনা দাম ৳১০,০০০, মোট ১০টি কেনা","m",16)}
''',900,260,"COGS")}
{callout("১০টি কিনলে ১০টির দাম খরচ হয় না। যেটা বিক্রি হলো শুধু সেটার কেনা দাম <b>COGS</b>। বাকিটা <b>স্টক</b>, যা একটা Asset (পরে দেখব)।")}
""", notes="COGS = cost of goods sold. Unsold stock stays on the balance sheet as inventory. In Dokani the cost per sold line is the purchase price snapshot at sale time.")

slide(P1, "Gross profit", f"""
<span class="tag">Income statement</span>
<h2>Gross profit: বিক্রি থেকে কেনা দাম বাদ</h2>
{svg(f'''
<rect x="60" y="40" width="{SALES*5/1000:.0f}" height="60" rx="8" class="bar-total"/>
{txt(60+SALES*5/2000,78,f"Revenue {tk(SALES)}","wt",20,weight=800)}
<rect x="60" y="120" width="{COGS*5/1000:.0f}" height="60" rx="8" class="bar-down"/>
{txt(60+COGS*5/2000,158,f"COGS {tk(COGS)}","wt",20,weight=800)}
<rect x="{60+COGS*5/1000:.0f}" y="120" width="{GROSS*5/1000:.0f}" height="60" rx="8" class="bar-up"/>
{txt(60+COGS*5/1000+GROSS*5/2000,158,tk(GROSS),"wt",20,weight=800)}
{txt(450,230,f"Gross profit = {tk(SALES)} − {tk(COGS)} = {tk(GROSS)}","t",22,weight=800)}
{txt(450,265,f"Gross margin = {tk(GROSS)} ÷ {tk(SALES)} = {pct(GROSS/SALES*100)}","t",22,weight=800)}
''',900,290,"Gross profit")}
{callout("প্রতি ১০০ টাকা বিক্রিতে কেনা দাম বাদ দিয়ে থাকে ২০ টাকা। এই ২০ টাকা থেকেই দোকানের সব খরচ মেটাতে হবে।")}
""")

slide(P1, "Operating expenses", f"""
<span class="tag">Income statement</span>
<h2>Operating expenses: দোকান চালানোর খরচ</h2>
{cols(table(["খরচ","এই মাসে"],[["দোকান ভাড়া",tk(RENT)],["বেতন",tk(SALARY)],["ইন্টারনেট",tk(NET_EXP)],["মোট",tk(EXPENSES)]],(1,),(3,)),
 table(["ধরন","মানে","উদাহরণ"],[["Fixed","বিক্রি যাই হোক, প্রতি মাসে প্রায় একই","ভাড়া, বেতন, ইন্টারনেট"],["Variable","বিক্রি বাড়লে বাড়ে","কমিশন, প্যাকেজিং, ডেলিভারি"]]))}
{callout("এখানে <b>পণ্য কেনার দাম নেই</b>। ওটা COGS। আর <b>নিজের জন্য তোলা টাকা</b>ও নেই, ওটা Drawings (পরে দেখব)।", "warn")}
""")

slide(P1, "Net profit", f"""
<span class="tag">Income statement</span>
<h2>Net profit: সব খরচের পর যা থাকল</h2>
{waterfall([("Revenue",SALES,"total"),("COGS",-COGS,"delta"),("Gross profit",GROSS,"total"),("খরচ",-EXPENSES,"delta"),("Net profit",NET,"total")])}
{callout(f"Net profit <b>{tk(NET)}</b>, অর্থাৎ প্রতি ১০০ টাকা বিক্রিতে ১২ টাকা নিট লাভ। একে বলে <b>net margin</b>।")}
""")

slide(P1, "Income statement", f"""
<span class="tag">Income statement</span>
<h2>প্রথম রিপোর্ট: Income statement</h2>
{table(["Rahim Mobile · এক মাস","টাকা"],[
 ["Revenue (মোট বিক্রি)",tk(SALES)],["− COGS (বিক্রীত পণ্যের কেনা দাম)",tk(-COGS)],["<b>Gross profit</b>",tk(GROSS)],
 ["− ভাড়া",tk(-RENT)],["− বেতন",tk(-SALARY)],["− ইন্টারনেট",tk(-NET_EXP)],["<b>Net profit</b>",tk(NET)]],(1,),(2,6))}
{callout("এটা পড়ে বলা যায়: মাসে কত বিক্রি, কেনা দাম কত, দোকান চালাতে কত গেল, শেষে কত থাকল। <b>কত টাকা হাতে আছে</b> সেটা কিন্তু এখানে নেই। সেজন্য আরও দুটো রিপোর্ট লাগে।", "warn")}
""")

slide(P1, "Assets", f"""
<span class="tag">Balance sheet</span>
<h2>Assets: ব্যবসার যা আছে</h2>
{cols(ul(["<b>Asset</b> মানে যা ব্যবসার মালিকানায় আছে এবং ভবিষ্যতে কাজে লাগবে বা টাকা আনবে","<b>Current asset:</b> দ্রুত ক্যাশে বদলায়: ক্যাশ, ব্যাংক, bKash, স্টক, গ্রাহকের কাছে পাওনা","<b>Fixed asset:</b> দীর্ঘদিন ব্যবহার হয়: কাউন্টার, কম্পিউটার, দোকানের ফার্নিচার"]),
 bars([("স্টক",CLOSE_STOCK,"bar-total"),("ক্যাশ",CLOSE_CASH,"bar-up"),("গ্রাহকের পাওনা",RECEIVABLE,"bar-warn")],900,260)
 )}
{callout(f"মোট Assets <b>{tk(ASSETS)}</b>")}
""", notes="Closing assets: cash 55,000 + stock 170,000 + receivable 15,000 = 240,000.")

slide(P1, "Liabilities", f"""
<span class="tag">Balance sheet</span>
<h2>Liabilities: ব্যবসার যা দেনা আছে</h2>
{cols(ul(["<b>Liability</b> মানে অন্যকে যা দিতে হবে","<b>Supplier payable:</b> বাকিতে কেনা মালের দাম","<b>Unpaid খরচ:</b> ভাড়া, বেতন যা এখনো দেওয়া হয়নি","<b>ঋণ</b> বা কিস্তি, <b>গ্রাহকের Advance</b> (মেরামত শেষ হয়নি, পণ্য দেওয়া হয়নি)"]),
 bars([("Supplier বাকি",PURCHASE_CREDIT,"bar-down"),("ভাড়া বাকি",EXP_UNPAID,"bar-down")],900,200)
 )}
{callout(f"মোট Liabilities <b>{tk(PAYABLE)}</b>", 'warn')}
{callout("দেনা মানেই খারাপ নয়। কিন্তু <b>ক্যাশের চেয়ে দেনা বেশি হলে</b> সময়মতো দিতে পারবেন না। তাই দুটো পাশাপাশি দেখুন।")}
""")

slide(P1, "Equity ও সমীকরণ", f"""
<span class="tag">Balance sheet</span>
<h2>Equity ও হিসাবের মূল সমীকরণ</h2>
{equation(OPEN_CAPITAL,0,OPEN_CAPITAL,title="মাসের শুরুতে")}
{cols(ul(["<b>Equity</b> = মালিকের অংশ = Assets − Liabilities","Equity বাড়ে: মালিক টাকা দিলে, লাভ হলে","Equity কমে: মালিক টাকা তুললে, লোকসান হলে"]),
 callout("<b>Assets = Liabilities + Equity</b><br>এই সমীকরণ সবসময় মিলতে হবে। এটাই হিসাবের ভিত্তি।"))}
""", notes="Opening: assets 200,000 = liabilities 0 + equity 200,000.")

slide(P1, "লেনদেন সমীকরণে কী করে", f"""
<span class="tag">Balance sheet</span>
<h2>প্রতিটি লেনদেন সমীকরণ মিলিয়ে রাখে</h2>
{table(["লেনদেন","Assets","Liabilities","Equity"],[
 [f"নগদে ৳{bn(70000)}-এর স্টক কেনা","স্টক +, ক্যাশ −","—","—"],
 [f"বাকিতে ৳{bn(PURCHASE_CREDIT)}-এর স্টক কেনা","স্টক +","Supplier +","—"],
 ["ফোন বিক্রি, ক্যাশে","ক্যাশ +, স্টক −","—","+ লাভ"],
 ["ফোন বিক্রি, বাকিতে","পাওনা +, স্টক −","—","+ লাভ"],
 ["ভাড়া দিইনি, মাস শেষ","—","ভাড়া বাকি +","− খরচ"],
 ["মালিক ৳৫,০০০ তুললেন","ক্যাশ −","—","− Drawings"]])}
{callout("প্রতিটি লেনদেন সমীকরণের দুই দিকেই প্রভাব ফেলে এবং দুই দিক সমান থাকে। নগদে স্টক কিনলে শুধু এক Asset অন্য Asset-এ বদলায়: লাভ-লোকসান কিছু হয় না।")}
""")

slide(P1, "Double-entry", f"""
<span class="tag">পেশাদার হিসাব</span>
<h2>Double-entry: প্রতিটি লেনদেনের দুই পিঠ</h2>
{svg(f'''
{txt(450,30,"ফোন বিক্রি ৳১২,০০০, কেনা দাম ৳৯,৫০০, ক্যাশে","m",17)}
{"".join(f'<rect x="{x}" y="50" width="200" height="170" rx="10" class="card-s"/><line x1="{x+100}" x2="{x+100}" y1="85" y2="220" class="axis"/><line x1="{x}" x2="{x+200}" y1="85" y2="85" class="axis"/>' for x in (30,250,470,690))}
{txt(130,76,"Cash","t",19,weight=800)}{txt(350,76,"Sales","t",19,weight=800)}{txt(570,76,"COGS","t",19,weight=800)}{txt(790,76,"Inventory","t",19,weight=800)}
{txt(80,112,"Debit","m",14)}{txt(180,112,"Credit","m",14)}{txt(300,112,"Debit","m",14)}{txt(400,112,"Credit","m",14)}{txt(520,112,"Debit","m",14)}{txt(620,112,"Credit","m",14)}{txt(740,112,"Debit","m",14)}{txt(840,112,"Credit","m",14)}
{txt(80,150,"১২,০০০","t",19,weight=800)}{txt(400,150,"১২,০০০","t",19,weight=800)}{txt(520,150,"৯,৫০০","t",19,weight=800)}{txt(840,150,"৯,৫০০","t",19,weight=800)}
''',900,250,"T-accounts")}
{cols(ul(["প্রতিটি লেনদেনে <b>Debit মোট = Credit মোট</b>","ক্যাশ বাড়ল (Debit), Sales বাড়ল (Credit)","COGS খরচ বাড়ল (Debit), Inventory কমল (Credit)"]),
 callout("<b>Dokani আপনাকে Debit-Credit লিখতে বলে না।</b> Dokani বিক্রি ও খরচ থেকে সরাসরি রিপোর্ট বানায়। এই স্লাইড শুধু বোঝার জন্য, যাতে হিসাবদাতার কথা বুঝতে পারেন।"))}
""", notes="Dokani is not a double-entry ledger. It is an operational reporting module. Say this clearly.")

slide(P1, "স্টক ও কেনা দামের হিসাব", f"""
<span class="tag">Inventory</span>
<h2>স্টক: কোন দামে ধরব?</h2>
<p class="lead">একই চার্জার দুই দামে কেনা: প্রথমটা ৳১০০, পরেরটা ৳১২০। একটা ৳২০০-তে বিক্রি হলো।</p>
{table(["পদ্ধতি","কোন দাম ধরা হয়","COGS","লাভ"],[
 ["FIFO","যেটা আগে কিনেছি সেটা আগে বিক্রি",tk(100),tk(100)],
 ["Weighted average","গড় দাম (১০০ + ১২০) ÷ ২",tk(110),tk(90)],
 ["Specific (নির্দিষ্ট)","ঠিক যে ইউনিটটা বিক্রি হলো, তার দাম","সেই ইউনিটের দাম","সঠিক"]],(2,3))}
{callout("<b>ফোনের ক্ষেত্রে সহজ:</b> প্রতিটি ফোনের IMEI আছে, তাই প্রতিটির কেনা দাম আলাদা জানা যায়। এটাই সবচেয়ে সঠিক পদ্ধতি (specific identification)। চার্জার, কভারের মতো একই ধরনের পণ্যে দাম গড় বা পরিবর্তিত হতে পারে।")}
""")

slide(P1, "পাওনা", f"""
<span class="tag">Receivables</span>
<h2>বাকিতে বিক্রি: পাওনা (Receivables)</h2>
{cols(svg(f'''
{txt(300,28,"কত দিনের পুরনো বাকি","m",16)}
<rect x="170" y="50" width="{8000*0.04:.0f}" height="50" rx="6" class="bar-up"/>{txt(160,83,"০–৩০ দিন","t",17,"end")}{txt(170+8000*0.04+8,83,tk(8000),"t",17,"start",800)}
<rect x="170" y="115" width="{5000*0.04:.0f}" height="50" rx="6" class="bar-warn"/>{txt(160,148,"৩১–৬০ দিন","t",17,"end")}{txt(170+5000*0.04+8,148,tk(5000),"t",17,"start",800)}
<rect x="170" y="180" width="{2000*0.04:.0f}" height="50" rx="6" class="bar-down"/>{txt(160,213,"৬০+ দিন","t",17,"end")}{txt(170+2000*0.04+8,213,tk(2000),"t",17,"start",800)}
{txt(300,265,f"মোট পাওনা {tk(RECEIVABLE)}","t",19,weight=800)}
''',560,285,"Ageing"),
 ul(["বিক্রি হয়ে গেছে, তাই লাভে ধরা হয়েছে","কিন্তু টাকা আসেনি, তাই ক্যাশ বাড়েনি","যত পুরনো, তত আদায়ের সম্ভাবনা কম","৬০ দিনের বেশি পুরনো বাকির দিকে নজর দিন"]))}
{callout("ভালো লাভ দেখিয়েও ব্যবসা ক্যাশের অভাবে আটকে যেতে পারে, যদি বেশিরভাগ বিক্রি বাকিতে হয়।", "warn")}
""")

slide(P1, "দেনা ও খরচের বাকি", f"""
<span class="tag">Payables</span>
<h2>দেনা: ক্যাশ যায়নি, কিন্তু দায় হয়েছে</h2>
{cols(ul([f"বাকিতে স্টক কিনলে {tk(PURCHASE_CREDIT)} Supplier-কে দিতে হবে। এটা এখনো খরচ নয়, কারণ স্টক Asset","কিন্তু যে ফোন বিক্রি হবে, তার কেনা দাম তখন COGS হবে","ভাড়া মাসের মধ্যে ব্যবহার হয়েছে, কিন্তু পরের মাসে দেবেন: এটা এই মাসের খরচ এবং দেনা"]),
 table(["","লাভে","ক্যাশে","দেনায়"],[["বাকিতে স্টক কেনা","এখনো না","না","হ্যাঁ"],["বাকি ভাড়া","হ্যাঁ, এই মাসে","না","হ্যাঁ"],["পরের মাসে ভাড়া দিলে","না","হ্যাঁ, তখন","কমে"]]))}
{callout("দেনা সময়মতো না দিলে সম্পর্ক ও ক্রেডিট নষ্ট হয়। তাই কার কত দেনা, কবে দিতে হবে, তা সবসময় সামনে রাখুন।")}
""")

slide(P1, "Drawings", f"""
<span class="tag">মালিক ও ব্যবসা</span>
<h2>মালিকের তোলা টাকা: খরচ নয়, Drawings</h2>
{cols(steps(["ব্যবসার লাভ-লোকসান ও মালিকের ব্যক্তিগত টাকা আলাদা","মালিক ব্যবসা থেকে টাকা তুললে সেটা <b>Drawings</b>","Drawings খরচ নয়, তাই Net profit কমায় না","কিন্তু Equity ও ক্যাশ কমায়"]),
 bars([("মাসের লাভ",NET,"bar-up"),("মালিক তুলেছেন",DRAW,"bar-down"),("ব্যবসায় রইল",NET-DRAW,"bar-total")],900,250)
 )}
{callout("<b>টিপ:</b> নিজের জন্য একটা নির্দিষ্ট মাসিক বেতন ঠিক করুন এবং সেটা খরচ হিসেবে লিখুন। তাহলে দোকানের আসল লাভ বোঝা যায়। নাহলে মালিক আসলে কত শ্রম দিয়ে কত পাচ্ছেন, সেটা হিসাবে আসে না।", "warn")}
""")

slide(P1, "Capital বনাম Revenue খরচ", f"""
<span class="tag">খরচের ধরন</span>
<h2>কিছু খরচ এক মাসে শেষ হয় না</h2>
{cols(table(["","ধরন","কীভাবে ধরব"],[["দোকান ভাড়া ৳৩,০০০","Revenue expense","এই মাসের খরচ"],["ডিসপ্লে কাউন্টার ৳১২,০০০","Capital (Fixed asset)","Asset, কয়েক বছরে ভাগ করে খরচ"]]),
 svg(f'''
{txt(280,28,"কাউন্টার ৳১২,০০০, ৪ বছর চলবে","m",16)}
{"".join(f'<rect x="{20+i*135}" y="50" width="125" height="90" rx="8" class="bar-total"/>{txt(82+i*135,88,"বছর "+str(i+1).translate(DIG),"wt",17)}{txt(82+i*135,118,"৳৩,০০০","wt",19,weight=800)}' for i in range(4))}
{txt(280,185,"প্রতি মাসে খরচ = ১২,০০০ ÷ ৪৮ = ৳২৫০","t",19,weight=800)}
{txt(280,215,"একে বলে Depreciation","m",16)}
''',560,240,"Depreciation"))}
{callout("কাউন্টারের পুরো ১২,০০০ এক মাসের খরচে ধরলে সেই মাসের লাভ ভুলভাবে কমে যায়, পরের মাসগুলোর লাভ ভুলভাবে বেশি দেখায়। এই ভাগ করাকে <b>depreciation</b> বলে।")}
{callout("<b>Dokani-তে আজ:</b> Fixed asset ও depreciation আলাদা করে ট্র্যাক হয় না। এই ধরনের বড় কেনা আলাদাভাবে মনে রাখুন বা হিসাবদাতার সাথে ঠিক করুন।", "warn")}
""")

slide(P1, "Cash flow statement", f"""
<span class="tag">Cash flow</span>
<h2>তৃতীয় রিপোর্ট: Cash flow</h2>
{cols(table(["Rahim Mobile · এক মাস","টাকা"],[
 ["মাসের শুরুর ক্যাশ",tk(OPEN_CASH)],
 ["+ বিক্রি থেকে ক্যাশ পেয়েছেন",tk(SALES_CASH)],
 ["− স্টকের জন্য দিয়েছেন",tk(-PURCHASE_PAID)],
 ["− খরচ দিয়েছেন (ভাড়া বাদে)",tk(-EXP_PAID)],
 ["<b>ব্যবসা চালিয়ে ক্যাশ</b>",tk(OP_CASH)],
 ["− মালিক তুলেছেন",tk(-DRAW)],
 ["<b>মাস শেষে ক্যাশ</b>",tk(CLOSE_CASH)]],(1,),(4,6)),
 ul(["Cash flow শুধু <b>টাকা সত্যি এলো-গেল</b> তা দেখে","তিন ভাগে ভাবা যায়: ব্যবসা চালানো (operating), বড় কেনা (investing), ঋণ বা মালিকের টাকা (financing)","এখানে ব্যবসা চালিয়ে ক্যাশ বেড়েছে "+tk(OP_CASH)+", মালিক তুলেছেন "+tk(DRAW)+", তাই মোট বেড়েছে "+tk(CLOSE_CASH-OPEN_CASH)]))}
""")

slide(P1, "লাভ ≠ ক্যাশ", f"""
<span class="tag">সবচেয়ে গুরুত্বপূর্ণ পাঠ</span>
<h2>লাভ {tk(NET)}, কিন্তু ক্যাশ বাড়ল মাত্র {tk(CLOSE_CASH-OPEN_CASH)}</h2>
{waterfall([("Net profit",NET,"total"),("স্টক বেড়েছে",-(CLOSE_STOCK-OPEN_STOCK),"delta"),("বাকিতে বিক্রি",-RECEIVABLE,"delta"),("Supplier বাকি",PURCHASE_CREDIT,"delta"),("ভাড়া বাকি",EXP_UNPAID,"delta"),("মালিক তুলেছেন",-DRAW,"delta"),("ক্যাশ বাড়ল",CLOSE_CASH-OPEN_CASH,"total")], h=380)}
{callout(f"লাভের টাকা ক্যাশে নেই। {tk(CLOSE_STOCK-OPEN_STOCK)} গেছে বেশি স্টকে, {tk(RECEIVABLE)} গ্রাহকের কাছে আটকে, আর {tk(PAYABLE)} এখনো দেওয়া হয়নি বলে ক্যাশ ঠিক আছে।", "warn")}
""", notes="Bridge: 12,000 profit - 20,000 stock increase - 15,000 receivable + 30,000 supplier credit + 3,000 unpaid rent - 5,000 drawings = +5,000 cash.")

slide(P1, "Balance sheet", f"""
<span class="tag">Balance sheet</span>
<h2>দ্বিতীয় রিপোর্ট: Balance sheet</h2>
{cols(table(["Assets","টাকা"],[["ক্যাশ",tk(CLOSE_CASH)],["ফোনের স্টক",tk(CLOSE_STOCK)],["গ্রাহকের কাছে পাওনা",tk(RECEIVABLE)],["<b>মোট Assets</b>",tk(ASSETS)]],(1,),(3,)),
 table(["Liabilities ও Equity","টাকা"],[["Supplier বাকি",tk(PURCHASE_CREDIT)],["ভাড়া বাকি",tk(EXP_UNPAID)],["Equity (শুরু "+tk(OPEN_CAPITAL)+" + লাভ "+tk(NET)+" − Drawings "+tk(DRAW)+")",tk(EQUITY)],["<b>মোট</b>",tk(PAYABLE+EQUITY)]],(1,),(3,)))}
{equation(ASSETS,PAYABLE,EQUITY,h=300,title="মাস শেষে: Assets = Liabilities + Equity")}
""")

slide(P1, "তিন রিপোর্ট কীভাবে জোড়া", f"""
<span class="tag">সব মিলিয়ে</span>
<h2>তিনটি রিপোর্ট আসলে একই গল্প</h2>
{svg(f'''
<rect x="30" y="30" width="250" height="110" rx="14" class="card-s"/>{txt(155,68,"Income statement","t",20,weight=800)}{txt(155,100,f"Net profit {tk(NET)}","m",17)}
<rect x="620" y="30" width="250" height="110" rx="14" class="card-s"/>{txt(745,68,"Balance sheet","t",20,weight=800)}{txt(745,100,f"Equity {tk(EQUITY)}","m",17)}
<rect x="325" y="190" width="250" height="110" rx="14" class="card-s"/>{txt(450,228,"Cash flow","t",20,weight=800)}{txt(450,260,f"শেষ ক্যাশ {tk(CLOSE_CASH)}","m",17)}
<line x1="280" x2="620" y1="85" y2="85" class="line-g" stroke-width="4"/>{txt(450,75,"লাভ Equity-তে যোগ হয়","t",15)}
<line x1="450" x2="450" y1="190" y2="150" class="line-g" stroke-width="3"/>
<line x1="450" x2="745" y1="170" y2="170" class="line-g" stroke-width="3"/><line x1="745" x2="745" y1="170" y2="140" class="line-g" stroke-width="3"/>
{txt(600,165,"শেষ ক্যাশ Balance sheet-এর ক্যাশ","t",15)}
''',900,330,"Connections")}
{callout("একটা মিললে বাকি দুটোও মেলে। কোনো একটা না মিললে কোথাও লেনদেন বাদ গেছে বা ভুল জায়গায় লেখা হয়েছে।")}
""")

slide(P1, "Margin বনাম Markup", f"""
<span class="tag">দাম ঠিক করা</span>
<h2>Margin আর Markup এক জিনিস নয়</h2>
{svg(f'''
<rect x="80" y="74" width="200" height="176" rx="8" class="bar-down"/>{txt(180,170,"কেনা দাম ৮০","wt",20,weight=800)}
<rect x="80" y="30" width="200" height="44" rx="8" class="bar-up"/>{txt(180,60,"লাভ ২০","wt",18,weight=800)}
{txt(180,282,"বিক্রয় মূল্য ১০০","t",19,weight=800)}
{txt(600,100,"Markup = লাভ ÷ কেনা দাম","t",21,weight=800)}{txt(600,138,"২০ ÷ ৮০ = ২৫%","g",26,weight=800)}
{txt(600,200,"Margin = লাভ ÷ বিক্রয় মূল্য","t",21,weight=800)}{txt(600,238,"২০ ÷ ১০০ = ২০%","g",26,weight=800)}
''',900,300,"Margin markup")}
{callout("ধরুন ২০% margin চান, কিন্তু কেনা দামের ওপর ২০% যোগ করলেন। আসলে margin হবে মাত্র ১৬.৭%। <b>২০% margin চাইলে</b> কেনা দামকে ০.৮ দিয়ে ভাগ করুন: ৮০ ÷ ০.৮ = ১০০।", "warn")}
""")

slide(P1, "Break-even", f"""
<span class="tag">দাম ও খরচ</span>
<h2>মাসে কত বিক্রি করলে ক্ষতি থামে?</h2>
{svg(f'''
<polygon points="80,160 470,160 80,290" class="shade-loss"/>
<polygon points="470,160 860,160 860,30" class="shade-gain"/>
<line x1="80" x2="860" y1="290" y2="290" class="axis"/><line x1="80" x2="80" y1="30" y2="290" class="axis"/>
<line x1="80" y1="290" x2="860" y2="30" class="line-g" stroke-width="5"/>
<line x1="80" x2="860" y1="160" y2="160" class="line-r" stroke-width="5"/>
<circle cx="470" cy="160" r="10" class="dot-a"/>
{txt(470,132,"Break-even ৳৪০,০০০","t",19,weight=800)}
{txt(700,95,"Gross profit (২০%)","g",17)}
{txt(700,190,"মাসিক খরচ ৳৮,০০০","r",17)}
{txt(80,316,"০","m",14)}{txt(470,316,"বিক্রি ৳৪০,০০০","m",14)}{txt(860,316,"৳৮০,০০০","m",14,"end")}
{txt(250,235,"ক্ষতি","r",17)}{txt(720,60,"লাভ","g",17)}
''',900,330,"Break-even")}
{callout("মাসিক খরচ ৳৮,০০০ ÷ gross margin ২০% = <b>৳৪০,০০০ বিক্রি</b>। এর নিচে বিক্রি হলে ক্ষতি, ওপরে হলে লাভ। Margin বাড়ালে বা খরচ কমালে এই সংখ্যা নেমে আসে।")}
""")

slide(P1, "স্টকে কত টাকা আটকে", f"""
<span class="tag">দক্ষতা</span>
<h2>স্টকে টাকা আটকে আছে কতদিন?</h2>
{cols(ul([f"গড় স্টক = ({tk(OPEN_STOCK)} + {tk(CLOSE_STOCK)}) ÷ ২ = <b>{tk((OPEN_STOCK+CLOSE_STOCK)/2)}</b>",f"মাসে COGS = <b>{tk(COGS)}</b>",f"Stock turnover = {bn(COGS)} ÷ {bn((OPEN_STOCK+CLOSE_STOCK)/2)} ≈ <b>০.৫ গুণ</b>/মাস","মানে <b>গড়ে ৬০ দিনের মাল</b> দোকানে পড়ে থাকে"]),
 svg(f'''
{txt(300,30,"স্টক পুরোপুরি বিক্রি হতে সময়","m",16)}
<rect x="40" y="60" width="520" height="50" rx="8" class="ghost"/><rect x="40" y="60" width="260" height="50" rx="8" class="bar-total"/>
{txt(170,92,"প্রথম ৩০ দিন","wt",17)}{txt(430,92,"পরের ৩০ দিন","t",17)}
{txt(300,160,"≈ ৬০ দিন","t",26,weight=800)}
''',600,200,"Days"))}
{callout("পুরনো স্টক মানে আটকে থাকা টাকা। ফোনের দাম সময়ের সাথে কমে। তাই যে মাল দ্রুত বিক্রি হয় সেটা বেশি রাখুন, ধীর মাল কম।", "warn")}
""")

slide(P1, "পাঁচটি সংখ্যা", f"""
<span class="tag">নজরে রাখুন</span>
<h2>প্রতি মাসে পাঁচটি সংখ্যা দেখুন</h2>
{table(["সংখ্যা","সূত্র","Rahim Mobile","কী বলে"],[
 ["Gross margin","Gross profit ÷ Revenue",pct(GROSS/SALES*100),"দাম আর কেনা দামের ফারাক ঠিক আছে কিনা"],
 ["Net margin","Net profit ÷ Revenue",pct(NET/SALES*100),"শেষে কত থাকে"],
 ["Break-even","মাসিক খরচ ÷ Gross margin",tk(EXPENSES/ (GROSS/SALES)),"ন্যূনতম বিক্রি কত লাগবে"],
 ["স্টক দিন","গড় স্টক ÷ (COGS ÷ ৩০)","≈ ৬০ দিন","টাকা কতদিন আটকে"],
 ["ক্যাশ বনাম দেনা","ক্যাশ ÷ মোট দেনা",f"{tk(CLOSE_CASH)} বনাম {tk(PAYABLE)}","সময়মতো দেনা মেটানো যাবে কিনা"]])}
{callout("কোনো একটা সংখ্যা একা দেখলে ভুল ধারণা হয়। পাঁচটা একসাথে এক পাতায় দেখলে ব্যবসার স্বাস্থ্য বোঝা যায়।")}
""")

slide(P1, "ক্যাশ মেলানো", f"""
<span class="tag">যাচাই</span>
<h2>খাতার হিসাব আর হাতের টাকা মেলানো</h2>
{cols(steps(["দিন শেষে ক্যাশ ড্রয়ারের টাকা গুনুন","খাতার (সিস্টেমের) <b>Expected cash</b> বের করুন","পার্থক্য লিখে রাখুন","কারণ খুঁজুন: ভুল রেট, ভুলে লেখা খরচ, খুচরা ফেরত, চুরি"]),
 table(["","টাকা"],[["Expected cash",tk(55000)],["গুনে পাওয়া",tk(54800)],["পার্থক্য",tk(-200)]],(1,),(2,)))}
{callout("ছোট পার্থক্য সবার হয়। কিন্তু প্রতিদিন একই দিকে পার্থক্য হলে সেটা সংকেত: কোথাও লেনদেন বাদ যাচ্ছে বা কেউ ভুল করছে। bKash, Nagad ও ব্যাংকের ক্ষেত্রেও মাঝেমধ্যে app-এর ব্যালেন্সের সাথে মেলান।")}
""")

slide(P1, "মাস শেষের নিয়ম", f"""
<span class="tag">অভ্যাস</span>
<h2>মাস শেষে ছয় ধাপ</h2>
{steps(["সব বিক্রি ও কেনা লেখা হয়েছে কিনা দেখুন","সব খরচ লিখুন, বাকি খরচ বাকি হিসেবে চিহ্নিত করুন","ক্যাশ, bKash, ব্যাংকের টাকা গুনে বা app দেখে মেলান","স্টক গুনে সিস্টেমের সাথে মেলান","তিনটি রিপোর্ট দেখুন: লাভ, Balance, Cash flow","পাঁচটি সংখ্যা দেখে পরের মাসের সিদ্ধান্ত নিন"])}
""")

slide(P1, "শব্দ তালিকা", f"""
<span class="tag">দ্রুত রেফারেন্স</span>
<h2>শব্দ তালিকা</h2>
{table(["শব্দ","মানে"],[
 ["Revenue","মোট বিক্রি"],["COGS","বিক্রি হওয়া পণ্যের কেনা দাম"],["Gross profit","Revenue − COGS"],
 ["Expenses","দোকান চালানোর খরচ"],["Net profit","Gross profit − Expenses"],
 ["Asset","ব্যবসার যা আছে"],["Liability","ব্যবসার যা দেনা"],["Equity","Asset − Liability, মালিকের অংশ"],
 ["Drawings","মালিকের তোলা টাকা, খরচ নয়"],["Receivable / Payable","পাওনা / দেনা"],["Accrual / Cash basis","কাজ হলে ধরা / টাকা এলে ধরা"]])}
""")

slide(P1, "নিজেকে যাচাই করুন", f"""
<span class="tag">কুইজ</span>
<h2>নিজেকে যাচাই করুন</h2>
<div class="quiz">
<details><summary>১. ১০টি ফোন কিনলেন, ৭টি বিক্রি হলো। COGS কতটা ফোনের দাম?</summary><p>৭টির। বাকি ৩টি স্টক, একটা Asset।</p></details>
<details><summary>২. লাভ ১০,০০০ কিন্তু ক্যাশ কমেছে। কেন হতে পারে?</summary><p>স্টক বেশি কেনা, বাকিতে বিক্রি, দেনা মেটানো, বা মালিকের তোলা টাকা।</p></details>
<details><summary>৩. মালিক ৫,০০০ তুললেন। কী প্রভাব?</summary><p>ক্যাশ ও Equity কমে। Net profit কমে না, কারণ এটা খরচ নয়।</p></details>
<details><summary>৪. ৩,০০০ ভাড়া এই মাসের, কিন্তু দেবেন পরের মাসে। এই মাসে লাভ, ক্যাশ ও দেনায় কী হয়?</summary><p>লাভ কমে ৩,০০০, ক্যাশ কমে না, দেনা ৩,০০০ বাড়ে।</p></details>
<details><summary>৫. ২৫% markup-এ কেনা দাম ৮০ হলে বিক্রয় মূল্য কত? Margin কত?</summary><p>১০০। Margin ২০%।</p></details>
<details><summary>৬. মাসিক খরচ ১০,০০০, gross margin ২৫%। Break-even বিক্রি কত?</summary><p>১০,০০০ ÷ ০.২৫ = ৪০,০০০।</p></details>
</div>
""")

# ================================================================== PART 2
slide(P2, "Part 2: Dokani-তে হিসাব", f"""
<span class="tag">Part 2</span>
<h1>এবার Dokani-তে দেখি</h1>
<p class="lead">আগের ধারণাগুলো Dokani-তে কোথায় আছে, কী আজই কাজ করে, আর কী এখনো নেই। সৎভাবে।</p>
""", hero=True, notes="Part 2 describes only what works today, then a clearly labelled roadmap.")

slide(P2, "ধারণা → Dokani", f"""
<span class="tag">মানচিত্র</span>
<h2>কোন ধারণা Dokani-র কোথায়</h2>
{table(["হিসাবের ধারণা","Dokani-তে কোথায়"],[
 ["Revenue","Accounts → Income: শুধু Completed বিক্রি"],
 ["COGS","প্রতিটি বিক্রিত পণ্যে সংরক্ষিত Purchase price"],
 ["Operating expenses","Expenses পেজ: Category ও Ledger সহ"],
 ["Net profit","Accounts → Overview ও Income"],
 ["Assets, Liabilities","Accounts → Balance: ক্যাশ, স্টক, পাওনা, দেনা (recorded position)"],
 ["Cash flow","Accounts → Cash flow"],
 ["Payment method","Settings → Payment methods"]])}
{callout("Dokani একটা <b>ব্যবসার হিসাব বোঝার রিপোর্ট</b>। এটা পূর্ণ double-entry accounting software বা ট্যাক্স রিপোর্ট নয়।", "warn")}
""")

slide(P2, "বিক্রি কীভাবে হিসাবে আসে", f"""
<span class="tag">Income</span>
<h2>একটা বিক্রি কীভাবে হিসাবে আসে</h2>
{flow([("POS-এ বিক্রি","ফোন ১২,০০০ টাকা"),("কেনা দাম সংরক্ষিত","৯,৫০০ টাকা, বিক্রির সময়ের দাম"),("Gross profit","২,৫০০ টাকা"),("Accounts রিপোর্ট","Income ট্যাবে যোগ হয়")])}
{callout("পরে product-এর কেনা দাম বদলালেও পুরনো বিক্রির লাভ বদলায় না, কারণ কেনা দাম বিক্রির সময়েই সংরক্ষিত থাকে।")}
{callout("Return, Cancel, Hold ও Bought back হওয়া বিক্রি আর্থিক রিপোর্টে ধরা হয় না। শুধু <b>Completed</b> ধরা হয়। বিক্রির ইতিহাসে সবই থাকে।", "warn")}
""")

slide(P2, "কেনা দাম", f"""
<span class="tag warn">সবচেয়ে গুরুত্বপূর্ণ</span>
<h2>কেনা দাম না থাকলে লাভ বের হয় না</h2>
{cols(ul(["প্রতিটি product-এ <b>Purchase price</b> বসান","কেনা দাম না থাকলে সেই invoice-এর লাভ ধরা হয় না। শূন্য ধরে নেওয়া হয় না","রিপোর্টে হলুদ সতর্কবার্তা আসে এবং এক ক্লিকে সেই invoice-গুলো দেখা যায়"]),
 table(["Invoice","বিক্রি","কেনা দাম","অবস্থা"],[["INV-101","১২,০০০","৯,৫০০",'<span class="pill paid">সম্পূর্ণ</span>'],["INV-102","৮,০০০","—",'<span class="pill unpaid">দাম নেই</span>'],["INV-103","৫,০০০","৩,৮০০",'<span class="pill paid">সম্পূর্ণ</span>']],(1,2)))}
{callout("মেরামতের Repair fee-তে কেনা দাম লাগে না। শুধু Product ও Part-এর দাম প্রয়োজন।")}
""", notes="For the many shops that never use supplier or POP purchases, the product purchase price is the only cost record, so this is the key habit.")

slide(P2, "খরচ ও Ledger", f"""
<span class="tag">Expenses</span>
<h2>খরচ লিখুন, Category ও Ledger বেছে নিন</h2>
{cols(ul(["Expenses পেজে একসাথে অনেক খরচ লিখুন: প্রতি লাইনে একটা","প্রতিটি খরচের একটা <b>Category</b> থাকে (Salary, Rent)","Category একটা <b>Ledger</b> গ্রুপের অধীনে যায়","<b>বেতন</b> যায় <span class='pill lock'>Salaries &amp; staff costs</span> Ledger-এ"]),
 table(["Ledger","উদাহরণ"],[["Salaries &amp; staff costs","বেতন, বোনাস, ওভারটাইম"],["Rent","দোকান ভাড়া"],["Utilities","বিদ্যুৎ, পানি"],["Internet &amp; phone","ইন্টারনেট, রিচার্জ"],["Taxes &amp; licenses","ট্রেড লাইসেন্স, ট্যাক্স"],["Loan interest &amp; finance charges","ঋণের সুদ, ব্যাংক চার্জ"]]))}
{callout("মোট ১৬টি Ledger। ঋণের আসল পরিশোধ ও মালিকের তোলা টাকা খরচ নয়, তাই এগুলো Expense হিসেবে লিখবেন না।", "warn")}
""")

slide(P2, "Paid ও Unpaid", f"""
<span class="tag">Expenses</span>
<h2>খরচ পরিশোধ হয়েছে, নাকি বাকি?</h2>
{cols(steps(["নতুন খরচ ডিফল্টভাবে <span class='pill paid'>Paid</span>, সেই দিনের তারিখে","খরচে ক্লিক করলে Edit মডাল খোলে","সেখানে <span class='pill unpaid'>Unpaid</span> করা যায়, অথবা Paid তারিখ ও মাধ্যম বদলানো যায়","Paid তারিখ ও মাধ্যম ফাঁকা রাখলেও চলে"]),
 table(["","লাভ-ক্ষতিতে","ক্যাশে"],[["Paid খরচ","খরচের তারিখে","Paid তারিখে"],["Unpaid খরচ","খরচের তারিখে","এখনো যায়নি"],["Balance ট্যাবে","Unpaid খরচ <b>Liability</b>",""]]))}
{callout(f"উদাহরণ (Rahim Mobile): অক্টোবরের ভাড়া {tk(RENT)} নভেম্বরের ১ তারিখে দেবেন। লাভ কমবে অক্টোবরে, ক্যাশ কমবে নভেম্বরে। ঠিক Part 1-এর accrual ধারণা।")}
""", notes="Existing expenses are treated as paid on their expense date (no backfill). New ones default to paid with paid date = expense date.")

slide(P2, "টাকার মাধ্যম", f"""
<span class="tag">Payment methods</span>
<h2>Cash, bKash, Nagad, Bank</h2>
{tiles([dict(b=n,s="বন্ধ রাখা যায়, নাম বদলানো বা মোছা যায় না") for n in ("Cash","bKash","Nagad")]+[dict(b="Bank",s="Settings খুললে বন্ধ অবস্থায় যোগ হয়, চালু করে নিন")],4)}
{ul(["নিজের মতো মাধ্যম (Dutch-Bangla, City Bank) যোগ, সম্পাদনা ও মুছে ফেলা যায়","যেটা ব্যবহার করেন না সেটা বন্ধ (pause) রাখুন: POS-এ আর দেখাবে না","লক করা মাধ্যমের নাম ঠিক থাকে, তাই ভবিষ্যতের ক্যাশ হিসাবে ভুল হয় না"])}
""")

slide(P2, "মেরামত", f"""
<span class="tag">Device Service</span>
<h2>মেরামতের টাকা কখন আয় হয়?</h2>
{flow([("ফোন জমা","Job তৈরি"),("Advance নেওয়া","ক্যাশ ইন, কিন্তু এখনো আয় নয়"),("Delivery","Invoice তৈরি"),("আয় গণনা","একবারই, Delivery-র পর")])}
{ul(["<b>Advance</b> আয় নয়: গ্রাহকের কাছে আপনার দায় (Part 1-এর Liability ধারণা)","Delivery-র পর পুরো Bill একবারই Revenue-তে যায়","<b>Repair fee</b>-তে কেনা দাম লাগে না; <b>Part</b>-এর দাম সংরক্ষিত থাকে"])}
""")

slide(P2, "Accounts পেজ", f"""
<span class="tag">Accounts</span>
<h2>চারটি ট্যাব, চারটি প্রশ্ন</h2>
{tiles([dict(b="Overview",s="এই সময়ে বিক্রি, লাভ, খরচ আর ক্যাশ ফ্লো কত?"),dict(b="Income",s="প্রতিটি বিক্রি থেকে লাভ কত? কোন invoice-এ দাম নেই?"),dict(b="Balance",s="দোকানের হাতে আর বাকিতে কত? কত দেনা?"),dict(b="Cash flow",s="ক্যাশে কত ঢুকল, কত বের হলো?")],4)}
{ul(["উপরে তারিখ ও শপ বেছে নিন: সব সংখ্যা সেই অনুযায়ী বদলায়","PDF ও Excel-এ একই সংখ্যা পাবেন","এটা ব্যবসার হিসাব বোঝার রিপোর্ট, ট্যাক্স রিপোর্ট নয়"])}
""")

slide(P2, "Balance ট্যাব: সীমা", f"""
<span class="tag warn">সৎ ব্যাখ্যা</span>
<h2>Balance ট্যাব একটা “recorded position”</h2>
{cols(ul(["<b>ক্যাশ</b> তৈরি হয় Dokani-তে লেখা লেনদেন থেকে। শুরুর ক্যাশ (opening balance) লেখা নেই","<b>স্টক</b> ধরা হয় বর্তমান Purchase price-এ, বাছাই করা তারিখের পরিমাণ হিসাব করে","<b>পাওনা, দেনা</b> শুধু যা Dokani-তে লেখা, সেটুকুই","যা লেখা নেই, তা বাদ। পেজে সেটা জানানো আছে"]),
 callout("তাই Part 1-এর Balance sheet-এর সাথে এটা হুবহু মিলবে না। এটা <b>দিক দেখার</b> জন্য ভালো, অডিটের জন্য নয়। এই ফারাক কমাতে ভবিষ্যতে opening balance আসছে।", "warn"))}
""")

slide(P2, "Cash flow সতর্কতা", f"""
<span class="tag warn">সৎ ব্যাখ্যা</span>
<h2>Cash flow কখন বিভ্রান্ত করতে পারে</h2>
{cols(ul(["অনেক দোকান Supplier বা POP purchase লেখে না। তারা শুধু প্রতিটি product-এ কেনা দাম বসায়","তখন স্টক কিনতে যাওয়া টাকা Cash flow-এ বাইরে যাওয়া হিসেবে আসে না","ফলে “Net cash flow” আসল ক্যাশের চেয়ে অনেক ভালো দেখায়"]),
 callout("<b>এখনকার পরামর্শ:</b> Net cash flow-কে চূড়ান্ত ক্যাশ ধরবেন না। আসল ক্যাশ ড্রয়ারে গুনে মেলান। Cash register আসছে, সেটাই এই সমস্যার সমাধান।", "warn"))}
""", notes="This is the known gap discussed earlier; the plan is to relabel it as estimated and add the cash register.")

slide(P2, "Shop Manager-এর অনুমতি", f"""
<span class="tag">অনুমতি</span>
<h2>Shop Manager কি Accounts দেখবে?</h2>
{cols(steps(["Business Settings → Employee Access খুলুন","“Accounts reports” লাইনে Shop Manager-এর ঘর চালু করুন","সাধারণ Employee-এর জন্য এটা সবসময় বন্ধ"]),
 ul(["ডিফল্টভাবে সবার জন্য বন্ধ","Manager শুধু নিজের Shop-এর হিসাব দেখে, অন্য শপ নয়","লাভ দেখায় বলে <b>Purchase price</b> দেখার অনুমতিও লাগে","Manager export করতে পারে না"]))}
""")

slide(P2, "Dokani-তে মাস শেষ", f"""
<span class="tag">অভ্যাস</span>
<h2>Dokani-তে মাস শেষের পাঁচ ধাপ</h2>
{steps(["Accounts → Income খুলুন। হলুদ সতর্কবার্তা থাকলে দাম নেই এমন invoice ঠিক করুন","Expenses পেজে মাসের সব খরচ আছে কিনা দেখুন, বাকি খরচ Unpaid করুন","Overview-তে Net profit দেখুন","Balance ট্যাবে পাওনা ও দেনা দেখুন","PDF বা Excel নামিয়ে রাখুন, এবং ক্যাশ ড্রয়ার গুনে মেলান"])}
""")

slide(P2, "চার ভুল", f"""
<span class="tag warn">সতর্কতা</span>
<h2>সবচেয়ে সাধারণ চার ভুল</h2>
{tiles([dict(b="কেনা দাম না লেখা",s="লাভের হিসাব অসম্পূর্ণ থাকে এবং invoice বাদ পড়ে",k="bad"),dict(b="খরচ না লেখা",s="মাসের শেষে লাভ বেশি দেখায়, কিন্তু ক্যাশ মেলে না",k="bad"),dict(b="নিজের টাকা ও দোকানের টাকা মেশানো",s="মালিকের ব্যক্তিগত খরচ Expense হিসেবে লিখলে লাভ ভুল হয়",k="bad"),dict(b="বেতন ও ঋণের আসল গুলিয়ে ফেলা",s="বেতন খরচ। ঋণের আসল পরিশোধ খরচ নয়, শুধু সুদ খরচ",k="bad")],2)}
""")

slide(P2, "আসছে", f"""
<span class="tag soon">আসছে, এখনো চালু হয়নি</span>
<h2>এরপর কী আসছে</h2>
{tiles([dict(b="Refund রেকর্ড",s="Return বা Cancel-এর সময় ফেরত দেওয়া টাকা ও মাধ্যম লেখা যাবে (ঐচ্ছিক)",k="warn"),dict(b="Cash register",s="দিন শুরু ও শেষ, Expected cash বনাম গোনা cash, পার্থক্য",k="warn"),dict(b="Money accounts",s="প্রতিটি মাধ্যমের ব্যালেন্স এবং এক অ্যাকাউন্ট থেকে অন্যটিতে Transfer",k="warn"),dict(b="Opening balance",s="শুরুর ক্যাশ ও স্টক একবার লিখে রাখা",k="warn"),dict(b="Expense template",s="ভাড়া, ইন্টারনেট, বেতন: এক ট্যাপে যোগ (স্বয়ংক্রিয় নয়)",k="warn"),dict(b="Manager-এর Register",s="Accounts-এর মতোই অনুমতি দিয়ে নিজের শপের জন্য",k="warn")])}
{callout("নীতি: নিয়মিত বিক্রি বা খরচ লেখায় কোনো নতুন ধাপ জোর করে যোগ হবে না। সবকিছু ঐচ্ছিক ও ডিফল্টসহ থাকবে।", "warn")}
""", notes="Roadmap only. Nothing on this slide is released.")

slide(P2, "সারকথা", f"""
<span class="tag">সারকথা</span>
<h2>মনে রাখার মতো পাঁচটি কথা</h2>
{steps(["বিক্রি মানেই লাভ নয়। কেনা দাম ও খরচ বাদ দিয়ে লাভ","লাভ আর ক্যাশ আলাদা। স্টক, বাকি ও দেনা এই ফারাক তৈরি করে","মালিকের তোলা টাকা খরচ নয়","Assets = Liabilities + Equity। সবসময় মিলতে হবে","Dokani-তে কেনা দাম, খরচ ও Paid/Unpaid ঠিক রাখুন। বাকিটা রিপোর্ট করে দেবে"])}
""", hero=False)

# ================================================================== render
CSS = """
:root{--u:min(1vw,1.55vh);--navy:#0C1E38;--green:#0D8A4A;--amber:#B7791F;--red:#C53030;--blue:#1F4E8C;--bg:#F3F7F5;--ink:#1B2A41;--muted:#5B6B80;--card:#fff;--line:#d9e3de}
:root[data-theme=dark]{--bg:#0A1424;--ink:#E8EEF6;--muted:#9BAABD;--card:#111f36;--line:#233450;--navy:#fff;--blue:#4C84D6;--green:#2FBF71;--amber:#E0A93B;--red:#F0716F;color-scheme:dark}
*{box-sizing:border-box;margin:0}
html,body{height:100%;overflow:hidden;background:var(--bg);color:var(--ink);font-family:'Noto Sans Bengali','Inter',system-ui,sans-serif}
#deck{height:100%;display:flex;transition:transform .45s cubic-bezier(.4,0,.2,1)}
.slide{flex:0 0 100vw;height:100%;overflow-y:auto;padding:5vh 5vw 10vh;display:flex;flex-direction:column;justify-content:safe center;gap:2vh}
h1{font-size:clamp(26px,calc(var(--u)*5.6),88px);font-weight:800;line-height:1.2;color:var(--navy)}
h2{font-size:clamp(20px,calc(var(--u)*3.4),54px);font-weight:800;line-height:1.25;color:var(--navy)}
.lead{font-size:clamp(13px,calc(var(--u)*1.9),30px);color:var(--muted);max-width:34em;line-height:1.6}
.tag{display:inline-block;align-self:flex-start;background:var(--green);color:#fff;font-weight:600;font-size:clamp(11px,calc(var(--u)*1.2),19px);padding:.35em 1em;border-radius:999px}
.tag.warn,.tag.soon{background:var(--amber)}
ul{list-style:none;padding:0;display:grid;gap:1.2vh}
li{font-size:clamp(13px,calc(var(--u)*1.7),27px);line-height:1.55;padding-left:1.3em;position:relative}
li::before{content:"";position:absolute;left:0;top:.65em;width:.5em;height:.5em;border-radius:50%;background:var(--green)}
.hero{align-items:center;text-align:center;background:radial-gradient(ellipse at 50% 40%,#12335c 0%,#0C1E38 72%);color:#fff}
.hero h1{color:#fff}.hero .lead{color:#cfe0f2;margin-inline:auto}.hero .tag{align-self:center}
.tiles{display:grid;gap:1.4vw;grid-template-columns:repeat(3,1fr)}.tiles.c2{grid-template-columns:repeat(2,1fr)}.tiles.c4{grid-template-columns:repeat(4,1fr)}
.tile{background:var(--card);border-radius:16px;padding:2.2vh 1.3vw;box-shadow:0 8px 26px rgba(12,30,56,.1);border-top:4px solid var(--green);display:grid;gap:.8vh;align-content:start}
.tile.warn{border-top-color:var(--amber)}.tile.bad{border-top-color:var(--red)}
.tile b{font-size:clamp(13px,calc(var(--u)*1.7),27px);color:var(--navy)}
.tile span{font-size:clamp(11px,calc(var(--u)*1.3),21px);color:var(--muted);line-height:1.55}
.tile em{font-style:normal;font-weight:800;color:var(--green);font-size:clamp(14px,calc(var(--u)*2),32px)}
.flow{display:flex;align-items:stretch;gap:.8vw;flex-wrap:wrap}
.flow .step{flex:1 1 12vw;background:var(--card);border-radius:14px;padding:2vh 1vw;text-align:center;box-shadow:0 6px 20px rgba(12,30,56,.1);display:grid;gap:.6vh;align-content:center}
.flow .step b{font-size:clamp(13px,calc(var(--u)*1.6),26px);color:var(--navy)}.flow .step span{font-size:clamp(11px,calc(var(--u)*1.25),20px);color:var(--muted)}
.flow .arrow{align-self:center;color:var(--green);font-size:clamp(18px,calc(var(--u)*3),44px);font-weight:800}
table{border-collapse:collapse;width:100%;background:var(--card);border-radius:14px;overflow:hidden;box-shadow:0 8px 26px rgba(12,30,56,.1)}
th,td{padding:1.05vh 1vw;text-align:left;font-size:clamp(11px,calc(var(--u)*1.4),23px);border-bottom:1px solid var(--line);line-height:1.45}
th{background:rgba(13,138,74,.12);color:var(--navy);font-weight:700}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
tr.total td{font-weight:800;border-top:2px solid var(--green)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:3vw;align-items:center}
.pill{display:inline-block;border-radius:999px;padding:.12em .75em;font-weight:700;font-size:.85em}
.pill.paid{background:rgba(13,138,74,.16);color:var(--green)}.pill.unpaid{background:rgba(183,121,31,.2);color:var(--amber)}.pill.lock{background:rgba(91,107,128,.2);color:var(--muted)}
.callout{background:var(--card);border-left:6px solid var(--green);border-radius:10px;padding:1.5vh 1.3vw;font-size:clamp(12px,calc(var(--u)*1.55),25px);line-height:1.6;box-shadow:0 6px 20px rgba(12,30,56,.08)}
.callout.warn{border-left-color:var(--amber)}.callout.bad{border-left-color:var(--red)}
.check{display:grid;gap:1.1vh}
.check div{background:var(--card);border-radius:12px;padding:1.3vh 1.1vw;font-size:clamp(12px,calc(var(--u)*1.6),26px);display:flex;gap:1vw;align-items:center;box-shadow:0 5px 16px rgba(12,30,56,.08);line-height:1.5}
.check i{flex:0 0 auto;width:2.1em;height:2.1em;border-radius:50%;background:var(--green);color:#fff;font-style:normal;font-weight:800;display:grid;place-items:center}
.quiz{display:grid;gap:1vh}
.quiz details{background:var(--card);border-radius:12px;padding:1.3vh 1.2vw;box-shadow:0 5px 16px rgba(12,30,56,.08)}
.quiz summary{cursor:pointer;font-weight:700;font-size:clamp(12px,calc(var(--u)*1.55),25px);line-height:1.5}
.quiz p{margin-top:.8vh;color:var(--green);font-weight:600;font-size:clamp(12px,calc(var(--u)*1.5),24px)}
.fig{width:100%;height:auto;max-height:52vh}
.fig .t{fill:var(--ink)}.fig .m{fill:var(--muted)}.fig .wt{fill:#fff}.fig .g{fill:var(--green)}.fig .r{fill:var(--red)}.fig .arrowt{fill:var(--green)}
.fig .axis{stroke:var(--muted);stroke-width:2}.fig .dash{stroke:var(--muted);stroke-width:2;stroke-dasharray:6 6}
.fig .bar-total{fill:var(--blue)}.fig .bar-up{fill:var(--green)}.fig .bar-down{fill:var(--red)}.fig .bar-warn{fill:var(--amber)}
.fig .ghost{fill:none;stroke:var(--muted);stroke-width:2;stroke-dasharray:6 5}
.fig .card-s{fill:var(--card);stroke:var(--line);stroke-width:2}.fig .card-s2{fill:var(--card);stroke:var(--muted);stroke-width:2;stroke-dasharray:6 5}
.fig .dot-a{fill:var(--green)}.fig .dot-b{fill:var(--amber)}.fig .line-g{stroke:var(--green)}.fig .line-r{stroke:var(--red)}
.fig .shade-loss{fill:rgba(197,48,48,.12)}.fig .shade-gain{fill:rgba(13,138,74,.14)}
.notes{display:none}
body.showNotes .notes{display:block;position:fixed;left:2vw;right:2vw;bottom:70px;max-height:34vh;overflow:auto;background:rgba(12,30,56,.96);color:#fff;padding:14px 18px;border-radius:12px;font-size:15px;line-height:1.55;z-index:6}
#hub{position:fixed;top:8px;right:16px;z-index:5;font:600 13px 'Noto Sans Bengali','Inter',sans-serif;color:var(--green);text-decoration:none;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:3px 12px}
#part{position:fixed;top:12px;left:16px;font:600 12px 'Inter',sans-serif;color:var(--muted);z-index:4;letter-spacing:.04em}
#bar{position:fixed;left:0;bottom:0;height:5px;background:var(--green);transition:width .4s;z-index:7}
#nav{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);display:flex;gap:10px;align-items:center;font:600 14px 'Inter',sans-serif;color:#fff;z-index:7;background:rgba(12,30,56,.88);padding:6px 10px;border-radius:999px}
#nav button{border:0;background:rgba(255,255,255,.14);color:#fff;width:38px;height:38px;border-radius:50%;font-size:17px;cursor:pointer}
#nav button:hover{background:var(--green)}
#menu{position:fixed;inset:0;background:rgba(10,20,36,.92);z-index:9;display:none;overflow:auto;padding:5vh 6vw}
#menu.open{display:block}
#menu h3{color:#fff;font-size:22px;margin:2vh 0 1vh}
#menu a{display:block;color:#dbe7f5;text-decoration:none;padding:.7vh 1vw;border-radius:8px;font-size:17px;cursor:pointer}
#menu a:hover{background:var(--green);color:#fff}
@media (max-width:820px){html,body{overflow:auto}.slide{padding:6vh 6vw 12vh}.tiles,.tiles.c4,.tiles.c2,.cols{grid-template-columns:1fr}.flow .arrow{display:none}}
@media print{#nav,#bar,#part,#menu,.notes{display:none!important}html,body{overflow:visible;height:auto}#deck{display:block;transform:none!important}.slide{height:100vh;page-break-after:always}}
"""

JS = """
(function(){
  var deck=document.getElementById('deck'),slides=[].slice.call(deck.children),n=slides.length,i=0;
  var bar=document.getElementById('bar'),count=document.getElementById('count'),part=document.getElementById('part'),root=document.documentElement,menu=document.getElementById('menu');
  function go(k){i=Math.max(0,Math.min(n-1,k));deck.style.transform='translateX(-'+(i*100)+'vw)';
    bar.style.width=((i+1)/n*100)+'%';count.textContent=(i+1)+' / '+n;part.textContent=slides[i].getAttribute('data-part')||'';
    slides.forEach(function(s,j){var a=s.querySelector('.notes');if(a)a.style.display=(j===i)?'':'none'});
    try{history.replaceState(null,'','#'+(i+1))}catch(e){}}
  function toggleNotes(){document.body.classList.toggle('showNotes')}
  function toggleFs(){try{document.fullscreenElement?document.exitFullscreen():root.requestFullscreen()}catch(e){}}
  function toggleTheme(){var t=root.getAttribute('data-theme')==='dark'?'light':'dark';root.setAttribute('data-theme',t);try{localStorage.setItem('accounts101-theme',t)}catch(e){}}
  function toggleMenu(){menu.classList.toggle('open')}
  var html='',last='';
  slides.forEach(function(s,j){var p=s.getAttribute('data-part');if(p!==last){html+='<h3>'+p+'</h3>';last=p}
    html+='<a data-go="'+j+'">'+(j+1)+'. '+s.getAttribute('data-title')+'</a>'});
  menu.innerHTML=html;
  menu.addEventListener('click',function(e){var g=e.target.getAttribute('data-go');if(g!==null){go(parseInt(g,10));menu.classList.remove('open')}else if(e.target===menu){menu.classList.remove('open')}});
  document.getElementById('prev').onclick=function(){go(i-1)};
  document.getElementById('next').onclick=function(){go(i+1)};
  document.getElementById('notesBtn').onclick=toggleNotes;
  document.getElementById('menuBtn').onclick=toggleMenu;
  document.getElementById('fs').onclick=toggleFs;
  document.getElementById('theme').onclick=toggleTheme;
  document.addEventListener('keydown',function(e){
    if(e.target.tagName==='SUMMARY'&&(e.key===' '||e.key==='Enter'))return;
    if(e.key==='Escape'){menu.classList.remove('open');return}
    if(['ArrowRight','PageDown',' ','Enter'].indexOf(e.key)>-1){e.preventDefault();go(i+1)}
    else if(['ArrowLeft','PageUp','Backspace'].indexOf(e.key)>-1){e.preventDefault();go(i-1)}
    else if(e.key==='Home')go(0);else if(e.key==='End')go(n-1);
    else if(e.key==='f'||e.key==='F')toggleFs();
    else if(e.key==='d'||e.key==='D')toggleTheme();
    else if(e.key==='n'||e.key==='N')toggleNotes();
    else if(e.key==='m'||e.key==='M')toggleMenu();});
  var saved=null;try{saved=localStorage.getItem('accounts101-theme')}catch(e){}
  if(saved==='dark')root.setAttribute('data-theme','dark');
  var x0=null;
  document.addEventListener('touchstart',function(e){x0=e.touches[0].clientX},{passive:true});
  document.addEventListener('touchend',function(e){if(x0===null)return;var d=e.changedTouches[0].clientX-x0;if(Math.abs(d)>50)go(i+(d<0?1:-1));x0=null});
  var start=parseInt((location.hash||'').slice(1),10);go(isNaN(start)?0:start-1);
})();
"""


def render():
    secs = ""
    for s in SLIDES:
        cls = "slide hero" if s["hero"] else "slide"
        title = s["title"].replace('"', "&quot;")
        notes = f'<aside class="notes">{s["notes"]}</aside>' if s["notes"] else ""
        secs += f'<section class="{cls}" data-part="{s["part"]}" data-title="{title}">{s["body"]}{notes}</section>\n'
    return f"""<!doctype html>
<html lang="bn" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Accounts 101 — Dokani</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+Bengali:wght@400;600;800&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div id="part"></div>
<a id="hub" href="../index.html">← সব টিউটোরিয়াল</a>
<main id="deck">
{secs}</main>
<div id="bar"></div>
<div id="menu"></div>
<div id="nav"><button id="prev" aria-label="Previous">‹</button><span id="count"></span><button id="next" aria-label="Next">›</button><button id="menuBtn" title="Slides (M)" aria-label="Slide list">☰</button><button id="notesBtn" title="Notes (N)" aria-label="Notes">✎</button><button id="fs" title="Fullscreen (F)" aria-label="Fullscreen">⛶</button><button id="theme" title="Dark mode (D)" aria-label="Theme">◐</button></div>
<script>{JS}</script>
</body>
</html>
"""


if __name__ == "__main__":
    out = Path(__file__).with_name("index.html")
    out.write_text(render(), encoding="utf-8")
    print(f"wrote {out} with {len(SLIDES)} slides")
