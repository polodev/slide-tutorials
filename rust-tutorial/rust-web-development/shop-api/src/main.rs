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
