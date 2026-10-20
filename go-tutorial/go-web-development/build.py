"""Go Web Development — net/http (Go 1.22+ routing), JSON, validation, middleware, database/sql + SQLite,
httptest, graceful shutdown, Docker. Server lessons are built, started and called with curl at build time;
the final lesson is also written to go-shop-api/ as a runnable project. Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402


def go(src, **kw):
    return code(src, "go", **kw)


def laravel(src, label="Laravel-এ"):
    return code(src, "php", run=False, label=label)


SQLITE = ["modernc.org/sqlite@latest"]
JSON_H = "-H 'Content-Type: application/json'"
KEY = "-H 'X-Api-Key: secret-123'"

c = Course(slug="go-web-development", title="Go Web Development — net/http দিয়ে API", folder=HERE,
           subtitle="Framework ছাড়াই: Go-র নিজের router, JSON, Laravel-এর মতো 422 validation, middleware, SQLite, test আর Docker",
           series="Go Web Development")

c.cover("Go Web Development<br>net/http দিয়ে API",
        "Go-র standard library-তেই production-মানের web server আছে — Laravel-এর মতো বড় framework লাগে না। শেষে পুরো একটা Product API, এক binary-তে।",
        learn=["Route: <code>GET /products/{id}</code>", "Query, JSON body আর status code", "Laravel-এর মতো 422 validation",
               "Middleware: log আর API key", "database/sql + SQLite: CRUD", "Search, pagination, SQL injection থেকে বাঁচা",
               "httptest দিয়ে handler test", "Graceful shutdown আর Docker"],
        need="Go 101–103 (struct, interface, error, context)।")

# ================================================================== start
c.section("শুরু")
c.lesson("Laravel থেকে Go: কোনটা কী",
    table(["Laravel", "Go (standard library)"], [
        ["<code>routes/api.php</code>", "<code>mux.HandleFunc(\"GET /products/{id}\", h)</code>"],
        ["Controller method", "<code>func(w http.ResponseWriter, r *http.Request)</code>"],
        ["<code>$request-&gt;route('id')</code>", "<code>r.PathValue(\"id\")</code>"],
        ["<code>$request-&gt;query('q')</code>", "<code>r.URL.Query().Get(\"q\")</code>"],
        ["<code>response()-&gt;json()</code>", "<code>json.NewEncoder(w).Encode(v)</code>"],
        ["Middleware", "<code>func(http.Handler) http.Handler</code>"], ["Eloquent", "<code>database/sql</code> (raw SQL)"],
        ["<code>php artisan serve</code>", "<code>go run .</code>"]]),
    tip("Go 1.22 থেকে standard router নিজেই method আর <code>{id}</code> বোঝে। আগে এর জন্য chi বা gin লাগত — এখনো জনপ্রিয়, কিন্তু বাধ্যতামূলক না।"))

c.lesson("প্রথম server",
    go('''
package main

import (
	"fmt"
	"log"
	"net/http"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "Hello, World! Shop API চলছে।")
	})
	log.Println("চলছে: http://127.0.0.1:3000")
	log.Fatal(http.ListenAndServe("127.0.0.1:3000", mux))
}
''', requests=["curl -s http://127.0.0.1:3000/"]),
    laravel("Route::get('/', fn () => 'Hello, World! Shop API চলছে।');"),
    shell("$ go run ."))

c.section("Routing ও Request")
c.lesson("Method, path আর {id}",
    say("Route-এর শুরুতে method, path-এ <code>{id}</code>। ভুল method-এ Go নিজেই 405, না মেলা path-এ 404 দেয়।"),
    go('''
package main

import (
	"fmt"
	"net/http"
	"strconv"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /products", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "সব product")
	})
	mux.HandleFunc("GET /products/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, err := strconv.Atoi(r.PathValue("id"))
		if err != nil {
			http.Error(w, "id সংখ্যা হতে হবে", http.StatusBadRequest)
			return
		}
		fmt.Fprintf(w, "Product #%d\\n", id)
	})
	http.ListenAndServe("127.0.0.1:3000", mux)
}
''', requests=["curl -s http://127.0.0.1:3000/products/42", "curl -s http://127.0.0.1:3000/products/abc",
               "curl -s -X POST http://127.0.0.1:3000/products", "curl -s http://127.0.0.1:3000/blog"]),
    php_note("Laravel-এর <code>whereNumber('id')</code>-এর কাজ এখানে <code>strconv.Atoi</code> দিয়ে নিজেই।"))

c.lesson("Query string",
    go('''
package main

import (
	"fmt"
	"net/http"
	"strconv"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /products", func(w http.ResponseWriter, r *http.Request) {
		q := r.URL.Query().Get("q")
		page, err := strconv.Atoi(r.URL.Query().Get("page"))
		if err != nil || page < 1 {
			page = 1
		}
		if q == "" {
			q = "সব"
		}
		fmt.Fprintf(w, "খোঁজা: %s, পাতা: %d\\n", q, page)
	})
	http.ListenAndServe("127.0.0.1:3000", mux)
}
''', requests=["curl -s 'http://127.0.0.1:3000/products?q=redmi&page=2'", "curl -s 'http://127.0.0.1:3000/products?page=two'"]))

c.lesson("JSON response",
    say("ছোট helper <code>writeJSON</code> সব জায়গায় কাজে লাগবে: header, status, তারপর encode।"),
    go('''
package main

import (
	"encoding/json"
	"net/http"
)

type Product struct {
	ID      int    `json:"id"`
	Name    string `json:"name"`
	Price   int    `json:"price"`
	InStock bool   `json:"in_stock"`
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /products", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, []Product{
			{1, "Redmi 13", 17500, true},
			{2, "Galaxy A15", 21000, false},
		})
	})
	http.ListenAndServe("127.0.0.1:3000", mux)
}
''', requests=["curl -s http://127.0.0.1:3000/products"]))

c.lesson("JSON body আর 422 validation",
    say("Body decode করি (<code>DisallowUnknownFields</code> — অজানা field এলে ভুল), তারপর নিয়ম যাচাই করে Laravel-এর মতো <code>{message, errors}</code> সহ 422।"),
    go('''
package main

import (
	"encoding/json"
	"net/http"
	"strings"
)

type NewProduct struct {
	Name  string `json:"name"`
	Price int    `json:"price"`
	Stock int    `json:"stock"`
}

func (p NewProduct) Validate() map[string][]string {
	errs := map[string][]string{}
	if strings.TrimSpace(p.Name) == "" {
		errs["name"] = append(errs["name"], "নাম দিতে হবে।")
	}
	if p.Price <= 0 {
		errs["price"] = append(errs["price"], "দাম ০-এর বেশি হতে হবে।")
	}
	if p.Stock < 0 {
		errs["stock"] = append(errs["stock"], "স্টক ঋণাত্মক হতে পারে না।")
	}
	return errs
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func create(w http.ResponseWriter, r *http.Request) {
	var in NewProduct
	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()
	if err := dec.Decode(&in); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"message": "JSON ঠিক নেই: " + err.Error()})
		return
	}
	if errs := in.Validate(); len(errs) > 0 {
		writeJSON(w, http.StatusUnprocessableEntity, map[string]any{"message": "দেওয়া তথ্য ঠিক নেই।", "errors": errs})
		return
	}
	writeJSON(w, http.StatusCreated, in)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /products", create)
	http.ListenAndServe("127.0.0.1:3000", mux)
}
''', requests=[f"""curl -s -X POST http://127.0.0.1:3000/products {JSON_H} -d '{{"name":" ","price":0,"stock":-2}}'""",
               f"""curl -s -X POST http://127.0.0.1:3000/products {JSON_H} -d '{{"name":"Vivo Y28","price":"18000"}}'""",
               f"""curl -s -X POST http://127.0.0.1:3000/products {JSON_H} -d '{{"name":"Vivo Y28","price":18000,"stock":4}}'"""]),
    laravel("$request->validate(['name' => 'required', 'price' => 'integer|min:1', 'stock' => 'integer|min:0']);"))

