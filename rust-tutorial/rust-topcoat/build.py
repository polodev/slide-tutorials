"""Rust Topcoat — Tokio-র full-stack web framework (axum-এর উপর), explained for Laravel developers.
Every server example is compiled, started and called with curl; interactive examples are bundled with the
Topcoat CLI and driven in headless Chromium. Real output everywhere.  Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
from kit import Course, code, jargon, php_note, points, quiz, say, shell, steps, table, task, tip, warn  # noqa: E402

HOME = "curl -s http://localhost:3000/"


def tc(src, requests=(HOME,), **kw):
    """Topcoat server example: compile, start, curl."""
    return code(src, "rust", topcoat="html", requests=list(requests), **kw)


def tcr(src, actions=(), **kw):
    """Topcoat runtime example: bundle assets, open in a real browser, click/type, screenshot."""
    return code(src, "rust", topcoat="runtime", actions=list(actions), requests=[], **kw)


def laravel(src, label="Laravel-এ"):
    return code(src, "php", run=False, label=label)


c = Course(slug="rust-topcoat", title="Rust Topcoat — Tokio-র Full-stack Framework", folder=HERE,
           subtitle="axum-এর উপর বানানো server-first framework: view! macro, async component, module routing, আর WebAssembly ছাড়া browser interactivity",
           series="Rust Topcoat", prev_course=("../rust-leptos/index.html", "Rust Leptos — Reactive Full-stack Web"))

c.cover("Rust Topcoat<br>Tokio-র Full-stack Framework",
        "Tokio আর axum যারা বানিয়েছেন, সেই টিমেরই নতুন framework: Laravel-এর মতো page, layout, route, form — সব Rust-এ, আর interactivity আসে WebAssembly ছাড়াই। প্রতিটি উদাহরণ আসলেই চালানো।",
        learn=["Topcoat কী আর Leptos/axum থেকে কীভাবে আলাদা", "view! macro: if, for, match", "async component আর child",
               "Module routing, layout, path/query parameter", "API route আর error", "Request context (Cx) আর shared app state",
               "Form আর redirect", "$() runtime: signal, event, procedure, shard"],
        need="Rust 101–103 আর Rust Web Development (axum)। Leptos পড়া থাকলে তুলনা বুঝতে সুবিধা।")


# ================================================================== শুরু
c.section("শুরু")
c.lesson("Topcoat কী?",
    say("Topcoat হলো Tokio টিমের (Carl Lerche ও Julien Scholz) বানানো full-stack web framework। এটা <b>axum-এর উপর</b> বসানো — axum যেখানে শুধু HTTP, Topcoat সেখানে page, layout, form, session আর browser interactivity-ও দেয়।"),
    points("<b>Server-first</b> — HTML বানানো হয় server-এ (Rust-এ)",
           "<b>WebAssembly নেই</b> — browser-এর অংশটুকু ছোট JavaScript-এ compile হয়",
           "Component <b>async</b> — সরাসরি database query করা যায়",
           "Module tree থেকেই URL (<code>src/app/about.rs</code> → <code>/about</code>)"),
    warn("Topcoat এখনো <b>early-stage ও experimental</b> (0.10)। API বদলাতে পারে — শেখার জন্য দারুণ, কিন্তু গুরুত্বপূর্ণ production app এখনই এতে সরাবেন না।"))

c.lesson("Laravel-এর সাথে মিল",
    table(["Laravel", "Topcoat"], [
        ["<code>routes/web.php</code> + controller", "<code>#[page]</code> function; path আসে module থেকে"],
        ["Blade template", "<code>view!</code> macro"],
        ["Blade component", "<code>#[component]</code> async function"],
        ["<code>layouts/app.blade.php</code> + <code>@yield</code>", "<code>#[layout]</code> + <code>Slot</code>"],
        ["<code>routes/api.php</code>", "<code>#[route(GET)]</code>"],
        ["<code>$request</code>, <code>app()</code>", "<code>cx: &amp;Cx</code>, <code>app_context</code>"],
        ["Livewire / Alpine.js", "<code>$()</code> runtime: signal, <code>@click</code>, shard"],
        ["Middleware", "সাধারণ function (<code>cx</code> নিয়ে) — আর দরকারে <code>#[layer]</code>"]]))

c.lesson("Leptos, axum আর Topcoat",
    table(["", "axum", "Leptos", "Topcoat"], [
        ["কী", "HTTP framework", "Reactive UI framework", "Server-first full-stack framework"],
        ["Browser code", "—", "Rust → WebAssembly", "Rust expression → JavaScript"],
        ["Interactivity", "নিজে লিখুন", "Fine-grained signal", "<code>$()</code> + signal + shard"],
        ["উপযোগী", "API", "Rich client app", "Content/form-ভিত্তিক site, dashboard"]]),
    tip("তিনটা প্রতিযোগী নয় — Topcoat axum-এর উপরেই চলে। Rust Web Development-এ যা শিখেছেন (async, handler, JSON) সবই কাজে লাগবে।"))

c.lesson("Topcoat-এর জার্গন: server-first",
    jargon(("Server-first", "প্রধান কাজ server-এ; browser-এ শুধু যতটুকু না হলেই নয়"),
           ("Async component", "component-এর ভিতরে <code>.await</code> করা যায় — database query সরাসরি"),
           ("Layout", "অনেক page-এর সাধারণ খোল (nav, footer) — Blade-এর <code>@extends</code>"),
           ("Routing", "URL দেখে কোন code চলবে তা ঠিক করা; Topcoat-এ module tree-ই"),
           ("RPC (Remote Procedure Call)", "দূরের function-কে নিজের function-এর মতো ডাকা — <code>#[procedure]</code> এমনই"),
           ("Early-stage / experimental", "API বদলাবে — production-এ ঝুঁকি আছে")))

c.lesson("Project বানানো",
    say("Cargo project, দুটো dependency, আর একটা CLI (dev server আর asset bundling-এর জন্য)।"),
    shell('''cargo new rahim-shop && cd rahim-shop
cargo add topcoat
cargo add tokio --features rt-multi-thread,macros

cargo install topcoat-cli     # topcoat dev, topcoat fmt, topcoat asset bundle
topcoat dev                   # build + চালু + কোড বদলালে auto rebuild'''),
    tip("<code>cargo run</code>-ও চলে — server <code>http://127.0.0.1:3000</code>-এ। Port বদলাতে <code>HOST</code> আর <code>PORT</code> environment variable।"))

c.lesson("প্রথম Hello, World!",
    say("সবচেয়ে ছোট Topcoat app। <code>#[page]</code> একটা URL-এর handler, <code>view!</code> HTML বানায়, আর <code>#[component]</code> function view-এর ভিতর থেকে <b>নাম ধরে</b> ডাকা যায়: <code>hello(name: \"World\")</code>। নিচে server-এর আসল response।"),
    tc(r'''
use topcoat::{
    Result,
    router::{module_router, page},
    view::{View, component, view},
};

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[page]
async fn home() -> Result<impl View> {
    Ok(view! {
        <!DOCTYPE html>
        <html>
            <head>
                <title>"Hello world"</title>
            </head>
            <body>
                hello(name: "World")
            </body>
        </html>
    })
}

#[component]
async fn hello(name: &str) -> Result<impl View> {
    Ok(view! {
        <h1>"Hello, " (name) "!"</h1>
    })
}
''', requests=["curl -si http://localhost:3000/", "curl -si http://localhost:3000/nope"]),
    php_note("<code>Route::get('/', fn () =&gt; view('home'))</code>-এর জায়গায় <code>#[page]</code> function। আর কোনো route ফাইল নেই।"))

# ================================================================== view!
c.section("view! macro")
c.lesson("Text আর element",
    say("<code>view!</code>-এ HTML-এর মতোই লেখা হয়, তবে নিয়ম কয়েকটা: text সবসময় quote-এ (<code>\"...\"</code>), void tag (<code>&lt;br&gt;</code>, <code>&lt;img&gt;</code>) বন্ধ করতে হয় না, বাকি tag বন্ধ করতেই হয়।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, view}};

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[page]
async fn home() -> Result<impl View> {
    Ok(view! {
        <h1>"Rahim Mobile"</h1>
        <label for="q">"খুঁজুন"</label>
        <input type="text" id="q" aria-label="Product search">
        <hr>
        <p>"Mirpur · Uttara · Gulshan"</p>
    })
}
'''))

c.lesson("Rust value বসানো: ( )",
    say("Blade-এ <code>{{ $name }}</code>, Topcoat-এ <code>(name)</code> — গোল বন্ধনীর ভিতরে যেকোনো Rust expression। Text-এ আর attribute-এর মান — দুই জায়গাতেই।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, view}};

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[page]
async fn home() -> Result<impl View> {
    let name = "Samsung A55";
    let price = 41500;
    let url = "/products/2";
    Ok(view! {
        <p>(name) " — " (price) " Taka"</p>
        <p>"VAT সহ: " (price * 115 / 100)</p>
        <a href=(url)>"বিস্তারিত"</a>
    })
}
'''),
    php_note("Blade-এর <code>{{ }}</code>-এর মতো এখানেও value HTML-escape হয়ে বসে — user-এর লেখা সরাসরি HTML হবে না।"))

c.lesson("Escape নিজে নিজে",
    say("User-এর input যা-ই হোক, <code>( )</code> সেটা escape করে — XSS-এর সবচেয়ে সাধারণ ফাঁদ থেকে বাঁচায়।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, view}};

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[page]
async fn home() -> Result<impl View> {
    let comment = "<script>alert('hacked')</script>";
    Ok(view! { <p>(comment)</p> })
}
'''))

c.lesson("if: শর্ত",
    say("<code>if</code>, <code>else if</code>, <code>else</code> — সরাসরি Rust-এর মতো, ভিতরে markup। Attribute-এর জায়গাতেও চলে (শর্ত মিললে attribute যোগ হবে)।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, view}};

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[page]
async fn home() -> Result<impl View> {
    let stock = 2;
    Ok(view! {
        if stock > 5 {
            <p>"স্টকে আছে"</p>
        } else if stock > 0 {
            <p class="low">"মাত্র " (stock) " টি বাকি!"</p>
        } else {
            <p>"স্টক শেষ"</p>
        }
        <a href="/cart" if stock < 5 { aria-label="কম স্টক" class="warn" }>"Cart"</a>
    })
}
'''),
    php_note("<code>@if ($stock &gt; 5) ... @elseif ... @else ... @endif</code> — একই গঠন, শুধু <code>@</code> আর <code>end...</code> ছাড়া।"))

c.lesson("for: list",
    say("<code>for item in list { ... }</code> — <code>@foreach</code>-এর জায়গায় সাধারণ Rust loop।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, view}};

struct Product { name: &'static str, price: u32 }

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[page]
async fn home() -> Result<impl View> {
    let products = vec![
        Product { name: "iPhone 15", price: 112000 },
        Product { name: "Samsung A55", price: 41500 },
        Product { name: "Redmi 13", price: 18500 },
    ];
    Ok(view! {
        <ul>
            for p in products {
                <li>(p.name) " — " (p.price) " Taka"</li>
            }
        </ul>
    })
}
'''))

c.lesson("match: enum দেখে view",
    say("Rust-এর সবচেয়ে প্রিয় জিনিস — <code>match</code> — এখানেও। প্রতিটা arm একটা view node; একাধিক হলে <code>{ }</code> দিয়ে মুড়ে নিন।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, view}};

enum Payment { Cash, Bkash { number: &'static str }, Due(u32) }

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[page]
async fn home() -> Result<impl View> {
    let payments = vec![Payment::Cash, Payment::Bkash { number: "01711-000000" }, Payment::Due(5000)];
    Ok(view! {
        <ul>
            for p in payments {
                <li>
                    match p {
                        Payment::Cash => "নগদ",
                        Payment::Bkash { number } => <span>"bKash: " (number)</span>,
                        Payment::Due(amount) => <b>"বাকি " (amount) " Taka"</b>,
                    }
                </li>
            }
        </ul>
    })
}
'''),
    tip("সব case না ঢাকলে compile error — তাই \"এই status-এর view লিখতে ভুলে গেছি\" ধরনের bug production-এ পৌঁছায় না।"))

c.lesson("let: মাঝপথে নাম দেওয়া",
    say("Markup-এর ভিতরেই <code>let</code> দিয়ে একটা হিসাব রেখে পরের node-এ ব্যবহার করা যায়।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, view}};

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[page]
async fn home() -> Result<impl View> {
    let price = 18500u32;
    let qty = 3u32;
    Ok(view! {
        <article>
            let subtotal = price * qty;
            let vat = subtotal * 15 / 100;
            <p>"Subtotal: " (subtotal)</p>
            <p>"VAT: " (vat)</p>
            <p><b>"Total: " (subtotal + vat)</b></p>
        </article>
    })
}
'''))

# ================================================================== Component
c.section("Component")
c.lesson("Component: নাম ধরে argument",
    say("<code>#[component]</code> দেওয়া async function। ডাকার সময় <code>নাম: মান</code>, কমা দিয়ে। Rust compiler type মিলিয়ে দেখে — ভুল type দিলে compile-ই হবে না।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, component, view}};

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[component]
async fn product_card(name: &str, price: u32) -> Result<impl View> {
    Ok(view! {
        <div class="card">
            <h3>(name)</h3>
            <p>(price) " Taka"</p>
        </div>
    })
}

#[page]
async fn home() -> Result<impl View> {
    Ok(view! {
        product_card(name: "iPhone 15", price: 112000)
        product_card(name: "Redmi 13", price: 18500)
    })
}
'''),
    php_note("Blade: <code>&lt;x-product-card name=\"...\" price=\"...\" /&gt;</code>। পার্থক্য: <code>:price</code>-এর জন্য আলাদা বাঁধন নেই, আর type compile-time-এ যাচাই হয়।"))

c.lesson("ভুল argument = compile error",
    say("Blade-এ ভুল prop চুপচাপ চলে যায়। এখানে <code>price</code>-এ text দিলে program build-ই হয় না।"),
    code(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, component, view}};

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[component]
async fn product_card(name: &str, price: u32) -> Result<impl View> {
    Ok(view! { <p>(name) ": " (price)</p> })
}

#[page]
async fn home() -> Result<impl View> {
    Ok(view! { product_card(name: "iPhone 15", price: "costly") })
}
''', "rust", topcoat="html", requests=[], err="E0308"))

c.lesson("Child: ভিতরে content",
    say("Component-এর ভিতরে যা লেখা হয় সেটা <code>child</code> হয়ে আসে। Parameter-এ <code>#[default] child: Child&lt;'_&gt;</code> রাখলে call-এ নাম ছাড়াই markup বসানো যায় — Blade-এর <code>{{ $slot }}</code>।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{Child, View, component, view}};

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[component]
async fn panel(title: &str, #[default] child: Child<'_>) -> Result<impl View> {
    Ok(view! {
        <section class="panel">
            <h3>(title)</h3>
            (child)
        </section>
    })
}

#[page]
async fn home() -> Result<impl View> {
    Ok(view! {
        panel(title: "Invoice INV-1001",
            <p>"Customer: Karim"</p>
            <p>"Total: 23500 Taka"</p>
        )
    })
}
'''),
    php_note("<code>&lt;x-panel title=\"...\"&gt; ... &lt;/x-panel&gt;</code> আর ভিতরে <code>{{ $slot }}</code>।"))

c.lesson("class!: শর্ত অনুযায়ী CSS class",
    say("<code>class!(\"base\", \"active\" if শর্ত)</code> — base class সবসময়, বাকিগুলো শর্ত মিললে। হাতে string জোড়া লাগাতে হয় না।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, class, view}};

#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}

#[page]
async fn home() -> Result<impl View> {
    let stock = 1;
    Ok(view! {
        <p class=(class!("stock", "low" if stock < 5, "empty" if stock == 0))>
            "স্টক: " (stock)
        </p>
    })
}
'''),
    php_note("Blade-এর <code>@class(['stock', 'low' =&gt; $stock &lt; 5])</code>।"))


# ================================================================== Router
c.section("Router")
MAIN_ROUTER = r'''
#[tokio::main]
async fn main() {
    topcoat::start(module_router!().build()).await.unwrap();
}
'''

MAIN_DISCOVER = r'''
#[tokio::main]
async fn main() {
    topcoat::start(module_router!().discover().build()).await.unwrap();
}
'''

c.lesson("Module routing: ফাইলই route",
    say("Laravel-এ <code>routes/web.php</code>-এ লিখতে হয়। Topcoat-এ <b>module tree-ই route table</b>: root module <code>/</code>, আর <code>mod about;</code> দিলে <code>about.rs</code>-এর page হয় <code>/about</code>। Function-এর নাম URL-এ কিছু করে না।"),
    code('''src/
├── main.rs          →  /        (mod about; mod posts;)
├── about.rs         →  /about
├── posts.rs         →  /posts
└── posts/
    └── post_id.rs   →  /posts/{post_id}''', "text", run=False, label="ফোল্ডার"),
    tip("আলাদা কোনো build step নেই — <code>module_router!()</code> macro compile-এর সময় module tree দেখে route বানায়।"))

ABOUT_RS = r'''
use topcoat::{Result, router::page, view::{View, view}};

#[page]
async fn about() -> Result<impl View> {
    Ok(view! { <h1>"আমাদের সম্পর্কে"</h1><p>"Rahim Mobile — Mirpur, Uttara, Gulshan"</p> })
}
'''
c.lesson("দ্বিতীয় page: about.rs",
    say("<code>main.rs</code>-এ শুধু <code>mod about;</code> যোগ করুন, আর <code>src/about.rs</code>-এ একটা <code>#[page]</code>।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, view}};

mod about;
''' + MAIN_ROUTER + r'''
#[page]
async fn home() -> Result<impl View> {
    Ok(view! { <h1>"Rahim Mobile"</h1> })
}
''', requests=["curl -s http://localhost:3000/", "curl -s http://localhost:3000/about"], files={"src/about.rs": ABOUT_RS}),
    code(ABOUT_RS, "rust", run=False, file="src/about.rs"))

c.lesson("href!: নিরাপদ link",
    say("<code>href!(handler)</code> handler-এর <b>Rust নাম</b> থেকে URL বানায়। পরে module সরালে বা নাম বদলালে link ভাঙে না — compiler ধরে দেয়। Laravel-এর <code>route('about')</code>।"),
    tc(r'''
use topcoat::{Result, router::{href, module_router, page}, view::{View, view}};

mod about;
''' + MAIN_ROUTER + r'''
#[page]
async fn home() -> Result<impl View> {
    Ok(view! {
        <nav>
            <a href=(href!(home))>"Home"</a>
            <a href=(href!(about::about))>"About"</a>
        </nav>
    })
}
''', files={"src/about.rs": ABOUT_RS.replace("async fn about()", "pub async fn about()")}),
    php_note("<code>route('about')</code> আর <code>url('/about')</code>-এর পার্থক্য মনে আছে? <code>href!</code> প্রথমটার মতো — নাম বদলালেও link ঠিক থাকে, আর ভুল নাম compile error।"))

LAYOUT_MAIN = r'''
use topcoat::{
    Result,
    router::{Slot, href, layout, module_router, page},
    view::{View, view},
};

mod about;
''' + MAIN_ROUTER + r'''
#[layout]
async fn root_layout(slot: Slot<'_>) -> Result<impl View> {
    Ok(view! {
        <!DOCTYPE html>
        <html>
            <head><title>"Rahim Mobile"</title></head>
            <body>
                <nav>
                    <a href=(href!(home))>"Home"</a>
                    <a href=(href!(about::about))>"About"</a>
                </nav>
                (slot)
                <footer>"© Rahim Mobile"</footer>
            </body>
        </html>
    })
}

#[page]
async fn home() -> Result<impl View> {
    Ok(view! { <h1>"স্বাগতম"</h1> })
}
'''
c.lesson("Layout: সব page-এর খোল",
    say("<code>#[layout]</code> function ভিতরের page-টা <code>Slot</code> হিসেবে পায়, আর নিজের markup-এর মাঝে বসায় — Blade-এর <code>@extends('layout')</code> আর <code>@yield('content')</code>। Root layout সব page-কে মুড়ে দেয়।"),
    tc(LAYOUT_MAIN, requests=["curl -s http://localhost:3000/", "curl -s http://localhost:3000/about"],
       files={"src/about.rs": ABOUT_RS.replace("async fn about()", "pub async fn about()")}),
    tip("Layout path-prefix ধরে মেলে: <code>/</code>-এর layout সব page-কে, <code>/settings</code>-এর layout <code>/settings/...</code>-কে মোড়ে — nested হয়ে।"))

POSTS_RS = r'''
use topcoat::{Result, router::page, view::{View, view}};

mod post_id;

#[page]
async fn posts() -> Result<impl View> {
    Ok(view! { <h1>"সব post"</h1> })
}
'''
POST_ID_RS = r'''
use topcoat::{
    Result,
    context::Cx,
    router::{module_param, page, path_param},
    view::{View, view},
};

module_param!(post_id: u32, error = bad_request);

#[page]
async fn post(cx: &Cx) -> Result<impl View> {
    let post_id = path_param::<PostId>(cx)?;
    Ok(view! { <h1>"Post #" (post_id)</h1> })
}
'''
c.lesson("Path parameter",
    say("ফাইলের নামই parameter: <code>post_id.rs</code>-এ <code>module_param!(post_id: u32)</code> দিলে URL হয় <code>/posts/{post_id}</code>। <code>path_param::&lt;PostId&gt;(cx)</code> দিয়ে typed মান পড়া যায় — <code>u32</code> না হলে <code>error = bad_request</code> মানে <b>400</b>।"),
    tc(r'''
use topcoat::{Result, router::{module_router, page}, view::{View, view}};

mod posts;
''' + MAIN_ROUTER + r'''
#[page]
async fn home() -> Result<impl View> {
    Ok(view! { <h1>"Rahim Mobile"</h1> })
}
''', requests=["curl -s http://localhost:3000/posts", "curl -s http://localhost:3000/posts/42",
               "curl -si http://localhost:3000/posts/abc | head -1"],
       files={"src/posts.rs": POSTS_RS, "src/posts/post_id.rs": POST_ID_RS}),
    code(POST_ID_RS, "rust", run=False, file="src/posts/post_id.rs"),
    php_note("<code>Route::get('/posts/{post}')</code> আর <code>where('post', '[0-9]+')</code>। এখানে type-ই সেই constraint।"))

QUERY_MAIN = r'''
use topcoat::{
    Result,
    context::Cx,
    router::{module_router, page, query_params},
    view::{View, view},
};

#[query_params(error = bad_request)]
struct ProductsQuery {
    q: Option<String>,
    page: Option<u32>,
}
''' + MAIN_ROUTER + r'''
#[page]
async fn home(cx: &Cx) -> Result<impl View> {
    let query = query_params::<ProductsQuery>(cx)?;
    Ok(view! {
        <p>"খোঁজা হচ্ছে: " (query.q.as_deref().unwrap_or("সব"))</p>
        <p>"page: " (query.page.unwrap_or(1))</p>
    })
}
'''
c.lesson("Query parameter",
    say("<code>#[query_params]</code> দেওয়া struct-ই query string-এর আকার। <code>Option</code> মানে থাকতেও পারে, নাও পারে। ভুল type এলে (<code>page=abc</code>) আপনা-আপনি 400।"),
    tc(QUERY_MAIN, requests=["curl -s 'http://localhost:3000/?q=redmi&page=2'", "curl -s http://localhost:3000/",
                             "curl -si 'http://localhost:3000/?page=abc' | head -1"]),
    php_note("<code>$request-&gt;query('q')</code> সব string দেয় আর validate আপনাকেই করতে হয়। এখানে struct-এর type-ই validation।"))

c.lesson("API route: JSON",
    say("Page ছাড়া শুধু data দিতে <code>#[route(GET)]</code> বা <code>#[route(POST)]</code>। <code>Json&lt;T&gt;</code> request body পড়ে, আবার response-ও বানায়। ফাইল <code>src/api/health.rs</code> হলে URL <code>/api/health</code>।"),
    tc(r'''
use serde::{Deserialize, Serialize};
use topcoat::{
    Result,
    router::{RouterBuilderDiscoverExt, content::Json, module_router, route},
};

#[derive(Deserialize, Serialize)]
struct NewProduct {
    name: String,
    price: u32,
}
''' + MAIN_DISCOVER + r'''
#[route(GET "/api/health")]
async fn health() -> Result<&'static str> {
    Ok("ok")
}

#[route(POST "/api/products")]
async fn create(Json(p): Json<NewProduct>) -> Result<Json<NewProduct>> {
    Ok(Json(NewProduct { name: p.name.to_uppercase(), price: p.price }))
}
''', requests=["curl -s http://localhost:3000/api/health",
               "curl -s -X POST http://localhost:3000/api/products -H 'Content-Type: application/json' -d '{\"name\":\"redmi 13\",\"price\":18500}'"],
       deps={"serde": '{ version = "1", features = ["derive"] }'}),
    tip("এখানে path সরাসরি attribute-এ (<code>\"/api/health\"</code>) দেওয়া — <b>explicit path</b>। Module routing আর explicit path মিশিয়েও চলে; <code>.discover()</code> (default feature) দিলে এগুলো নিজে নিজে খুঁজে router-এ বসে — না দিলে route registered হয় না, তাই ওপরের কোডে <code>.discover()</code> আছে।"),
    php_note("<code>routes/api.php</code>-এর <code>Route::post('/products', ...)</code> আর <code>$request-&gt;validate()</code>-এর জায়গায় struct + <code>Json</code> extractor।"))


c.lesson("Error: 404 নিজে থেকে",
    say("Handler <code>Result</code> ফেরত দেয়। <code>Option</code>-কে <code>.ok_or_not_found()?</code> দিলে <code>None</code> মানে <b>404</b> response — হাতে <code>abort(404)</code> লিখতে হয় না। অন্য কোনো error হলে 500।"),
    tc(r'''
use topcoat::{
    Result,
    router::{RouterBuilderDiscoverExt, error::RouterErrorExt, module_router, page, path_param},
    context::Cx,
    view::{View, view},
};

struct Product { id: u32, name: &'static str }

const PRODUCTS: [Product; 2] = [
    Product { id: 1, name: "iPhone 15" },
    Product { id: 2, name: "Redmi 13" },
];

path_param!(id: u32, error = bad_request);
''' + MAIN_DISCOVER + r'''
#[page("/products/{id}")]
async fn product(cx: &Cx) -> Result<impl View> {
    let id = *path_param::<Id>(cx)?;
    let product = PRODUCTS.iter().find(|p| p.id == id).ok_or_not_found()?;
    Ok(view! { <h1>(product.name)</h1> })
}
''', requests=["curl -s http://localhost:3000/products/2", "curl -si http://localhost:3000/products/99 | head -1"]),
    php_note("Laravel-এ <code>Product::findOrFail($id)</code> বা <code>abort(404)</code>।"))

c.section("Context আর state")
c.lesson("Cx: request-এর খবর",
    say("<code>cx: &amp;Cx</code> parameter চাইলেই Topcoat নিজে দিয়ে দেয়। এর মাধ্যমে request-এর method, URL, header সব পড়া যায় — Laravel-এর <code>$request</code>।"),
    tc(r'''
use topcoat::{
    Result,
    context::Cx,
    router::{module_router, page, request::{headers, method, uri}},
    view::{View, view},
};
''' + MAIN_ROUTER + r'''
#[page]
async fn home(cx: &Cx) -> Result<impl View> {
    let agent = headers(cx)
        .get("user-agent")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("অজানা");
    Ok(view! {
        <p>"Method: " (method(cx).as_str())</p>
        <p>"Path: " (uri(cx).path())</p>
        <p>"Browser: " (agent)</p>
    })
}
''', requests=["curl -s -A 'rahim-test/1.0' http://localhost:3000/"]),
    php_note("<code>$request-&gt;method()</code>, <code>$request-&gt;path()</code>, <code>$request-&gt;header('User-Agent')</code>।"))

SHOP_MAIN = r'''
use topcoat::{
    Result,
    context::{Cx, app_context},
    router::{module_router, page},
    view::{View, view},
};

struct Shop {
    name: &'static str,
    branches: Vec<&'static str>,
}

fn shop(cx: &Cx) -> &Shop {
    app_context::<Shop>(cx)
}

#[tokio::main]
async fn main() {
    let router = module_router!()
        .app_context(Shop { name: "Rahim Mobile", branches: vec!["Mirpur", "Uttara", "Gulshan"] })
        .build();
    topcoat::start(router).await.unwrap();
}

#[page]
async fn home(cx: &Cx) -> Result<impl View> {
    let shop = shop(cx);
    Ok(view! {
        <h1>(shop.name)</h1>
        <ul>
            for b in &shop.branches {
                <li>(*b)</li>
            }
        </ul>
    })
}
'''
c.lesson("App context: সব request-এর shared value",
    say("Database pool, config — যা সব request-এ লাগে — router-এ <code>.app_context(value)</code> দিয়ে রাখুন, handler-এ <code>app_context::&lt;T&gt;(cx)</code> দিয়ে নিন। Value-র <b>type</b>ই তার চাবি। ছোট একটা helper function (<code>shop(cx)</code>) বানিয়ে নেওয়াই রীতি।"),
    tc(SHOP_MAIN),
    php_note("Laravel-এর service container: <code>app(Shop::class)</code>। Topcoat-এ container ছোট — শুধু type দিয়ে খোঁজা।"),
    warn("Type register না থাকলে <code>app_context</code> panic করে। তাই helper-এ মুড়ে এক জায়গায় রাখুন; অপশনাল হলে <code>try_app_context</code>।"))

c.lesson("Function, middleware নয়",
    say("Topcoat-এর দর্শন: login-এর মতো জিনিস middleware-এ লুকিয়ে না রেখে <b>সাধারণ function</b> বানান যা <code>cx</code> নেয়। Page নিজেই বলে \"আমার current user লাগবে\" — ফলে পড়লেই বোঝা যায় page কী শর্তে চলে।"),
    code(r'''
use topcoat::{Result, context::Cx, router::{error::RouterErrorExt, page}, view::{View, view}};

struct User { name: &'static str }

// সাধারণ async function — cx নেয়, Option ফেরত দেয়
async fn current_user(_cx: &Cx) -> Option<User> {
    Some(User { name: "Rahim" })
}

#[page]
async fn dashboard(cx: &Cx) -> Result<impl View> {
    let user = current_user(cx).await.ok_or_unauthorized()?;   // না থাকলে 401
    Ok(view! { <h1>"স্বাগতম, " (user.name)</h1> })
}
''', "rust", run=False, file="src/dashboard.rs"),
    php_note("Laravel-এ <code>Route::middleware('auth')</code> দূর থেকে কাজ করে; পরে <code>auth()-&gt;user()</code> আছেই ধরে নেওয়া হয়। Topcoat-এ নির্ভরতা চোখের সামনে।"))

CART_MAIN = r'''
use serde::Deserialize;
use std::sync::Mutex;
use topcoat::{
    Result,
    context::{Cx, app_context},
    router::{
        RouterBuilderDiscoverExt, content::Form, error::see_other, href, module_router, page, route,
    },
    view::{View, view},
};

struct Cart(Mutex<Vec<String>>);

#[derive(Deserialize)]
struct AddItem {
    name: String,
}

#[tokio::main]
async fn main() {
    let router = module_router!().discover().app_context(Cart(Mutex::new(vec![]))).build();
    topcoat::start(router).await.unwrap();
}

#[page("/cart")]
async fn cart_page(cx: &Cx) -> Result<impl View> {
    let items = app_context::<Cart>(cx).0.lock().unwrap().clone();
    Ok(view! {
        <h1>"Cart (" (items.len()) ")"</h1>
        <ul>
            for item in items {
                <li>(item)</li>
            }
        </ul>
        <form method="post" action="/cart/add">
            <input name="name" placeholder="Product">
            <button>"যোগ করুন"</button>
        </form>
    })
}

#[route(POST "/cart/add")]
async fn add(cx: &Cx, Form(input): Form<AddItem>) -> Result<impl topcoat::router::response::IntoResponse> {
    app_context::<Cart>(cx).0.lock().unwrap().push(input.name);
    Ok(see_other(href!(cart_page).resolve(cx)))
}
'''
c.lesson("নিরাপত্তার জার্গন: XSS, CSRF, PRG",
    say("আগে দেখেছেন <code>&lt;script&gt;</code> text হয়ে গেল (escape); পরের lesson-এ আসছে POST-এর পর redirect — দুটোর পেছনেই একটা নিরাপত্তার ধারণা।"),
    jargon(("XSS (Cross-Site Scripting)", "attacker-এর লেখা JavaScript আপনার page-এ ঢুকে অন্য user-দের browser-এ চলা; <code>( )</code>-এর escape এটা আটকায়"),
           ("CSRF (Cross-Site Request Forgery)", "অন্য site-এর form/script আপনার login-করা user-কে দিয়ে চুপিসারে POST পাঠিয়ে দেওয়া; Topcoat default-এ cross-origin POST-কে 403 করে"),
           ("PRG (Post/Redirect/Get)", "POST-এর পর redirect (303) করে GET page দেখানো — refresh-এ form আবার submit হয় না"),
           ("Escape", "<code>&lt;</code> কে <code>&amp;lt;</code> বানানো যাতে text-টা HTML হিসেবে না চলে"),
           ("Memoization", "একই হিসাব একবার করে ফল মনে রাখা; Topcoat-এর <code>#[memoize]</code> প্রতি request-এ এটা করে")),
    php_note("Laravel-এ <code>{{ }}</code> escape করে (XSS) আর <code>@csrf</code> token ফেলে (CSRF)। Topcoat-এ প্রথমটা <code>( )</code> আর দ্বিতীয়টা origin policy।"))

c.lesson("Form আর redirect",
    say("<code>Form&lt;T&gt;</code> extractor form-এর data পড়ে। কাজ শেষে <code>see_other(...)</code> দিয়ে <b>303 redirect</b> — যাতে browser refresh করলে form আবার submit না হয় (Post/Redirect/Get)। Laravel-এর <code>redirect()-&gt;route('cart')</code>।"),
    tc(CART_MAIN, requests=["curl -si -X POST http://localhost:3000/cart/add -d 'name=Redmi+13'",
                            "curl -s -X POST http://localhost:3000/cart/add -d 'name=Charger'",
                            "curl -s http://localhost:3000/cart"],
       deps={"serde": '{ version = "1", features = ["derive"] }'}),
    tip("Browser থেকে আসা অন্য-site-এর POST (CSRF) Topcoat নিজেই <b>403</b> করে দেয় — default origin policy। <code>curl</code>-এ Origin header নেই, তাই এখানে চলেছে।"))


# ================================================================== Browser runtime
c.section("Browser interactivity")
RT_USE = r'''
use topcoat::{
    Result,
    asset::{AssetBundle, RouterBuilderAssetExt},
    context::Cx,
    router::{RouterBuilderDiscoverExt, module_router, page},
    runtime::{Event, RouterBuilderRuntimeExt, signal},
    view::{View, view},
};
'''
RT_MAIN = r'''
#[tokio::main]
async fn main() {
    let router = module_router!()
        .discover()
        .assets(AssetBundle::load().unwrap())
        .runtime()
        .build();
    topcoat::start(router).await.unwrap();
}
'''
c.lesson("Browser-এ code: $() runtime",
    say("Server-rendered page-এ click-এ কিছু বদলাতে চাই — কিন্তু WebAssembly ছাড়া। Topcoat-এর উত্তর: <code>$( ... )</code> ভিতরের Rust expression server প্রথমবার চালায়, আর একই expression <b>JavaScript-এ compile হয়ে</b> browser-এও চলে।"),
    points("<code>$(...)</code> — runtime expression",
           "<code>signal(cx, || 0)</code> — browser-এর state",
           "<code>@click=$(...)</code> — event handler",
           "<code>:hidden=$(...)</code> — বদলে যাওয়া attribute"),
    warn("Runtime এখনো <b>highly experimental</b> — সব Rust operation এখানে চলে না, শুধু একটা সীমিত অংশ। সীমার বাইরে গেলে compiler বলে দেয়।"))

c.lesson("Setup: runtime চালু করা",
    say("তিনটা জিনিস: head-এ <code>topcoat::runtime::script()</code>, router-এ <code>.runtime()</code>, আর browser script বিলি করতে asset bundle (<code>.assets(AssetBundle::load()...)</code>)। Bundle বানায় CLI: <code>topcoat dev</code> বা <code>topcoat asset bundle</code>।"),
    code(RT_MAIN, "rust", run=False, file="src/main.rs"),
    shell('''topcoat asset bundle    # build করে browser script আর asset বান্ডেল বানায়
topcoat dev             # প্রতি build-এর পর এটা নিজেই করে'''),
    tip("Deploy-এর সময় binary আর তার পাশের <code>assets</code> ফোল্ডার <b>একই build</b> থেকে একসাথে নিতে হবে।"))

COUNTER = RT_USE + RT_MAIN + r'''
#[page]
async fn home(cx: &Cx) -> Result<impl View> {
    let sold = signal(cx, || 0usize);
    Ok(view! {
        <!DOCTYPE html>
        <html>
            <head>topcoat::runtime::script()</head>
            <body>
                <button @click=$(|_e| sold.set(sold.get() + 1))>"বিক্রি হলো"</button>
                <p>"আজ বিক্রি: " $(sold.get()) " টি"</p>
            </body>
        </html>
    })
}
'''
c.lesson("Signal আর @click: Counter",
    say("<code>signal(cx, || 0)</code> একটা state, <code>.get()</code> দিয়ে পড়া, <code>.set()</code> দিয়ে লেখা। <code>@click</code>-এর মান একটা closure। Button চাপলে signal বদলায়, আর <code>$(sold.get())</code> text নিজেই আবার আঁকে — সবটা browser-এই, server-এ না গিয়ে। তিনবার চাপার পর আসল screenshot:"),
    tcr(COUNTER, actions=[("click", "button")] * 3),
    php_note("Alpine.js-এর <code>x-data=\"{ sold: 0 }\"</code> আর <code>@click=\"sold++\"</code>-এর মতো — কিন্তু লেখা হচ্ছে Rust-এ, type-checked।"))

c.lesson("Server আগেই HTML পাঠায়",
    say("Counter-এর page প্রথমে সাধারণ server-rendered HTML হিসেবে আসে — <code>আজ বিক্রি: <b>0</b> টি</code> আগে থেকেই লেখা, JavaScript চলার আগেই। আর <code>data-topcoat-on:click</code> attribute-এ দেখুন: আপনার Rust closure (<code>sold.set(sold.get() + 1)</code>) <b>JavaScript হয়ে</b> বসে আছে — এটাই WebAssembly-ছাড়া কৌশল।"),
    code(COUNTER, "rust", topcoat="runtime", actions=[], requests=["curl -s http://localhost:3000/ | grep -o '<body>.*</body>'"], run=True, hidden=False))

TOGGLE = RT_USE + RT_MAIN + r'''
#[page]
async fn home(cx: &Cx) -> Result<impl View> {
    let open = signal(cx, || false);
    Ok(view! {
        <!DOCTYPE html>
        <html>
            <head>topcoat::runtime::script()</head>
            <body>
                <button @click=$(|_e| open.set(!open.get()))>"Warranty কত দিন?"</button>
                <p :hidden=$(!open.get())>"সব ফোনে ১ বছরের warranty।"</p>
            </body>
        </html>
    })
}
'''
c.lesson("Bind attribute: দেখানো/লুকানো",
    say("<code>:নাম=$(...)</code> হলো bind attribute — signal বদলালে attribute-ও বদলায়। FAQ-এর মতো toggle বানাতে <code>:hidden</code> যথেষ্ট।"),
    tcr(TOGGLE, actions=[("click", "button")]))

INPUT = RT_USE + RT_MAIN + r'''
#[page]
async fn home(cx: &Cx) -> Result<impl View> {
    let name = signal(cx, String::new);
    Ok(view! {
        <!DOCTYPE html>
        <html>
            <head>topcoat::runtime::script()</head>
            <body>
                <input placeholder="গ্রাহকের নাম"
                    :value=$(name.get())
                    @input=$(|e: Event| name.set(e.target.value))
                >
                <p>"Invoice: " $(name.get()) "-এর জন্য"</p>
            </body>
        </html>
    })
}
'''
c.lesson("Input আর signal",
    say("<code>:value</code> (signal → input) আর <code>@input</code> (input → signal) — Leptos-এর মতোই দুই লাইনের binding। <code>e.target.value</code> দিয়ে লেখা পড়া হয়।"),
    tcr(INPUT, actions=[("fill", "input", "Karim")]),
    php_note("Livewire-এর <code>wire:model</code>, Vue-এর <code>v-model</code> — Topcoat-এ হাতে দুই লাইন।"))

PROC = RT_USE.replace("runtime::{Event, RouterBuilderRuntimeExt, signal}", "runtime::{RouterBuilderRuntimeExt, procedure, signal}") + RT_MAIN + r'''
#[procedure]
async fn price_with_vat(price: usize) -> Result<usize> {
    // এই code শুধু server-এ চলে — database query-ও এখানে হতে পারত
    Ok(price * 115 / 100)
}

#[page]
async fn home(cx: &Cx) -> Result<impl View> {
    let price = signal(cx, || 18500usize);
    Ok(view! {
        <!DOCTYPE html>
        <html>
            <head>topcoat::runtime::script()</head>
            <body>
                <button @click=$(async |_e| {
                    let with_vat = price_with_vat(price.get()).await;
                    price.set(with_vat);
                })>"VAT যোগ করুন"</button>
                <p>"দাম: " $(price.get()) " Taka"</p>
            </body>
        </html>
    })
}
'''
c.lesson("Procedure: browser থেকে server function",
    say("Click-এ database বা secret লাগলে <code>#[procedure]</code> — একটা async function যা <b>server-এ চলে</b>, কিন্তু runtime expression থেকে <code>.await</code> করে ডাকা যায়। ভিতরে Topcoat নিজেই HTTP request পাঠায়।"),
    tcr(PROC, actions=[("click", "button"), ("wait", 500)]),
    warn("Procedure একটা public HTTP endpoint — কেউ নিজে request পাঠিয়ে যেকোনো argument দিতে পারে। <b>Argument validate আর authorization procedure-এর ভিতরেই</b> করুন।"))

SHARD = RT_USE + RT_MAIN + r'''
use topcoat::runtime::shard;

const PRODUCTS: [&str; 4] = ["iPhone 15", "Samsung A55", "Redmi 13", "Redmi Note 13"];

#[shard]
async fn results(query: String) -> Result<impl View> {
    let q = query.to_lowercase();
    let found: Vec<&str> = PRODUCTS.iter().copied().filter(|p| p.to_lowercase().contains(&q)).collect();
    Ok(view! {
        <p>(found.len()) " টি পাওয়া গেছে"</p>
        <ul>
            for p in found {
                <li>(p)</li>
            }
        </ul>
    })
}

#[page]
async fn home(cx: &Cx) -> Result<impl View> {
    let query = signal(cx, String::new);
    Ok(view! {
        <!DOCTYPE html>
        <html>
            <head>topcoat::runtime::script()</head>
            <body>
                <input placeholder="খুঁজুন" @input=$(|e: Event| query.set(e.target.value))>
                results(query: $(query.get()))
            </body>
        </html>
    })
}
'''
c.lesson("Shard: server থেকে আবার আঁকা অংশ",
    say("Search result-এর মতো server-এর data দিয়ে বানানো অংশ বদলাতে <code>#[shard]</code>: একটা component যার argument (<code>$(query.get())</code>) বদলালে <b>server আবার HTML বানায়</b>, আর browser শুধু সেই অংশ জায়গা-মতো বদলে দেয়। \"redmi\" লিখে দেখুন:"),
    tcr(SHARD, actions=[("wait", 300), ("shot", "সব product"), ("fill", "input", "redmi"), ("wait", 700)]),
    php_note("Livewire-এর মূল কৌশলের কাছাকাছি: state বদলালে server HTML আবার বানায়। পার্থক্য — Topcoat শুধু ওই shard-টুকু আনে, আর state browser-এ signal-এ থাকে।"),
    warn("Shard-এর নিজস্ব HTTP endpoint আছে; page-এর guard ওখানে চলে না। Argument validate আর authorization shard-এর ভিতরেই করুন।"))


# ================================================================== প্রজেক্ট
c.section("প্রজেক্ট ও deploy")
MINI = r'''
use topcoat::{
    Result,
    asset::{AssetBundle, RouterBuilderAssetExt},
    context::{Cx, app_context},
    router::{
        RouterBuilderDiscoverExt, Slot, error::RouterErrorExt, href, layout, module_router, page, path_param,
    },
    runtime::{RouterBuilderRuntimeExt, signal},
    view::{View, view},
};

struct Product { id: u32, name: &'static str, price: u32 }
struct Catalog(Vec<Product>);

path_param!(id: u32, error = bad_request);

#[tokio::main]
async fn main() {
    let catalog = Catalog(vec![
        Product { id: 1, name: "iPhone 15", price: 112000 },
        Product { id: 2, name: "Samsung A55", price: 41500 },
        Product { id: 3, name: "Redmi 13", price: 18500 },
    ]);
    let router = module_router!()
        .discover()
        .app_context(catalog)
        .assets(AssetBundle::load().unwrap())
        .runtime()
        .build();
    topcoat::start(router).await.unwrap();
}

#[layout]
async fn shell(slot: Slot<'_>) -> Result<impl View> {
    Ok(view! {
        <!DOCTYPE html>
        <html>
            <head><title>"Rahim Mobile"</title> topcoat::runtime::script()</head>
            <body>
                <nav><a href=(href!(home))>"← সব product"</a></nav>
                (slot)
            </body>
        </html>
    })
}

#[page]
async fn home(cx: &Cx) -> Result<impl View> {
    let catalog = app_context::<Catalog>(cx);
    Ok(view! {
        <h1>"Rahim Mobile"</h1>
        <ul>
            for p in &catalog.0 {
                <li><a href=(format!("/products/{}", p.id))>(p.name)</a> " — " (p.price) " Taka"</li>
            }
        </ul>
    })
}

#[page("/products/{id}")]
async fn product(cx: &Cx) -> Result<impl View> {
    let id = *path_param::<Id>(cx)?;
    let p = app_context::<Catalog>(cx).0.iter().find(|p| p.id == id).ok_or_not_found()?;
    let qty = signal(cx, || 0usize);
    let price = p.price as usize;
    Ok(view! {
        <h1>(p.name)</h1>
        <p>(p.price) " Taka"</p>
        <button @click=$(|_e| qty.set(qty.get() + 1))>"Cart-এ দিন"</button>
        <p>"Cart-এ: " $(qty.get()) " টি · মোট " $(qty.get() * price) " Taka"</p>
    })
}
'''
c.lesson("Mini project: Rahim Mobile",
    say("সব মিলিয়ে: <code>#[layout]</code>, <code>app_context</code> থেকে product list, <code>/products/{id}</code> page (না পেলে 404), আর browser-এ চলা <code>signal</code>। নিচের screenshot-এ প্রথমে list, তারপর Redmi 13-এর page-এ দুবার \"Cart-এ দিন\"।"),
    tcr(MINI, actions=[("shot", "Home"), ("goto", "/products/3"), ("click", "button"), ("click", "button")]),
    task("Product page-এ \"Cart থেকে বাদ\" button যোগ করুন, যেটা <code>qty</code> কমায় কিন্তু ০-র নিচে যায় না। (ইঙ্গিত: <code>if</code> runtime expression-এর ভিতরেও চলে)"))

c.lesson("Quiz",
    quiz("Topcoat-এ browser-এর interactivity WebAssembly দিয়ে হয় কি?",
         "না। <code>$(...)</code>-এর ভিতরের Rust expression-এর একটা সীমিত অংশ JavaScript-এ compile হয়। সেটাই Leptos থেকে বড় পার্থক্য — Leptos Rust-কে wasm বানায়।"),
    quiz("<code>#[shard]</code> আর <code>#[procedure]</code>-এর পার্থক্য কী?",
         "Procedure একটা server function — browser ডেটা চায়, JavaScript সেই ডেটা নিয়ে যা খুশি করে। Shard একটা component — argument বদলালে server আবার HTML বানায়, আর browser সেই অংশ বদলে দেয়।"),
    quiz("Layout আর Slot-এর কাজ কী?",
         "Layout ভিতরের page-টা <code>Slot</code> হিসেবে পায় এবং নিজের markup-এর মাঝখানে বসায় — যেমন Blade-এর <code>@extends</code> আর <code>@yield</code>।"))

c.lesson("Release আর deploy",
    say("Topcoat app একটা সাধারণ Rust binary — Rust Web Development-এর মতোই deploy: release build, Nginx reverse proxy, systemd। শুধু একটা নতুন জিনিস — <b>asset bundle binary-র সাথে নিতে হবে</b>।"),
    shell('''topcoat asset bundle --release      # release build + assets ফোল্ডার
# target/release/ এর app আর assets/ একসাথে server-এ নিন

HOST=127.0.0.1 PORT=8080 ./app          # Nginx এই port-এ proxy করবে
topcoat fmt                             # view! macro-র ভিতরের code format'''),
    tip("Topcoat ফোল্ডার-ভিত্তিক routing দেয় বলে project বড় হলে ফাইলের গঠনই আপনার site map হয়ে ওঠে — module-এর নাম সাবধানে দিন।"))

c.lesson("কখন কোনটা?",
    table(["দরকার", "বেছে নিন"], [
        ["শুধু JSON API", "<b>axum</b> (Rust Web Development)"],
        ["Rich, app-এর মতো client UI; অনেক client state", "<b>Leptos</b>"],
        ["Server-rendered site/dashboard, form আর সামান্য interactivity", "<b>Topcoat</b>"],
        ["গুরুত্বপূর্ণ production app এখনই", "axum বা Laravel — Topcoat-এ আরও সময় দিন"]]),
    warn("Topcoat 0.10, Leptos 0.8 — দুটোই দ্রুত বদলায়। Project-এ version লক রাখুন, upgrade-এর আগে CHANGELOG পড়ুন।"))

# @@END
c.lesson("Topcoat-এর জার্গন কার্ড",
    table(["শব্দ", "এক লাইনে"], [
        ["Server-first", "বেশিরভাগ কাজ server-এ"],
        ["Async component", "ভিতরে <code>.await</code> চলে"],
        ["Layout / Slot", "page-এর খোল / খোলের ভিতরের ফাঁকা জায়গা"],
        ["Module routing", "ফাইলের গঠনই URL"],
        ["Cx", "request-এর খবর আর shared value-র হাতল"],
        ["App context", "সব request-এ ভাগ করা value (type দিয়ে খোঁজা)"],
        ["Signal / <code>$()</code>", "browser-এর state / JavaScript-এ যাওয়া Rust expression"],
        ["Procedure / Shard", "browser থেকে ডাকা server function / server-এ আবার আঁকা অংশ"],
        ["XSS / CSRF / PRG", "script ঢোকানো / অন্য site থেকে জাল POST / POST-এর পর redirect"]]))

c.finish("Topcoat শেখা শেষ", "Rust-এ server-first full-stack web: page, layout, component আর browser interactivity এক জায়গায়।",
         recap=["Topcoat = axum-এর উপর server-first framework", "view! macro, async component", "Module routing আর layout",
                "Cx, app context", "$() runtime, signal, procedure, shard"])
c.build()
