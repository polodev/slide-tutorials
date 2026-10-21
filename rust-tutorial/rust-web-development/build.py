"""Rust Web Development — axum + SQLite, explained for Laravel developers.
Every server lesson is compiled, started, and called with curl at build time; the real responses are shown.
The final lesson's code is also written to shop-api/ as a runnable project.
Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, steps, table, task, tip, warn  # noqa: E402

AXUM = {"axum": "0.8", "tokio": '{ version = "1", features = ["full"] }',
        "serde": '{ version = "1", features = ["derive"] }', "serde_json": "1"}
DB = {**AXUM, "sqlx": '{ version = "0.9", features = ["runtime-tokio", "sqlite"] }'}
WEB = {**DB, "tower-http": '{ version = "0.7", features = ["cors", "trace"] }', "tracing-subscriber": "0.3",
       "dotenvy": "0.15"}


def laravel(src, label="Laravel-এ"):
    return code(src, "php", run=False, label=label)


JSON_H = "-H 'Content-Type: application/json'"

c = Course(slug="rust-web-development", title="Rust Web Development — axum দিয়ে API", folder=HERE,
           subtitle="Laravel জানেন? axum, tokio আর sqlx দিয়ে একটা দোকানের Product API: route, JSON, validation, database, middleware, deploy",
           series="Rust Web Development", next_course=("../rust-leptos/index.html", "Rust Leptos — Reactive Full-stack Web"))

c.cover("Rust Web Development<br>axum দিয়ে API",
        "Laravel-এ যা প্রতিদিন করেন — route, controller, validation, Eloquent, middleware — সেগুলোই Rust-এ। শেষে পুরো একটা Product API, যা চালানো যায়।",
        learn=["axum-এ route আর handler", "Path, Query আর JSON body", "Status code আর error response",
               "Laravel-এর মতো 422 validation", "Shared state (Arc<Mutex>)", "SQLite + sqlx: CRUD, search, pagination",
               "Middleware: log, CORS, API key", "Release build, Nginx, systemd, Docker"],
        need="Rust 101–103 (বিশেষ করে struct, Result, trait, serde আর async)।")

# ================================================================== start
c.section("শুরু")
c.lesson("Laravel থেকে axum: কোনটা কী",
    say("axum হলো Rust-এর জনপ্রিয় web framework, tokio টিমের বানানো। Laravel-এর মতো সব কিছু একসাথে দেয় না — ছোট ছোট crate জুড়ে বানাতে হয়।"),
    table(["Laravel", "Rust (axum)"], [
        ["<code>routes/api.php</code>", "<code>Router::new().route(...)</code>"],
        ["Controller method", "async handler function"],
        ["<code>$request</code>, route model binding", "Extractor: <code>Path</code>, <code>Query</code>, <code>Json</code>, <code>State</code>"],
        ["<code>response()-&gt;json()</code>", "<code>Json(data)</code>"],
        ["<code>$request-&gt;validate()</code>", "serde + নিজের validate function"],
        ["Eloquent / Query Builder", "sqlx (raw SQL, compile-time নিরাপদ)"],
        ["Middleware", "tower layer / <code>middleware::from_fn</code>"],
        ["<code>php artisan serve</code>", "<code>cargo run</code>"], [".env + <code>config()</code>", "dotenvy + <code>std::env::var</code>"]]),
    tip("পার্থক্যটা মনে রাখুন: Laravel প্রতি request-এ নতুন করে শুরু হয়। Rust server একবার চালু হয়ে চলতেই থাকে — তাই memory-তে state রাখা যায়, আর খুব দ্রুত।"))

c.lesson("Project বানানো",
    shell("$ cargo new shop-api\n$ cd shop-api\n$ cargo add axum\n$ cargo add tokio --features full\n$ cargo add serde --features derive\n$ cargo add serde_json"),
    code('''
[package]
name = "shop-api"
version = "0.1.0"
edition = "2024"

[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
''', "toml", file="Cargo.toml"),
    points("<b>axum</b> — routing আর request/response", "<b>tokio</b> — async runtime (server চালায়)",
           "<b>serde</b> — JSON ↔ struct"),
    php_note("<code>composer create-project laravel/laravel</code> এর জায়গায় <code>cargo new</code> + দরকারি crate।"))

c.lesson("প্রথম server",
    say("<code>Router</code>-এ route যোগ করি, তারপর port-এ listen করে <code>axum::serve</code>। Handler হলো সাধারণ <code>async fn</code>।"),
    code(r'''
use axum::{Router, routing::get};

async fn home() -> &'static str {
    "Hello, World! Shop API চলছে।"
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/", get(home));

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    println!("চলছে: http://127.0.0.1:3000");
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=["curl -s http://127.0.0.1:3000/"]),
    laravel('''
Route::get('/', function () {
    return 'Hello, World! Shop API চলছে।';
});
'''),
    shell("$ cargo run"))

# ================================================================== routing
c.section("Routing ও Request")
c.lesson("কয়েকটা route আর 404",
    say("একই path-এ আলাদা method: <code>get(list).post(create)</code>। কোনো route না মিললে <code>fallback</code>।"),
    code(r'''
use axum::{Router, http::StatusCode, routing::get};

async fn list() -> &'static str { "সব product" }
async fn create() -> &'static str { "নতুন product যোগ হলো" }
async fn about() -> &'static str { "Rahim Mobile, Mirpur 10" }
async fn not_found() -> (StatusCode, &'static str) {
    (StatusCode::NOT_FOUND, "এই পাতা নেই")
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/products", get(list).post(create))
        .route("/about", get(about))
        .fallback(not_found);

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=["curl -s http://127.0.0.1:3000/products",
                          "curl -s -X POST http://127.0.0.1:3000/products",
                          "curl -s http://127.0.0.1:3000/blog"]),
    php_note("<code>Route::get('/products', ...)</code> আর <code>Route::post('/products', ...)</code> — axum-এ এক লাইনে। <code>Route::fallback()</code>-ও আছে।"))

c.lesson("Path parameter: /products/{id}",
    say("<code>{id}</code> path-এর অংশ ধরে। <code>Path(id): Path&lt;u32&gt;</code> লিখলে axum নিজেই number-এ বদলায় — না পারলে 400।"),
    code(r'''
use axum::{Router, extract::Path, routing::get};

async fn show(Path(id): Path<u32>) -> String {
    format!("Product #{id}")
}

async fn branch_sale(Path((branch, day)): Path<(String, u32)>) -> String {
    format!("{branch} শাখা, {day} তারিখের বিক্রি")
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/products/{id}", get(show))
        .route("/branches/{branch}/sales/{day}", get(branch_sale));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=["curl -s http://127.0.0.1:3000/products/42",
                          "curl -s http://127.0.0.1:3000/branches/Mirpur/sales/21",
                          "curl -s http://127.0.0.1:3000/products/abc"]),
    php_note("Laravel-এর <code>Route::get('/products/{id}', fn (int $id) =&gt; ...)</code>। axum 0.8 থেকে path-এ <code>{id}</code> (আগে ছিল <code>:id</code>)।"))

c.lesson("Query string: ?q=redmi&page=2",
    say("Query-কে একটা struct-এ deserialize করি। <code>Option</code> field মানে ঐচ্ছিক; <code>#[serde(default)]</code> দিলে না থাকলে ডিফল্ট মান।"),
    code(r'''
use axum::{Router, extract::Query, routing::get};
use serde::Deserialize;

#[derive(Deserialize)]
struct Search {
    q: Option<String>,
    #[serde(default = "first_page")]
    page: u32,
}

fn first_page() -> u32 { 1 }

async fn search(Query(s): Query<Search>) -> String {
    let q = s.q.unwrap_or_else(|| "সব".to_string());
    format!("খোঁজা: {q}, পাতা: {}", s.page)
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/products", get(search));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=["curl -s 'http://127.0.0.1:3000/products?q=redmi&page=2'",
                          "curl -s 'http://127.0.0.1:3000/products'",
                          "curl -s 'http://127.0.0.1:3000/products?page=two'"]),
    php_note("<code>$request-&gt;query('q')</code> আর <code>$request-&gt;integer('page', 1)</code> — এখানে সব একটা typed struct-এ।"))

c.lesson("JSON response",
    say("struct-এ <code>#[derive(Serialize)]</code> দিয়ে <code>Json(...)</code>-এ মুড়ে ফেরত দিলেই JSON, সাথে <code>Content-Type: application/json</code>।"),
    code(r'''
use axum::{Json, Router, routing::get};
use serde::Serialize;

#[derive(Serialize)]
struct Product {
    id: u32,
    name: String,
    price: u32,
    in_stock: bool,
}

async fn list() -> Json<Vec<Product>> {
    Json(vec![
        Product { id: 1, name: "Redmi 13".into(), price: 17500, in_stock: true },
        Product { id: 2, name: "Galaxy A15".into(), price: 21000, in_stock: false },
    ])
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/products", get(list));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=["curl -s http://127.0.0.1:3000/products"]),
    laravel('''
Route::get('/products', fn () => response()->json([
    ['id' => 1, 'name' => 'Redmi 13', 'price' => 17500, 'in_stock' => true],
]));
'''))

c.lesson("JSON body নেওয়া (POST)",
    say("<code>Json(input): Json&lt;NewProduct&gt;</code> — body পড়ে struct বানায়। ভুল JSON বা field না থাকলে handler-এ ঢোকার আগেই axum 400/422 দিয়ে দেয়।"),
    code(r'''
use axum::{Json, Router, http::StatusCode, routing::post};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct NewProduct {
    name: String,
    price: u32,
}

#[derive(Serialize)]
struct Product {
    id: u32,
    name: String,
    price: u32,
}

async fn create(Json(input): Json<NewProduct>) -> (StatusCode, Json<Product>) {
    let p = Product { id: 101, name: input.name, price: input.price };
    (StatusCode::CREATED, Json(p))
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/products", post(create));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=[
        f"""curl -s -X POST http://127.0.0.1:3000/products {JSON_H} -d '{{"name":"Vivo Y28","price":18000}}'""",
        f"""curl -s -X POST http://127.0.0.1:3000/products {JSON_H} -d '{{"name":"Vivo Y28"}}'""",
        f"""curl -s -X POST http://127.0.0.1:3000/products {JSON_H} -d '{{"name":"Vivo Y28","price":-5}}'"""]),
    tip("ঋণাত্মক দাম <code>u32</code>-এ বসে না, তাই সেটাও আটকে গেল — type নিজেই অর্ধেক validation করে দিচ্ছে।"))