c.section("Middleware ও State")
c.lesson("Middleware: log আর API key",
    say("Middleware হলো এমন function যা একটা handler নিয়ে আরেকটা handler ফেরত দেয়। আগে-পরে কাজ করে, বা আটকে দেয়।"),
    go('''
package main

import (
	"fmt"
	"log"
	"net/http"
	"time"
)

func logging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("%s %s (%s)", r.Method, r.URL.Path, time.Since(start).Round(time.Millisecond))
	})
}

func requireKey(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("X-Api-Key") != "secret-123" {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func main() {
	log.SetFlags(0)
	mux := http.NewServeMux()
	mux.HandleFunc("GET /", func(w http.ResponseWriter, r *http.Request) { fmt.Fprintln(w, "public") })
	mux.Handle("GET /reports/today", requireKey(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "আজকের বিক্রি: ৳১,৭০,৪০০")
	})))
	http.ListenAndServe("127.0.0.1:3000", logging(mux))
}
''', server_log=True, requests=["curl -s http://127.0.0.1:3000/reports/today", f"curl -s {KEY} http://127.0.0.1:3000/reports/today",
                                 "curl -s http://127.0.0.1:3000/"]),
    php_note("Laravel middleware-এর <code>handle($request, $next)</code> — এখানে <code>next.ServeHTTP(w, r)</code>।"))

