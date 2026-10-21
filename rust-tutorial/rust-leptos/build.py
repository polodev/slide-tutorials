"""Rust Leptos — reactive full-stack web with Leptos, explained for Laravel developers.
SSR examples are compiled natively and print the real HTML. Browser examples (web=True) are compiled to wasm,
opened in headless Chromium, clicked/typed with Playwright, and the real screenshots are shown.
Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
from kit import Course, code, jargon, php_note, points, quiz, say, shell, steps, table, task, tip, warn  # noqa: E402

SSR = {"leptos": '{ version = "0.8", features = ["ssr"] }'}
CSR = {"leptos": '{ version = "0.8", features = ["csr"] }'}
SSR_TOKIO = {**SSR, "reactive_graph": '{ version = "0.2", features = ["effects"] }', "any_spawner": '{ version = "0.3", features = ["tokio"] }',
             "tokio": '{ version = "1", features = ["full"] }'}


def ssr(src, **kw):
    return code(src, "rust", deps=SSR, **kw)


def web(src, actions=None, deps=None, **kw):
    return code(src, "rust", deps={**CSR, **(deps or {})}, web=True, actions=actions, **kw)


MAIN = "\nfn main() {\n    leptos::mount::mount_to_body(App);\n}\n"


def laravel(src, label="Laravel / Livewire-এ"):
    return code(src, "php", run=False, label=label)


c = Course(slug="rust-leptos", title="Rust Leptos — Reactive Full-stack Web", folder=HERE,
           subtitle="Leptos হলো Rust-ভিত্তিক full-stack web framework: fine-grained reactivity, Virtual DOM ছাড়া, একই Rust code-এ client-side rendering, SSR আর hydration",
           series="Rust Leptos", prev_course=("../rust-web-development/index.html", "Rust Web Development"),
           next_course=("../rust-topcoat/index.html", "Rust Topcoat — Tokio-র Full-stack Framework"))

c.cover("Rust Leptos<br>Reactive Full-stack Web",
        "Livewire আর Vue/React যা করে — interactive UI — সেটাই পুরোপুরি Rust-এ। Virtual DOM ছাড়া, fine-grained reactivity দিয়ে। প্রতিটি উদাহরণ আসলেই browser-এ চালানো, screenshot আসল।",
        learn=["Leptos কী, আর Virtual DOM ছাড়া কীভাবে চলে", "view! macro আর component", "Signal, Memo, Effect — reactivity",
               "Event, form আর list (For, Show)", "Context আর shared state", "Resource আর Suspense (async data)",
               "Router: একাধিক page", "SSR, server function আর hydration"],
        need="Rust 101–103 (struct, closure, trait, Option/Result)। Rust Web Development পড়া থাকলে SSR অংশ সহজ লাগবে।")

# ================================================================== শুরু
c.section("শুরু")
c.lesson("Leptos কী?",
    say("Leptos হলো Rust-ভিত্তিক full-stack web framework। একই Rust code browser-এ (client-side rendering), server-এ (SSR) আর server-এর HTML-কে জীবন্ত করতে (hydration) চলে।"),
    points("<b>Fine-grained reactivity</b> — যে value বদলাল, শুধু সেই text/attribute বদলায়",
           "<b>Virtual DOM নেই</b> — React-এর মতো পুরো tree তুলনা করা হয় না",
           "Component function <b>একবারই</b> চলে, তারপর signal DOM আপডেট করে",
           "Compile হয় WebAssembly-তে, তাই browser-এ Rust চলে"),
    php_note("Livewire-এ button চাপলে server-এ round trip হয়ে HTML ফেরত আসে। Leptos-এ (CSR) logic browser-এই চলে, server-কে ডাকতে হয় শুধু data লাগলে।"))

c.lesson("Laravel-এর সাথে মিল",
    say("নতুন শব্দগুলো আসলে চেনা জিনিসেরই রূপ:"),
    table(["Laravel / Livewire / Vue", "Leptos"], [
        ["Blade template", "<code>view! { ... }</code> macro (HTML-এর মতো, Rust-এ)"],
        ["Blade component / Vue component", "<code>#[component]</code> function"],
        ["<code>@props</code>, Vue props", "component function-এর argument"],
        ["Livewire property / Vue <code>ref()</code>", "<code>signal(...)</code>"],
        ["Vue <code>computed()</code>", "<code>Memo</code> বা derived signal"],
        ["Vue <code>watchEffect()</code>", "<code>Effect</code>"],
        ["<code>@foreach</code> / <code>v-for</code>", "<code>&lt;For&gt;</code>"],
        ["<code>@if</code> / <code>v-if</code>", "<code>&lt;Show&gt;</code> বা <code>if</code>"],
        ["<code>routes/web.php</code>", "<code>leptos_router</code>"],
        ["Controller + API call", "<code>#[server]</code> function"]]))

c.lesson("Web frontend-এর জার্গন",
    say("Leptos, React, Vue — এই জগতের আলোচনায় কিছু শব্দ বারবার আসে। আগে একবার সবগুলো চিনে নিন; প্রতিটা এই কোর্সেই কাজে দেখবেন।"),
    jargon(("DOM", "browser page-কে যে tree আকারে মনে রাখে (<code>html → body → p</code>…); JavaScript/wasm এই tree বদলে page বদলায়"),
           ("Virtual DOM", "React-এর কৌশল: আগে একটা কপি-tree বানিয়ে পুরনোটার সাথে তুলনা, তারপর পার্থক্যটুকু আসল DOM-এ — Leptos এই ধাপই বাদ দেয়"),
           ("Reactivity", "data বদলালে যা যা data-র উপর নির্ভরশীল সেগুলো নিজে নিজে আপডেট হওয়া"),
           ("WebAssembly (wasm)", "browser-এ চলা compile-করা binary format; Rust compile করে এখানে নেওয়া যায়"),
           ("SPA (Single Page App)", "একটাই page লোড হয়, পরে JavaScript/wasm দিয়ে অংশ বদলায়"),
           ("CSR / SSR / Hydration", "browser-এ বানানো / server-এ বানানো / server-এর HTML-কে browser-এ জীবন্ত করা"),
           ("Isomorphic / universal", "একই code server আর browser দুই জায়গাতেই চলে")),
    php_note("Blade সবসময় server-এ HTML বানায় (SSR)। jQuery/Alpine তারপর DOM হাতে বদলায়। Leptos একই code-এ দুটোই করে।"))

c.lesson("প্রথম Hello, World! — server-এ render",
    say("সবচেয়ে ছোট Leptos program। এখানে browser নেই — <code>to_html()</code> view-কে সরাসরি HTML string বানায়, ঠিক SSR যা করে।"),
    ssr(r'''
use leptos::prelude::*;

#[component]
fn Hello() -> impl IntoView {
    view! { <h1>"Hello, World!"</h1> }
}

fn main() {
    println!("{}", view! { <Hello/> }.to_html());
}
'''),
    tip("<code>view!</code>-এর ভিতরে text সবসময় quote-এ (<code>\"...\"</code>) লিখতে হয়। এটা Rust-এর নিয়ম, HTML-এর না।"))

c.lesson("Hello, World! — browser-এ",
    say("এবার একই component browser-এ। <code>csr</code> feature, আর <code>mount_to_body</code> দিয়ে body-তে বসানো। নিচে একটা আসল browser-এ চালানোর screenshot।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    view! { <h1>"Hello, World!"</h1> }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
'''),
    php_note("<code>mount_to_body</code> অনেকটা Vue-এর <code>createApp(App).mount('#app')</code>।"))

c.lesson("Project বানানোর ধাপ",
    say("Leptos browser-এ চালাতে WebAssembly target আর একটা build tool লাগে। এই tutorial-এর সব example এই ধাপেই build হয়েছে।"),
    steps("<code>rustup target add wasm32-unknown-unknown</code> — Rust-কে wasm-এ compile করার ক্ষমতা",
          "<code>cargo add leptos --features csr</code> — client-side rendering-এর জন্য",
          "<code>cargo install trunk</code> — build + dev server (hot reload সহ)",
          "<code>trunk serve --open</code> — browser-এ চালু"),
    shell('''cargo new rahim-ui && cd rahim-ui
rustup target add wasm32-unknown-unknown
cargo add leptos --features csr
cargo install trunk
trunk serve --open'''),
    tip("Trunk-এর জন্য project root-এ একটা <code>index.html</code> লাগে (খালি <code>&lt;body&gt;&lt;/body&gt;</code> হলেও চলে)। Full-stack হলে <code>cargo-leptos</code> ব্যবহার হয় — শেষের দিকে দেখব।"))

# ================================================================== view! ও component
c.section("view! ও component")
c.lesson("view! আসলে macro",
    say("Rust 101-এ <code>println!</code> দেখে শিখেছেন: নামের শেষে <code>!</code> মানে macro। <code>view!</code> সেই জাতেরই — তবে অনেক বেশি শক্তিশালী। <code>view!</code>-এর ভিতরের HTML-সদৃশ লেখা compile-এর সময় সাধারণ Rust code-এ বদলে যায়, তাই HTML-এ ভুল করলে program চলার আগেই ধরা পড়ে:"),
    code(r'''
use leptos::prelude::*;

fn main() {
    let page = view! { <div><p>"Hello"</div> };
    println!("{}", page.to_html());
}
''', "rust", deps=SSR, err="error"),
    jargon(("Function-like macro", "<code>view!(...)</code>, <code>println!(...)</code> — ডাকার ধরন function-এর মতো"),
           ("Attribute macro", "<code>#[component]</code>, <code>#[page]</code> — নিচের function বদলে দেয় (Rust 102-এর attribute)"),
           ("Derive macro", "<code>#[derive(...)]</code> — struct দেখে trait-এর code বানায়"),
           ("DSL (Domain-Specific Language)", "একটা নির্দিষ্ট কাজের জন্য ছোট ভাষা — <code>view!</code>-এর ভিতরের HTML-সদৃশ ভাষা")),
    tip("এই তিন ধরনকেই একসাথে বলে <b>procedural macro</b> — Rust code পড়ে Rust code লেখে। Leptos আর Topcoat দুজনেরই প্রাণ এখানে।"))

c.lesson("view! — Rust-এর ভিতরে HTML",
    say("<code>view!</code> HTML-এর মতো লেখা যায়, কিন্তু এটা type-checked Rust। ভুল tag বা ভুল attribute হলে compile-ই হবে না।"),
    ssr(r'''
use leptos::prelude::*;

fn main() {
    let view = view! {
        <div class="card" id="p1">
            <h2>"iPhone 15"</h2>
            <p style="color: green">"In stock"</p>
            <a href="/products/1">"Details"</a>
        </div>
    };
    println!("{}", view.to_html());
}
'''),
    php_note("Blade-এ <code>&lt;div class=\"card\"&gt;</code> সরাসরি লিখি। এখানেও প্রায় তাই — শুধু text-এ quote আর self-closing tag-এ <code>/</code>।"))

c.lesson("Text-এ value বসানো",
    say("<code>{...}</code>-এর ভিতরে যেকোনো Rust expression বসানো যায় — Blade-এর <code>{{ $x }}</code>-এর মতো।"),
    ssr(r'''
use leptos::prelude::*;

fn main() {
    let name = "Samsung A55";
    let price = 41500;
    let view = view! {
        <p>{name} " — " {price} " Taka"</p>
        <p>"VAT সহ: " {price * 115 / 100}</p>
    };
    println!("{}", view.to_html());
}
'''),
    tip("আউটপুটের <code>&lt;!&gt;</code> হলো hydration-এর জন্য ছোট marker comment — পরে hydration lesson-এ কাজে লাগবে। Browser-এ এগুলো কিছু দেখায় না।"))


c.lesson("Component: ছোট function, বড় কাজ",
    say("<code>#[component]</code> দেওয়া function-ই একটা component। নাম বড় হাতের অক্ষরে শুরু (<code>ProductCard</code>), আর view-তে <code>&lt;ProductCard/&gt;</code> লিখে ব্যবহার।"),
    ssr(r'''
use leptos::prelude::*;

#[component]
fn ProductCard() -> impl IntoView {
    view! {
        <div class="card">
            <h2>"iPhone 15"</h2>
            <p>"Price: 112000 Taka"</p>
        </div>
    }
}

fn main() {
    let page = view! {
        <ProductCard/>
        <ProductCard/>
    };
    println!("{}", page.to_html());
}
'''),
    php_note("Blade-এ <code>&lt;x-product-card /&gt;</code> — ঠিক একই ধারণা, শুধু class-এর বদলে function।"))

c.lesson("Props: component-কে data দেওয়া",
    say("Component function-এর argument-ই তার props। view-তে লেখা হয় HTML attribute-এর মতো: <code>name=\"...\"</code>।"),
    ssr(r'''
use leptos::prelude::*;

#[component]
fn ProductCard(name: &'static str, price: u32) -> impl IntoView {
    view! {
        <div class="card">
            <h2>{name}</h2>
            <p>"Price: " {price} " Taka"</p>
        </div>
    }
}

fn main() {
    let page = view! {
        <ProductCard name="iPhone 15" price=112000/>
        <ProductCard name="Redmi 13" price=18500/>
    };
    println!("{}", page.to_html());
}
'''),
    php_note("Blade-এ <code>@props(['name', 'price'])</code>। Rust-এ type দিতে হয় — ভুল type দিলে compile error।"))

c.lesson("Prop ভুল দিলে compile error",
    say("Laravel-এ ভুল prop runtime-এ ধরা পড়ে (বা পড়েই না)। Leptos-এ <code>price</code>-এ text দিলে compile-ই হয় না।"),
    code(r'''
use leptos::prelude::*;

#[component]
fn ProductCard(name: &'static str, price: u32) -> impl IntoView {
    view! { <p>{name} ": " {price}</p> }
}

fn main() {
    let page = view! { <ProductCard name="iPhone 15" price="costly"/> };
    println!("{}", page.to_html());
}
''', "rust", deps=SSR, err="E0308"))

c.lesson("Optional আর default prop",
    say("সব prop বাধ্যতামূলক নয়। <code>#[prop(optional)]</code> দিলে না দিলে <code>Option</code> বা default; <code>#[prop(into)]</code> দিলে <code>&str</code> থেকে <code>String</code> নিজে হয়ে যায়।"),
    ssr(r'''
use leptos::prelude::*;

#[component]
fn ProductCard(
    #[prop(into)] name: String,
    price: u32,
    #[prop(optional)] discount: u32,
    #[prop(default = "Mirpur")] branch: &'static str,
) -> impl IntoView {
    view! { <p>{name} ": " {price - discount} " Taka (" {branch} ")"</p> }
}

fn main() {
    let page = view! {
        <ProductCard name="Redmi 13" price=18500/>
        <ProductCard name="Redmi 13" price=18500 discount=1500 branch="Uttara"/>
    };
    println!("{}", page.to_html());
}
'''),
    php_note("<code>@props(['branch' => 'Mirpur'])</code>-এর মতো default value।"))

c.lesson("Children: ভিতরে content বসানো",
    say("Component-এর ভিতরে যা লেখা হয়, সেটা <code>children: Children</code> হয়ে আসে। Blade-এর <code>{{ $slot }}</code>-এর মতো।"),
    ssr(r'''
use leptos::prelude::*;

#[component]
fn Card(#[prop(into)] title: String, children: Children) -> impl IntoView {
    view! {
        <section class="card">
            <h3>{title}</h3>
            {children()}
        </section>
    }
}

fn main() {
    let page = view! {
        <Card title="Invoice INV-1001">
            <p>"Customer: Karim"</p>
            <p>"Total: 23500 Taka"</p>
        </Card>
    };
    println!("{}", page.to_html());
}
'''),
    php_note("Blade: <code>&lt;x-card title=\"...\"&gt; ... &lt;/x-card&gt;</code> আর card-এর ভিতরে <code>{{ $slot }}</code>।"))

# ================================================================== Reactivity
c.section("Reactivity")
c.lesson("Signal: বদলাতে পারে এমন value",
    say("<code>signal(0)</code> দুটো জিনিস দেয়: পড়ার handle (<code>get</code>) আর লেখার handle (<code>set</code>/<code>update</code>)। এটাই Leptos-এর হৃদয়।"),
    ssr(r'''
use leptos::prelude::*;

fn main() {
    let (stock, set_stock) = signal(10);
    println!("শুরুতে: {}", stock.get());

    set_stock.set(8);
    println!("set(8) এর পর: {}", stock.get());

    set_stock.update(|n| *n -= 3);
    println!("update(-3) এর পর: {}", stock.get());
}
'''),
    php_note("Vue-এর <code>const stock = ref(10)</code>-এ read/write একই object-এ। Leptos-এ read আর write আলাদা — কে বদলাতে পারবে সেটা নিয়ন্ত্রণে রাখা যায়।"))

c.lesson("প্রথম interactive component: Counter",
    say("Signal-কে view-তে বসাতে <code>{stock}</code> লিখলেই হয়। <code>on:click</code>-এ signal বদলালে শুধু ওই text বদলায়। নিচে button তিনবার চাপা হয়েছে — আসল browser-এ।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (sold, set_sold) = signal(0);

    view! {
        <button on:click=move |_| set_sold.update(|n| *n += 1)>
            "বিক্রি হলো"
        </button>
        <p>"আজ বিক্রি: " {sold} " টি"</p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
''', actions=[("click", "button"), ("click", "button"), ("click", "button")]),
    tip("Event handler <code>move |_| ...</code> closure — <code>move</code> দিয়ে signal-এর handle closure-এ নিয়ে নেওয়া হয়। Signal <code>Copy</code> হওয়ায় clone করতে হয় না।"))

c.lesson("Component function একবারই চলে",
    say("React-এ state বদলালে পুরো component আবার চলে। Leptos-এ component শুধু <b>একবার</b> চলে — view বানায়। এরপর signal সরাসরি ওই text node-টাকে বদলায়। প্রমাণ নিচে:"),
    web(r'''
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let runs = StoredValue::new(0);
    runs.update_value(|n| *n += 1);   // component body-তে — কয়বার চলল গুনছি
    let (clicks, set_clicks) = signal(0);

    view! {
        <button on:click=move |_| set_clicks.update(|n| *n += 1)>"Click"</button>
        <p>"Component body চলেছে: " {runs.get_value()} " বার"</p>
        <p>"Click হয়েছে: " {clicks} " বার"</p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
''', actions=[("click", "button")] * 5),
    say("পাঁচ click-এও body চলেছে ১ বার — Virtual DOM diff-এর দরকারই পড়েনি।"))

c.lesson("Derived signal: signal থেকে হিসাব",
    say("Signal-এর উপর নির্ভর করা হিসাব লিখতে সাধারণ closure-ই যথেষ্ট: <code>move || price.get() * qty.get()</code>। View-তে বসালে signal বদলালেই নতুন হিসাব।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (qty, set_qty) = signal(1);
    let price = 18500;
    let total = move || price * qty.get();

    view! {
        <button on:click=move |_| set_qty.update(|q| *q += 1)>"+"</button>
        <button on:click=move |_| set_qty.update(|q| *q = (*q - 1).max(1))>"−"</button>
        <p>"Redmi 13 × " {qty}</p>
        <p class="bold">"Total: " {total} " Taka"</p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
''', actions=[("click", "button:nth-of-type(1)"), ("click", "button:nth-of-type(1)")]),
    php_note("Vue-এর <code>computed(() =&gt; price * qty.value)</code>। Livewire-এ <code>#[Computed]</code> property।"))

c.lesson("Memo: দামী হিসাব একবারই",
    say("Derived closure প্রতিবার পড়ার সময় আবার চলে। হিসাব ভারী হলে <code>Memo</code> ব্যবহার করুন — dependency বদলালে তবেই নতুন করে হিসাব, নইলে আগের ফল।"),
    ssr(r'''
use leptos::prelude::*;

fn main() {
    let (qty, set_qty) = signal(2);
    let (note, set_note) = signal("cash");

    let total = Memo::new(move |_| {
        println!("  (হিসাব চলছে)");
        18500 * qty.get()
    });

    println!("১ম পড়া: {}", total.get());
    println!("২য় পড়া: {}", total.get());
    set_note.set("bkash");               // qty বদলায়নি
    println!("note বদলানোর পর: {} ({})", total.get(), note.get());
    set_qty.set(3);
    println!("qty বদলানোর পর: {}", total.get());
}
'''),
    tip("Memo শুধু ততক্ষণই নতুন করে চলে যতক্ষণ সে যে signal পড়ে তার কোনোটা বদলায়। উপরে <code>note</code> বদলালে হিসাব চলেনি।"))

c.lesson("Effect: signal বদলালে side effect",
    say("<code>Effect</code> একটা কাজ চালায় (log, localStorage, API call) আর সে যে signal পড়ে সেগুলো বদলালেই আবার চলে। এখানে আমরা terminal-এ চালাচ্ছি বলে async executor (<code>tokio</code>) আর <code>effects</code> feature চালু করা হয়েছে।"),
    code(r'''
use any_spawner::Executor;
use leptos::prelude::*;
use reactive_graph::effect::Effect;
use std::time::Duration;

#[tokio::main]
async fn main() {
    tokio::task::LocalSet::new().run_until(run()).await;
}

async fn run() {
    Executor::init_tokio().unwrap();
    let owner = Owner::new();
    owner.set();

    let (stock, set_stock) = signal(10);
    Effect::new(move |_| {
        println!("stock এখন {}", stock.get());
    });

    tokio::time::sleep(Duration::from_millis(50)).await;
    set_stock.set(7);
    tokio::time::sleep(Duration::from_millis(50)).await;
    set_stock.set(4);
    tokio::time::sleep(Duration::from_millis(50)).await;
}
''', "rust", deps=SSR_TOKIO),
    php_note("Vue-এর <code>watchEffect()</code> বা <code>watch()</code>। Laravel-এ কাছাকাছি হলো model <code>observer</code>/event listener।"),
    tip("Server-এ (SSR) Effect <b>চলে না</b> — শুধু browser-এ। তাই DOM বা localStorage ছোঁয়া code Effect-এর ভিতরে রাখুন, component body-তে নয়।"),
    warn("Effect দিয়ে অন্য signal সেট করে হিসাব বানাবেন না — সেটার জন্য derived signal বা Memo। Effect শুধু বাইরের জগতের (DOM, log, storage) জন্য।"))


# ================================================================== Dynamic view
c.section("Dynamic view")
c.lesson("Dynamic class আর style",
    say("<code>class:নাম=...</code> একটা condition true হলে class যোগ করে। শুধু ওই attribute বদলায়, পুরো element নয়। Stock ৫-এর নিচে নামলে লাল হয়ে যাবে।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (stock, set_stock) = signal(7);
    let low = move || stock.get() < 5;

    view! {
        <button on:click=move |_| set_stock.update(|n| *n -= 1)>"১টা বিক্রি"</button>
        <p class:low=low class:ok=move || !low()>
            "Redmi 13 stock: " {stock}
        </p>
        <p style:font-size=move || format!("{}px", 12 + stock.get())>"stock যত কমে, লেখা তত ছোট"</p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
''', actions=[("click", "button")] * 3),
    warn("<code>view!</code>-এর attribute-এর ভিতরে সরাসরি <code>&lt;</code> বা <code>&gt;</code> লিখলে macro সেটাকে tag-এর অংশ ভাবে। তুলনা আলাদা closure-এ রাখুন (<code>let low = move || stock.get() &lt; 5;</code>) — code-ও পরিষ্কার থাকে।"),
    php_note("Blade-এ <code>@class(['low' =&gt; $stock &lt; 5])</code>। Vue-এ <code>:class=\"{ low: stock &lt; 5 }\"</code>।"))

c.lesson("Input আর two-way binding",
    say("Leptos-এ binding হাতে লিখতে হয় — দুই লাইন: <code>prop:value</code> (signal → input) আর <code>on:input</code> (input → signal)। জাদু নেই, তাই বোঝাও সহজ।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (name, set_name) = signal(String::new());

    view! {
        <input type="text" placeholder="গ্রাহকের নাম"
            prop:value=name
            on:input:target=move |ev| set_name.set(ev.target().value())
        />
        <p>"Invoice: " {move || if name.get().is_empty() { "—".to_string() } else { format!("{} -এর জন্য", name.get()) }}</p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
''', actions=[("fill", "input", "Karim")]),
    php_note("Vue-এর <code>v-model</code> বা Livewire-এর <code>wire:model</code> এই দুই লাইনের shortcut। Leptos-এ shortcut নেই; ফলে কী হচ্ছে সবসময় চোখের সামনে।"))

c.lesson("Form submit",
    say("<code>on:submit</code>-এ <code>ev.prevent_default()</code> না দিলে page reload হয়ে যায় — ঠিক সাধারণ HTML form-এর মতো। সব input একবারে signal-এ রাখা যায়।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (qty, set_qty) = signal(1u32);
    let (msg, set_msg) = signal(String::new());

    view! {
        <form on:submit=move |ev| {
            ev.prevent_default();
            set_msg.set(format!("INV-1001 তৈরি: {} টি, মোট {} Taka", qty.get(), qty.get() * 18500));
        }>
            <input type="number" min="1"
                prop:value=qty
                on:input:target=move |ev| set_qty.set(ev.target().value().parse().unwrap_or(1))
            />
            <button type="submit">"Invoice বানান"</button>
        </form>
        <p class="ok">{msg}</p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
''', actions=[("fill", "input", "3"), ("click", "button")]))

c.lesson("Checkbox আর select",
    say("Checkbox-এ <code>prop:checked</code> আর <code>on:change</code>; select-এও একই ধরন। Input যা-ই হোক, নিয়ম এক: signal ↔ DOM property।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (vat, set_vat) = signal(false);
    let (branch, set_branch) = signal("Mirpur".to_string());
    let total = move || if vat.get() { 18500 * 115 / 100 } else { 18500 };

    view! {
        <label>
            <input type="checkbox" prop:checked=vat on:change:target=move |ev| set_vat.set(ev.target().checked())/>
            " VAT যোগ করুন"
        </label>
        <p>
            <select on:change:target=move |ev| set_branch.set(ev.target().value())>
                <option>"Mirpur"</option>
                <option>"Uttara"</option>
                <option>"Gulshan"</option>
            </select>
        </p>
        <p class="bold">{branch} " শাখা — " {total} " Taka"</p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
''', actions=[("click", "input"), ("select", "select", "Uttara")]))

c.lesson("Show: শর্ত অনুযায়ী দেখানো",
    say("<code>&lt;Show when=... fallback=...&gt;</code> condition true হলে ভিতরের অংশ দেখায়, না হলে fallback। Blade-এর <code>@if / @else</code>।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn App() -> impl IntoView {
    let (stock, set_stock) = signal(2);
    let in_stock = move || stock.get() > 0;

    view! {
        <button on:click=move |_| set_stock.update(|n| *n -= 1)>"১টা বিক্রি"</button>
        <Show
            when=in_stock
            fallback=|| view! { <p class="low">"স্টক শেষ!"</p> }
        >
            <p class="ok">"স্টকে আছে: " {stock}</p>
        </Show>
    }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
''', actions=[("click", "button"), ("click", "button")]),
    tip("সাধারণ <code>{move || if ... { ... } else { ... }}</code>-ও চলে। দুই branch-এর type আলাদা হলে শেষে <code>.into_any()</code> লাগে — <code>Show</code> সেই ঝামেলা সামলে দেয়।"))

c.lesson("For: list দেখানো",
    say("<code>&lt;For&gt;</code>-এ তিনটে জিনিস: <code>each</code> (list), <code>key</code> (প্রতিটার unique id), <code>children</code> (প্রতিটা কেমন দেখাবে)। key থাকায় Leptos জানে কোন row যোগ/বাদ হলো — বাকিগুলো ছোঁয় না।"),
    web(r'''
use leptos::prelude::*;

#[derive(Clone)]
struct Product { id: u32, name: &'static str, price: u32 }

#[component]
fn App() -> impl IntoView {
    let (products, _) = signal(vec![
        Product { id: 1, name: "iPhone 15", price: 112000 },
        Product { id: 2, name: "Samsung A55", price: 41500 },
        Product { id: 3, name: "Redmi 13", price: 18500 },
    ]);

    view! {
        <ul>
            <For
                each=move || products.get()
                key=|p| p.id
                children=|p| view! { <li>{p.name} " — " {p.price} " Taka"</li> }
            />
        </ul>
    }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
''', actions=[]),
    php_note("<code>@foreach ($products as $p)</code>। বাড়তি <code>key</code> লাগে যাতে list বদলালে শুধু বদলানো row-টাই DOM-এ আপডেট হয়।"))

c.lesson("List-এ যোগ আর বাদ",
    say("Cart বানাই: Vec-টা একটা signal। <code>update</code>-এ <code>push</code>/<code>retain</code> করলেই list নিজে আপডেট হয়।"),
    web(r'''
use leptos::prelude::*;

#[derive(Clone)]
struct Item { id: u32, name: &'static str, price: u32 }

#[component]
fn App() -> impl IntoView {
    let (cart, set_cart) = signal(Vec::<Item>::new());
    let (next_id, set_next_id) = signal(1u32);

    let add = move |name: &'static str, price: u32| {
        set_cart.update(|c| c.push(Item { id: next_id.get(), name, price }));
        set_next_id.update(|n| *n += 1);
    };
    let total = move || cart.get().iter().map(|i| i.price).sum::<u32>();

    view! {
        <button on:click=move |_| add("Redmi 13", 18500)>"Redmi 13"</button>
        <button on:click=move |_| add("Charger", 1200)>"Charger"</button>
        <ul>
            <For
                each=move || cart.get()
                key=|i| i.id
                children=move |i| {
                    let id = i.id;
                    view! {
                        <li>
                            {i.name} " — " {i.price} " "
                            <button on:click=move |_| set_cart.update(|c| c.retain(|x| x.id != id))>"✕"</button>
                        </li>
                    }
                }
            />
        </ul>
        <p class="total">"মোট: " {total} " Taka"</p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App);
}
''', actions=[("click", "button:nth-of-type(1)"), ("click", "button:nth-of-type(2)"),
              ("click", "button:nth-of-type(1)"), ("shot", "তিনটে যোগ হলো"), ("click", "li:nth-child(2) button")]))


# ================================================================== Component-এর মধ্যে যোগাযোগ
c.section("Component-এর যোগাযোগ")
c.lesson("Signal child-কে পাঠানো",
    say("Signal <code>Copy</code> — তাই child component-এ prop হিসেবে সহজেই যায়। Parent-এর signal বদলালে child-এর text নিজেই বদলায়, কোনো event বা callback ছাড়া।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn StockBadge(stock: ReadSignal<u32>) -> impl IntoView {
    view! { <p class="bold">"স্টক: " {stock}</p> }
}

#[component]
fn SellButton(set_stock: WriteSignal<u32>) -> impl IntoView {
    view! { <button on:click=move |_| set_stock.update(|n| *n -= 1)>"১টা বিক্রি"</button> }
}

#[component]
fn App() -> impl IntoView {
    let (stock, set_stock) = signal(10);
    view! {
        <StockBadge stock=stock/>
        <SellButton set_stock=set_stock/>
    }
}
''' + MAIN, actions=[("click", "button")] * 4),
    tip("পড়ার handle (<code>ReadSignal</code>) আর লেখার handle (<code>WriteSignal</code>) আলাদা পাঠানো যায় — child শুধু পড়তে পারবে, বদলাতে পারবে না।"))

c.lesson("Callback: child থেকে parent-কে খবর",
    say("Child-এর কাছে parent-এর signal না দিয়ে একটা <code>Callback</code> দিলে child জানে না state কোথায় — শুধু বলে \"কিছু একটা হয়েছে\"। এটাই Vue-এর <code>emit</code>।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn SellButton(#[prop(into)] on_sell: Callback<u32>, qty: u32) -> impl IntoView {
    view! { <button on:click=move |_| on_sell.run(qty)>{format!("{} টা বিক্রি", qty)}</button> }
}

#[component]
fn App() -> impl IntoView {
    let (stock, set_stock) = signal(20u32);
    view! {
        <SellButton qty=1 on_sell=move |n| set_stock.update(|s| *s -= n)/>
        <SellButton qty=5 on_sell=move |n| set_stock.update(|s| *s -= n)/>
        <p>"স্টক: " {stock}</p>
    }
}
''' + MAIN, actions=[("click", "button:nth-of-type(1)"), ("click", "button:nth-of-type(2)")]),
    php_note("Livewire-এ child থেকে <code>$this-&gt;dispatch('sold', qty: 5)</code> আর parent-এ <code>#[On('sold')]</code>।"))

c.lesson("Context: prop drilling ছাড়া",
    say("গভীর component-এ data পাঠাতে প্রতিটা স্তরে prop দেওয়া বিরক্তিকর। <code>provide_context</code> দিয়ে উপরে রাখুন, নিচে যেকোনো জায়গায় <code>expect_context</code> দিয়ে নিন।"),
    web(r'''
use leptos::prelude::*;

#[component]
fn CartCount() -> impl IntoView {
    let cart = expect_context::<RwSignal<Vec<&'static str>>>();
    view! { <p class="bold">"Cart-এ " {move || cart.get().len()} " টি জিনিস"</p> }
}

#[component]
fn AddButton(name: &'static str) -> impl IntoView {
    let cart = expect_context::<RwSignal<Vec<&'static str>>>();
    view! { <button on:click=move |_| cart.update(|c| c.push(name))>{name}</button> }
}

#[component]
fn App() -> impl IntoView {
    provide_context(RwSignal::new(Vec::<&'static str>::new()));
    view! {
        <CartCount/>
        <AddButton name="Redmi 13"/>
        <AddButton name="Charger"/>
    }
}
''' + MAIN, actions=[("click", "button:nth-of-type(1)"), ("click", "button:nth-of-type(2)"), ("click", "button:nth-of-type(2)")]),
    php_note("Laravel-এর service container/<code>app()</code>-এর ছোট সংস্করণ — তবে এখানে context শুধু ওই component tree-র ভিতরে।"),
    tip("<code>RwSignal</code> হলো read আর write একসাথে একটা handle — context-এ রাখার জন্য সুবিধার।"))

# ================================================================== Async data
c.section("Async data")
PRODUCTS_JSON = '''[
  {"id": 1, "name": "iPhone 15", "price": 112000, "stock": 4},
  {"id": 2, "name": "Samsung A55", "price": 41500, "stock": 9},
  {"id": 3, "name": "Redmi 13", "price": 18500, "stock": 2}
]'''
FETCH = {"gloo-net": '{ version = "0.6", features = ["http"] }', "serde": '{ version = "1", features = ["derive"] }',
         "gloo-timers": '{ version = "0.3", features = ["futures"] }'}

c.lesson("API থেকে data আনা: LocalResource",
    say("Browser-এ server থেকে data আনতে <code>LocalResource</code> — একটা async block দিন, ফল আসা পর্যন্ত Leptos অপেক্ষা করে। <code>&lt;Suspense&gt;</code> বলে অপেক্ষার সময় কী দেখাবে। এখানে আসলেই <code>/products.json</code> request যাচ্ছে।"),
    web(r'''
use gloo_net::http::Request;
use gloo_timers::future::TimeoutFuture;
use leptos::prelude::*;
use serde::Deserialize;

#[derive(Clone, Deserialize)]
struct Product { name: String, price: u32, stock: u32 }

async fn load_products() -> Vec<Product> {
    TimeoutFuture::new(1500).await;   // ধীর network বোঝাতে
    Request::get("/products.json").send().await.unwrap().json().await.unwrap()
}

#[component]
fn App() -> impl IntoView {
    let products = LocalResource::new(load_products);

    view! {
        <h3>"Rahim Mobile"</h3>
        <Suspense fallback=|| view! { <p class="muted">"লোড হচ্ছে…"</p> }>
            {move || Suspend::new(async move {
                let list = products.await;
                view! {
                    <ul>
                        {list.into_iter().map(|p| view! { <li>{p.name} " — " {p.price} " Taka (" {p.stock} ")"</li> }).collect_view()}
                    </ul>
                }
            })}
        </Suspense>
    }
}
''' + MAIN, deps=FETCH, site={"products.json": PRODUCTS_JSON},
        actions=[("wait", 2500)]),
    php_note("Vue-এ <code>onMounted(() =&gt; fetch(...))</code> আর <code>v-if=\"loading\"</code> হাতে লিখতে হয়। এখানে Resource + Suspense সেটা একসাথে সামলায়।"))

c.lesson("Resource আবার চালানো",
    say("Resource-এর async block যে signal পড়ে, সেটা বদলালে সে নিজে নতুন করে data আনে। Branch বদলালে stock আবার আসছে — হাতে কিছু লিখতে হয়নি।"),
    web(r'''
use gloo_net::http::Request;
use gloo_timers::future::TimeoutFuture;
use leptos::prelude::*;
use serde::Deserialize;

#[derive(Clone, Deserialize)]
struct Product { name: String, stock: u32 }

#[component]
fn App() -> impl IntoView {
    let (min_stock, set_min_stock) = signal(0u32);

    let products = LocalResource::new(move || {
        let min = min_stock.get();
        async move {
            TimeoutFuture::new(200).await;
            let all: Vec<Product> = Request::get("/products.json").send().await.unwrap().json().await.unwrap();
            all.into_iter().filter(|p| p.stock >= min).collect::<Vec<_>>()
        }
    });

    view! {
        <button on:click=move |_| set_min_stock.set(5)>"স্টক ≥ ৫ দেখান"</button>
        <Suspense fallback=|| view! { <p class="muted">"লোড হচ্ছে…"</p> }>
            {move || Suspend::new(async move {
                let list = products.await;
                view! { <ul>{list.into_iter().map(|p| view! { <li>{p.name} " (" {p.stock} ")"</li> }).collect_view()}</ul> }
            })}
        </Suspense>
    }
}
''' + MAIN, deps=FETCH, site={"products.json": PRODUCTS_JSON},
        actions=[("wait", 800), ("shot", "সব product"), ("click", "button"), ("wait", 800)]))


# ================================================================== Router
c.section("Router")
ROUTER = {"leptos_router": "0.8"}

c.lesson("Router: একাধিক page",
    say("<code>leptos_router</code> client-side routing দেয় — link চাপলে page reload হয় না, শুধু ঠিক অংশটা বদলায়। <code>&lt;A&gt;</code> হলো <code>&lt;a&gt;</code>-এর router-aware রূপ।"),
    web(r'''
use leptos::prelude::*;
use leptos_router::components::{Route, Router, Routes, A};
use leptos_router::path;

#[component]
fn Home() -> impl IntoView {
    view! { <h3>"Rahim Mobile"</h3><p>"স্বাগতম!"</p> }
}

#[component]
fn Branches() -> impl IntoView {
    view! { <h3>"আমাদের শাখা"</h3><ul><li>"Mirpur"</li><li>"Uttara"</li><li>"Gulshan"</li></ul> }
}

#[component]
fn App() -> impl IntoView {
    view! {
        <Router>
            <nav>
                <A href="/">"Home"</A>" | "<A href="/branches">"Branches"</A>
            </nav>
            <main>
                <Routes fallback=|| view! { <p>"পাতাটা পাওয়া যায়নি (404)"</p> }>
                    <Route path=path!("/") view=Home/>
                    <Route path=path!("/branches") view=Branches/>
                </Routes>
            </main>
        </Router>
    }
}
''' + MAIN, deps=ROUTER, actions=[("click", "a[href='/branches']")]),
    php_note("<code>routes/web.php</code>-এ <code>Route::get('/branches', ...)</code>। পার্থক্য: এখানে server-এ না গিয়ে browser নিজেই view বদলায়।"))

c.lesson("Route parameter",
    say("<code>path!(\"/products/:id\")</code> — Laravel-এর <code>/products/{id}</code>। Component-এর ভিতরে <code>use_params_map()</code> দিয়ে মান পড়া যায়।"),
    web(r'''
use leptos::prelude::*;
use leptos_router::components::{Route, Router, Routes, A};
use leptos_router::hooks::use_params_map;
use leptos_router::path;

#[component]
fn List() -> impl IntoView {
    view! {
        <ul>
            <li><A href="/products/1">"iPhone 15"</A></li>
            <li><A href="/products/2">"Samsung A55"</A></li>
        </ul>
    }
}

#[component]
fn Detail() -> impl IntoView {
    let params = use_params_map();
    let id = move || params.read().get("id").unwrap_or_default();
    view! {
        <h3>"Product #" {id}</h3>
        <A href="/">"← সব product"</A>
    }
}

#[component]
fn App() -> impl IntoView {
    view! {
        <Router>
            <Routes fallback=|| "404">
                <Route path=path!("/") view=List/>
                <Route path=path!("/products/:id") view=Detail/>
            </Routes>
        </Router>
    }
}
''' + MAIN, deps=ROUTER, actions=[("click", "a[href='/products/2']")]),
    tip("Parameter বদলালে (<code>/products/1</code> → <code>/products/2</code>) component আবার তৈরি হয় না — <code>params</code> signal বদলায়, তাই শুধু ওই text আপডেট হয়।"))

c.lesson("Nested route আর layout",
    say("Admin panel-এর মতো সাধারণ layout (sidebar) রেখে ভিতরের অংশ বদলাতে <code>ParentRoute</code> আর <code>&lt;Outlet/&gt;</code>। Blade-এর <code>@extends('layout')</code>।"),
    web(r'''
use leptos::prelude::*;
use leptos_router::components::{Outlet, ParentRoute, Route, Router, Routes, A};
use leptos_router::path;

#[component]
fn AdminLayout() -> impl IntoView {
    view! {
        <h3>"Admin"</h3>
        <nav><A href="/admin/stock">"Stock"</A>" | "<A href="/admin/invoices">"Invoices"</A></nav>
        <div class="card"><Outlet/></div>
    }
}

#[component]
fn Stock() -> impl IntoView { view! { <p>"Redmi 13: 2 টি বাকি"</p> } }

#[component]
fn Invoices() -> impl IntoView { view! { <p>"INV-1001 — 23500 Taka"</p> } }

#[component]
fn App() -> impl IntoView {
    view! {
        <Router>
            <Routes fallback=|| "404">
                <Route path=path!("/") view=|| view! { <A href="/admin/stock">"Admin-এ যান"</A> }/>
                <ParentRoute path=path!("/admin") view=AdminLayout>
                    <Route path=path!("stock") view=Stock/>
                    <Route path=path!("invoices") view=Invoices/>
                </ParentRoute>
            </Routes>
        </Router>
    }
}
''' + MAIN, deps=ROUTER, actions=[("click", "a"), ("shot", "Stock page"), ("click", "a[href='/admin/invoices']")]))


# ================================================================== Full-stack
c.section("Full-stack: SSR আর hydration")

SERVER_MAIN = r'''
use app::App;
use axum::Router;
use leptos::prelude::*;
use leptos_axum::{LeptosRoutes, generate_route_list};

fn shell(options: LeptosOptions) -> impl IntoView {
    view! {
        <!DOCTYPE html>
        <html lang="bn">
            <head>
                <meta charset="utf-8"/>
                <HydrationScripts options/>
            </head>
            <body><App/></body>
        </html>
    }
}

#[tokio::main]
async fn main() {
    let options = LeptosOptions::builder()
        .output_name("app")
        .site_root("site")
        .site_addr("127.0.0.1:3000".parse::<std::net::SocketAddr>().unwrap())
        .build();
    let routes = generate_route_list(App);
    let app = Router::new()
        .leptos_routes(&options, routes, {
            let options = options.clone();
            move || shell(options.clone())
        })
        .fallback(leptos_axum::file_and_error_handler(shell))
        .with_state(options.clone());
    let listener = tokio::net::TcpListener::bind(options.site_addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
'''


def fullstack(lib_src, actions=None, requests=None, deps=None, **kw):
    return code(lib_src, "rust", fullstack=True, app=SERVER_MAIN, deps=deps or {}, actions=actions,
                requests=requests or [], file="src/lib.rs", **kw)


c.lesson("তিন রকম rendering",
    say("একই Leptos code তিনভাবে চলতে পারে। এতক্ষণ আমরা প্রথমটা আর (to_html দিয়ে) দ্বিতীয়টার স্বাদ পেয়েছি:"),
    table(["", "কোথায় HTML বানায়", "কখন ভালো"], [
        ["<b>CSR</b> — client-side", "Browser (wasm)", "Dashboard, admin panel; SEO দরকার নেই"],
        ["<b>SSR</b> — server-side", "Server (Rust)", "প্রথম load দ্রুত, SEO, ধীর phone"],
        ["<b>Hydration</b>", "Server HTML বানায়, browser-এর wasm তাতে event জুড়ে দেয়", "SSR-এর গতি + CSR-এর interactivity"]]),
    php_note("সাধারণ Laravel Blade হলো SSR (interactivity নেই)। Inertia/Livewire SSR-এ HTML আসে, তারপর JS জীবন্ত করে — সেটাই hydration।"))

c.lesson("Hydration ধাপে ধাপে",
    steps("Browser <code>GET /</code> করে — server পুরো HTML পাঠায় (লেখা আগে থেকেই আছে)",
          "User সঙ্গে সঙ্গে content দেখে — JavaScript/wasm-এর জন্য অপেক্ষা নেই",
          "পাশাপাশি <code>app.js</code> আর <code>app_bg.wasm</code> download হয়",
          "<code>hydrate()</code> চলে: <b>DOM নতুন করে বানায় না</b>, আছে যে node সেগুলোতে event listener আর signal জুড়ে দেয়",
          "এরপর page পুরোপুরি interactive"),
    tip("আগের <code>&lt;!&gt;</code> marker মনে আছে? Hydration ওগুলো দেখেই বোঝে কোন text node কোন signal-এর।"))

c.lesson("Project গঠন: এক crate, দুই target",
    say("একটা crate-কে দুইভাবে compile করা হয়: <b>server</b> (native, <code>ssr</code> feature) আর <b>browser</b> (wasm, <code>hydrate</code> feature)। UI code <code>lib.rs</code>-এ একটাই — দুই জায়গায় শেয়ার।"),
    code(r'''
[lib]
crate-type = ["cdylib", "rlib"]     # cdylib → wasm, rlib → server

[[bin]]
name = "server"
path = "src/main.rs"
required-features = ["ssr"]

[features]
hydrate = ["leptos/hydrate"]                                  # browser build
ssr = ["dep:axum", "dep:tokio", "dep:leptos_axum", "leptos/ssr"]   # server build
''', "toml", run=False, file="Cargo.toml"),
    tip("বাস্তবে এই দুই build একসাথে চালায় <code>cargo-leptos</code>: <code>cargo leptos watch</code>। এই tutorial-এ আমরা দুটো <code>cargo build</code> আর <code>wasm-bindgen</code> দিয়ে হাতে করেছি, যাতে ভিতরে কী হয় দেখা যায়।"))

c.lesson("Server: axum আর shell",
    say("Server হলো সাধারণ axum app (Rust Web Development-এর মতোই)। <code>shell</code> হলো পুরো HTML page; <code>HydrationScripts</code> সঠিক <code>&lt;script&gt;</code> বসায়; <code>leptos_routes</code> আপনার App render করে।"),
    code(SERVER_MAIN, "rust", run=False, file="src/main.rs"))

c.lesson("সবকিছু একসাথে: server render + hydrate",
    say("Counter-টা এবার full-stack। প্রথমে <code>curl</code> দেখাচ্ছে server আসলে কী পাঠায় — <b>লেখা আগে থেকেই আছে</b>, JavaScript ছাড়াই। তারপর browser-এ wasm hydrate করে, আর click কাজ করে।"),
    fullstack(r'''
use leptos::prelude::*;

#[component]
pub fn App() -> impl IntoView {
    let (sold, set_sold) = signal(0);
    view! {
        <h3>"Rahim Mobile"</h3>
        <button on:click=move |_| set_sold.update(|n| *n += 1)>"বিক্রি হলো"</button>
        <p>"আজ বিক্রি: " {sold} " টি"</p>
    }
}

#[cfg(feature = "hydrate")]
#[wasm_bindgen::prelude::wasm_bindgen]
pub fn hydrate() {
    leptos::mount::hydrate_body(App);
}
''', requests=["curl -s http://localhost:3000/"], actions=[("click", "button")] * 3),
    php_note("<code>curl</code> যা পেল সেটাই <code>php artisan serve</code>-এর Blade output-এর মতো: সম্পূর্ণ HTML। পরের wasm অংশটুকু বাড়তি জাদু।"))

c.lesson("Server function: browser থেকে server-এর Rust function",
    say("<code>#[server]</code> দিলে function-টা <b>শুধু server-এ</b> চলে। Browser-এ সেটার জায়গায় একটা stub বসে, যে নিজে HTTP request পাঠায়। আলাদা API route, controller, <code>fetch</code> কিছু লিখতে হয় না।"),
    fullstack(r'''
use leptos::prelude::*;

#[server(endpoint = "stock")]
pub async fn stock_of(id: u32) -> Result<u32, ServerFnError> {
    // এখানে database query-ও চলতে পারত — এই code browser-এ কখনো পৌঁছায় না
    Ok(match id {
        1 => 4,
        2 => 9,
        _ => 2,
    })
}

#[component]
pub fn App() -> impl IntoView {
    let check = Action::new(|id: &u32| stock_of(*id));
    view! {
        <button on:click=move |_| { check.dispatch(2); }>"Samsung A55-এর stock দেখুন"</button>
        <p>"Stock: " {move || check.value().get().map(|r| format!("{:?}", r))}</p>
    }
}

#[cfg(feature = "hydrate")]
#[wasm_bindgen::prelude::wasm_bindgen]
pub fn hydrate() {
    leptos::mount::hydrate_body(App);
}
''', requests=["curl -s -X POST http://localhost:3000/api/stock -d 'id=2'"],
        actions=[("click", "button"), ("wait", 600)]),
    php_note("Laravel-এ <code>Route::post('/api/stock')</code> + controller + browser-এ <code>fetch('/api/stock')</code> — তিনটা জিনিস। Leptos-এ একটাই function, type-checked দুই দিকেই।"),
    warn("Server function public HTTP endpoint — Laravel-এর মতোই এখানেও authentication/validation আপনার দায়িত্ব।"))

c.lesson("Server data আগেই HTML-এ",
    say("<code>Resource</code> + server function + <code>Suspense</code>-এ server নিজেই data আনে। Route-এ <code>ssr=SsrMode::Async</code> দিলে server সব data আসা পর্যন্ত অপেক্ষা করে, তারপর <b>পুরো HTML একবারে</b> পাঠায়। User \"লোড হচ্ছে…\" দেখে না, আর search engine পুরো list পায়।"),
    fullstack(r'''
use leptos::prelude::*;
use leptos_router::components::{Route, Router, Routes};
use leptos_router::{SsrMode, path};

#[server(endpoint = "products")]
pub async fn products() -> Result<Vec<(String, u32)>, ServerFnError> {
    Ok(vec![
        ("iPhone 15".to_string(), 112000),
        ("Samsung A55".to_string(), 41500),
        ("Redmi 13".to_string(), 18500),
    ])
}

#[component]
fn Home() -> impl IntoView {
    let list = Resource::new(|| (), |_| products());
    view! {
        <h3>"Rahim Mobile"</h3>
        <Suspense fallback=|| view! { <p>"লোড হচ্ছে…"</p> }>
            {move || Suspend::new(async move {
                let items = list.await.unwrap_or_default();
                view! {
                    <ul>
                        {items.into_iter().map(|(n, p)| view! { <li>{n} " — " {p} " Taka"</li> }).collect_view()}
                    </ul>
                }
            })}
        </Suspense>
    }
}

#[component]
pub fn App() -> impl IntoView {
    view! {
        <Router>
            <Routes fallback=|| "404">
                <Route path=path!("/") view=Home ssr=SsrMode::Async/>
            </Routes>
        </Router>
    }
}

#[cfg(feature = "hydrate")]
#[wasm_bindgen::prelude::wasm_bindgen]
pub fn hydrate() {
    leptos::mount::hydrate_body(App);
}
''', requests=["curl -s http://localhost:3000/"], deps=ROUTER),
    say("উপরের curl-এ <code>&lt;li&gt;</code>গুলো দেখুন — JavaScript ছাড়াই data HTML-এ আছে।"),
    tip("ডিফল্ট mode-এ Leptos আগে fallback (\"লোড হচ্ছে…\") পাঠায়, data পরে একই response-এ stream করে — page দ্রুত খোলে। SEO বা পুরো HTML দরকার হলে <code>SsrMode::Async</code>।"))


# ================================================================== প্রজেক্ট ও deploy
c.section("প্রজেক্ট ও deploy")
c.lesson("Mini project: Rahim Mobile POS",
    say("এ পর্যন্ত যা শিখলাম — signal, Memo, For, Show, component, callback — সব একসাথে। Product-এ চাপলে cart-এ যায়, stock কমে, মোট হিসাব নিজে হয়, stock শেষ হলে button বন্ধ।"),
    web(r'''
use leptos::prelude::*;

#[derive(Clone, Copy)]
struct Phone { name: &'static str, price: u32 }

const PHONES: [Phone; 3] = [
    Phone { name: "iPhone 15", price: 112000 },
    Phone { name: "Samsung A55", price: 41500 },
    Phone { name: "Redmi 13", price: 18500 },
];

#[component]
fn Row(phone: Phone, stock: RwSignal<u32>, #[prop(into)] on_add: Callback<Phone>) -> impl IntoView {
    let empty = move || stock.get() == 0;
    view! {
        <div class="card">
            <span class="bold">{phone.name}</span>" — " {phone.price} " Taka"
            <p class:low=empty class:muted=move || !empty()>"স্টক: " {stock}</p>
            <button disabled=empty on:click=move |_| on_add.run(phone)>"Cart-এ দিন"</button>
        </div>
    }
}

#[component]
fn App() -> impl IntoView {
    let stocks: Vec<RwSignal<u32>> = vec![RwSignal::new(1), RwSignal::new(5), RwSignal::new(2)];
    let (cart, set_cart) = signal(Vec::<Phone>::new());
    let total = Memo::new(move |_| cart.get().iter().map(|p| p.price).sum::<u32>());

    let rows = PHONES.iter().zip(stocks.clone()).map(|(p, stock)| {
        view! {
            <Row phone=*p stock=stock on_add=move |p: Phone| {
                stock.update(|s| *s -= 1);
                set_cart.update(|c| c.push(p));
            }/>
        }
    }).collect_view();

    view! {
        <h3>"Rahim Mobile"</h3>
        {rows}
        <p class="total">"Cart: " {move || cart.get().len()} " টি · মোট " {total} " Taka"</p>
    }
}
''' + MAIN, actions=[("click", ".card:nth-of-type(1) button"), ("click", ".card:nth-of-type(3) button"),
                     ("click", ".card:nth-of-type(3) button")]),
    task("Cart-এর প্রতিটা item-এর পাশে \"✕\" button যোগ করুন, যা item বাদ দিয়ে stock আবার ফেরত দেয়। (ইঙ্গিত: <code>For</code> আর <code>retain</code>)"))

c.lesson("Quiz",
    quiz("Signal বদলালে Leptos-এ component function আবার চলে কি?",
         "না। Component function শুধু একবার চলে। Signal বদলালে শুধু সেই text/attribute (যে signal পড়ছে) আপডেট হয় — Virtual DOM diff লাগে না।"),
    quiz("<code>&lt;For&gt;</code>-এ <code>key</code> কেন লাগে?",
         "যাতে list বদলালে Leptos বোঝে কোন item যোগ/বাদ/সরল — শুধু সেই row DOM-এ বদলায়, বাকিগুলো যেমন আছে তেমনই থাকে।"),
    quiz("Hydration আর CSR-এর পার্থক্য কী?",
         "CSR-এ browser খালি page থেকে শুরু করে DOM বানায়। Hydration-এ server আগেই HTML পাঠিয়েছে; wasm এসে সেই DOM-এই event আর signal জুড়ে দেয় — নতুন করে বানায় না।"))

c.lesson("Release build আর wasm-এর আকার",
    say("Debug build-এর wasm বড়। Production-এ <code>--release</code> আর নিচের profile দিলে wasm অনেক ছোট হয় — mobile network-এ এটাই পার্থক্য গড়ে।"),
    code(r'''
[profile.release]
opt-level = "z"      # আকার ছোট করার জন্য optimize
lto = true           # পুরো program একসাথে optimize
codegen-units = 1
panic = "abort"
''', "toml", run=False, file="Cargo.toml"),
    shell('''# শুধু client-side app (Trunk)
trunk build --release        # dist/ ফোল্ডারে static file, যেকোনো hosting-এ চলে

# full-stack app (cargo-leptos)
cargo install cargo-leptos
cargo leptos build --release # server binary + wasm + CSS একসাথে'''),
    tip("CSR app শুধু static file — Nginx, GitHub Pages, Netlify-তে দিয়ে দিলেই হয়। SSR app একটা server binary — Rust Web Development-এর মতোই systemd বা Docker-এ চালান।"))

c.lesson("কখন কোনটা?",
    table(["দরকার", "বেছে নিন"], [
        ["Admin panel, dashboard, internal tool", "<b>CSR</b> + Trunk — সবচেয়ে সহজ"],
        ["Public site, SEO, দ্রুত প্রথম load", "<b>SSR + hydration</b> + cargo-leptos"],
        ["শুধু HTML পাতা, ইন্টারঅ্যাকশন কম", "Blade/Laravel-ই যথেষ্ট; Leptos-এর দরকার নেই"],
        ["Rust-এর একই type server আর browser-এ", "<b>Server function</b> — Leptos-এর সবচেয়ে বড় সুবিধা"]]),
    warn("Leptos এখনো দ্রুত বদলায় (0.x)। নতুন version-এ API একটু আলাদা হতে পারে — project-এ version লক করে রাখুন, আর upgrade-এর আগে release note পড়ুন।"))

# @@END
c.lesson("Leptos-এর জার্গন কার্ড",
    table(["শব্দ", "এক লাইনে"], [
        ["DOM / Virtual DOM", "page-এর tree / তুলনার কপি-tree (Leptos-এ নেই)"],
        ["Reactivity", "data বদলালে নির্ভরশীল অংশ নিজে আপডেট"],
        ["Signal", "বদলানো যায় এমন reactive মান"],
        ["Memo / Derived", "অন্য signal থেকে হিসাব করা মান"],
        ["Effect / Side effect", "বাইরের জগতে কাজ (log, storage) যা signal বদলালে চলে"],
        ["Component", "পুনর্ব্যবহারযোগ্য UI অংশ (function)"],
        ["Prop", "component-কে দেওয়া argument"],
        ["CSR / SSR / Hydration", "browser-এ / server-এ বানানো / server-এর HTML জীবন্ত করা"],
        ["Server function", "server-এ চলে, browser থেকে ডাকা যায় এমন function"],
        ["WebAssembly", "browser-এ চলা compile-করা binary"]]))

c.finish("Leptos শেখা শেষ", "আপনি এখন Rust-এ interactive UI বানাতে পারেন — browser-এ, server-এ, দুই জায়গাতেই এক code।",
         recap=["Leptos: fine-grained reactivity, Virtual DOM নেই", "view! আর #[component], props, children",
                "signal, Memo, Effect — component একবারই চলে", "on:click, prop:value, For, Show",
                "Callback, context দিয়ে component-এর যোগাযোগ", "LocalResource + Suspense, leptos_router",
                "SSR + hydration, #[server] function", "Trunk (CSR) বনাম cargo-leptos (full-stack)"])
c.build()