c.lesson("Status code আর header",
    say("Handler যা ফেরত দেয় তা <code>IntoResponse</code> হলেই চলে। <code>(StatusCode, header, body)</code> tuple দিয়ে সব নিয়ন্ত্রণ করা যায়।"),
    code(r'''
use axum::{Router, http::{StatusCode, header}, response::IntoResponse, routing::get};

async fn health() -> impl IntoResponse {
    (StatusCode::OK, [(header::CACHE_CONTROL, "no-store")], "ok")
}

async fn old_url() -> impl IntoResponse {
    (StatusCode::MOVED_PERMANENTLY, [(header::LOCATION, "/products")])
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/health", get(health)).route("/items", get(old_url));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=["curl -s -i http://127.0.0.1:3000/health", "curl -s -i http://127.0.0.1:3000/items"]),
    php_note("<code>response('ok', 200)-&gt;header('Cache-Control', 'no-store')</code> আর <code>redirect('/products', 301)</code>।"))

# ================================================================== state + errors
c.section("State, Error ও Validation")
c.lesson("Shared state: সব request-এর জন্য এক store",
    say("Server চলতেই থাকে, তাই memory-তে data রাখা যায়। অনেক request একসাথে আসে বলে <code>Arc&lt;Mutex&lt;..&gt;&gt;</code>। <code>.with_state()</code> দিয়ে দিই, handler-এ <code>State</code> দিয়ে নিই।"),
    code(r'''
use axum::{Json, Router, extract::State, routing::get};
use std::sync::{Arc, Mutex};

#[derive(Clone, Default)]
struct AppState {
    visits: Arc<Mutex<u32>>,
}

async fn visit(State(state): State<AppState>) -> Json<serde_json::Value> {
    let mut n = state.visits.lock().unwrap();
    *n += 1;
    Json(serde_json::json!({ "visits": *n }))
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/visit", get(visit)).with_state(AppState::default());
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=["curl -s http://127.0.0.1:3000/visit"] * 3),
    php_note("PHP-তে request শেষ হলেই সব মুছে যায়, তাই এর জন্য Redis/cache লাগে। Rust server-এ state থেকে যায় — কিন্তু restart দিলে memory-র data হারায়, তাই আসল data database-এ।"))

c.lesson("Error-কে JSON বানানো",
    say("নিজের <code>AppError</code> enum বানিয়ে <code>IntoResponse</code> implement করি। তারপর handler <code>Result&lt;Json&lt;T&gt;, AppError&gt;</code> ফেরত দেয়, আর <code>?</code> দিয়ে error সোজা response হয়ে যায়।"),
    code(r'''
use axum::{Json, Router, extract::Path, http::StatusCode,
           response::{IntoResponse, Response}, routing::get};
use serde_json::json;

enum AppError {
    NotFound(String),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            AppError::NotFound(m) => (StatusCode::NOT_FOUND, m),
        };
        (status, Json(json!({ "message": message }))).into_response()
    }
}

async fn show(Path(id): Path<u32>) -> Result<Json<serde_json::Value>, AppError> {
    if id != 1 {
        return Err(AppError::NotFound(format!("Product {id} পাওয়া যায়নি")));
    }
    Ok(Json(json!({ "id": 1, "name": "Redmi 13" })))
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/products/{id}", get(show));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=["curl -s http://127.0.0.1:3000/products/1", "curl -s http://127.0.0.1:3000/products/7"]),
    php_note("Laravel-এর <code>findOrFail()</code> + exception handler JSON-এ <code>{\"message\": ...}</code> দেয় — এখানে আমরা নিজেই সেই কাজটা করলাম।"))

c.lesson("Validation: Laravel-এর মতো 422",
    say("Type ঠিক থাকলেও নিয়ম যাচাই করতে হয় (নাম খালি না, দাম ০-এর বেশি)। Laravel-এর মতো <code>{message, errors}</code> আকারে 422 ফেরত দিলে frontend-এর কোড বদলাতে হয় না।"),
    code(r'''
use axum::{Json, Router, http::StatusCode, routing::post};
use serde::Deserialize;
use serde_json::{Value, json};
use std::collections::BTreeMap;

#[derive(Deserialize)]
struct NewProduct { name: String, price: u32, stock: u32 }

fn validate(p: &NewProduct) -> BTreeMap<&'static str, Vec<String>> {
    let mut errors = BTreeMap::new();
    if p.name.trim().is_empty() {
        errors.insert("name", vec!["নাম দিতে হবে।".to_string()]);
    }
    if p.price == 0 {
        errors.insert("price", vec!["দাম ০-এর বেশি হতে হবে।".to_string()]);
    }
    if p.stock > 1000 {
        errors.insert("stock", vec!["একবারে ১০০০-এর বেশি না।".to_string()]);
    }
    errors
}

async fn create(Json(p): Json<NewProduct>) -> (StatusCode, Json<Value>) {
    let errors = validate(&p);
    if !errors.is_empty() {
        let body = json!({ "message": "দেওয়া তথ্য ঠিক নেই।", "errors": errors });
        return (StatusCode::UNPROCESSABLE_ENTITY, Json(body));
    }
    (StatusCode::CREATED, Json(json!({ "name": p.name, "price": p.price, "stock": p.stock })))
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/products", post(create));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=[
        f"""curl -s -X POST http://127.0.0.1:3000/products {JSON_H} -d '{{"name":" ","price":0,"stock":5000}}'""",
        f"""curl -s -X POST http://127.0.0.1:3000/products {JSON_H} -d '{{"name":"Walton NEXG N9","price":9990,"stock":10}}'"""]),
    laravel('''
$data = $request->validate([
    'name'  => 'required|string',
    'price' => 'required|integer|min:1',
    'stock' => 'required|integer|max:1000',
]);
'''),
    tip("বড় project-এ <code>validator</code> বা <code>garde</code> crate দিয়ে attribute-এ নিয়ম লেখা যায়: <code>#[validate(length(min = 1))]</code>।"))