c.lesson("Shared state: memory-তে store",
    say("Go server একবার চালু হয়ে চলতেই থাকে, আর প্রতিটি request আলাদা goroutine-এ — তাই shared data-তে <code>sync.Mutex</code> লাগবেই।"),
    go('''
package main

import (
	"encoding/json"
	"net/http"
	"sync"
)

type Counter struct {
	mu     sync.Mutex
	visits int
}

func (c *Counter) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	c.mu.Lock()
	c.visits++
	n := c.visits
	c.mu.Unlock()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]int{"visits": n})
}

func main() {
	mux := http.NewServeMux()
	mux.Handle("GET /visit", &Counter{})
	http.ListenAndServe("127.0.0.1:3000", mux)
}
''', requests=["curl -s http://127.0.0.1:3000/visit"] * 3),
    php_note("PHP-তে প্রতিটি request শেষে সব মুছে যায় (তাই Redis লাগে)। Go-তে memory-তে থাকে — কিন্তু restart দিলে হারায়, তাই আসল data database-এ।"))

# ================================================================== db
c.section("Database")
c.lesson("database/sql + SQLite",
    say("<code>database/sql</code> হলো Go-র সাধারণ database interface; driver আলাদা। <code>modernc.org/sqlite</code> pure Go — C compiler লাগে না, Docker-এ সহজ।"),
    shell("$ go get modernc.org/sqlite"),
    go('''
package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "modernc.org/sqlite"
)

func main() {
	db, err := sql.Open("sqlite", ":memory:")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	db.SetMaxOpenConns(1)

	db.Exec(`CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price INTEGER NOT NULL)`)
	for _, p := range []struct {
		name  string
		price int
	}{{"Redmi 13", 17500}, {"Galaxy A15", 21000}, {"Charger", 650}} {
		res, _ := db.Exec(`INSERT INTO products (name, price) VALUES (?, ?)`, p.name, p.price)
		id, _ := res.LastInsertId()
		fmt.Println("যোগ হলো", id, p.name)
	}

	rows, err := db.Query(`SELECT id, name, price FROM products WHERE price < ? ORDER BY price`, 20000)
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()
	for rows.Next() {
		var id, price int
		var name string
		rows.Scan(&id, &name, &price)
		fmt.Printf("#%d %-10s %6d\\n", id, name, price)
	}
}
''', deps=SQLITE),
    laravel("Product::where('price', '<', 20000)->orderBy('price')->get();"),
    tip("MySQL চাইলে <code>github.com/go-sql-driver/mysql</code>, PostgreSQL-এ <code>github.com/jackc/pgx/v5</code> — বাকি কোড প্রায় একই (PostgreSQL-এ placeholder <code>$1</code>)।"))

