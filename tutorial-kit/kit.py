"""Tutorial kit: byte-size Bangla slide courses with verified, highlighted code.

A course is a Python file that builds a `Course` and calls `course.build()`. Every slide is one small
idea. Code blocks are *executed at build time* and the real output (or the real compiler error) is
put on the slide, so nothing shown to the learner is made up:

    rust         single-file program, compiled with rustc (edition 2024) and run
    rust+cargo   Cargo project with crates (`deps=`); can start a server and run curl `requests=`
    php          run with the php CLI
    mysql        run in one MySQL database per course (statements build on each other)
    postgresql   same, with psql
    anything     else (toml, bash, ...) is shown only

The deck: arrow keys / swipe, slide list (M), dark mode (D), fullscreen (F), copy button on code,
and progress kept in localStorage so a learner can close the tab and continue later.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

KIT = Path(__file__).resolve().parent
CACHE = KIT / ".cache"
DIG = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
e = html.escape


def bn(n):
    return str(n).translate(DIG)


# ------------------------------------------------------------------ blocks (left column)
class Html(str):
    """Marker for raw HTML blocks placed in the text column."""


def say(*paras):
    return Html("".join(f"<p>{x}</p>" for x in paras))


def points(*items):
    return Html("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")


def tip(x):
    return Html(f'<div class="callout">💡 {x}</div>')


def warn(x):
    return Html(f'<div class="callout warn">⚠️ {x}</div>')


def php_note(x):
    """'PHP-তে যেমন' bridge for PHP/Laravel developers."""
    return Html(f'<div class="callout php"><b>PHP/Laravel-এ যেমন</b> {x}</div>')


def task(x):
    return Html(f'<div class="callout task"><b>নিজে করুন</b> {x}</div>')


def quiz(q, a):
    return Html(f'<details class="quiz"><summary>❓ {q}</summary><p>{a}</p></details>')


def table(head, rows):
    h = "".join(f"<th>{c}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return Html(f'<table class="tbl"><tr>{h}</tr>{b}</table>')


def steps(*items):
    return Html('<div class="steps">' + "".join(
        f"<div><i>{bn(i)}</i><span>{t}</span></div>" for i, t in enumerate(items, 1)) + "</div>")


# ------------------------------------------------------------------ code (right column)
class Code:
    """A code block. `run` executes it (per language); `err` = expected compile/SQL error code;
    `panic` = expected runtime panic; `stdin` feeds input; `file` labels the block."""

    def __init__(self, src, lang="rust", *, run=None, err=None, panic=False, stdin=None, file=None,
                 deps=None, requests=None, hl=(), args=None, show_output=True, label=None, test=False):
        self.src = src.strip("\n")
        self.lang = lang
        self.run = (lang in ("rust", "php", "mysql", "postgresql")) if run is None else run
        self.err, self.panic, self.stdin = err, panic, stdin
        self.file, self.deps, self.requests, self.hl, self.args = file, deps, requests, hl, args or []
        self.show_output, self.label, self.test = show_output, label, test
        self.result = None   # filled by the runner: dict(kind, text)


def code(src, lang="rust", **kw):
    return Code(src, lang, **kw)


def shell(src, out=None):
    """Terminal commands (shown, not run). `out` is a hand-written sample output."""
    c = Code(src, "console", run=False)
    c.sample = out
    return c


# ------------------------------------------------------------------ runners
def _hash(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:20]


class Results:
    def __init__(self):
        self.path = CACHE / "results.json"
        CACHE.mkdir(exist_ok=True)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def save(self):
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=1))


def _clean_rustc(text):
    text = re.sub(r"\n+For more information about (this|an) error.*", "", text, flags=re.S)
    text = re.sub(r"\n+error: aborting due to.*", "", text, flags=re.S)
    return text.strip()


def run_rust(c: Code, res: Results):
    key = _hash("rust", c.src, c.stdin, c.err, c.panic, c.args, c.test)
    if key in res.data:
        return res.data[key]
    d = CACHE / "rust" / key
    (d / "src").mkdir(parents=True, exist_ok=True)
    (d / "src/main.rs").write_text(c.src + "\n")
    extra = ["--test"] if c.test else []
    comp = subprocess.run(["rustc", "--edition", "2024", "--color", "never", *extra, "-o", "app", "src/main.rs"],
                          cwd=d, capture_output=True, text=True)
    if c.err:
        if comp.returncode == 0:
            raise SystemExit(f"expected compile error {c.err}, but it compiled:\n{c.src}")
        if c.err not in comp.stderr:
            raise SystemExit(f"expected {c.err}, got:\n{comp.stderr}\n{c.src}")
        out = dict(kind="error", text=_clean_rustc(comp.stderr))
    else:
        if comp.returncode != 0:
            raise SystemExit(f"compile failed:\n{comp.stderr}\n--- source ---\n{c.src}")
        if "warning" in comp.stderr:
            print(f"  ! warning:\n{comp.stderr}", file=sys.stderr)
        args = ["--test-threads=1"] if c.test else c.args   # one thread: stable test order
        r = subprocess.run([str(d / "app"), *args], input=c.stdin, capture_output=True, text=True, timeout=20, cwd=d)
        if c.test:
            r = subprocess.CompletedProcess(r.args, 0 if c.panic or r.returncode == 0 else r.returncode,
                                            re.sub(r"finished in [\d.]+s", "finished in 0.00s", r.stdout), r.stderr)
            if c.panic:   # a failing test is the point of the slide
                out = dict(kind="panic", text=r.stdout.rstrip())
                res.data[key] = out
                res.save()
                return out
        if c.panic:
            if r.returncode == 0:
                raise SystemExit(f"expected panic, got exit 0:\n{c.src}")
            err = re.sub(r"\nnote: run with `RUST_BACKTRACE.*", "", r.stderr).strip()
            out = dict(kind="panic", text=(r.stdout + err).strip())
        else:
            if r.returncode != 0:
                raise SystemExit(f"run failed ({r.returncode}):\n{r.stderr}\n{c.src}")
            out = dict(kind="out", text=r.stdout.rstrip(), stdin=c.stdin)
    res.data[key] = out
    res.save()
    return out


def _wait_port(port, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.2)
    return False


def run_cargo(c: Code, res: Results):
    key = _hash("cargo", c.src, c.deps, c.requests, c.stdin, c.err)
    if key in res.data:
        return res.data[key]
    d = CACHE / "cargo" / key
    (d / "src").mkdir(parents=True, exist_ok=True)
    deps = "\n".join(f"{k} = {v if v.startswith('{') else json.dumps(v)}" for k, v in (c.deps or {}).items())
    (d / "Cargo.toml").write_text(f'[package]\nname = "app"\nversion = "0.1.0"\nedition = "2024"\n\n[dependencies]\n{deps}\n')
    (d / "src/main.rs").write_text(c.src + "\n")
    env = {**os.environ, "CARGO_TARGET_DIR": str(CACHE / "target")}
    b = subprocess.run(["cargo", "build", "--color", "never", "-q"], cwd=d, capture_output=True, text=True, env=env)
    if c.err:
        if b.returncode == 0 or c.err not in b.stderr:
            raise SystemExit(f"expected cargo error {c.err}:\n{b.stderr}\n{c.src}")
        out = dict(kind="error", text=_clean_rustc(b.stderr))
    else:
        if b.returncode != 0:
            raise SystemExit(f"cargo build failed:\n{b.stderr}\n--- source ---\n{c.src}")
        if "warning" in b.stderr:
            print(f"  ! warning:\n{b.stderr}", file=sys.stderr)
        exe = CACHE / "target/debug/app"
        if c.requests:
            for f in ("shop.db", "shop.db-wal", "shop.db-shm"):
                (d / f).unlink(missing_ok=True)
            p = subprocess.Popen([str(exe)], cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 env={**env, "RUST_LOG": "info", "NO_COLOR": "1"}, start_new_session=True)
            try:
                if not _wait_port(3000):
                    raise SystemExit(f"server did not start:\n{c.src}")
                parts = []
                for cmd in c.requests:
                    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
                    parts.append(f"$ {cmd}\n{r.stdout.rstrip()}")
                out = dict(kind="http", text="\n\n".join(parts))
            finally:
                os.killpg(p.pid, signal.SIGTERM)
                p.wait(timeout=10)
        else:
            r = subprocess.run([str(exe)], cwd=d, input=c.stdin, capture_output=True, text=True, timeout=30, env=env)
            if r.returncode != 0 and not c.panic:
                raise SystemExit(f"run failed:\n{r.stderr}\n{c.src}")
            out = dict(kind="out", text=r.stdout.rstrip())
    res.data[key] = out
    res.save()
    return out


def run_php(c: Code, res: Results):
    key = _hash("php", c.src, c.stdin)
    if key in res.data:
        return res.data[key]
    d = CACHE / "php"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{key}.php"
    f.write_text(c.src + "\n")
    r = subprocess.run(["php", str(f)], input=c.stdin, capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        raise SystemExit(f"php failed:\n{r.stdout}{r.stderr}\n{c.src}")
    out = dict(kind="out", text=r.stdout.rstrip())
    res.data[key] = out
    res.save()
    return out


class SqlSession:
    """One fresh database per course; blocks run in order so they can build on each other."""

    def __init__(self, engine, db):
        self.engine, self.db = engine, db
        if engine == "mysql":
            self._mysql(f"DROP DATABASE IF EXISTS {db}; CREATE DATABASE {db} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;", use_db=False)
        else:
            subprocess.run(["psql", "-X", "-q", "-d", "postgres", "-c", f"DROP DATABASE IF EXISTS {db}"], check=True, capture_output=True)
            subprocess.run(["psql", "-X", "-q", "-d", "postgres", "-c", f"CREATE DATABASE {db}"], check=True, capture_output=True)

    def _mysql(self, sql, use_db=True):
        cmd = ["mysql", "-uroot", "--default-character-set=utf8mb4", "-t"] + ([self.db] if use_db else [])
        return subprocess.run(cmd, input=sql, capture_output=True, text=True, timeout=60)

    def run(self, c: Code):
        if self.engine == "mysql":
            r = self._mysql(c.src)
            text = (r.stdout + r.stderr).rstrip()
        else:
            r = subprocess.run(["psql", "-X", "-d", self.db, "-v", "ON_ERROR_STOP=1"], input=c.src,
                               capture_output=True, text=True, timeout=60)
            text = (r.stdout + r.stderr).rstrip()
            text = re.sub(r"^psql:<stdin>:\d+: ", "", text, flags=re.M)
        failed = r.returncode != 0 or "ERROR" in text
        if c.err:
            if not failed or c.err not in text:
                raise SystemExit(f"expected SQL error {c.err}, got:\n{text}\n{c.src}")
            return dict(kind="error", text=text)
        if failed:
            raise SystemExit(f"SQL failed:\n{text}\n--- source ---\n{c.src}")
        return dict(kind="out", text=text or "(কোনো আউটপুট নেই — কাজ সম্পন্ন)")


# ------------------------------------------------------------------ rendering
FORMATTER_OPTS = dict(nowrap=False, wrapcode=False, cssclass="hl")
LANG_LABEL = {"rust": "Rust", "php": "PHP", "mysql": "MySQL", "postgresql": "PostgreSQL", "toml": "TOML",
              "console": "Terminal", "bash": "Terminal", "sql": "SQL", "json": "JSON", "ini": ".env", "html": "HTML",
              "dockerfile": "Dockerfile", "nginx": "Nginx", "text": ""}
LEXER = {"mysql": "mysql", "postgresql": "postgresql", "console": "console", "ini": "ini", "php": "php"}


def hl_code(src, lang, hl_lines=()):
    name = LEXER.get(lang, lang)
    opts = {"startinline": True} if lang == "php" and not src.lstrip().startswith("<?php") else {}
    lexer = get_lexer_by_name(name, **opts)
    return highlight(src, lexer, HtmlFormatter(hl_lines=list(hl_lines), **FORMATTER_OPTS))


def render_code(c: Code):
    label = c.label or c.file or LANG_LABEL.get(c.lang, c.lang)
    cls = " php" if c.lang == "php" else ""
    head = f'<div class="code-h{cls}"><span>{e(label)}</span><button class="copy" type="button">কপি</button></div>'
    out = ""
    if getattr(c, "sample", None):
        out = f'<div class="term"><div class="term-h">উদাহরণ আউটপুট</div><pre>{e(c.sample)}</pre></div>'
    r = c.result
    if r and c.show_output:
        title = {"out": "cargo test" if c.test else "আউটপুট", "http": "Response (curl)", "error": "Compiler বলছে (ইচ্ছাকৃত ভুল)",
                 "panic": "Program থেমে গেল (panic)"}[r["kind"]]
        if c.test and r["kind"] == "panic":
            title = "cargo test — একটা test ব্যর্থ (ইচ্ছাকৃত)"
        if c.lang in ("mysql", "postgresql"):
            title = "ফলাফল" if r["kind"] == "out" else "Database বলছে (ইচ্ছাকৃত ভুল)"
        if c.lang == "php":
            title = "PHP আউটপুট"
        kind = r["kind"]
        r = {**r, "text": re.sub(r"thread '(\w+)' \(\d+\)", r"thread '\1'", r["text"])}   # drop the OS thread id
        stdin = f'<div class="stdin">ইনপুট: {e(r.get("stdin").strip())}</div>' if r.get("stdin") else ""
        out = (f'<div class="term {kind}"><div class="term-h">{title}</div>{stdin}'
               f'<pre>{e(r["text"]) if r["text"] else "(কিছু প্রিন্ট হয়নি)"}</pre></div>')
    return f'<div class="code{cls}">{head}{hl_code(c.src, c.lang, c.hl)}</div>{out}'


class Course:
    def __init__(self, *, slug, title, subtitle, folder, home="../index.html", hub="../../index.html", series="",
                 next_course=None, prev_course=None, sql_engine=None):
        self.slug, self.title, self.subtitle, self.folder = slug, title, subtitle, Path(folder)
        self.hub = hub
        self.home, self.series, self.next_course, self.prev_course = home, series, next_course, prev_course
        self.sql_engine = sql_engine
        self.slides, self.part, self.lesson_no = [], "", 0

    def section(self, name):
        self.part = name

    def cover(self, title, lead, learn=(), need=None):
        learn_html = "".join(f"<li>{x}</li>" for x in learn)
        need_html = f'<p class="need"><b>আগে জানা দরকার:</b> {need}</p>' if need else ""
        body = (f'<span class="tag">{e(self.series)}</span><h1>{title}</h1><p class="lead">{lead}</p>'
                f'<ul class="learn">{learn_html}</ul>{need_html}'
                f'<p class="howto">→ তীর চাপুন বা swipe করুন · <b>M</b> সব পাঠের তালিকা · অগ্রগতি নিজে থেকেই সেভ হয়</p>')
        self.slides.append(dict(part=self.part or "শুরু", title=re.sub("<[^>]+>", "", title), body=body, hero=True, codes=[]))

    def lesson(self, title, *blocks, tag=None):
        self.lesson_no += 1
        left = [b for b in blocks if not isinstance(b, Code)]
        right = [b for b in blocks if isinstance(b, Code)]
        self.slides.append(dict(part=self.part, title=title, tag=tag, left=left, codes=right, hero=False,
                                no=self.lesson_no))

    def finish(self, title, lead, recap=()):
        nxt = ""
        if self.next_course:
            href, name = self.next_course
            nxt = f'<a class="btn" href="{href}">পরের কোর্স: {e(name)} →</a>'
        home = (f'<a class="btn ghost" href="{self.home}">সব কোর্স</a>'
                f'<a class="btn ghost" href="{self.hub}">সব টিউটোরিয়াল</a>')
        rec = "".join(f"<div><i>✓</i><span>{x}</span></div>" for x in recap)
        body = (f'<span class="tag">শেষ</span><h1>{title}</h1><p class="lead">{lead}</p>'
                f'<div class="steps done">{rec}</div><div class="btns">{nxt}{home}</div>')
        self.slides.append(dict(part=self.part, title="শেষ", body=body, hero=True, codes=[], end=True))

    # ---- verify every runnable block, then write index.html
    def run_all(self):
        res = Results()
        sql = SqlSession(self.sql_engine, f"tut_{self.slug.replace('-', '_')}") if self.sql_engine else None
        n = 0
        for s in self.slides:
            for c in s["codes"]:
                if not c.run:
                    continue
                n += 1
                if c.lang == "rust" and c.deps is not None:
                    c.result = run_cargo(c, res)
                elif c.lang == "rust":
                    c.result = run_rust(c, res)
                elif c.lang == "php":
                    c.result = run_php(c, res)
                elif c.lang in ("mysql", "postgresql"):
                    c.result = sql.run(c)
        return n

    def render_slide(self, i, s):
        if s.get("hero"):
            cls = "slide hero" + (" end" if s.get("end") else "")
            return (f'<section class="{cls}" data-part="{e(s["part"])}" data-title="{e(s["title"])}">'
                    f'<div class="inner">{s["body"]}</div></section>')
        tag = f'পাঠ {bn(s["no"])}' + (f' · {s["tag"]}' if s.get("tag") else "")
        left = "".join(s["left"])
        right = "".join(render_code(c) for c in s["codes"])
        cols = "two" if left and right else "one"
        return (f'<section class="slide" data-part="{e(s["part"])}" data-title="{e(s["title"])}">'
                f'<div class="inner"><div class="head"><span class="tag">{tag}</span><h2>{s["title"]}</h2></div>'
                f'<div class="body {cols}"><div class="txt">{left}</div>'
                f'{f"<div class=codecol>{right}</div>" if right else ""}</div></div></section>')

    def build(self):
        t0 = time.time()
        n = self.run_all()
        secs = "\n".join(self.render_slide(i, s) for i, s in enumerate(self.slides))
        page = PAGE.format(title=e(self.title), subtitle=e(self.subtitle), slug=self.slug, home=self.home, hub=self.hub,
                           series=e(self.series), css=CSS + HL_CSS, js=JS, slides=secs,
                           fonts=FONTS)
        out = self.folder / "index.html"
        out.write_text(page, encoding="utf-8")
        meta = dict(slug=self.slug, title=self.title, subtitle=self.subtitle,
                    lessons=self.lesson_no, slides=len(self.slides))
        (self.folder / "course.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
        print(f"{self.slug}: {len(self.slides)} slides, {self.lesson_no} lessons, {n} code blocks verified "
              f"({time.time() - t0:.0f}s) -> {out}")
        return meta


def build_home(folder, title, lead, courses, extra="", hub="../index.html"):
    """Landing page: course cards with live progress read from localStorage."""
    cards = ""
    for i, (path, emoji) in enumerate(courses, 1):
        if not (Path(folder) / path / "course.json").exists():
            continue   # course not built yet
        meta = json.loads((Path(folder) / path / "course.json").read_text())
        cards += (f'<a class="card" href="{path}/index.html" data-slug="{meta["slug"]}" data-total="{meta["slides"]}">'
                  f'<span class="num">{bn(f"{i:02d}")}</span><span class="emoji">{emoji}</span>'
                  f'<b>{e(meta["title"])}</b><span class="sub">{e(meta["subtitle"])}</span>'
                  f'<span class="meta">{bn(meta["lessons"])}টি ছোট পাঠ</span>'
                  f'<span class="prog"><i></i></span><span class="state">শুরু করুন →</span></a>')
    page = HOME.format(title=e(title), lead=lead, cards=cards, css=CSS + HOME_CSS, fonts=FONTS, extra=extra, hub=hub)
    (Path(folder) / "index.html").write_text(page, encoding="utf-8")
    print(f"home -> {Path(folder) / 'index.html'}")


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">')

CSS = """
:root{--u:min(1vw,1.6vh);--navy:#0C1E38;--accent:#0D8A4A;--accent2:#E8F6EE;--amber:#B7791F;--red:#C53030;--php:#4F5B93;
  --bg:#F4F7FA;--ink:#18263A;--muted:#5B6B80;--card:#fff;--line:#DCE4EE;--codebg:#1E2430}
:root[data-theme=dark]{--bg:#0B1220;--ink:#E6EDF5;--muted:#98A7BA;--card:#131C2D;--line:#24324A;--navy:#fff;--accent:#34C77B;--accent2:#12301F;--amber:#E0A93B;--red:#F0716F;--php:#8892BF;color-scheme:dark}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0B1220;--ink:#E6EDF5;--muted:#98A7BA;--card:#131C2D;--line:#24324A;--navy:#fff;--accent:#34C77B;--accent2:#12301F;--amber:#E0A93B;--red:#F0716F;--php:#8892BF;color-scheme:dark}}
*{box-sizing:border-box;margin:0}
body{background:var(--bg);color:var(--ink);font-family:'Hind Siliguri','Noto Sans Bengali',system-ui,sans-serif}
.deck html,.deck body{height:100%}
body.deck{height:100vh;overflow:hidden}
#deck{height:100%;display:flex;transition:transform .4s cubic-bezier(.4,0,.2,1)}
.slide{flex:0 0 100vw;height:100%;overflow-y:auto;padding:60px 4vw 84px}
.slide .inner{max-width:1500px;margin:0 auto;min-height:100%;display:flex;flex-direction:column;justify-content:safe center;gap:2.2vh}
h1{font-size:clamp(28px,calc(var(--u)*5),76px);font-weight:700;line-height:1.2;color:var(--navy)}
h2{font-size:clamp(21px,calc(var(--u)*3),46px);font-weight:700;line-height:1.25;color:var(--navy)}
.lead{font-size:clamp(15px,calc(var(--u)*1.9),28px);color:var(--muted);max-width:36em;line-height:1.6}
.tag{display:inline-block;align-self:flex-start;background:var(--accent);color:#fff;font-weight:600;font-size:clamp(12px,calc(var(--u)*1.15),17px);padding:.3em 1em;border-radius:999px}
.head{display:flex;flex-direction:column;gap:1vh}
.body.two{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:3vw;align-items:start}
.body.one{max-width:1100px}
.txt{display:flex;flex-direction:column;gap:1.6vh}
.txt p,.txt li{font-size:clamp(15px,calc(var(--u)*1.6),24px);line-height:1.7}
.txt ul{list-style:none;padding:0;display:grid;gap:1vh}
.txt li{padding-left:1.3em;position:relative}
.txt li::before{content:"";position:absolute;left:0;top:.7em;width:.45em;height:.45em;border-radius:50%;background:var(--accent)}
code.i,.txt code{font-family:'JetBrains Mono',monospace;font-size:.86em;background:var(--accent2);color:var(--ink);padding:.08em .4em;border-radius:6px}
.callout{background:var(--card);border-left:5px solid var(--accent);border-radius:10px;padding:1.3vh 1.2vw;font-size:clamp(14px,calc(var(--u)*1.45),22px);line-height:1.65;box-shadow:0 4px 16px rgba(12,30,56,.07)}
.callout.warn{border-left-color:var(--amber)}
.callout.php{border-left-color:var(--php)}.callout.php b{color:var(--php);margin-right:.4em}
.callout.task{border-left-color:#7C3AED}.callout.task b{color:#7C3AED;margin-right:.4em}
.quiz{background:var(--card);border-radius:10px;padding:1.2vh 1.1vw;box-shadow:0 4px 16px rgba(12,30,56,.07)}
.quiz summary{cursor:pointer;font-weight:600;font-size:clamp(14px,calc(var(--u)*1.45),22px);line-height:1.5}
.quiz p{margin-top:.8vh;color:var(--accent);font-weight:600;font-size:clamp(14px,calc(var(--u)*1.4),21px);line-height:1.6}
.tbl{border-collapse:collapse;width:100%;background:var(--card);border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(12,30,56,.07)}
.tbl th,.tbl td{padding:.9vh .9vw;text-align:left;font-size:clamp(13px,calc(var(--u)*1.35),20px);border-bottom:1px solid var(--line);line-height:1.5}
.tbl th{background:var(--accent2);font-weight:600}
.steps{display:grid;gap:1vh}
.steps div{background:var(--card);border-radius:10px;padding:1.1vh 1vw;font-size:clamp(14px,calc(var(--u)*1.5),22px);display:flex;gap:.9vw;align-items:center;box-shadow:0 3px 12px rgba(12,30,56,.07);line-height:1.5}
.steps i{flex:0 0 auto;width:2em;height:2em;border-radius:50%;background:var(--accent);color:#fff;font-style:normal;font-weight:700;display:grid;place-items:center}
.codecol{display:flex;flex-direction:column;gap:1.2vh;min-width:0}
.code{background:var(--codebg);border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.18)}
.code-h{display:flex;justify-content:space-between;align-items:center;padding:7px 14px;background:#151A23;color:#9AA7B8;font:600 13px 'JetBrains Mono',monospace}
.code-h.php{background:#262B47;color:#C3C9EE}
.copy{border:0;background:#2A3242;color:#C9D4E3;font:600 12px 'Hind Siliguri',sans-serif;padding:3px 10px;border-radius:6px;cursor:pointer}
.copy:hover{background:var(--accent);color:#fff}
.hl pre{margin:0;padding:12px 16px;overflow-x:auto;font:clamp(12.5px,calc(var(--u)*1.08),17px)/1.55 'JetBrains Mono',monospace;color:#E3E8EF;tab-size:4}
.hl .hll{background:rgba(255,214,102,.13);display:inline-block;width:100%}
.term{border-radius:12px;overflow:hidden;border:1px solid var(--line);background:#0F141C}
.term-h{padding:5px 14px;background:#0D8A4A;color:#fff;font:600 13px 'Hind Siliguri',sans-serif}
.term.error .term-h,.term.panic .term-h{background:#B83434}
.term.http .term-h{background:#1F5FA8}
.term pre{margin:0;padding:10px 16px;overflow-x:auto;font:clamp(12px,calc(var(--u)*1),15px)/1.5 'JetBrains Mono',monospace;color:#D5DEE9;white-space:pre}
pre,code{font-variant-ligatures:none;font-feature-settings:'liga' 0,'calt' 0}  /* show <= -> => as typed */
.term.error pre,.term.panic pre{color:#FFB4B4}
.stdin{padding:6px 16px 0;color:#9FE6BE;font:600 13px 'JetBrains Mono',monospace}
.hero{background:radial-gradient(ellipse at 30% 20%,#173a66 0%,#0C1E38 70%);color:#fff}
.hero .inner{justify-content:center;max-width:1100px}
.hero h1{color:#fff}.hero .lead{color:#CFDDEE}
.hero .learn{list-style:none;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:1vh 2vw}
.hero .learn li{font-size:clamp(14px,calc(var(--u)*1.55),23px);padding-left:1.4em;position:relative;line-height:1.5;color:#E6EEF8}
.hero .learn li::before{content:"✓";position:absolute;left:0;color:#4ADE80;font-weight:700}
.hero .need,.hero .howto{color:#AFC2D8;font-size:clamp(13px,calc(var(--u)*1.35),20px)}
.hero .need b{color:#fff}
.hero.end .steps div{background:rgba(255,255,255,.08);color:#fff;box-shadow:none}
.hero.end .steps i{background:#4ADE80;color:#0C1E38}
.btns{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-block;background:#4ADE80;color:#0C1E38;font-weight:700;text-decoration:none;padding:.7em 1.4em;border-radius:999px;font-size:clamp(14px,calc(var(--u)*1.5),21px)}
.btn.ghost{background:transparent;color:#fff;border:2px solid rgba(255,255,255,.5)}
#top{position:fixed;top:0;left:0;right:0;height:44px;display:flex;align-items:center;gap:12px;padding:0 16px;z-index:6;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);font-size:14px}
#top a{color:var(--accent);font-weight:600;text-decoration:none;white-space:nowrap}
#top .crumb{color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}
#top .hub{border:1px solid var(--line);border-radius:999px;padding:2px 12px}
#bar{position:fixed;left:0;top:44px;height:3px;background:var(--accent);transition:width .4s;z-index:7}
#nav{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);display:flex;gap:8px;align-items:center;font:600 14px 'Hind Siliguri',sans-serif;color:#fff;z-index:7;background:rgba(12,30,56,.9);padding:6px 10px;border-radius:999px;white-space:nowrap}
#nav button{border:0;background:rgba(255,255,255,.14);color:#fff;width:38px;height:38px;border-radius:50%;font-size:17px;cursor:pointer}
#nav button:hover{background:var(--accent)}
#count{min-width:64px;text-align:center}
#menu{position:fixed;inset:0;background:rgba(8,15,28,.94);z-index:9;display:none;overflow:auto;padding:5vh 6vw}
#menu.open{display:block}
#menu h3{color:#fff;font-size:20px;margin:2.4vh 0 .8vh}
#menu a{display:flex;gap:.6em;color:#dbe7f5;text-decoration:none;padding:.55vh 1vw;border-radius:8px;font-size:17px;cursor:pointer}
#menu a.seen::after{content:"✓";color:#4ADE80;margin-left:auto}
#menu a.cur{background:rgba(74,222,128,.18)}
#menu a:hover{background:var(--accent);color:#fff}
#resume{position:fixed;left:50%;top:60px;transform:translateX(-50%);background:var(--card);color:var(--ink);border:1px solid var(--line);box-shadow:0 10px 30px rgba(0,0,0,.25);border-radius:14px;padding:12px 16px;z-index:8;display:none;gap:10px;align-items:center;font-size:15px;flex-wrap:wrap;justify-content:center}
#resume.show{display:flex}
#resume button{border:0;border-radius:999px;padding:6px 14px;font:600 14px 'Hind Siliguri',sans-serif;cursor:pointer;background:var(--accent);color:#fff}
#resume button.alt{background:var(--line);color:var(--ink)}
@media (max-width:900px){body.deck{overflow:hidden}.slide{padding:56px 5vw 96px}.body.two{grid-template-columns:1fr}.hero .learn{grid-template-columns:1fr}}
@media print{#nav,#bar,#top,#menu,#resume{display:none!important}body.deck{overflow:visible;height:auto}#deck{display:block;transform:none!important}.slide{height:auto;min-height:100vh;page-break-after:always}}
"""

# One Dark-like palette, class based (Pygments short names)
HL_CSS = """
.hl .c,.hl .c1,.hl .cm,.hl .cs,.hl .ch,.hl .cp,.hl .cpf{color:#7F8C98;font-style:italic}
.hl .k,.hl .kd,.hl .kn,.hl .kr,.hl .kp,.hl .ow{color:#C678DD}
.hl .kc{color:#D19A66}
.hl .kt,.hl .nc,.hl .nn{color:#E5C07B}
.hl .s,.hl .s1,.hl .s2,.hl .sb,.hl .sc,.hl .sd,.hl .sh,.hl .sx,.hl .dl{color:#98C379}
.hl .se,.hl .si,.hl .sa{color:#56B6C2}
.hl .m,.hl .mi,.hl .mf,.hl .mh,.hl .mb,.hl .il,.hl .mo{color:#D19A66}
.hl .nf,.hl .fm{color:#61AFEF}
.hl .nb,.hl .bp{color:#56B6C2}
.hl .nd,.hl .nl{color:#E06C75}
.hl .nt{color:#E06C75}.hl .na{color:#D19A66}
.hl .nv,.hl .vi,.hl .vc,.hl .vg{color:#E06C75}
.hl .o{color:#ABB2BF}.hl .p{color:#ABB2BF}
.hl .gp{color:#4ADE80;font-weight:600;user-select:none}.hl .go{color:#9AA7B8}
.hl .err{color:#E3E8EF;background:none}
"""

PAGE = """<!doctype html>
<html lang="bn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{subtitle}">
{fonts}
<style>{css}</style>
</head>
<body class="deck">
<div id="top"><a href="{home}">← সব কোর্স</a><span class="crumb">{series} · <b id="part"></b></span><a class="hub" href="{hub}">সব টিউটোরিয়াল</a></div>
<div id="bar"></div>
<div id="resume"><span id="resumeText"></span><button id="resumeGo">চালিয়ে যান</button><button class="alt" id="resumeNo">শুরু থেকে</button></div>
<main id="deck">
{slides}
</main>
<div id="menu"></div>
<div id="nav"><button id="prev" aria-label="আগের">‹</button><span id="count"></span><button id="next" aria-label="পরের">›</button><button id="menuBtn" title="সব পাঠ (M)" aria-label="সব পাঠ">☰</button><button id="fs" title="Fullscreen (F)" aria-label="Fullscreen">⛶</button><button id="theme" title="Dark mode (D)" aria-label="Theme">◐</button></div>
<script>window.COURSE="{slug}";{js}</script>
</body>
</html>
"""

JS = r"""
(function(){
  var B=function(n){return String(n).replace(/\d/g,function(d){return '০১২৩৪৫৬৭৮৯'[d]})};
  var deck=document.getElementById('deck'),slides=[].slice.call(deck.children),n=slides.length,i=0,root=document.documentElement;
  var bar=document.getElementById('bar'),count=document.getElementById('count'),part=document.getElementById('part'),menu=document.getElementById('menu');
  var KEY='tut:'+window.COURSE,st={last:0,seen:{}};
  try{var s=JSON.parse(localStorage.getItem(KEY)||'null');if(s)st=s}catch(e){}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
  function go(k){i=Math.max(0,Math.min(n-1,k));deck.style.transform='translateX(-'+(i*100)+'vw)';
    bar.style.width=((i+1)/n*100)+'%';count.textContent=B(i+1)+' / '+B(n);part.textContent=slides[i].getAttribute('data-part')||'';
    st.last=i;st.seen[i]=1;st.total=n;save();slides[i].scrollTop=0;
    try{history.replaceState(null,'','#'+(i+1))}catch(e){}}
  function buildMenu(){var h='',last=null;slides.forEach(function(s,j){var p=s.getAttribute('data-part');if(p!==last){h+='<h3>'+p+'</h3>';last=p}
    h+='<a data-go="'+j+'" class="'+(st.seen[j]?'seen ':'')+(j===i?'cur':'')+'"><span>'+B(j+1)+'.</span><span>'+s.getAttribute('data-title')+'</span></a>'});menu.innerHTML=h}
  function toggleMenu(){if(!menu.classList.contains('open'))buildMenu();menu.classList.toggle('open')}
  function toggleFs(){try{document.fullscreenElement?document.exitFullscreen():root.requestFullscreen()}catch(e){}}
  function toggleTheme(){var dark=getComputedStyle(root).getPropertyValue('--bg').trim()==='#0B1220';var t=dark?'light':'dark';root.setAttribute('data-theme',t);try{localStorage.setItem('tut-theme',t)}catch(e){}}
  try{var th=localStorage.getItem('tut-theme');if(th)root.setAttribute('data-theme',th)}catch(e){}
  menu.addEventListener('click',function(e){var a=e.target.closest('a');if(a){go(+a.getAttribute('data-go'));menu.classList.remove('open')}else if(e.target===menu)menu.classList.remove('open')});
  document.getElementById('prev').onclick=function(){go(i-1)};
  document.getElementById('next').onclick=function(){go(i+1)};
  document.getElementById('menuBtn').onclick=toggleMenu;
  document.getElementById('fs').onclick=toggleFs;
  document.getElementById('theme').onclick=toggleTheme;
  document.addEventListener('click',function(e){var b=e.target.closest('.copy');if(!b)return;
    var pre=b.closest('.code').querySelector('pre');var t=pre.innerText.replace(/^\$ /gm,'');
    var done=function(){b.textContent='কপি হয়েছে ✓';setTimeout(function(){b.textContent='কপি'},1500)};
    if(navigator.clipboard)navigator.clipboard.writeText(t).then(done,done);else done()});
  document.addEventListener('keydown',function(e){
    if(e.target.tagName==='SUMMARY'&&(e.key===' '||e.key==='Enter'))return;
    if(e.metaKey||e.ctrlKey||e.altKey)return;
    if(e.key==='Escape'){menu.classList.remove('open');return}
    if(['ArrowRight','PageDown'].indexOf(e.key)>-1){e.preventDefault();go(i+1)}
    else if(['ArrowLeft','PageUp'].indexOf(e.key)>-1){e.preventDefault();go(i-1)}
    else if(e.key==='Home')go(0);else if(e.key==='End')go(n-1);
    else if(e.key==='f'||e.key==='F')toggleFs();
    else if(e.key==='d'||e.key==='D')toggleTheme();
    else if(e.key==='m'||e.key==='M')toggleMenu();});
  var x0=null,y0=null;
  document.addEventListener('touchstart',function(e){x0=e.touches[0].clientX;y0=e.touches[0].clientY},{passive:true});
  document.addEventListener('touchend',function(e){if(x0===null)return;var dx=e.changedTouches[0].clientX-x0,dy=e.changedTouches[0].clientY-y0;
    if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy)*1.5&&!e.target.closest('pre'))go(i+(dx<0?1:-1));x0=null});
  var h=parseInt((location.hash||'').slice(1),10);
  if(!isNaN(h)){go(h-1)}else{var last=st.last||0;go(0);
    if(last>0){var r=document.getElementById('resume');document.getElementById('resumeText').textContent='আগেরবার স্লাইড '+B(last+1)+' পর্যন্ত পড়েছিলেন।';
      r.classList.add('show');document.getElementById('resumeGo').onclick=function(){go(last);r.classList.remove('show')};
      document.getElementById('resumeNo').onclick=function(){r.classList.remove('show')};}}
})();
"""

HOME_CSS = """
body.home{min-height:100vh}
.wrap{max-width:1180px;margin:0 auto;padding:56px 20px 64px}
.home header{background:radial-gradient(ellipse at 30% 20%,#173a66 0%,#0C1E38 70%);color:#fff}
.home header .wrap{padding:56px 20px 48px}
.home header h1{color:#fff}
.home header .back{display:inline-block;color:#9FE6BE;text-decoration:none;font-weight:600;margin-bottom:14px}.home header .lead{color:#CFDDEE;margin-top:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:18px;margin-top:-28px}
.card{position:relative;display:flex;flex-direction:column;gap:6px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px;text-decoration:none;color:var(--ink);box-shadow:0 8px 26px rgba(12,30,56,.08);transition:transform .15s}
.card:hover{transform:translateY(-3px);border-color:var(--accent)}
.card .num{position:absolute;right:18px;top:16px;color:var(--muted);font-weight:700}
.card .emoji{font-size:30px}
.card b{font-size:21px;color:var(--navy)}
.card .sub{color:var(--muted);line-height:1.5;font-size:15px;flex:1}
.card .meta{font-size:14px;color:var(--muted)}
.card .prog{height:6px;background:var(--line);border-radius:9px;overflow:hidden}
.card .prog i{display:block;height:100%;width:0;background:var(--accent)}
.card .state{color:var(--accent);font-weight:700}
.home .note{margin-top:28px;color:var(--muted);line-height:1.7}
.home .note code{font-family:'JetBrains Mono',monospace;background:var(--accent2);padding:.1em .4em;border-radius:6px}
"""

HOME = """<!doctype html>
<html lang="bn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{fonts}
<style>{css}</style>
</head>
<body class="home">
<header><div class="wrap"><a class="back" href="{hub}">← সব টিউটোরিয়াল</a><h1>{title}</h1><p class="lead">{lead}</p></div></header>
<main class="wrap" style="padding-top:0"><div class="grid">{cards}</div>{extra}</main>
<script>
var B=function(n){{return String(n).replace(/\\d/g,function(d){{return '০১২৩৪৫৬৭৮৯'[d]}})}};
document.querySelectorAll('.card').forEach(function(c){{var st=null;try{{st=JSON.parse(localStorage.getItem('tut:'+c.dataset.slug)||'null')}}catch(e){{}}
  if(!st)return;var seen=Object.keys(st.seen||{{}}).length,total=+c.dataset.total,p=Math.min(100,Math.round(seen/total*100));
  c.querySelector('.prog i').style.width=p+'%';
  c.querySelector('.state').textContent=p>=100?'শেষ ✓ আবার দেখুন':'চালিয়ে যান · '+B(p)+'% →';
  c.href=c.getAttribute('href').split('#')[0]+'#'+((st.last||0)+1)}});
try{{var th=localStorage.getItem('tut-theme');if(th)document.documentElement.setAttribute('data-theme',th)}}catch(e){{}}
</script>
</body>
</html>
"""


def build_hub(folder, title, lead, tutorials, extra=""):
    """Top-level index: one card per tutorial series. tutorials = (path, emoji, title, desc, meta)."""
    cards = ""
    tutorials = [t for t in tutorials if (Path(folder) / t[0] / "index.html").exists()]
    for i, (path, emoji, name, desc, meta) in enumerate(tutorials, 1):
        cards += (f'<a class="card" href="{path}/index.html"><span class="num">{bn(f"{i:02d}")}</span>'
                  f'<span class="emoji">{emoji}</span><b>{e(name)}</b><span class="sub">{desc}</span>'
                  f'<span class="meta">{meta}</span><span class="state">খুলুন →</span></a>')
    page = HOME.format(title=e(title), lead=lead, cards=cards, css=CSS + HOME_CSS + ".home header .back{display:none}",
                       fonts=FONTS, extra=extra, hub="#")
    (Path(folder) / "index.html").write_text(page, encoding="utf-8")
    print(f"hub -> {Path(folder) / 'index.html'}")


def series_meta(folder):
    """'N টি কোর্স · M টি পাঠ' from the course.json files under a series folder."""
    metas = [json.loads(p.read_text()) for p in sorted(Path(folder).glob("*/course.json"))]
    return f"{bn(len(metas))}টি কোর্স · {bn(sum(m['lessons'] for m in metas))}টি ছোট পাঠ"