# ================================================================== database
c.section("Database (SQLite + sqlx)")
c.lesson("sqlx যোগ করা আর connect",
    say("<b>sqlx</b> async SQL library — Eloquent-এর মতো ORM না, আপনি SQL লেখেন, সে নিরাপদে চালায় আর ফলাফল struct-এ বসায়। শুরুতে SQLite (একটা file), পরে শুধু URL বদলে MySQL/PostgreSQL।"),
    shell('$ cargo add sqlx --features runtime-tokio,sqlite'),
    code(r'''
use sqlx::{SqlitePool, sqlite::SqliteConnectOptions};
use std::str::FromStr;

#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {
    let opts = SqliteConnectOptions::from_str("sqlite:shop.db")?.create_if_missing(true);
    let db = SqlitePool::connect_with(opts).await?;

    let (version,): (String,) = sqlx::query_as("SELECT sqlite_version()").fetch_one(&db).await?;
    println!("SQLite {version} এর সাথে যুক্ত হলাম");
    Ok(())
}
''', deps=DB),
    php_note("Laravel 11-এর ডিফল্ট database-ও SQLite (<code>database/database.sqlite</code>)। MySQL-এ যেতে শুধু <code>.env</code>-এর connection বদলান — এখানেও তাই।"))

c.lesson("Table বানানো (migration)",
    say("বড় project-এ <code>sqlx-cli</code> দিয়ে migration file বানানো হয়, Laravel-এর মতোই। ছোট project-এ চালু হওয়ার সময় <code>CREATE TABLE IF NOT EXISTS</code> চালিয়ে দিলেও চলে।"),
    shell("$ cargo install sqlx-cli --no-default-features --features sqlite\n$ sqlx migrate add create_products\n$ sqlx migrate run",
          out="Creating migrations/20261021120000_create_products.sql\nApplied 20261021120000/migrate create products (3.1ms)"),
    code('''
CREATE TABLE products (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    brand      TEXT    NOT NULL,
    price      INTEGER NOT NULL,          -- টাকায়
    stock      INTEGER NOT NULL DEFAULT 0,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
''', "sql", file="migrations/20261021120000_create_products.sql"),
    laravel('''
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('brand');
    $table->unsignedInteger('price');
    $table->unsignedInteger('stock')->default(0);
    $table->timestamps();
});
''', "Laravel migration-এ তুলনা"),
    tip("কোডে <code>sqlx::migrate!().run(&db).await?</code> লিখলে server চালুর সময় নতুন migration নিজেই চলে।"))