c.lesson("SQL injection: Sprintf দিয়ে কখনো না",
    go('''
package main

import (
	"database/sql"
	"fmt"

	_ "modernc.org/sqlite"
)

func main() {
	db, _ := sql.Open("sqlite", ":memory:")
	db.SetMaxOpenConns(1)
	db.Exec(`CREATE TABLE customers (name TEXT, phone TEXT);
		INSERT INTO customers VALUES ('Karim', '01711000001'), ('Nusrat', '01811000002')`)

	search := "x' OR '1'='1"
	var n int
	db.QueryRow(fmt.Sprintf(`SELECT count(*) FROM customers WHERE name = '%s'`, search)).Scan(&n)
	fmt.Println("Sprintf দিয়ে:", n, "জন — সবাই বেরিয়ে গেল!")

	db.QueryRow(`SELECT count(*) FROM customers WHERE name = ?`, search).Scan(&n)
	fmt.Println("? placeholder দিয়ে:", n, "জন")
}
''', deps=SQLITE),
    warn("নিয়ম: SQL-এ মান সবসময় <code>?</code> দিয়ে, আলাদা argument হিসেবে। Laravel-এ যেমন <code>where('name', $search)</code> নিরাপদ, <code>DB::raw(\"'$search'\")</code> বিপজ্জনক।"))

