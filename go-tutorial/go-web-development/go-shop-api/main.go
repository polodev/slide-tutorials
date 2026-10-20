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