c.lesson("Insert আর Select: Eloquent-এর বদলে SQL",
    say("<code>#[derive(FromRow)]</code> দিলে row থেকে struct বানায়। মান সবসময় <code>?</code> placeholder আর <code>.bind()</code> দিয়ে — কখনো string জোড়া লাগাবেন না (SQL injection)।"),
    code(r'''
use sqlx::{FromRow, sqlite::{SqliteConnectOptions, SqlitePoolOptions}};
use std::str::FromStr;

#[derive(FromRow)]
struct Product { id: i64, name: String, price: i64 }

#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {
    let opts = SqliteConnectOptions::from_str("sqlite::memory:")?;
    let db = SqlitePoolOptions::new().max_connections(1).connect_with(opts).await?;
    sqlx::raw_sql("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price INTEGER NOT NULL)")
        .execute(&db).await?;

    for (name, price) in [("Redmi 13", 17500), ("Galaxy A15", 21000), ("Charger", 650)] {
        let id = sqlx::query("INSERT INTO products (name, price) VALUES (?, ?)")
            .bind(name).bind(price).execute(&db).await?.last_insert_rowid();
        println!("যোগ হলো #{id} {name}");
    }

    let cheap: Vec<Product> = sqlx::query_as("SELECT id, name, price FROM products WHERE price < ? ORDER BY price")
        .bind(20000).fetch_all(&db).await?;
    for p in &cheap {
        println!("#{} {:<10} {:>6} টাকা", p.id, p.name, p.price);
    }
    Ok(())
}
''', deps=DB),
    laravel('''
$id = Product::create(['name' => 'Redmi 13', 'price' => 17500])->id;
$cheap = Product::where('price', '<', 20000)->orderBy('price')->get();
'''))

c.lesson("format! দিয়ে SQL? compiler আটকাবে",
    say("User-এর লেখা সরাসরি SQL-এ জুড়লে SQL injection হয়। sqlx 0.9 তাই <code>format!</code> দিয়ে বানানো String query হিসেবে নেয়ই না — শুধু কোডে লেখা স্থির <code>\"...\"</code> (<code>&amp;'static str</code>)।"),
    code(r'''
use sqlx::{SqlitePool, sqlite::SqliteConnectOptions};
use std::str::FromStr;

#[tokio::main]
async fn main() -> Result<(), sqlx::Error> {
    let db = SqlitePool::connect_with(SqliteConnectOptions::from_str("sqlite::memory:")?).await?;
    let search = "Redmi' OR '1'='1";        // কেউ চালাকি করে এটা লিখল
    let sql = format!("SELECT name FROM products WHERE name = '{search}'");
    sqlx::query(&sql).fetch_all(&db).await?;
    Ok(())
}
''', deps=DB, err="E0277"),
    say("ঠিক উপায় সবসময়: <code>sqlx::query(\"... WHERE name = ?\").bind(search)</code>। মান আলাদা যায়, তাই SQL-এর অংশ হতে পারে না।"),
    php_note("Laravel-এর <code>DB::select(\"... name = '$search'\")</code> একই বিপদ; <code>where('name', $search)</code> বা <code>?</code> binding নিরাপদ। Rust এখানে ভুলটাকে compile error বানিয়ে দেয়।"))

c.lesson("CRUD API: database-এর সাথে",
    say("এবার সব জোড়া লাগাই: pool থাকে state-এ, প্রতিটি handler SQL চালায়, <code>sqlx::Error</code> নিজে থেকেই <code>AppError</code>-এ বদলায় (<code>From</code> impl)।"),
    code(r'''
use axum::{Json, Router, extract::{Path, State}, http::StatusCode,
           response::{IntoResponse, Response}, routing::get};
use serde::{Deserialize, Serialize};
use serde_json::json;
use sqlx::{FromRow, SqlitePool, sqlite::SqliteConnectOptions};
use std::str::FromStr;

#[derive(Serialize, FromRow)]
struct Product { id: i64, name: String, price: i64, stock: i64 }

#[derive(Deserialize)]
struct Input { name: String, price: i64, stock: i64 }

enum AppError { NotFound, Db(sqlx::Error) }

impl From<sqlx::Error> for AppError {
    fn from(e: sqlx::Error) -> Self { AppError::Db(e) }
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (code, msg) = match self {
            AppError::NotFound => (StatusCode::NOT_FOUND, "Product পাওয়া যায়নি".to_string()),
            AppError::Db(e) => (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()),
        };
        (code, Json(json!({ "message": msg }))).into_response()
    }
}

async fn index(State(db): State<SqlitePool>) -> Result<Json<Vec<Product>>, AppError> {
    let rows = sqlx::query_as("SELECT id, name, price, stock FROM products ORDER BY id").fetch_all(&db).await?;
    Ok(Json(rows))
}

async fn show(State(db): State<SqlitePool>, Path(id): Path<i64>) -> Result<Json<Product>, AppError> {
    let p: Option<Product> = sqlx::query_as("SELECT id, name, price, stock FROM products WHERE id = ?")
        .bind(id).fetch_optional(&db).await?;
    p.map(Json).ok_or(AppError::NotFound)
}

async fn store(State(db): State<SqlitePool>, Json(i): Json<Input>) -> Result<(StatusCode, Json<Product>), AppError> {
    let id = sqlx::query("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)")
        .bind(&i.name).bind(i.price).bind(i.stock).execute(&db).await?.last_insert_rowid();
    Ok((StatusCode::CREATED, Json(Product { id, name: i.name, price: i.price, stock: i.stock })))
}

async fn update(State(db): State<SqlitePool>, Path(id): Path<i64>, Json(i): Json<Input>) -> Result<Json<Product>, AppError> {
    let done = sqlx::query("UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?")
        .bind(&i.name).bind(i.price).bind(i.stock).bind(id).execute(&db).await?;
    if done.rows_affected() == 0 { return Err(AppError::NotFound); }
    Ok(Json(Product { id, name: i.name, price: i.price, stock: i.stock }))
}

async fn destroy(State(db): State<SqlitePool>, Path(id): Path<i64>) -> Result<StatusCode, AppError> {
    let done = sqlx::query("DELETE FROM products WHERE id = ?").bind(id).execute(&db).await?;
    if done.rows_affected() == 0 { return Err(AppError::NotFound); }
    Ok(StatusCode::NO_CONTENT)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let db = SqlitePool::connect_with(SqliteConnectOptions::from_str("sqlite:shop.db")?.create_if_missing(true)).await?;
    sqlx::raw_sql("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, price INTEGER NOT NULL, stock INTEGER NOT NULL DEFAULT 0)").execute(&db).await?;

    let app = Router::new()
        .route("/products", get(index).post(store))
        .route("/products/{id}", get(show).put(update).delete(destroy))
        .with_state(db);
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await?;
    axum::serve(listener, app).await?;
    Ok(())
}
''', deps=DB, requests=[
        f"""curl -s -X POST http://127.0.0.1:3000/products {JSON_H} -d '{{"name":"Redmi 13","price":17500,"stock":5}}'""",
        f"""curl -s -X POST http://127.0.0.1:3000/products {JSON_H} -d '{{"name":"Galaxy A15","price":21000,"stock":2}}'""",
        f"""curl -s -X PUT http://127.0.0.1:3000/products/2 {JSON_H} -d '{{"name":"Galaxy A15","price":20500,"stock":3}}'""",
        "curl -s -X DELETE http://127.0.0.1:3000/products/1",
        "curl -s http://127.0.0.1:3000/products",
        "curl -s http://127.0.0.1:3000/products/1"]),
    php_note("এটাই Laravel-এর <code>Route::apiResource('products', ProductController::class)</code> — index, show, store, update, destroy।"))