c.section("সম্পূর্ণ API")
FINAL = '''
// Shop API — net/http + SQLite: Product CRUD, 422 validation, search + pagination,
// API key for writes, request log, graceful shutdown.
package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	_ "modernc.org/sqlite"
)

type Product struct {
	ID    int64  `json:"id"`
	Name  string `json:"name"`
	Brand string `json:"brand"`
	Price int    `json:"price"`
	Stock int    `json:"stock"`
}

func (p Product) Validate() map[string][]string {
	errs := map[string][]string{}
	if strings.TrimSpace(p.Name) == "" {
		errs["name"] = []string{"নাম দিতে হবে।"}
	}
	if strings.TrimSpace(p.Brand) == "" {
		errs["brand"] = []string{"Brand দিতে হবে।"}
	}
	if p.Price <= 0 {
		errs["price"] = []string{"দাম ০-এর বেশি হতে হবে।"}
	}
	if p.Stock < 0 {
		errs["stock"] = []string{"স্টক ঋণাত্মক হতে পারে না।"}
	}
	return errs
}

type App struct {
	db     *sql.DB
	apiKey string
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func message(w http.ResponseWriter, status int, msg string) {
	writeJSON(w, status, map[string]string{"message": msg})
}

func (a *App) index(w http.ResponseWriter, r *http.Request) {
	const perPage = 10
	page, _ := strconv.Atoi(r.URL.Query().Get("page"))
	page = max(page, 1)
	like := "%" + r.URL.Query().Get("q") + "%"
	var total int
	if err := a.db.QueryRowContext(r.Context(),
		`SELECT count(*) FROM products WHERE name LIKE ?1 OR brand LIKE ?1`, like).Scan(&total); err != nil {
		message(w, 500, "Server error")
		return
	}
	rows, err := a.db.QueryContext(r.Context(), `SELECT id, name, brand, price, stock FROM products
		WHERE name LIKE ?1 OR brand LIKE ?1 ORDER BY id DESC LIMIT ?2 OFFSET ?3`, like, perPage, (page-1)*perPage)
	if err != nil {
		message(w, 500, "Server error")
		return
	}
	defer rows.Close()
	data := []Product{}
	for rows.Next() {
		var p Product
		rows.Scan(&p.ID, &p.Name, &p.Brand, &p.Price, &p.Stock)
		data = append(data, p)
	}
	writeJSON(w, 200, map[string]any{"data": data, "meta": map[string]int{"page": page, "per_page": perPage, "total": total}})
}

func (a *App) find(ctx context.Context, id string) (Product, error) {
	var p Product
	err := a.db.QueryRowContext(ctx, `SELECT id, name, brand, price, stock FROM products WHERE id = ?`, id).
		Scan(&p.ID, &p.Name, &p.Brand, &p.Price, &p.Stock)
	return p, err
}

func (a *App) show(w http.ResponseWriter, r *http.Request) {
	p, err := a.find(r.Context(), r.PathValue("id"))
	if errors.Is(err, sql.ErrNoRows) {
		message(w, 404, "Product পাওয়া যায়নি।")
		return
	}
	writeJSON(w, 200, p)
}

func decode(w http.ResponseWriter, r *http.Request) (Product, bool) {
	var p Product
	if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
		message(w, 400, "JSON ঠিক নেই।")
		return p, false
	}
	if errs := p.Validate(); len(errs) > 0 {
		writeJSON(w, 422, map[string]any{"message": "দেওয়া তথ্য ঠিক নেই।", "errors": errs})
		return p, false
	}
	return p, true
}

func (a *App) store(w http.ResponseWriter, r *http.Request) {
	p, ok := decode(w, r)
	if !ok {
		return
	}
	res, err := a.db.ExecContext(r.Context(), `INSERT INTO products (name, brand, price, stock) VALUES (?, ?, ?, ?)`,
		p.Name, p.Brand, p.Price, p.Stock)
	if err != nil {
		message(w, 500, "Server error")
		return
	}
	p.ID, _ = res.LastInsertId()
	writeJSON(w, 201, p)
}

func (a *App) update(w http.ResponseWriter, r *http.Request) {
	p, ok := decode(w, r)
	if !ok {
		return
	}
	res, _ := a.db.ExecContext(r.Context(), `UPDATE products SET name = ?, brand = ?, price = ?, stock = ? WHERE id = ?`,
		p.Name, p.Brand, p.Price, p.Stock, r.PathValue("id"))
	if n, _ := res.RowsAffected(); n == 0 {
		message(w, 404, "Product পাওয়া যায়নি।")
		return
	}
	p.ID, _ = strconv.ParseInt(r.PathValue("id"), 10, 64)
	writeJSON(w, 200, p)
}

func (a *App) destroy(w http.ResponseWriter, r *http.Request) {
	res, _ := a.db.ExecContext(r.Context(), `DELETE FROM products WHERE id = ?`, r.PathValue("id"))
	if n, _ := res.RowsAffected(); n == 0 {
		message(w, 404, "Product পাওয়া যায়নি।")
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

func (a *App) requireKey(h http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("X-Api-Key") != a.apiKey {
			message(w, 401, "Unauthorized")
			return
		}
		h(w, r)
	}
}

func logging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("%s %s %s", r.Method, r.URL.RequestURI(), time.Since(start).Round(time.Millisecond))
	})
}

func env(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func main() {
	log.SetFlags(0)
	db, err := sql.Open("sqlite", env("DATABASE_PATH", "shop.db"))
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	db.SetMaxOpenConns(1)
	if _, err := db.Exec(`CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL, brand TEXT NOT NULL, price INTEGER NOT NULL, stock INTEGER NOT NULL DEFAULT 0)`); err != nil {
		log.Fatal(err)
	}
	app := &App{db: db, apiKey: env("API_KEY", "secret-123")}

	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/v1/products", app.index)
	mux.HandleFunc("GET /api/v1/products/{id}", app.show)
	mux.HandleFunc("POST /api/v1/products", app.requireKey(app.store))
	mux.HandleFunc("PUT /api/v1/products/{id}", app.requireKey(app.update))
	mux.HandleFunc("DELETE /api/v1/products/{id}", app.requireKey(app.destroy))

	srv := &http.Server{Addr: env("APP_ADDR", "127.0.0.1:3000"), Handler: logging(mux),
		ReadTimeout: 10 * time.Second, WriteTimeout: 10 * time.Second}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	go func() {
		log.Println("Shop API চলছে:", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatal(err)
		}
	}()
	<-ctx.Done()
	log.Println("বন্ধ হচ্ছে: চলমান request শেষ হওয়ার অপেক্ষা...")
	shutdown, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	srv.Shutdown(shutdown)
}
'''

