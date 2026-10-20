"""PostgreSQL 103 — index types & EXPLAIN, pg_trgm, transaction + savepoint + SKIP LOCKED, window function,
recursive CTE, JSONB, array, full-text search, materialized view, enum, plpgsql trigger.
Runs on ../shop_schema.py plus a generated 50,000-row orders table. Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402
from pg_shop_schema import SCHEMA, SEED  # noqa: E402


def sql(src, **kw):
    return code(src, "postgresql", **kw)


def laravel(src, label="Laravel-এ"):
    return code(src, "php", run=False, label=label)


BIG = '''
CREATE TABLE orders (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id      bigint NOT NULL,
    customer_phone text NOT NULL,
    status         text NOT NULL,
    total          numeric(10,2) NOT NULL,
    created_at     timestamp NOT NULL
);

INSERT INTO orders (branch_id, customer_phone, status, total, created_at)
SELECT n % 3 + 1,
       '017' || lpad((n % 20000)::text, 8, '0'),
       (ARRAY['paid', 'due', 'cancelled'])[n % 3 + 1],
       (n % 500) * 100 + 500,
       timestamp '2026-01-01' + (n % 290) * interval '1 day' + (n % 86400) * interval '1 second'
FROM generate_series(1, 50000) AS n;

ANALYZE orders;
'''

c = Course(slug="postgresql-103", title="PostgreSQL 103 — Index, JSONB ও Full-text", folder=HERE,
           subtitle="Index-এর ধরন আর EXPLAIN, transaction ও SKIP LOCKED, window function, JSONB, array, full-text search, materialized view আর trigger",
           series="PostgreSQL 103", sql_engine="postgresql",
           next_course=("../postgresql-for-laravel/index.html", "PostgreSQL for Laravel"))

c.cover("PostgreSQL 103<br>Index, JSONB ও Full-text",
        "PostgreSQL-কে এত জনপ্রিয় করেছে যে ক্ষমতাগুলো — নানা রকম index, JSONB, ভিতরেই search engine, আর নিখুঁত transaction।",
        learn=["EXPLAIN আর B-tree index", "Partial আর expression index", "pg_trgm: ILIKE '%...%' দ্রুত",
               "Transaction, SAVEPOINT, SKIP LOCKED", "Window function আর recursive CTE", "JSONB আর GIN index",
               "Array আর full-text search", "Materialized view, enum, plpgsql trigger"],
        need="PostgreSQL 102।")

c.section("প্রস্তুতি")
c.lesson("আজকের data",
    sql(SCHEMA + SEED, show_output=False, label="PostgreSQL — দোকানের table (102 থেকে)"),
    sql(BIG, show_output=False, label="PostgreSQL — ৫০,০০০ order"),
    sql("SELECT count(*) AS orders, min(created_at) AS first, max(created_at) AS last FROM orders;"),
    say("<code>generate_series(1, 50000)</code> দিয়ে এক statement-এ ৫০ হাজার row — MySQL-এর মতো recursive CTE লাগল না।"))

c.section("Index")
c.lesson("EXPLAIN: Seq Scan",
    say("<code>EXPLAIN</code> দেখায় PostgreSQL কীভাবে query চালাবে। <code>(COSTS OFF)</code> দিলে শুধু পরিকল্পনা — পড়তে সহজ।"),
    sql("EXPLAIN (COSTS OFF)\nSELECT * FROM orders WHERE customer_phone = '01700001234';"),
    tip("<code>Seq Scan</code> = পুরো table পড়া। আসল সময় দেখতে <code>EXPLAIN ANALYZE</code> (query সত্যি চালায়)।"))

c.lesson("B-tree index",
    sql("CREATE INDEX orders_customer_phone_idx ON orders (customer_phone);"),
    sql("EXPLAIN (COSTS OFF)\nSELECT * FROM orders WHERE customer_phone = '01700001234';"),
    say("<code>Bitmap Index Scan</code>/<code>Index Scan</code> — সরাসরি মিল থাকা row-এ।"),
    tip("বড় production table-এ <code>CREATE INDEX CONCURRENTLY</code> দিন — index বানানোর সময় table-এ লেখা বন্ধ হয় না।"))

c.lesson("Composite index",
    sql("CREATE INDEX orders_branch_created_idx ON orders (branch_id, created_at);"),
    sql('''
EXPLAIN (COSTS OFF)
SELECT count(*) FROM orders
WHERE branch_id = 2 AND created_at >= '2026-10-01' AND created_at < '2026-10-08';
'''),
    laravel("$table->index(['branch_id', 'created_at']);"))

c.lesson("Partial index: শুধু দরকারি row-এর",
    say("বাকি (due) order-গুলোই বারবার খোঁজা হয়, কিন্তু সেগুলো মোটের এক-তৃতীয়াংশ। শুধু ঐ row-গুলোর জন্য index — ছোট আর দ্রুত।"),
    sql("CREATE INDEX orders_due_idx ON orders (created_at) WHERE status = 'due';"),
    sql("EXPLAIN (COSTS OFF)\nSELECT id, total FROM orders\nWHERE status = 'due' AND created_at >= '2026-10-10';"),
    php_note("Soft delete-এর জন্য দারুণ: <code>CREATE UNIQUE INDEX ... ON users (email) WHERE deleted_at IS NULL</code> — মুছে ফেলা user-এর email আবার ব্যবহার করা যায়।"))

c.lesson("Expression index",
    say("<code>WHERE lower(name) = ...</code> সাধারণ index ব্যবহার করতে পারে না। Expression-এর উপরেই index দিন।"),
    sql("CREATE INDEX orders_day_idx ON orders ((created_at::date));"),
    sql("EXPLAIN (COSTS OFF)\nSELECT count(*) FROM orders WHERE created_at::date = '2026-10-05';"),
    tip("Laravel-এর <code>whereDate()</code> pgsql-এ <code>created_at::date = ?</code> বানায় — এই index দিলে সেটাও দ্রুত।"))

c.lesson("pg_trgm: মাঝখানের অংশ দিয়ে খোঁজা",
    say("<code>ILIKE '%1234%'</code> সাধারণ B-tree ব্যবহার করতে পারে না। <code>pg_trgm</code> extension লেখাকে ৩ অক্ষরের টুকরো করে GIN index বানায় — মাঝখানের মিলও দ্রুত।"),
    sql('''
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX orders_phone_trgm_idx ON orders USING gin (customer_phone gin_trgm_ops);
'''),
    sql("EXPLAIN (COSTS OFF)\nSELECT count(*) FROM orders WHERE customer_phone ILIKE '%12345%';"),
    php_note("Laravel migration-এ: <code>DB::statement('CREATE EXTENSION IF NOT EXISTS pg_trgm');</code> তারপর raw SQL দিয়ে index।"))

c.section("Transaction")
c.lesson("BEGIN, COMMIT, ROLLBACK",
    sql('''
BEGIN;
UPDATE products SET stock = 0 WHERE brand = 'Xiaomi';
SELECT name, stock FROM products WHERE brand = 'Xiaomi';
ROLLBACK;

SELECT name, stock FROM products WHERE brand = 'Xiaomi';
'''))

c.lesson("Error হলে পুরো transaction বাতিল",
    say("PostgreSQL-এ transaction-এর ভিতরে একটা error হলে পরের সব কমান্ড অগ্রাহ্য হয় — commit করতেই দেয় না।"),
    sql('''
BEGIN;
UPDATE products SET stock = stock - 1 WHERE id = 8;
UPDATE products SET stock = stock - 5 WHERE id = 4;   -- CHECK (stock >= 0) ভাঙবে
COMMIT;
''', err="check constraint"),
    sql("SELECT id, name, stock FROM products WHERE id IN (4, 8);"))

c.lesson("SAVEPOINT: আংশিক ফেরত",
    sql('''
BEGIN;
UPDATE products SET stock = stock - 1 WHERE id = 8;
SAVEPOINT before_risky;
UPDATE products SET price = 0 WHERE brand = 'Apple';
ROLLBACK TO SAVEPOINT before_risky;    -- শুধু দ্বিতীয়টা বাতিল
COMMIT;

SELECT name, stock, price FROM products WHERE id IN (4, 8);
'''),
    php_note("Laravel-এ <code>DB::transaction()</code>-এর ভিতরে আরেকটা <code>DB::transaction()</code> দিলে Laravel নিজেই SAVEPOINT ব্যবহার করে।"))

c.lesson("FOR UPDATE SKIP LOCKED: job queue",
    say("অনেক worker একসাথে কাজ নিচ্ছে। <code>SKIP LOCKED</code> — অন্য কেউ তালা দেওয়া row ছেড়ে পরেরটা নেয়, অপেক্ষা করে না।"),
    sql('''
CREATE TABLE jobs (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, task text, done boolean DEFAULT false);
INSERT INTO jobs (task) VALUES ('send SMS INV-1001'), ('send SMS INV-1002'), ('send SMS INV-1003');

BEGIN;
SELECT id, task FROM jobs
WHERE NOT done
ORDER BY id
LIMIT 1
FOR UPDATE SKIP LOCKED;
UPDATE jobs SET done = true WHERE id = 1;
COMMIT;
'''),
    php_note("Laravel-এর <code>database</code> queue driver PostgreSQL/MySQL 8-এ ঠিক এভাবেই job নেয় — তাই একাধিক <code>queue:work</code> একই job দুইবার পায় না।"))

c.section("Window ও CTE")
c.lesson("Window function",
    sql('''
SELECT b.name AS branch, s.invoice_no, s.total,
       rank() OVER (PARTITION BY s.branch_id ORDER BY s.total DESC) AS rank_in_branch,
       round(100 * s.total / sum(s.total) OVER (PARTITION BY s.branch_id), 1) AS pct_of_branch
FROM sales s JOIN branches b ON b.id = s.branch_id
ORDER BY b.name, rank_in_branch;
'''))

c.lesson("চলমান যোগফল আর LAG",
    sql('''
WITH daily AS (
    SELECT sold_at::date AS day, sum(total) AS revenue FROM sales GROUP BY 1
)
SELECT day, revenue,
       sum(revenue) OVER (ORDER BY day)                  AS running_total,
       revenue - lag(revenue) OVER (ORDER BY day)        AS vs_yesterday,
       round(avg(revenue) OVER (ORDER BY day ROWS 2 PRECEDING)) AS avg_3_days
FROM daily;
'''))

c.lesson("Recursive CTE: category গাছ",
    sql('''
CREATE TABLE category_tree (id int PRIMARY KEY, parent_id int, name text);
INSERT INTO category_tree VALUES
    (1, NULL, 'Mobile'), (2, 1, 'Smartphone'), (3, 1, 'Accessories'),
    (4, 3, 'Charger'), (5, 3, 'Cover'), (6, 4, 'Fast charger');

WITH RECURSIVE tree AS (
    SELECT id, name, 0 AS depth, name AS path FROM category_tree WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, t.depth + 1, t.path || ' › ' || c.name
    FROM category_tree c JOIN tree t ON c.parent_id = t.id
)
SELECT repeat('  ', depth) || name AS category, path FROM tree ORDER BY path;
'''))

c.section("JSONB ও Array")
c.lesson("JSONB: binary JSON",
    say("<code>jsonb</code> parse করে binary আকারে রাখে — query দ্রুত, key-এর ক্রম আর ফাঁকা জায়গা থাকে না। <code>-&gt;</code> JSON দেয়, <code>-&gt;&gt;</code> লেখা দেয়।"),
    sql('''
ALTER TABLE products ADD COLUMN specs jsonb NOT NULL DEFAULT '{}';

UPDATE products SET specs = '{"ram": 8, "storage": 256, "colors": ["Black", "Green"], "5g": false}' WHERE id = 2;
UPDATE products SET specs = '{"ram": 4, "storage": 128, "colors": ["Blue"], "5g": false}'           WHERE id = 3;
UPDATE products SET specs = '{"ram": 4, "storage": 64,  "colors": ["Black"], "5g": true}'           WHERE id = 4;

SELECT name,
       specs->>'ram'                     AS ram,
       (specs->>'storage')::int          AS storage,
       specs->'colors'                   AS colors,
       jsonb_array_length(specs->'colors') AS n_colors
FROM products
WHERE specs ? 'ram'
ORDER BY name;
'''))

c.lesson("JSONB খোঁজা: @> আর GIN index",
    say("<code>@&gt;</code> মানে \"ভিতরে আছে\"। GIN index দিলে বড় table-এও দ্রুত।"),
    sql('''
CREATE INDEX products_specs_gin ON products USING gin (specs);

SELECT name FROM products WHERE specs @> '{"colors": ["Black"]}';
SELECT name FROM products WHERE specs @> '{"5g": true}';

UPDATE products SET specs = jsonb_set(specs, '{ram}', '6') WHERE id = 3
RETURNING name, specs;
'''),
    laravel('''
protected $casts = ['specs' => 'array'];
Product::whereJsonContains('specs->colors', 'Black')->get();   // pgsql: specs->'colors' @> '["Black"]'
Product::where('specs->5g', true)->get();
'''))

c.lesson("Array column",
    sql('''
ALTER TABLE customers ADD COLUMN tags text[] NOT NULL DEFAULT '{}';
UPDATE customers SET tags = ARRAY['vip', 'wholesale'] WHERE id = 1;
UPDATE customers SET tags = ARRAY['vip'] WHERE id = 3;

SELECT name, tags FROM customers WHERE 'vip' = ANY (tags);
SELECT name FROM customers WHERE tags @> ARRAY['vip', 'wholesale'];
SELECT unnest(tags) AS tag, count(*) FROM customers GROUP BY 1;
'''),
    tip("ছোট, সরল তালিকার জন্য array চমৎকার। Tag-এর নিজের তথ্য (রং, বিবরণ) লাগলে আলাদা table + pivot ভালো।"))

c.section("Full-text ও অন্যান্য")
c.lesson("Full-text search",
    say("<code>to_tsvector</code> লেখাকে শব্দে ভাঙে (stemming সহ: charging → charg), <code>websearch_to_tsquery</code> Google-এর মতো query বোঝে। <code>ts_rank</code> দিয়ে প্রাসঙ্গিকতা।"),
    sql('''
ALTER TABLE products ADD COLUMN search tsvector
    GENERATED ALWAYS AS (to_tsvector('english', name || ' ' || brand)) STORED;
CREATE INDEX products_search_idx ON products USING gin (search);

SELECT name, brand, round(ts_rank(search, q)::numeric, 3) AS rank
FROM products, websearch_to_tsquery('english', 'redmi OR galaxy') AS q
WHERE search @@ q
ORDER BY rank DESC, name;

SELECT name FROM products WHERE search @@ websearch_to_tsquery('english', 'redmi -note');
SELECT websearch_to_tsquery('english', 'redmi OR galaxy -note') AS how_postgres_reads_it;
'''),
    tip("শেষ query দেখুন: <code>-note</code> শুধু পাশের শব্দের সাথে বাঁধে — <code>'redmi' | 'galaxi' &amp; !'note'</code>। তাই \"redmi OR galaxy -note\" দিলেও Redmi Note আসবে।"),
    php_note("Laravel: <code>Product::whereFullText(['name', 'brand'], 'redmi')</code> pgsql-এ <code>to_tsvector(...) @@ plainto_tsquery(...)</code> বানায়। বাংলার জন্য <code>'simple'</code> config বা pg_trgm ভালো।"))

c.lesson("Materialized view",
    sql('''
CREATE MATERIALIZED VIEW monthly_branch_sales AS
SELECT branch_id, date_trunc('month', created_at)::date AS month, count(*) AS orders, sum(total) AS revenue
FROM orders
GROUP BY 1, 2;

CREATE INDEX ON monthly_branch_sales (branch_id, month);

SELECT * FROM monthly_branch_sales WHERE branch_id = 1 ORDER BY month DESC LIMIT 3;
REFRESH MATERIALIZED VIEW monthly_branch_sales;
'''),
    say("৫০ হাজার row-এর হিসাব একবার করে জমা রাখা — dashboard এখন ছোট table পড়ে। নতুন data এলে <code>REFRESH</code> (Laravel scheduler দিয়ে রাতে)।"))

c.lesson("Enum type",
    sql('''
CREATE TYPE sale_status AS ENUM ('draft', 'paid', 'returned');
ALTER TABLE sales ADD COLUMN status sale_status NOT NULL DEFAULT 'paid';
UPDATE sales SET status = 'returned' WHERE invoice_no = 'INV-1009';
SELECT status, count(*) FROM sales GROUP BY status ORDER BY status;
'''),
    sql("UPDATE sales SET status = 'cancelled' WHERE id = 1;", err="invalid input value for enum"))

c.lesson("plpgsql function আর trigger",
    say("Trigger চালাতে PostgreSQL-এ আগে একটা function লাগে (<code>plpgsql</code> ভাষায়)। স্টক বদলালেই log।"),
    sql('''
CREATE TABLE stock_logs (
    product_id bigint, old_stock int, new_stock int, changed_at timestamptz DEFAULT now()
);

CREATE FUNCTION log_stock_change() RETURNS trigger AS $$
BEGIN
    IF NEW.stock <> OLD.stock THEN
        INSERT INTO stock_logs (product_id, old_stock, new_stock) VALUES (NEW.id, OLD.stock, NEW.stock);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER products_stock_log AFTER UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION log_stock_change();

UPDATE products SET stock = stock + 10 WHERE id = 6;
UPDATE products SET price = price WHERE id = 7;
SELECT product_id, old_stock, new_stock FROM stock_logs;
'''))

c.lesson("Role আর অনুমতি",
    say("App-এর জন্য আলাদা role, শুধু দরকারি অনুমতি। Superuser দিয়ে Laravel চালাবেন না।"),
    shell("shop=# CREATE ROLE shop_app LOGIN PASSWORD 'a-long-random-password';\n"
          "shop=# GRANT CONNECT ON DATABASE shop TO shop_app;\n"
          "shop=# GRANT USAGE ON SCHEMA public TO shop_app;\n"
          "shop=# GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO shop_app;\n"
          "shop=# GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO shop_app;"),
    tip("Multi-tenant app-এ <b>Row Level Security</b> (<code>CREATE POLICY</code>) দিয়ে database নিজেই অন্য tenant-এর row লুকাতে পারে।"))

c.finish("PostgreSQL 103 শেষ! 🎉",
         "Index-এর নানা রূপ, JSONB, full-text, SKIP LOCKED — PostgreSQL-এর আসল শক্তি এখন জানা। শেষ কোর্সে Laravel-এর সাথে।",
         recap=["<code>EXPLAIN</code>: Seq Scan দেখলে index ভাবুন", "Partial, expression আর trigram (GIN) index",
                "Error হলে পুরো transaction বাতিল; SAVEPOINT দিয়ে আংশিক",
                "<code>FOR UPDATE SKIP LOCKED</code> = নিরাপদ job queue", "JSONB + <code>@&gt;</code> + GIN; array + <code>ANY</code>",
                "tsvector দিয়ে full-text; materialized view দিয়ে দ্রুত dashboard"])

if __name__ == "__main__":
    c.build()