c.lesson("Search আর pagination",
    say("<code>LIKE</code> দিয়ে খোঁজা, <code>LIMIT/OFFSET</code> দিয়ে পাতা। মোট কতগুলো, সেটাও ফেরত দিই — Laravel <code>paginate()</code>-এর <code>meta</code>-এর মতো।"),
    code(r'''
use axum::{Json, Router, extract::{Query, State}, routing::get};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sqlx::{FromRow, SqlitePool, sqlite::{SqliteConnectOptions, SqlitePoolOptions}};
use std::str::FromStr;

#[derive(Serialize, FromRow)]
struct Product { id: i64, name: String, price: i64 }

#[derive(Deserialize)]
struct Params { q: Option<String>, page: Option<i64> }

async fn index(State(db): State<SqlitePool>, Query(p): Query<Params>) -> Json<Value> {
    let per_page = 2;
    let page = p.page.unwrap_or(1).max(1);
    let like = format!("%{}%", p.q.unwrap_or_default());

    let (total,): (i64,) = sqlx::query_as("SELECT COUNT(*) FROM products WHERE name LIKE ?")
        .bind(&like).fetch_one(&db).await.unwrap();
    let data: Vec<Product> = sqlx::query_as(
        "SELECT id, name, price FROM products WHERE name LIKE ? ORDER BY id LIMIT ? OFFSET ?")
        .bind(&like).bind(per_page).bind((page - 1) * per_page).fetch_all(&db).await.unwrap();

    Json(json!({ "data": data, "meta": { "page": page, "per_page": per_page, "total": total,
        "last_page": (total + per_page - 1) / per_page } }))
}

#[tokio::main]
async fn main() {
    let db = SqlitePoolOptions::new().max_connections(1)
        .connect_with(SqliteConnectOptions::from_str("sqlite::memory:").unwrap()).await.unwrap();
    sqlx::raw_sql("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER);
        INSERT INTO products (name, price) VALUES ('Redmi 13', 17500), ('Redmi Note 13', 23500),
        ('Galaxy A15', 21000), ('Redmi 12C', 13000), ('Vivo Y28', 18000);").execute(&db).await.unwrap();

    let app = Router::new().route("/products", get(index)).with_state(db);
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=DB, requests=["curl -s 'http://127.0.0.1:3000/products?q=redmi&page=2'"]),
    warn("<code>sqlite::memory:</code>-এ প্রতিটি connection আলাদা খালি database দেখে — তাই উদাহরণে <code>max_connections(1)</code>। আসল app-এ file বা MySQL/PostgreSQL ব্যবহার করুন।"))

c.lesson("MySQL বা PostgreSQL-এ যাওয়া",
    say("sqlx একই API দিয়ে তিনটাই চালায়। বদলাতে হয় feature, pool type, আর placeholder।"),
    table(["", "SQLite", "MySQL", "PostgreSQL"], [
        ["feature", "<code>sqlite</code>", "<code>mysql</code>", "<code>postgres</code>"],
        ["Pool", "<code>SqlitePool</code>", "<code>MySqlPool</code>", "<code>PgPool</code>"],
        ["URL", "<code>sqlite:shop.db</code>", "<code>mysql://root:pass@localhost/shop</code>", "<code>postgres://user:pass@localhost/shop</code>"],
        ["Placeholder", "<code>?</code>", "<code>?</code>", "<code>$1, $2</code>"],
        ["নতুন id", "<code>last_insert_rowid()</code>", "<code>last_insert_id()</code>", "<code>RETURNING id</code>"]]),
    tip("SQL শিখতে এই সাইটেরই MySQL আর PostgreSQL টিউটোরিয়াল দেখুন — সেখানে প্রতিটি query আসল database-এ চালানো।"))

# ================================================================== middleware
c.section("Middleware ও Config")
c.lesson("Route group: /api/v1 prefix",
    say("আলাদা Router বানিয়ে <code>nest(\"/api/v1\", ...)</code> দিয়ে জুড়ে দিই। Laravel-এর <code>Route::prefix()-&gt;group()</code>।"),
    code(r'''
use axum::{Router, routing::get};

async fn products() -> &'static str { "product list" }
async fn customers() -> &'static str { "customer list" }

fn api_v1() -> Router {
    Router::new()
        .route("/products", get(products))
        .route("/customers", get(customers))
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(|| async { "home" }))
        .nest("/api/v1", api_v1());
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=["curl -s http://127.0.0.1:3000/api/v1/products", "curl -s http://127.0.0.1:3000/api/v1/customers"]))