c.lesson("সব একসাথে: Shop API",
    say("এই কোডটাই <code>go-shop-api/</code> folder-এ পুরো project হিসেবে আছে। নিচে server log-এ শেষ লাইন দেখুন: SIGTERM পেয়ে <b>graceful shutdown</b> — চলমান request শেষ করে তারপর বন্ধ।"),
    go(FINAL, deps=SQLITE, file="main.go", server_log=True, requests=[
        f"""curl -s -X POST http://127.0.0.1:3000/api/v1/products {JSON_H} -d '{{"name":"Redmi 13","brand":"Xiaomi","price":17500,"stock":5}}'""",
        f"""curl -s -X POST http://127.0.0.1:3000/api/v1/products {KEY} {JSON_H} -d '{{"name":"Redmi 13","brand":"Xiaomi","price":17500,"stock":5}}'""",
        f"""curl -s -X POST http://127.0.0.1:3000/api/v1/products {KEY} {JSON_H} -d '{{"name":"Galaxy A15","brand":"Samsung","price":21000,"stock":2}}'""",
        f"""curl -s -X POST http://127.0.0.1:3000/api/v1/products {KEY} {JSON_H} -d '{{"name":"","brand":"Vivo","price":0,"stock":-1}}'""",
        f"""curl -s -X PUT http://127.0.0.1:3000/api/v1/products/2 {KEY} {JSON_H} -d '{{"name":"Galaxy A15","brand":"Samsung","price":20500,"stock":3}}'""",
        "curl -s 'http://127.0.0.1:3000/api/v1/products?q=xiaomi'",
        f"curl -s -X DELETE http://127.0.0.1:3000/api/v1/products/2 {KEY}",
        "curl -s http://127.0.0.1:3000/api/v1/products/2"]),
    php_note("এটা Laravel-এর <code>Route::apiResource()</code> + FormRequest + <code>auth</code> middleware + exception handler — সব এক file-এ, কোনো framework ছাড়া।"))

c.lesson("Handler test: httptest",
    say("<code>httptest.NewRecorder</code> দিয়ে server চালু না করেই handler-এ request পাঠানো যায় — দ্রুত, বিচ্ছিন্ন test।"),
    go('''
package main

import (
	"database/sql"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	_ "modernc.org/sqlite"
)

func newTestApp(t *testing.T) *App {
	db, err := sql.Open("sqlite", ":memory:")
	if err != nil {
		t.Fatal(err)
	}
	db.SetMaxOpenConns(1)
	db.Exec(`CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, brand TEXT, price INTEGER, stock INTEGER)`)
	return &App{db: db, apiKey: "k"}
}

func TestStoreValidation(t *testing.T) {
	app := newTestApp(t)
	cases := []struct {
		name string
		body string
		want int
	}{
		{"ঠিক তথ্য", `{"name":"Redmi 13","brand":"Xiaomi","price":17500,"stock":5}`, 201},
		{"দাম নেই", `{"name":"Redmi 13","brand":"Xiaomi","price":0}`, 422},
		{"ভাঙা JSON", `{"name":`, 400},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			req := httptest.NewRequest("POST", "/api/v1/products", strings.NewReader(tc.body))
			rec := httptest.NewRecorder()
			app.store(rec, req)
			if rec.Code != tc.want {
				t.Fatalf("status %d, চাই %d: %s", rec.Code, tc.want, rec.Body)
			}
		})
	}
}

func TestShowNotFound(t *testing.T) {
	app := newTestApp(t)
	req := httptest.NewRequest("GET", "/api/v1/products/99", nil)
	req.SetPathValue("id", "99")
	rec := httptest.NewRecorder()
	app.show(rec, req)
	if rec.Code != http.StatusNotFound {
		t.Fatalf("status %d", rec.Code)
	}
}
''', test=True, app=FINAL, deps=SQLITE, file="main_test.go"),
    php_note("Laravel feature test-এর <code>$this-&gt;postJson('/api/products', [...])-&gt;assertStatus(422)</code>-এর মতো।"))

