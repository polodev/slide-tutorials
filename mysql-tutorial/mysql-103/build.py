"""MySQL 103 — index & EXPLAIN, transaction, window function, CTE, JSON, constraint, trigger, full-text, users.
Runs on the shared shop schema plus a generated 50,000-row orders table. Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402
from shop_schema import SCHEMA, SEED  # noqa: E402


def sql(src, **kw):
    return code(src, "mysql", **kw)


def laravel(src, label="Laravel-এ"):
    return code(src, "php", run=False, label=label)


BIG = '''
CREATE TABLE orders (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    branch_id      INT UNSIGNED NOT NULL,
    customer_phone VARCHAR(15)  NOT NULL,
    status         ENUM('paid', 'due', 'cancelled') NOT NULL,
    total          DECIMAL(10,2) NOT NULL,
    created_at     DATETIME NOT NULL
);

SET SESSION cte_max_recursion_depth = 100000;

INSERT INTO orders (branch_id, customer_phone, status, total, created_at)
WITH RECURSIVE seq (n) AS (
    SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 50000
)
SELECT n % 3 + 1,
       CONCAT('017', LPAD(n % 20000, 8, '0')),
       ELT(n % 3 + 1, 'paid', 'due', 'cancelled'),
       (n % 500) * 100 + 500,
       '2026-01-01' + INTERVAL (n % 290) DAY + INTERVAL (n % 86400) SECOND
FROM seq;

ANALYZE TABLE orders;
'''

c = Course(slug="mysql-103", title="MySQL 103 — Index, Transaction ও Window function", folder=HERE,
           subtitle="বড় data-তে দ্রুত query (index, EXPLAIN), নিরাপদ লেনদেন (transaction), window function, CTE, JSON আর trigger",
           series="MySQL 103", sql_engine="mysql",
           next_course=("../mysql-for-laravel/index.html", "MySQL for Laravel"))

c.cover("MySQL 103<br>Index, Transaction ও Window function",
        "Query লিখতে পারেন। এবার শিখব কীভাবে ৫০ হাজার row-এও query মুহূর্তে চলে, টাকা-স্টকের হিসাব কখনো আধাআধি না হয়, আর এক query-তে র‍্যাংকিং বা চলমান যোগফল।",
        learn=["Index কী, EXPLAIN পড়া", "Composite index আর leftmost নিয়ম", "কোন query index ব্যবহার করতে পারে না",
               "Transaction: COMMIT, ROLLBACK", "Window function: ROW_NUMBER, RANK, LAG", "CTE আর recursive CTE",
               "JSON column আর generated column", "CHECK, trigger, full-text, user permission"],
        need="MySQL 102 (JOIN, GROUP BY, subquery)।")

# ================================================================== setup
c.section("প্রস্তুতি")
c.lesson("আজকের data: দোকান + ৫০ হাজার order",
    say("আগের কোর্সের দোকানের table আর সাথে একটা বড় <code>orders</code> table, যেটা recursive CTE দিয়ে ৫০,০০০ row বানিয়ে ভরা। Index-এর পার্থক্য বুঝতে বড় data লাগে।"),
    sql(SCHEMA + SEED, show_output=False, label="MySQL — দোকানের table (MySQL 102 থেকে)"),
    sql(BIG, show_output=False, label="MySQL — ৫০,০০০ order"),
    sql("SELECT COUNT(*) AS orders, MIN(created_at) AS first, MAX(created_at) AS last FROM orders;"))

# ================================================================== index
c.section("Index ও EXPLAIN")
c.lesson("Index ছাড়া: পুরো table পড়া",
    say("একটা ফোন নম্বরের order খুঁজতে MySQL-কে ৫০,০০০ row-ই পড়তে হয় (<b>table scan</b>)। <code>EXPLAIN</code> দেখায় MySQL কীভাবে query চালাবে।"),
    sql("EXPLAIN FORMAT=TREE\nSELECT * FROM orders WHERE customer_phone = '01700001234';"),
    tip("<code>Table scan</code> আর <code>rows=</code> সংখ্যাটা দেখুন — প্রায় সব row।"))

c.lesson("Index দিলে: সরাসরি খুঁজে পাওয়া",
    say("Index হলো বইয়ের শেষের সূচির মতো — সাজানো তালিকা, যেখান থেকে সোজা পাতায় যাওয়া যায়।"),
    sql("CREATE INDEX orders_customer_phone_index ON orders (customer_phone);"),
    sql("EXPLAIN FORMAT=TREE\nSELECT * FROM orders WHERE customer_phone = '01700001234';"),
    laravel("$table->index('customer_phone');   // migration-এ"))

c.lesson("Composite index আর leftmost নিয়ম",
    say("দুই column একসাথে: <code>(branch_id, created_at)</code>। Index সাজানো থাকে আগে branch, তারপর তারিখ ধরে — ফোনবুক যেমন আগে পদবি, তারপর নাম। তাই branch + তারিখ দিয়ে খোঁজা সবচেয়ে দ্রুত।"),
    sql("CREATE INDEX orders_branch_created_index ON orders (branch_id, created_at);"),
    sql('''
EXPLAIN FORMAT=TREE
SELECT COUNT(*) FROM orders
WHERE branch_id = 2 AND created_at >= '2026-10-01' AND created_at < '2026-10-08';
'''),
    sql('''
EXPLAIN FORMAT=TREE
SELECT COUNT(*) FROM orders
WHERE created_at >= '2026-10-01' AND created_at < '2026-10-08';
'''),
    tip("দুটো <code>cost</code> তুলনা করুন: branch + তারিখে ~৮২, শুধু তারিখে ~১৪১০। শুধু তারিখ দিলে MySQL 8 \"skip scan\" দিয়ে প্রতিটি branch আলাদা করে ঘোরে — চলে, কিন্তু অনেক বেশি খরচে। প্রায়ই শুধু তারিখে খুঁজলে আলাদা <code>(created_at)</code> index দিন।"),
    laravel("$table->index(['branch_id', 'created_at']);"))

c.lesson("Column-এ function দিলে index কাজ করে না",
    say("<code>DATE(created_at) = ...</code> লিখলে MySQL index-এর তারিখ অংশ ব্যবহার করতে পারে না — branch ধরে ~২৫ হাজার row পড়ে, তারপর প্রতিটিতে function চালিয়ে ছাঁকে। Range শর্তে মাত্র ~৫৮ row (দুটোর <code>rows=</code> দেখুন)।"),
    sql('''
EXPLAIN FORMAT=TREE
SELECT COUNT(*) FROM orders WHERE branch_id = 2 AND DATE(created_at) = '2026-10-05';
'''),
    sql('''
EXPLAIN FORMAT=TREE
SELECT COUNT(*) FROM orders
WHERE branch_id = 2 AND created_at >= '2026-10-05' AND created_at < '2026-10-06';
'''),
    php_note("Laravel-এর <code>whereDate('created_at', $day)</code> ভিতরে <code>DATE(created_at) = ?</code> বানায়! বড় table-এ <code>whereBetween('created_at', [$start, $end])</code> দিন।"))

c.lesson("LIKE: শুরু জানা থাকলে index চলে",
    sql("EXPLAIN FORMAT=TREE\nSELECT COUNT(*) FROM orders WHERE customer_phone LIKE '0170000%';"),
    sql("EXPLAIN FORMAT=TREE\nSELECT COUNT(*) FROM orders WHERE customer_phone LIKE '%1234';"),
    tip("শেষের অংশ দিয়ে খুঁজতে হলে (যেমন IMEI-এর শেষ ৪ সংখ্যা) আলাদা column-এ উল্টো করে রাখা বা full-text/search engine লাগে।"))

c.lesson("Index-এর খরচ",
    sql("SHOW INDEX FROM orders;"),
    points("প্রতিটি index disk-এ জায়গা নেয়", "INSERT/UPDATE-এ প্রতিটি index-ও আপডেট হয় — লেখা ধীর হয়",
           "যে column দিয়ে <b>প্রায়ই</b> WHERE, JOIN বা ORDER BY করেন, শুধু সেগুলোতে index",
           "Foreign key column-এ MySQL নিজেই index বানায়"),
    quiz("<code>status</code> column-এ (মাত্র ৩টা আলাদা মান) একা index দেওয়া কি ভালো?",
         "সাধারণত না — এক-তৃতীয়াংশ row মিলে যায়, table scan-ই প্রায় সমান দ্রুত। অন্য column-এর সাথে composite index হলে কাজে লাগতে পারে।"))

# ================================================================== transactions
c.section("Transaction")
c.lesson("Transaction কেন?",
    say("একটা বিক্রিতে তিনটা কাজ: sale লেখা, item লেখা, স্টক কমানো। মাঝখানে ভুল হলে? স্টক কমে গেল কিন্তু বিক্রি লেখা হলো না — হিসাব নষ্ট।"),
    points("<b>Transaction</b>: কয়েকটা কাজ একসাথে — হয় সব হবে, নয়তো একটাও না",
           "<code>START TRANSACTION</code> → কাজ → <code>COMMIT</code> (পাকা করো) অথবা <code>ROLLBACK</code> (সব বাতিল)",
           "InnoDB engine (MySQL-এর ডিফল্ট) transaction সমর্থন করে"),
    php_note("Laravel-এর <code>DB::transaction(function () { ... });</code> ভিতরে এটাই করে: exception হলে ROLLBACK, নইলে COMMIT।"))

c.lesson("COMMIT: পুরো বিক্রি একসাথে",
    sql('''
SELECT stock FROM products WHERE id = 1;

START TRANSACTION;
INSERT INTO sales (invoice_no, branch_id, employee_id, customer_id, sold_at, total)
VALUES ('INV-1011', 1, 1, 6, '2026-10-20 12:00:00', 17500);
INSERT INTO sale_items (sale_id, product_id, qty, unit_price) VALUES (LAST_INSERT_ID(), 1, 1, 17500);
UPDATE products SET stock = stock - 1 WHERE id = 1;
COMMIT;

SELECT stock FROM products WHERE id = 1;
'''))

c.lesson("ROLLBACK: সব বাতিল",
    sql('''
START TRANSACTION;
UPDATE products SET stock = 0 WHERE brand = 'Xiaomi';
SELECT name, stock FROM products WHERE brand = 'Xiaomi';
ROLLBACK;

SELECT name, stock FROM products WHERE brand = 'Xiaomi';
'''),
    tip("Production-এ হাতে বড় UPDATE চালানোর আগে <code>START TRANSACTION</code> দিন, ফলাফল দেখে তারপর COMMIT বা ROLLBACK।"))

c.lesson("মাঝপথে error হলে",
    say("স্টক <code>UNSIGNED</code> — ০-এর নিচে যেতে পারে না। দ্বিতীয় UPDATE ব্যর্থ হয়, client থেমে যায়, আর commit না হওয়া transaction নিজে থেকেই বাতিল (rollback) হয়।"),
    sql('''
START TRANSACTION;
UPDATE products SET stock = stock - 1 WHERE id = 8;    -- Charger: ঠিক আছে
UPDATE products SET stock = stock - 5 WHERE id = 4;    -- iPhone 12: আছে মাত্র ১টা
COMMIT;
''', err="1690"),
    sql("SELECT id, name, stock FROM products WHERE id IN (4, 8);"),
    say("Charger-এর স্টকও কমেনি (৩০ আছে) — কারণ দুটো UPDATE একই transaction-এ ছিল।"))

c.lesson("একই স্টক দুইজন বিক্রি করলে: FOR UPDATE",
    say("দুই কাউন্টার একসাথে শেষ iPhone বিক্রি করছে — দুজনেই দেখল stock = 1। <code>SELECT ... FOR UPDATE</code> row-টা তালাবদ্ধ করে; দ্বিতীয়জন অপেক্ষা করে, প্রথমজনের COMMIT-এর পর নতুন মান দেখে।"),
    sql('''
START TRANSACTION;
SELECT id, name, stock FROM products WHERE id = 4 FOR UPDATE;
-- stock > 0 হলে বিক্রি; অন্য transaction এই row-এর জন্য এখন অপেক্ষা করবে
UPDATE products SET stock = stock - 1 WHERE id = 4;
COMMIT;
'''),
    laravel('''
DB::transaction(function () use ($productId) {
    $product = Product::lockForUpdate()->findOrFail($productId);
    abort_if($product->stock < 1, 422, 'স্টক নেই');
    $product->decrement('stock');
});
'''),
    tip("Transaction ছোট রাখুন — ভিতরে API call বা ধীর কাজ করবেন না, নইলে অন্যরা তালার জন্য অপেক্ষা করবে (lock wait, deadlock)।"))

# ================================================================== window
c.section("Window function")
c.lesson("ROW_NUMBER: র‍্যাংকিং",
    say("Window function GROUP BY-এর মতো row একত্র করে না — প্রতিটি row রেখে পাশে হিসাব যোগ করে। <code>OVER (...)</code> বলে কোন \"জানালা\" ধরে।"),
    sql('''
SELECT invoice_no, total,
       ROW_NUMBER() OVER (ORDER BY total DESC) AS position
FROM sales
LIMIT 5;
'''))

c.lesson("PARTITION BY: প্রতি শাখায় আলাদা র‍্যাংক",
    sql('''
SELECT b.name AS branch, s.invoice_no, s.total,
       ROW_NUMBER() OVER (PARTITION BY s.branch_id ORDER BY s.total DESC) AS rank_in_branch
FROM sales s
JOIN branches b ON b.id = s.branch_id;
'''),
    say("প্রতিটি শাখার জন্য গণনা আবার ১ থেকে শুরু।"))

c.lesson("প্রতি শাখার সেরা invoice",
    say("Window function সরাসরি WHERE-এ দেওয়া যায় না — আগে CTE (<code>WITH</code>)-এ হিসাব, তারপর বাইরে filter।"),
    sql('''
WITH ranked AS (
    SELECT branch_id, invoice_no, total,
           ROW_NUMBER() OVER (PARTITION BY branch_id ORDER BY total DESC) AS rn
    FROM sales
)
SELECT b.name AS branch, r.invoice_no, r.total
FROM ranked r
JOIN branches b ON b.id = r.branch_id
WHERE r.rn = 1;
'''),
    php_note("\"প্রতিটি customer-এর সর্বশেষ order\" — Laravel-এ <code>latestOfMany()</code> relationship ভিতরে এরকম query বানায়।"))

c.lesson("RANK বনাম DENSE_RANK",
    sql('''
SELECT p.name, SUM(si.qty) AS sold,
       ROW_NUMBER() OVER (ORDER BY SUM(si.qty) DESC) AS row_no,
       RANK()       OVER (ORDER BY SUM(si.qty) DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY SUM(si.qty) DESC) AS dense
FROM sale_items si
JOIN products p ON p.id = si.product_id
GROUP BY p.id, p.name
LIMIT 6;
'''),
    points("<code>ROW_NUMBER</code> — সমান হলেও আলাদা নম্বর", "<code>RANK</code> — সমানরা একই নম্বর, তারপর ফাঁক (১,১,৩)",
           "<code>DENSE_RANK</code> — সমানরা একই, ফাঁক নেই (১,১,২)"))

c.lesson("চলমান যোগফল আর আগের দিনের তুলনা",
    sql('''
WITH daily AS (
    SELECT DATE(sold_at) AS day, SUM(total) AS revenue
    FROM sales
    GROUP BY DATE(sold_at)
)
SELECT day,
       revenue,
       SUM(revenue) OVER (ORDER BY day)   AS running_total,
       revenue - LAG(revenue) OVER (ORDER BY day) AS vs_yesterday
FROM daily;
'''),
    points("<code>SUM() OVER (ORDER BY day)</code> — শুরু থেকে আজ পর্যন্ত যোগফল", "<code>LAG(revenue)</code> — আগের row-এর মান; <code>LEAD</code> পরের"))

# ================================================================== CTE
c.section("CTE")
c.lesson("Recursive CTE: খালি দিনও দেখানো",
    say("যে দিনে বিক্রি নেই, GROUP BY সেই দিন দেখায় না — chart-এ ফাঁক পড়ে। Recursive CTE দিয়ে সব তারিখ বানিয়ে LEFT JOIN করি।"),
    sql('''
WITH RECURSIVE days (day) AS (
    SELECT DATE('2026-10-14')
    UNION ALL
    SELECT day + INTERVAL 1 DAY FROM days WHERE day < '2026-10-21'
)
SELECT d.day,
       COUNT(s.id)             AS invoices,
       IFNULL(SUM(s.total), 0) AS revenue
FROM days d
LEFT JOIN sales s ON DATE(s.sold_at) = d.day
GROUP BY d.day
ORDER BY d.day;
'''))

# ================================================================== JSON
c.section("JSON ও Constraint")
c.lesson("JSON column",
    say("সব ফোনের spec এক রকম না — কিছু field ঐচ্ছিক। <code>JSON</code> column-এ নমনীয় data রাখা যায়, আবার query-ও করা যায়।"),
    sql('''
ALTER TABLE products ADD COLUMN specs JSON NULL;

UPDATE products SET specs = '{"ram": 8, "storage": 256, "colors": ["Black", "Green"]}' WHERE id = 2;
UPDATE products SET specs = '{"ram": 4, "storage": 128, "colors": ["Blue"]}'           WHERE id = 3;
UPDATE products SET specs = '{"ram": 4, "storage": 64,  "colors": ["Black"]}'          WHERE id = 4;

SELECT name,
       specs->>'$.ram'     AS ram_gb,
       specs->>'$.storage' AS storage_gb,
       JSON_LENGTH(specs->'$.colors') AS colors
FROM products
WHERE specs->>'$.ram' >= 4
ORDER BY name;
'''),
    laravel('''
protected $casts = ['specs' => 'array'];
Product::where('specs->ram', '>=', 4)->get();
Product::whereJsonContains('specs->colors', 'Black')->get();
'''))

c.lesson("Generated column: JSON-এর উপর index",
    say("JSON-এর ভিতরের মান দিয়ে প্রায়ই খুঁজলে সেটাকে <b>generated column</b> বানিয়ে index দিন।"),
    sql('''
ALTER TABLE products
    ADD COLUMN ram_gb TINYINT UNSIGNED AS (specs->>'$.ram') STORED,
    ADD INDEX products_ram_index (ram_gb);

SELECT name, ram_gb FROM products WHERE ram_gb = 4;
'''),
    php_note("Laravel migration: <code>$table-&gt;tinyInteger('ram_gb')-&gt;storedAs(\"specs-&gt;&gt;'$.ram'\")-&gt;index();</code>"))

c.lesson("CHECK constraint",
    say("MySQL 8 থেকে নিজের নিয়ম লেখা যায়: বিক্রির দাম কেনার দামের কম হবে না।"),
    sql("ALTER TABLE products ADD CONSTRAINT price_not_below_cost CHECK (price >= cost);"),
    sql("UPDATE products SET price = 100 WHERE name = 'Galaxy A15';", err="3819"))

c.lesson("Trigger: স্টক বদলালে log",
    say("Trigger হলো এমন কোড যা table-এ কিছু হলে database নিজেই চালায়। এখানে স্টক বদলালেই একটা log row।"),
    sql('''
CREATE TABLE stock_logs (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_id INT UNSIGNED NOT NULL,
    old_stock  INT UNSIGNED NOT NULL,
    new_stock  INT UNSIGNED NOT NULL,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER products_stock_log AFTER UPDATE ON products
FOR EACH ROW
INSERT INTO stock_logs (product_id, old_stock, new_stock)
SELECT NEW.id, OLD.stock, NEW.stock FROM DUAL WHERE OLD.stock <> NEW.stock;

UPDATE products SET stock = stock + 10 WHERE id = 6;
UPDATE products SET price = price WHERE id = 7;    -- স্টক বদলায়নি: log হবে না
SELECT product_id, old_stock, new_stock FROM stock_logs;
'''),
    php_note("Laravel-এ সাধারণত Model event/Observer (<code>updated()</code>) দিয়ে এই কাজ করা হয়। Trigger সব জায়গা থেকে আসা UPDATE ধরে — এমনকি হাতে চালানো SQL-ও।"))

c.lesson("Full-text search",
    say("<code>LIKE '%word%'</code> বড় table-এ ধীর। <code>FULLTEXT</code> index আর <code>MATCH ... AGAINST</code> শব্দ ধরে খোঁজে, প্রাসঙ্গিকতা অনুযায়ী সাজায়।"),
    sql('''
ALTER TABLE products ADD FULLTEXT INDEX products_name_fulltext (name, brand);

SELECT name, brand
FROM products
WHERE MATCH (name, brand) AGAINST ('redmi xiaomi' IN NATURAL LANGUAGE MODE);
'''),
    laravel("Product::whereFullText(['name', 'brand'], 'redmi xiaomi')->get();"),
    tip("বড় app-এ Laravel Scout + Meilisearch/Typesense ভালো — typo সহ্য করে, বাংলাও খোঁজে।"))

# ================================================================== ops
c.section("নিরাপত্তা ও Performance")
c.lesson("App-এর জন্য আলাদা user",
    say("Laravel app কখনো <code>root</code> দিয়ে চালাবেন না। শুধু ঐ database-এ, শুধু দরকারি অনুমতি দিয়ে user বানান।"),
    shell("mysql> CREATE USER 'shop_app'@'localhost' IDENTIFIED BY 'a-long-random-password';\n"
          "mysql> GRANT SELECT, INSERT, UPDATE, DELETE ON shop.* TO 'shop_app'@'localhost';\n"
          "mysql> -- migration চালানোর জন্য আলাদা user-কে CREATE, ALTER, INDEX, DROP দিন\n"
          "mysql> SHOW GRANTS FOR 'shop_app'@'localhost';"),
    code("DB_USERNAME=shop_app\nDB_PASSWORD=a-long-random-password", "ini", run=False, file=".env"))

c.lesson("ধীর query খুঁজে বের করা",
    say("Slow query log চালু করলে নির্দিষ্ট সময়ের বেশি লাগা query file-এ লেখা হয়। তারপর সেগুলো <code>EXPLAIN</code> দিয়ে দেখুন।"),
    shell("mysql> SET GLOBAL slow_query_log = 'ON';\nmysql> SET GLOBAL long_query_time = 0.5;   -- ০.৫ সেকেন্ডের বেশি\nmysql> SHOW VARIABLES LIKE 'slow_query_log_file';"),
    table(["সমস্যা", "সমাধান"], [
        ["WHERE/JOIN column-এ index নেই", "Index যোগ করুন (EXPLAIN-এ table scan)"],
        ["<code>SELECT *</code> বড় TEXT/JSON সহ", "দরকারি column বাছুন"],
        ["Column-এ function (<code>DATE()</code>, <code>LOWER()</code>)", "Range শর্ত বা generated column"],
        ["অনেক বড় OFFSET (পাতা ১০০০০)", "Keyset/cursor pagination (MySQL for Laravel)"],
        ["Loop-এ query (N+1)", "JOIN বা eager loading"]]),
    php_note("Laravel Telescope / Debugbar প্রতিটি request-এর query আর সময় দেখায় — ধীর query ধরার সহজ উপায়।"))

c.finish("MySQL 103 শেষ! 🎉",
         "Index, transaction আর window function — production database চালানোর আসল হাতিয়ার এখন আপনার। শেষ কোর্সে এগুলো Laravel-এর ভিতরে বসাব।",
         recap=["<code>EXPLAIN</code>: table scan দেখলেই index ভাবুন",
                "Composite index বাম দিক থেকে কাজ করে; column-এ function দেবেন না",
                "টাকা-স্টকের একাধিক কাজ = একটা transaction",
                "একই row দুইজন বদলালে <code>FOR UPDATE</code> / <code>lockForUpdate()</code>",
                "Window function: র‍্যাংক, চলমান যোগফল, আগের দিনের তুলনা",
                "JSON + generated column, CHECK, trigger, full-text"])

if __name__ == "__main__":
    c.build()