c.lesson("নিজের middleware: API key",
    say("<code>middleware::from_fn</code> দিয়ে async function-ই middleware। Request দেখে হয় আটকাই (401), নয়তো <code>next.run(req)</code> দিয়ে এগিয়ে দিই। <code>route_layer</code> শুধু ঐ route-গুলোতে বসে।"),
    code(r'''
use axum::{Router, extract::Request, http::StatusCode, middleware::{self, Next},
           response::Response, routing::get};

async fn require_key(req: Request, next: Next) -> Result<Response, StatusCode> {
    match req.headers().get("x-api-key").and_then(|v| v.to_str().ok()) {
        Some("secret-123") => Ok(next.run(req).await),
        _ => Err(StatusCode::UNAUTHORIZED),
    }
}

async fn report() -> &'static str { "আজকের বিক্রি: ৳১,৭০,৪০০" }

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/reports/today", get(report))
        .route_layer(middleware::from_fn(require_key))
        .route("/", get(|| async { "public" }));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=AXUM, requests=["curl -s http://127.0.0.1:3000/reports/today",
                          "curl -s -H 'x-api-key: secret-123' http://127.0.0.1:3000/reports/today",
                          "curl -s http://127.0.0.1:3000/"]),
    laravel('''
public function handle(Request $request, Closure $next)
{
    if ($request->header('X-Api-Key') !== 'secret-123') {
        abort(401);
    }
    return $next($request);
}
''', "Laravel middleware-এ তুলনা"),
    warn("আসল project-এ key কোডে লিখবেন না — <code>.env</code> থেকে পড়ুন (পরের পাঠ)। User login-এর জন্য JWT বা session crate ব্যবহার করুন।"))

c.lesson("Log, CORS আর .env",
    say("<code>tower-http</code> থেকে তৈরি layer: <code>TraceLayer</code> প্রতিটি request log করে, <code>CorsLayer</code> Vue/React frontend-কে call করতে দেয়। <code>dotenvy</code> <code>.env</code> পড়ে।"),
    shell("$ cargo add tower-http --features cors,trace\n$ cargo add tracing-subscriber dotenvy"),
    code(r'''
use axum::{Router, routing::get};
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use tracing_subscriber::filter::LevelFilter;

#[tokio::main]
async fn main() {
    dotenvy::dotenv().ok();   // .env থাকলে পড়ে, না থাকলে সমস্যা নেই
    let addr = std::env::var("APP_ADDR").unwrap_or_else(|_| "127.0.0.1:3000".to_string());
    tracing_subscriber::fmt().with_max_level(LevelFilter::DEBUG).with_target(false).without_time().init();

    let app = Router::new()
        .route("/products", get(|| async { "[]" }))
        .layer(TraceLayer::new_for_http())
        .layer(CorsLayer::permissive());

    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
''', deps=WEB, server_log=True, requests=[
        "curl -s -i -H 'Origin: http://localhost:5173' http://127.0.0.1:3000/products"]),
    code('''
APP_ADDR=0.0.0.0:3000
DATABASE_URL=sqlite:shop.db
API_KEY=change-me
''', "ini", file=".env"),
    tip("<code>access-control-allow-origin: *</code> header-টা দেখুন — CORS layer যোগ করেছে। Production-এ <code>permissive()</code> না দিয়ে নির্দিষ্ট domain দিন।"))

# ================================================================== deploy
c.section("Deploy")
c.lesson("Release build",
    say("<code>--release</code> build অনেক দ্রুত আর ছোট। ফলাফল একটা মাত্র file — server-এ PHP, Composer, vendor কিছুই লাগে না।"),
    shell("$ cargo build --release\n$ ls -lh target/release/shop-api\n$ ./target/release/shop-api",
          out="    Finished `release` profile [optimized] target(s) in 48.20s\n-rwxr-xr-x  1 rahim  staff   4.1M  Oct 21 12:00 target/release/shop-api"),
    points("Server-এ binary কপি করুন (<code>scp</code>) অথবা server-এই build করুন",
           "Linux server-এর জন্য Linux-এই build করুন (বা Docker দিয়ে)",
           "<code>.env</code> আর database file binary-র পাশে রাখুন"),
    php_note("Laravel deploy-এ লাগে PHP-FPM, extension, <code>composer install</code>, cache clear। Rust-এ শুধু একটা binary চালু করা।"))

c.lesson("systemd দিয়ে সবসময় চালু রাখা",
    say("Server restart হলে বা app crash করলে নিজে থেকে আবার চালু করতে systemd service। Laravel-এর queue worker যেভাবে Supervisor দিয়ে চালান, সেরকম।"),
    code('''
[Unit]
Description=Shop API (Rust)
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/shop-api
EnvironmentFile=/var/www/shop-api/.env
ExecStart=/var/www/shop-api/shop-api
Restart=always

[Install]
WantedBy=multi-user.target
''', "ini", file="/etc/systemd/system/shop-api.service"),
    shell("$ sudo systemctl daemon-reload\n$ sudo systemctl enable --now shop-api\n$ sudo journalctl -u shop-api -f"))

c.lesson("Nginx reverse proxy আর HTTPS",
    say("App চলে <code>127.0.0.1:3000</code>-এ। বাইরের দুনিয়া আসে Nginx-এ (80/443), Nginx request পাঠায় app-এ। HTTPS-এর জন্য certbot।"),
    code('''
server {
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
''', "nginx", file="/etc/nginx/sites-available/shop-api"),
    shell("$ sudo ln -s /etc/nginx/sites-available/shop-api /etc/nginx/sites-enabled/\n$ sudo nginx -t && sudo systemctl reload nginx\n$ sudo certbot --nginx -d api.example.com"),
    php_note("Laravel-এ Nginx পাঠায় PHP-FPM-এ (<code>fastcgi_pass</code>)। এখানে সাধারণ <code>proxy_pass</code> — যেমন Node.js app-এ করেন।"))

c.lesson("Docker (ঐচ্ছিক)",
    say("Multi-stage Dockerfile: প্রথম ধাপে Rust image-এ build, দ্বিতীয় ধাপে ছোট Debian image-এ শুধু binary। শেষ image মাত্র কয়েক MB + base।"),
    code('''
FROM rust:1-bookworm AS build
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=build /app/target/release/shop-api /app/shop-api
ENV APP_ADDR=0.0.0.0:3000
EXPOSE 3000
CMD ["/app/shop-api"]
''', "dockerfile", file="Dockerfile"),
    shell("$ docker build -t shop-api .\n$ docker run -p 3000:3000 -v $(pwd)/data:/app/data shop-api"),
    tip("Container-এর ভিতরে <code>127.0.0.1</code> না, <code>0.0.0.0</code>-এ listen করতে হয় — নইলে বাইরে থেকে পৌঁছানো যায় না। তাই <code>APP_ADDR</code>।"))

# ================================================================== final
c.section("সম্পূর্ণ Project")
FINAL = r'''
//! Shop API — axum + SQLite. Laravel-এর apiResource-এর মতো Product CRUD,
//! 422 validation, search + pagination, API key middleware, log আর CORS।
use axum::{Json, Router, extract::{Path, Query, Request, State}, http::StatusCode, middleware::{self, Next},
           response::{IntoResponse, Response}, routing::get};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sqlx::{FromRow, SqlitePool, sqlite::SqliteConnectOptions};
use std::{collections::BTreeMap, str::FromStr};
use tower_http::{cors::CorsLayer, trace::TraceLayer};

#[derive(Clone)]
struct AppState { db: SqlitePool, api_key: String }

#[derive(Serialize, FromRow)]
struct Product { id: i64, name: String, brand: String, price: i64, stock: i64 }

#[derive(Deserialize)]
struct Input { name: String, brand: String, price: i64, stock: i64 }

#[derive(Deserialize)]
struct Params { q: Option<String>, page: Option<i64> }

enum AppError { NotFound, Invalid(BTreeMap<&'static str, Vec<String>>), Db(sqlx::Error) }

impl From<sqlx::Error> for AppError {
    fn from(e: sqlx::Error) -> Self { AppError::Db(e) }
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (code, body) = match self {
            AppError::NotFound => (StatusCode::NOT_FOUND, json!({ "message": "Product পাওয়া যায়নি।" })),
            AppError::Invalid(errors) => (StatusCode::UNPROCESSABLE_ENTITY,
                json!({ "message": "দেওয়া তথ্য ঠিক নেই।", "errors": errors })),
            AppError::Db(e) => {
                eprintln!("database error: {e}");
                (StatusCode::INTERNAL_SERVER_ERROR, json!({ "message": "Server error" }))
            }
        };
        (code, Json(body)).into_response()
    }
}

fn validate(i: &Input) -> Result<(), AppError> {
    let mut errors = BTreeMap::new();
    if i.name.trim().is_empty() { errors.insert("name", vec!["নাম দিতে হবে।".to_string()]); }
    if i.brand.trim().is_empty() { errors.insert("brand", vec!["Brand দিতে হবে।".to_string()]); }
    if i.price <= 0 { errors.insert("price", vec!["দাম ০-এর বেশি হতে হবে।".to_string()]); }
    if i.stock < 0 { errors.insert("stock", vec!["স্টক ঋণাত্মক হতে পারে না।".to_string()]); }
    if errors.is_empty() { Ok(()) } else { Err(AppError::Invalid(errors)) }
}

const PER_PAGE: i64 = 10;

async fn index(State(s): State<AppState>, Query(p): Query<Params>) -> Result<Json<Value>, AppError> {
    let page = p.page.unwrap_or(1).max(1);
    let like = format!("%{}%", p.q.unwrap_or_default());
    let (total,): (i64,) = sqlx::query_as("SELECT COUNT(*) FROM products WHERE name LIKE ?1 OR brand LIKE ?1")
        .bind(&like).fetch_one(&s.db).await?;
    let data: Vec<Product> = sqlx::query_as("SELECT id, name, brand, price, stock FROM products
        WHERE name LIKE ?1 OR brand LIKE ?1 ORDER BY id DESC LIMIT ?2 OFFSET ?3")
        .bind(&like).bind(PER_PAGE).bind((page - 1) * PER_PAGE).fetch_all(&s.db).await?;
    Ok(Json(json!({ "data": data, "meta": { "page": page, "per_page": PER_PAGE, "total": total } })))
}

async fn show(State(s): State<AppState>, Path(id): Path<i64>) -> Result<Json<Product>, AppError> {
    let p: Option<Product> = sqlx::query_as("SELECT id, name, brand, price, stock FROM products WHERE id = ?")
        .bind(id).fetch_optional(&s.db).await?;
    p.map(Json).ok_or(AppError::NotFound)
}

async fn store(State(s): State<AppState>, Json(i): Json<Input>) -> Result<(StatusCode, Json<Product>), AppError> {
    validate(&i)?;
    let id = sqlx::query("INSERT INTO products (name, brand, price, stock) VALUES (?, ?, ?, ?)")
        .bind(&i.name).bind(&i.brand).bind(i.price).bind(i.stock).execute(&s.db).await?.last_insert_rowid();
    Ok((StatusCode::CREATED, Json(Product { id, name: i.name, brand: i.brand, price: i.price, stock: i.stock })))
}

async fn update(State(s): State<AppState>, Path(id): Path<i64>, Json(i): Json<Input>) -> Result<Json<Product>, AppError> {
    validate(&i)?;
    let done = sqlx::query("UPDATE products SET name = ?, brand = ?, price = ?, stock = ? WHERE id = ?")
        .bind(&i.name).bind(&i.brand).bind(i.price).bind(i.stock).bind(id).execute(&s.db).await?;
    if done.rows_affected() == 0 { return Err(AppError::NotFound); }
    Ok(Json(Product { id, name: i.name, brand: i.brand, price: i.price, stock: i.stock }))
}

async fn destroy(State(s): State<AppState>, Path(id): Path<i64>) -> Result<StatusCode, AppError> {
    let done = sqlx::query("DELETE FROM products WHERE id = ?").bind(id).execute(&s.db).await?;
    if done.rows_affected() == 0 { return Err(AppError::NotFound); }
    Ok(StatusCode::NO_CONTENT)
}

async fn require_key(State(s): State<AppState>, req: Request, next: Next) -> Result<Response, StatusCode> {
    let given = req.headers().get("x-api-key").and_then(|v| v.to_str().ok());
    if given == Some(s.api_key.as_str()) { Ok(next.run(req).await) } else { Err(StatusCode::UNAUTHORIZED) }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok();
    let env = |k: &str, d: &str| std::env::var(k).unwrap_or_else(|_| d.to_string());
    tracing_subscriber::fmt().with_target(false).init();

    let opts = SqliteConnectOptions::from_str(&env("DATABASE_URL", "sqlite:shop.db"))?.create_if_missing(true);
    let db = SqlitePool::connect_with(opts).await?;
    sqlx::raw_sql("CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, brand TEXT NOT NULL,
        price INTEGER NOT NULL, stock INTEGER NOT NULL DEFAULT 0)").execute(&db).await?;
    let state = AppState { db, api_key: env("API_KEY", "secret-123") };

    let write = Router::new()   // লেখার route-এ API key লাগবে
        .route("/products", axum::routing::post(store))
        .route("/products/{id}", axum::routing::put(update).delete(destroy))
        .route_layer(middleware::from_fn_with_state(state.clone(), require_key));
    let read = Router::new()
        .route("/products", get(index))
        .route("/products/{id}", get(show));

    let app = Router::new()
        .nest("/api/v1", read.merge(write))
        .layer(TraceLayer::new_for_http())
        .layer(CorsLayer::permissive())
        .with_state(state);

    let addr = env("APP_ADDR", "127.0.0.1:3000");
    println!("Shop API চলছে: http://{addr}/api/v1/products");
    axum::serve(tokio::net::TcpListener::bind(&addr).await?, app).await?;
    Ok(())
}
'''
KEY = "-H 'x-api-key: secret-123'"
c.lesson("সব একসাথে: Shop API",
    say("আগের সব পাঠ এক file-এ: read route সবার জন্য, write route-এ API key। এই কোডটাই <code>shop-api/</code> folder-এ পুরো project হিসেবে আছে — <code>cargo run</code> দিলেই চলে।"),
    steps("<code>GET /api/v1/products?q=&amp;page=</code> — খোঁজা + পাতা", "<code>GET /api/v1/products/{id}</code>",
          "<code>POST</code> / <code>PUT</code> / <code>DELETE</code> — <code>x-api-key</code> লাগবে", "ভুল তথ্যে Laravel-এর মতো 422"),
    code(FINAL, deps=WEB, file="src/main.rs", requests=[
        f"""curl -s -X POST http://127.0.0.1:3000/api/v1/products {JSON_H} -d '{{"name":"Redmi 13","brand":"Xiaomi","price":17500,"stock":5}}'""",
        f"""curl -s -X POST http://127.0.0.1:3000/api/v1/products {KEY} {JSON_H} -d '{{"name":"Redmi 13","brand":"Xiaomi","price":17500,"stock":5}}'""",
        f"""curl -s -X POST http://127.0.0.1:3000/api/v1/products {KEY} {JSON_H} -d '{{"name":"Galaxy A15","brand":"Samsung","price":21000,"stock":2}}'""",
        f"""curl -s -X POST http://127.0.0.1:3000/api/v1/products {KEY} {JSON_H} -d '{{"name":"","brand":"Vivo","price":0,"stock":-1}}'""",
        "curl -s 'http://127.0.0.1:3000/api/v1/products?q=xiaomi'",
        f"curl -s -X DELETE http://127.0.0.1:3000/api/v1/products/2 {KEY}",
        "curl -s http://127.0.0.1:3000/api/v1/products/2"]),
    task("<code>category</code> field যোগ করুন, আর <code>GET /api/v1/products?brand=Xiaomi</code> দিয়ে brand ধরে filter করুন।"))

c.lesson("এরপর কী শিখবেন",
    table(["বিষয়", "crate"], [
        ["Login, JWT", "<code>jsonwebtoken</code>, <code>argon2</code> (password hash)"],
        ["HTML page (Blade-এর মতো)", "<code>askama</code> বা <code>minijinja</code>"],
        ["Attribute দিয়ে validation", "<code>validator</code> / <code>garde</code>"],
        ["Integration test", "<code>tower::ServiceExt::oneshot</code>, <code>axum-test</code>"],
        ["Background job (queue)", "<code>tokio::spawn</code>, <code>apalis</code>"],
        ["OpenAPI/Swagger doc", "<code>utoipa</code>"]]),
    tip("Laravel-এ যা করতে পারেন, Rust-এ প্রায় সবই পারবেন — শুধু একটু বেশি লিখতে হয়, বিনিময়ে অনেক কম memory আর অনেক বেশি গতি।"))

c.finish("Rust Web Development শেষ! 🎉",
         "আপনি এখন Rust দিয়ে একটা আসল JSON API বানাতে, database-এ রাখতে আর server-এ চালাতে পারেন।",
         recap=["Route + async handler + extractor (<code>Path</code>, <code>Query</code>, <code>Json</code>, <code>State</code>)",
                "<code>IntoResponse</code> দিয়ে error → JSON, Laravel-এর মতো 422",
                "sqlx: bind দিয়ে নিরাপদ SQL, <code>FromRow</code> দিয়ে struct",
                "Middleware: <code>from_fn</code>, TraceLayer, CorsLayer",
                "Release binary + systemd + Nginx = production"])


def write_project():
    """shop-api/: the final lesson as a runnable Cargo project (same source as the slide)."""
    proj = HERE / "shop-api"
    (proj / "src").mkdir(parents=True, exist_ok=True)
    deps = "\n".join(f"{k} = {v if v.startswith('{') else chr(34) + v + chr(34)}" for k, v in WEB.items())
    (proj / "Cargo.toml").write_text(f'[package]\nname = "shop-api"\nversion = "0.1.0"\nedition = "2024"\n\n[dependencies]\n{deps}\n')
    (proj / "src/main.rs").write_text(FINAL.strip() + "\n")
    (proj / ".env.example").write_text("APP_ADDR=127.0.0.1:3000\nDATABASE_URL=sqlite:shop.db\nAPI_KEY=secret-123\n")
    (proj / ".gitignore").write_text("/target\nshop.db*\n.env\n")
    (proj / "README.md").write_text(
        "# Shop API (Rust Web Development course)\n\n"
        "```bash\ncp .env.example .env\ncargo run\n"
        "curl -s localhost:3000/api/v1/products\n"
        "curl -s -X POST localhost:3000/api/v1/products -H 'x-api-key: secret-123' -H 'Content-Type: application/json' \\\n"
        "  -d '{\"name\":\"Redmi 13\",\"brand\":\"Xiaomi\",\"price\":17500,\"stock\":5}'\n```\n")


if __name__ == "__main__":
    c.build()
    write_project()
