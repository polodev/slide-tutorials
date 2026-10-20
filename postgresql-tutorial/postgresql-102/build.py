"""PostgreSQL 102 — foreign key, GROUP BY + FILTER, JOIN, DISTINCT ON, string_agg/array_agg,
subquery, LATERAL, ON CONFLICT, view. Runs on ../shop_schema.py. Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
from kit import Course, code, php_note, points, quiz, say, table, task, tip, warn  # noqa: E402
from shop_schema import SCHEMA, SEED  # noqa: E402


def sql(src, **kw):
    return code(src, "postgresql", **kw)


def laravel(src, label="Laravel-এ"):
    return code(src, "php", run=False, label=label)


c = Course(slug="postgresql-102", title="PostgreSQL 102 — JOIN ও বিশেষ কৌশল", folder=HERE,
           subtitle="Relationship, GROUP BY, JOIN — আর PostgreSQL-এর নিজস্ব: FILTER, DISTINCT ON, string_agg, LATERAL, ON CONFLICT",
           series="PostgreSQL 102", sql_engine="postgresql",
           next_course=("../postgresql-103/index.html", "PostgreSQL 103 — Index, JSONB ও Full-text"))

c.cover("PostgreSQL 102<br>JOIN ও বিশেষ কৌশল",
        "অনেক table জুড়ে রিপোর্ট — আর এমন কিছু কৌশল যা MySQL-এ নেই বা অনেক কষ্টে লিখতে হয়।",
        learn=["Foreign key আর ON DELETE", "GROUP BY, HAVING, ROLLUP", "FILTER: এক query-তে অনেক শর্তের যোগফল",
               "INNER, LEFT JOIN আর anti-join", "DISTINCT ON: প্রতি দলের প্রথম row", "string_agg আর array_agg",
               "LATERAL: প্রতি row-এর জন্য subquery", "ON CONFLICT (upsert) আর VIEW"],
        need="PostgreSQL 101, অথবা MySQL 101।")

c.section("আজকের Database")
c.lesson("Rahim Mobile — PostgreSQL সংস্করণ",
    say("MySQL টিউটোরিয়ালের একই দোকান। পার্থক্য: identity column, <code>numeric</code>, <code>timestamp</code>, আর foreign key column-এর পাশেই <code>REFERENCES</code>।"),
    sql(SCHEMA, show_output=False, label="PostgreSQL — schema"),
    sql(SEED, show_output=False, label="PostgreSQL — seed data"),
    sql("\\dt"),
    warn("PostgreSQL foreign key column-এ নিজে থেকে index বানায় <b>না</b> (MySQL বানায়)। JOIN দ্রুত করতে নিজে দিন: <code>CREATE INDEX ON sales (customer_id);</code>"))

c.section("GROUP BY")
c.lesson("শাখা ধরে যোগফল",
    sql('''
SELECT b.name AS branch, count(*) AS invoices, sum(s.total) AS revenue
FROM sales s
JOIN branches b ON b.id = s.branch_id
GROUP BY b.name
ORDER BY revenue DESC;
'''),
    tip("PostgreSQL-এ <code>count(*)</code>-এর ফল <code>bigint</code>, <code>sum(numeric)</code>-এর ফল <code>numeric</code> — PHP-তে string হয়ে আসতে পারে।"))

c.lesson("কঠোর GROUP BY",
    say("SELECT-এ যা আছে তা GROUP BY-তে বা aggregate-এ থাকতেই হবে — PostgreSQL কোনো ছাড় দেয় না।"),
    sql("SELECT branch_id, invoice_no, sum(total) FROM sales GROUP BY branch_id;", err="must appear in the GROUP BY"),
    tip("ব্যতিক্রম: primary key দিয়ে GROUP BY করলে ঐ table-এর বাকি column নিজেই চলে — <code>GROUP BY b.id</code> দিলে <code>b.name</code> লেখা যায়।"))

c.lesson("FILTER: এক query-তে অনেক শর্ত",
    say("<code>count(*) FILTER (WHERE ...)</code> — একই দলে আলাদা শর্তের হিসাব। MySQL-এ এর জন্য <code>SUM(CASE WHEN ...)</code> লিখতে হয়।"),
    sql('''
SELECT b.name AS branch,
       count(*)                                             AS invoices,
       count(*) FILTER (WHERE s.customer_id IS NULL)        AS walk_in,
       sum(s.total) FILTER (WHERE s.total >= 20000)         AS big_sales,
       round(avg(s.total) FILTER (WHERE s.total < 20000))   AS avg_small
FROM sales s
JOIN branches b ON b.id = s.branch_id
GROUP BY b.id
ORDER BY b.id;
'''))

c.lesson("HAVING আর ROLLUP",
    sql('''
SELECT customer_id, count(*) AS visits, sum(total) AS spent
FROM sales
WHERE customer_id IS NOT NULL
GROUP BY customer_id
HAVING count(*) >= 2;
'''),
    sql('''
SELECT coalesce(b.name, 'মোট') AS branch, sum(s.total) AS revenue
FROM sales s JOIN branches b ON b.id = s.branch_id
GROUP BY ROLLUP (b.name)
ORDER BY b.name NULLS LAST;
'''))

c.lesson("দৈনিক বিক্রি আর খালি দিন",
    say("<code>generate_series</code> দিয়ে তারিখের তালিকা বানানো এক লাইনে — MySQL-এ recursive CTE লাগে।"),
    sql('''
SELECT d::date                      AS day,
       count(s.id)                  AS invoices,
       coalesce(sum(s.total), 0)    AS revenue
FROM generate_series(date '2026-10-14', date '2026-10-20', interval '1 day') AS d
LEFT JOIN sales s ON s.sold_at::date = d::date
GROUP BY d
ORDER BY d;
'''))

c.section("Foreign key")
c.lesson("ভুল id আটকানো",
    sql("INSERT INTO sales (invoice_no, branch_id, employee_id, sold_at, total)\nVALUES ('INV-9999', 99, 1, now(), 500);", err="foreign key"),
    sql("DELETE FROM branches WHERE name = 'Gulshan';", err="foreign key"))

c.lesson("ON DELETE CASCADE",
    sql('''
WITH new_sale AS (
    INSERT INTO sales (invoice_no, branch_id, employee_id, sold_at, total)
    VALUES ('INV-TEST', 1, 1, '2026-10-19 21:00', 650)
    RETURNING id
)
INSERT INTO sale_items (sale_id, product_id, qty, unit_price)
SELECT id, 8, 1, 650 FROM new_sale;

SELECT count(*) AS items_before FROM sale_items;
DELETE FROM sales WHERE invoice_no = 'INV-TEST';
SELECT count(*) AS items_after FROM sale_items;
'''),
    tip("উপরে <code>WITH ... INSERT ... RETURNING</code> — এক statement-এ sale বানিয়ে তার id দিয়ে item বানানো। PostgreSQL-এর অন্যতম সুন্দর কৌশল।"))

c.section("JOIN")
c.lesson("পুরো invoice",
    sql('''
SELECT s.invoice_no, c.name AS customer, e.name AS sold_by,
       p.name AS product, si.qty, si.qty * si.unit_price AS line_total
FROM sales s
JOIN employees  e  ON e.id = s.employee_id
JOIN customers  c  ON c.id = s.customer_id
JOIN sale_items si ON si.sale_id = s.id
JOIN products   p  ON p.id = si.product_id
WHERE s.invoice_no IN ('INV-1001', 'INV-1005');
'''))

c.lesson("LEFT JOIN আর anti-join",
    sql('''
SELECT s.invoice_no, coalesce(c.name, 'Walk-in') AS customer, s.total
FROM sales s
LEFT JOIN customers c ON c.id = s.customer_id
ORDER BY s.id
LIMIT 4;
'''),
    sql('''
SELECT p.name, p.stock FROM products p
WHERE NOT EXISTS (SELECT 1 FROM sale_items si WHERE si.product_id = p.id);
'''),
    php_note("<code>Product::doesntHave('saleItems')</code> ঠিক এই <code>NOT EXISTS</code> বানায়।"))

c.lesson("string_agg: invoice-এর সব product এক লাইনে",
    say("একটা দলের সব লেখা কমা দিয়ে জোড়া — MySQL-এর <code>GROUP_CONCAT</code>-এর মতো।"),
    sql('''
SELECT s.invoice_no,
       string_agg(p.name, ', ' ORDER BY p.name) AS products,
       sum(si.qty)                              AS items
FROM sales s
JOIN sale_items si ON si.sale_id = s.id
JOIN products p ON p.id = si.product_id
GROUP BY s.invoice_no
ORDER BY s.invoice_no
LIMIT 5;
'''))

c.lesson("array_agg: আসল array",
    sql('''
SELECT e.name AS employee,
       array_agg(s.invoice_no ORDER BY s.sold_at) AS invoices,
       cardinality(array_agg(s.id))               AS how_many
FROM employees e
JOIN sales s ON s.employee_id = e.id
GROUP BY e.id
ORDER BY how_many DESC;
'''),
    php_note("Laravel-এ pgsql array column পড়লে <code>{INV-1001,INV-1005}</code> আকারের string আসে — JSON চাইলে <code>json_agg()</code> দিন, PHP-তে <code>json_decode</code>।"))

c.lesson("DISTINCT ON: প্রতি দলের প্রথম row",
    say("\"প্রতিটি customer-এর সর্বশেষ কেনা\" — MySQL-এ window function বা subquery লাগে। PostgreSQL-এ <code>DISTINCT ON</code>।"),
    sql('''
SELECT DISTINCT ON (c.id)
       c.name, s.invoice_no, s.sold_at::date AS last_visit, s.total
FROM customers c
JOIN sales s ON s.customer_id = c.id
ORDER BY c.id, s.sold_at DESC;
'''),
    tip("নিয়ম: <code>ORDER BY</code> শুরু হবে <code>DISTINCT ON</code>-এর column দিয়ে, তারপর কোন row \"প্রথম\" সেটা ঠিক করার ক্রম।"))

c.lesson("LATERAL: প্রতি row-এর জন্য subquery",
    say("<code>JOIN LATERAL</code>-এর ভিতরের subquery বাইরের row দেখতে পায়। \"প্রতিটি শাখার সবচেয়ে বড় ২টা invoice\"।"),
    sql('''
SELECT b.name AS branch, top.invoice_no, top.total
FROM branches b
JOIN LATERAL (
    SELECT invoice_no, total
    FROM sales s
    WHERE s.branch_id = b.id
    ORDER BY total DESC
    LIMIT 2
) AS top ON true
ORDER BY b.name, top.total DESC;
'''))

c.section("Subquery, Upsert ও View")
c.lesson("Subquery",
    sql("SELECT name, price FROM products\nWHERE price > (SELECT avg(price) FROM products)\nORDER BY price DESC;"),
    sql('''
SELECT name FROM customers c
WHERE EXISTS (SELECT 1 FROM sales s WHERE s.customer_id = c.id AND s.total > 20000);
'''))

c.lesson("ON CONFLICT: upsert",
    say("Unique key-তে সংঘর্ষ হলে কী হবে বলে দিই: কিছু না (<code>DO NOTHING</code>) বা update (<code>DO UPDATE</code>)। <code>EXCLUDED</code> মানে যে row ঢুকতে চাইছিল।"),
    sql("CREATE UNIQUE INDEX products_name_unique ON products (name);"),
    sql('''
INSERT INTO products (category_id, name, brand, cost, price, stock) VALUES
    (1, 'Redmi 13',  'Xiaomi', 15500, 17200, 5),
    (1, 'Redmi 14C', 'Xiaomi', 13000, 14500, 6)
ON CONFLICT (name) DO UPDATE
    SET cost = EXCLUDED.cost, price = EXCLUDED.price
RETURNING name, price, (xmax = 0) AS inserted;
'''),
    php_note("Laravel-এর <code>upsert()</code> pgsql-এ ঠিক এই <code>ON CONFLICT ... DO UPDATE</code> বানায়। <code>insertOrIgnore()</code> → <code>ON CONFLICT DO NOTHING</code>।"))

c.lesson("View",
    sql('''
CREATE VIEW branch_daily_sales AS
SELECT b.name AS branch, s.sold_at::date AS day, sum(s.total) AS revenue
FROM sales s JOIN branches b ON b.id = s.branch_id
GROUP BY b.name, s.sold_at::date;

SELECT * FROM branch_daily_sales WHERE branch = 'Mirpur' ORDER BY day;
'''),
    tip("হিসাব ভারী হলে <code>MATERIALIZED VIEW</code> — ফলাফল জমা থাকে, <code>REFRESH</code> দিলে আবার হিসাব (PostgreSQL 103)।"))

c.lesson("Project: সপ্তাহের রিপোর্ট",
    sql('''
SELECT b.name AS branch,
       e.name AS employee,
       count(DISTINCT s.id)                                  AS invoices,
       sum(si.qty * si.unit_price)                           AS revenue,
       sum(si.qty * (si.unit_price - p.cost))                AS profit,
       string_agg(DISTINCT p.brand, ', ')                    AS brands
FROM sales s
JOIN branches   b  ON b.id = s.branch_id
JOIN employees  e  ON e.id = s.employee_id
JOIN sale_items si ON si.sale_id = s.id
JOIN products   p  ON p.id = si.product_id
WHERE s.sold_at >= '2026-10-15' AND s.sold_at < '2026-10-20'
GROUP BY b.name, e.name
ORDER BY profit DESC;
'''),
    task("<code>FILTER</code> দিয়ে একই রিপোর্টে আরেকটা column যোগ করুন: শুধু Smartphone category-র লাভ।"))

c.finish("PostgreSQL 102 শেষ! 🎉",
         "JOIN আর রিপোর্ট হয়ে গেল, সাথে PostgreSQL-এর নিজস্ব কৌশল। এরপর index, JSONB, full-text আর transaction।",
         recap=["Foreign key column-এ নিজে index দিন", "<code>FILTER (WHERE ...)</code> — শর্তসাপেক্ষ aggregate",
                "<code>generate_series</code> — তারিখ/সংখ্যার তালিকা", "<code>DISTINCT ON</code> — প্রতি দলের প্রথম row",
                "<code>string_agg</code>, <code>array_agg</code>, <code>LATERAL</code>", "<code>ON CONFLICT</code> — upsert, <code>RETURNING</code> সহ"])

if __name__ == "__main__":
    c.build()