c.section("Deploy")
c.lesson("Docker: কয়েক MB-এর image",
    say("Multi-stage build: প্রথম ধাপে Go দিয়ে compile, দ্বিতীয় ধাপে শুধু binary একটা খালি (distroless) image-এ। <code>CGO_ENABLED=0</code> — pure Go binary, কোনো system library লাগে না।"),
    code('''
FROM golang:1.27 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /shop-api .

FROM gcr.io/distroless/static-debian12
COPY --from=build /shop-api /shop-api
ENV APP_ADDR=0.0.0.0:3000 DATABASE_PATH=/data/shop.db
VOLUME /data
EXPOSE 3000
USER nonroot
ENTRYPOINT ["/shop-api"]
''', "dockerfile", file="Dockerfile"),
    shell("$ docker build -t shop-api .\n$ docker images shop-api\n$ docker run -p 3000:3000 -v shop-data:/data -e API_KEY=change-me shop-api",
          out="REPOSITORY   TAG       IMAGE ID       SIZE\nshop-api     latest    3f2a9c1e7b4d   14.6MB"),
    tip("Laravel-এর Docker image সাধারণত কয়েকশো MB; Go-র এই image ১৫ MB-এর মতো। DevOps টিউটোরিয়ালে Docker আর Kubernetes বিস্তারিত।"))

c.lesson("এরপর কী",
    table(["প্রয়োজন", "জনপ্রিয় package"], [
        ["আরও সুবিধার router", "<code>chi</code>, <code>echo</code>, <code>gin</code>"], ["Type-safe SQL কোড বানানো", "<code>sqlc</code>"],
        ["PostgreSQL", "<code>pgx</code>"], ["Migration", "<code>golang-migrate</code>, <code>goose</code>"],
        ["Validation tag", "<code>go-playground/validator</code>"], ["Hot reload (development)", "<code>air</code>"],
        ["Structured log", "<code>log/slog</code> (standard library)"], ["OpenAPI", "<code>oapi-codegen</code>, <code>huma</code>"]]),
    tip("নতুন project-এ আগে standard library দিয়ে শুরু করুন; সত্যিই দরকার হলে তবেই package যোগ করুন — Go community এভাবেই কাজ করে।"))

c.finish("Go Web Development শেষ! 🎉",
         "Framework ছাড়াই Go দিয়ে পুরো একটা JSON API — database, validation, middleware, test আর ১৫ MB-এর Docker image।",
         recap=["<code>mux.HandleFunc(\"GET /products/{id}\", h)</code> + <code>r.PathValue</code>",
                "<code>writeJSON</code> helper; Laravel-এর মতো 422", "Middleware = <code>func(http.Handler) http.Handler</code>",
                "<code>database/sql</code> + <code>?</code> placeholder, <code>sql.ErrNoRows</code> → 404",
                "<code>httptest</code> দিয়ে handler test", "Graceful shutdown + distroless Docker"])


def write_project():
    proj = HERE / "go-shop-api"
    proj.mkdir(exist_ok=True)
    final = next(k for sl in c.slides for k in sl["codes"] if k.src.startswith("// Shop API"))
    (proj / "main.go").write_text(final.src + "\n")    # the gofmt-ed final lesson
    (proj / ".gitignore").write_text("shop.db*\nshop-api\n")
    (proj / "README.md").write_text(
        "# Go Shop API (Go Web Development course)\n\n```bash\ngo mod init shop-api && go mod tidy\ngo run .\n"
        "curl -s localhost:3000/api/v1/products\n"
        "curl -s -X POST localhost:3000/api/v1/products -H 'X-Api-Key: secret-123' -H 'Content-Type: application/json' \\\n"
        "  -d '{\"name\":\"Redmi 13\",\"brand\":\"Xiaomi\",\"price\":17500,\"stock\":5}'\n```\n")


if __name__ == "__main__":
    c.build()
    write_project()
