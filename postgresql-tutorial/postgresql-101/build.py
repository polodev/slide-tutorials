"""PostgreSQL 101 — psql, types, CRUD with RETURNING, filtering, functions, MySQL differences.
Every query runs on a private PostgreSQL 16 cluster started by the kit. Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402


def sql(src, **kw):
    return code(src, "postgresql", **kw)


def laravel(src, label="Laravel-এ"):
    return code(src, "php", run=False, label=label)


c = Course(slug="postgresql-101", title="PostgreSQL 101 — শূন্য থেকে শুরু", folder=Path(__file__).parent,
           subtitle="psql, data type, CRUD আর RETURNING, ILIKE, তারিখ — আর MySQL থেকে কোথায় আলাদা",
           series="PostgreSQL 101", sql_engine="postgresql",
           next_course=("../postgresql-102/index.html", "PostgreSQL 102 — JOIN ও PostgreSQL-এর বিশেষ কৌশল"))

c.cover("PostgreSQL 101<br>শূন্য থেকে শুরু",
        "PostgreSQL পৃথিবীর সবচেয়ে উন্নত open-source database — কঠোর নিয়ম, শক্তিশালী type, JSON, full-text search সব ভিতরেই। Laravel-ও এর সাথে চমৎকার চলে।",
        learn=["PostgreSQL কেন, MySQL-এর সাথে পার্থক্য", "psql আর \\d কমান্ড", "Identity, text, numeric, boolean, timestamp",
               "INSERT ... RETURNING", "WHERE, ILIKE, IN, NULL", "UPDATE/DELETE আর RETURNING",
               "Constraint আর ALTER TABLE", "String আর তারিখের function"],
        need="কিছুই না। MySQL জানলে তুলনাগুলো বাড়তি সুবিধা।")

# ================================================================== start
c.section("শুরু")
c.lesson("PostgreSQL কেন?",
    table(["", "MySQL", "PostgreSQL"], [
        ["নিয়ম", "কিছু ক্ষেত্রে ছাড় দেয়", "কঠোর — ভুল type বা ভুল GROUP BY সাথে সাথে error"],
        ["বিশেষ type", "JSON", "JSONB, array, UUID, range, enum, geometry"],
        ["Index", "B-tree, full-text", "B-tree, GIN, GiST, BRIN, partial, expression"],
        ["নতুন id ফেরত", "<code>LAST_INSERT_ID()</code>", "<code>RETURNING id</code>"],
        ["কোথায় দেখবেন", "শেয়ার্ড hosting, WordPress", "Supabase, Neon, Heroku, অনেক SaaS"]]),
    php_note("Laravel দুটোই সমর্থন করে — <code>.env</code>-এ <code>DB_CONNECTION=pgsql</code> দিলেই হয়। পার্থক্যগুলো এই কোর্সে আর PostgreSQL for Laravel-এ।"))

c.lesson("Install আর psql",
    points("<b>macOS:</b> Postgres.app অথবা <code>brew install postgresql@16</code>", "<b>Windows:</b> EDB installer (pgAdmin সাথে আসে)",
           "<b>Ubuntu:</b> <code>sudo apt install postgresql</code>", "অথবা Docker: <code>docker run -e POSTGRES_PASSWORD=secret -p 5432:5432 postgres:16</code>"),
    shell("$ psql -U postgres\npostgres=# CREATE DATABASE shop;\npostgres=# \\c shop\nshop=# SELECT version();"),
    tip("এই কোর্সের প্রতিটি query আসল PostgreSQL 16-এ চালিয়ে ফলাফল বসানো।"))

c.lesson("psql-এর ছোট কমান্ড",
    say("<code>\\</code> দিয়ে শুরু কমান্ডগুলো psql-এর নিজের (SQL না)। সবচেয়ে কাজের কয়েকটা:"),
    table(["কমান্ড", "কাজ", "MySQL-এ"], [
        ["<code>\\l</code>", "সব database", "<code>SHOW DATABASES</code>"], ["<code>\\c shop</code>", "database বদলানো", "<code>USE shop</code>"],
        ["<code>\\dt</code>", "সব table", "<code>SHOW TABLES</code>"], ["<code>\\d products</code>", "table-এর গঠন", "<code>DESCRIBE products</code>"],
        ["<code>\\x</code>", "লম্বা row লম্বালম্বি দেখানো", "<code>\\G</code>"], ["<code>\\q</code>", "বের হওয়া", "<code>exit</code>"]]),
    sql("SELECT 2 + 3 AS total, now() > '2020-01-01' AS is_after_2020, 'Assalamu Alaikum' AS greeting;"))

# ================================================================== table
c.section("Table")
c.lesson("CREATE TABLE: identity column",
    say("PostgreSQL-এ auto-increment-এর আধুনিক উপায় <code>GENERATED ALWAYS AS IDENTITY</code> (পুরনো <code>serial</code>-ও চলে)। লেখার জন্য সাধারণত <code>text</code> — দৈর্ঘ্যের সীমা না দিলেও চলে, গতিতেও পার্থক্য নেই।"),
    sql('''
CREATE TABLE customers (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       text NOT NULL,
    phone      varchar(15) NOT NULL,
    district   text,
    created_at timestamp NOT NULL DEFAULT now()
);
'''),
    sql("\\d customers"),
    laravel("$table->id();   // pgsql-এ: bigserial primary key"))

c.lesson("Data type বেছে নেওয়া",
    table(["কী রাখবেন", "PostgreSQL", "MySQL-এ ছিল"], [
        ["id", "<code>bigint ... IDENTITY</code>", "<code>BIGINT AUTO_INCREMENT</code>"],
        ["টাকা", "<code>numeric(12,2)</code>", "<code>DECIMAL(12,2)</code>"],
        ["লেখা", "<code>text</code> / <code>varchar(n)</code>", "<code>VARCHAR</code>, <code>TEXT</code>"],
        ["হ্যাঁ/না", "<code>boolean</code> (আসল true/false)", "<code>TINYINT(1)</code>"],
        ["সময়", "<code>timestamptz</code> (timezone সহ — সুপারিশকৃত)", "<code>DATETIME</code>/<code>TIMESTAMP</code>"],
        ["আলাদা পরিচয়", "<code>uuid</code>", "<code>CHAR(36)</code>"], ["নমনীয় data", "<code>jsonb</code>", "<code>JSON</code>"],
        ["তালিকা", "<code>text[]</code> (array)", "—"]]),
    warn("PostgreSQL-এ <code>unsigned</code> নেই। ঋণাত্মক আটকাতে <code>CHECK (stock &gt;= 0)</code> দিন।"))

c.lesson("products table",
    sql('''
CREATE TABLE products (
    id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name      text NOT NULL,
    brand     text NOT NULL,
    price     numeric(10,2) NOT NULL,
    stock     integer NOT NULL DEFAULT 0 CHECK (stock >= 0),
    is_used   boolean NOT NULL DEFAULT false
);
'''),
    php_note("Laravel-এর <code>$table-&gt;boolean('is_used')</code> pgsql-এ আসল <code>boolean</code> হয় — query-তে <code>where('is_used', true)</code>।"))

# ================================================================== insert/select
c.section("INSERT ও SELECT")
c.lesson("INSERT ... RETURNING",
    say("<code>RETURNING</code> দিলে নতুন row-এর id (বা যেকোনো column) সাথে সাথে ফেরত আসে — আলাদা query লাগে না।"),
    sql('''
INSERT INTO customers (name, phone, district)
VALUES ('Karim Uddin', '01711000001', 'Dhaka')
RETURNING id, name, created_at::date AS joined;
'''),
    php_note("Laravel-এর <code>insertGetId()</code> pgsql-এ ভিতরে <code>RETURNING id</code>-ই ব্যবহার করে।"))

c.lesson("একসাথে অনেক row",
    sql('''
INSERT INTO customers (name, phone, district) VALUES
    ('Nusrat Jahan', '01811000002', 'Sylhet'),
    ('Rahim Mia',    '01911000003', 'Khulna'),
    ('Sadia Islam',  '01611000004', 'Dhaka'),
    ('Tanvir Hasan', '01511000005', NULL);

INSERT INTO products (name, brand, price, stock, is_used) VALUES
    ('Redmi 13',       'Xiaomi',  17500, 5, false),
    ('Redmi Note 13',  'Xiaomi',  23500, 2, false),
    ('Galaxy A15',     'Samsung', 21000, 0, false),
    ('Galaxy S21',     'Samsung', 32000, 1, true),
    ('iPhone 12',      'Apple',   48000, 2, true),
    ('Vivo Y28',       'Vivo',    18000, 4, false),
    ('Walton NEXG N9', 'Walton',   9990, 7, false),
    ('Charger 20W',    'Anker',     650, 30, false);
'''),
    say("আউটপুট <code>INSERT 0 4</code>: শেষ সংখ্যাটা কয়টা row ঢুকল।"))

c.lesson("SELECT",
    sql("SELECT name, brand, price FROM products ORDER BY price DESC LIMIT 4;"),
    sql("SELECT * FROM customers;"))

# ================================================================== filter
c.section("খোঁজা")
c.lesson("WHERE আর boolean",
    sql("SELECT name, price FROM products WHERE brand = 'Xiaomi' AND price < 20000;"),
    sql("SELECT name, brand FROM products WHERE is_used;            -- = true লিখতে হয় না"),
    sql("SELECT name, brand FROM products WHERE NOT is_used AND stock > 5;"))

c.lesson("LIKE বনাম ILIKE",
    say("PostgreSQL-এ <code>LIKE</code> ছোট-বড় হাতের অক্ষর <b>আলাদা ধরে</b> (MySQL ধরে না)। ছোট-বড় না মানতে <code>ILIKE</code>।"),
    sql("SELECT name FROM products WHERE name LIKE 'redmi%';"),
    sql("SELECT name FROM products WHERE name ILIKE 'redmi%';"),
    warn("MySQL থেকে Laravel app সরালে search হঠাৎ কাজ না করার সবচেয়ে বড় কারণ এটা। Laravel-এ <code>where('name', 'ilike', ...)</code> অথবা <code>whereLike(..., caseSensitive: false)</code>।"))

c.lesson("IN, BETWEEN, NULL",
    sql("SELECT name, brand FROM products WHERE brand IN ('Samsung', 'Vivo');"),
    sql("SELECT name, price FROM products WHERE price BETWEEN 15000 AND 25000;"),
    sql("SELECT name, COALESCE(district, 'জানা নেই') AS district FROM customers WHERE district IS NULL;"),
    php_note("<code>COALESCE(a, b)</code> হলো PHP-র <code>$a ?? $b</code> — SQL standard, MySQL-এও চলে (<code>IFNULL</code>-এর বদলে এটাই অভ্যাস করুন)।"))

c.lesson("হিসাব, CASE আর type cast",
    say("<code>::</code> দিয়ে type বদলানো যায়: <code>price::int</code>, <code>'2026-10-21'::date</code>।"),
    sql('''
SELECT name,
       price * stock                    AS stock_value,
       round(price * 1.15, 2)           AS with_vat,
       brand || ' — ' || name           AS label,
       CASE WHEN stock = 0 THEN 'শেষ'
            WHEN stock <= 2 THEN 'কম'
            ELSE 'আছে' END              AS status
FROM products
ORDER BY stock_value DESC;
'''),
    tip("<code>||</code> দিয়ে লেখা জোড়া লাগে (MySQL-এ <code>CONCAT</code>)। PostgreSQL-এ <code>concat()</code>-ও আছে, যেটা NULL পেলে বাদ দেয়।"))

c.lesson("Type নিয়ে কঠোরতা",
    say("MySQL অনেক সময় নীরবে type বদলে নেয়। PostgreSQL সোজা error দেয় — ভুল আগেই ধরা পড়ে।"),
    sql("SELECT name FROM products WHERE price = 'free';", err="invalid input syntax"),
    sql("SELECT 'Stock: ' || 5 AS ok, 7 / 2 AS int_div, 7 / 2.0 AS decimal_div;"),
    quiz("<code>7 / 2</code> কেন ৩?", "দুটোই integer, তাই integer ভাগ — দশমিক চাইলে একটাকে numeric দিন: <code>7 / 2.0</code> বা <code>7::numeric / 2</code>।"))

# ================================================================== change
c.section("বদলানো ও মোছা")
c.lesson("UPDATE ... RETURNING",
    sql("UPDATE products SET stock = stock + 10 WHERE brand = 'Xiaomi'\nRETURNING name, stock;"),
    say("কী বদলাল সেটা সাথে সাথে দেখা যায় — আলাদা SELECT লাগে না।"))

c.lesson("DELETE ... RETURNING",
    sql("DELETE FROM customers WHERE district IS NULL\nRETURNING id, name;"),
    tip("হাতে UPDATE/DELETE চালানোর আগে <code>BEGIN;</code> দিন, ফলাফল দেখে <code>COMMIT;</code> বা <code>ROLLBACK;</code>। psql-এ এটা খুব সহজ।"))

c.lesson("CHECK constraint কাজ করছে",
    sql("UPDATE products SET stock = stock - 5 WHERE name = 'Galaxy S21';", err="check constraint"),
    say("স্টক ১ থেকে ৫ কমালে ঋণাত্মক হতো — table বানানোর সময় দেওয়া <code>CHECK</code> আটকে দিল।"))

c.lesson("UNIQUE আর NOT NULL",
    sql("ALTER TABLE customers ADD CONSTRAINT customers_phone_unique UNIQUE (phone);"),
    sql("INSERT INTO customers (name, phone) VALUES ('Another Karim', '01711000001');", err="duplicate key"),
    sql("INSERT INTO customers (name, phone) VALUES ('Mitu', NULL);", err="null value"))

c.lesson("ALTER TABLE",
    sql('''
ALTER TABLE customers ADD COLUMN due numeric(10,2) NOT NULL DEFAULT 0;
ALTER TABLE customers ALTER COLUMN district SET DEFAULT 'Dhaka';
ALTER TABLE customers RENAME COLUMN district TO city;
UPDATE customers SET due = 1500 WHERE name = 'Rahim Mia';
SELECT name, city, due FROM customers ORDER BY id;
'''),
    tip("PostgreSQL-এ DDL (ALTER, CREATE) transaction-এর ভিতরে চলে — migration মাঝপথে ভাঙলে পুরোটা ফিরে যায়। MySQL-এ এটা হয় না।"))

# ================================================================== functions
c.section("Function")
c.lesson("String function আর বাংলা",
    sql('''
INSERT INTO customers (name, phone, city) VALUES ('রাশেদ খান', '01311000006', 'রাজশাহী');

SELECT name,
       length(name)        AS chars,
       octet_length(name)  AS bytes,
       upper(name)         AS upper_name,
       left(phone, 3)      AS operator
FROM customers
ORDER BY id;
'''),
    php_note("PostgreSQL-এ <code>length()</code> অক্ষর গোনে (PHP-র <code>mb_strlen</code>), byte গুনতে <code>octet_length()</code> — MySQL-এর উল্টো।"))

c.lesson("তারিখ আর সময়",
    sql('''
SELECT date '2026-10-21' + 7                          AS plus_7_days,
       date '2026-12-16' - date '2026-10-21'          AS days_to_victory_day,
       to_char(date '2026-10-21', 'DD/MM/YYYY')        AS bd_format,
       date_trunc('month', timestamp '2026-10-21 15:30') AS month_start,
       extract(dow FROM date '2026-10-23')            AS weekday_no,
       age(date '2026-10-21', date '1971-12-16')      AS bangladesh_age;
'''),
    table(["PostgreSQL", "MySQL", "Carbon"], [
        ["<code>now()</code>, <code>current_date</code>", "<code>NOW()</code>, <code>CURDATE()</code>", "<code>now()</code>"],
        ["<code>d + interval '7 days'</code>", "<code>DATE_ADD(d, INTERVAL 7 DAY)</code>", "<code>addDays(7)</code>"],
        ["<code>date_trunc('month', t)</code>", "<code>DATE_FORMAT(t, '%Y-%m-01')</code>", "<code>startOfMonth()</code>"]]))

c.lesson("timestamp বনাম timestamptz",
    say("<code>timestamptz</code> সময়কে UTC-তে রাখে আর দেখানোর সময় session-এর timezone-এ বদলায়। Bangladesh (UTC+6) থেকে দেখলে ঠিক স্থানীয় সময়।"),
    sql('''
SET timezone = 'Asia/Dhaka';
SELECT timestamptz '2026-10-21 10:00:00+00' AS utc_10am_in_dhaka;

SET timezone = 'UTC';
SELECT timestamptz '2026-10-21 10:00:00+00' AS same_moment_in_utc;
'''),
    php_note("Laravel-এ <code>$table-&gt;timestampsTz()</code> আর <code>config/app.php</code>-এর <code>timezone</code>। একাধিক দেশের user হলে সবসময় timestamptz।"))

c.lesson("Project: দোকানের প্রশ্ন",
    sql('''
SELECT brand || ' ' || name AS phone,
       price,
       stock
FROM products
WHERE NOT is_used
  AND stock > 0
  AND price < 20000
  AND name NOT ILIKE 'charger%'
ORDER BY price;
'''),
    task("লিখুন: (১) used ফোনের মোট স্টক-মূল্য; (২) যাদের বাকি ১০০০-এর বেশি তাদের নাম আর বাকি, <code>RETURNING</code> দিয়ে বাকি ১০% কমিয়ে দিন।"))

c.lesson("Backup আর restore",
    shell("$ pg_dump -Fc shop > shop.dump\n$ createdb shop_copy\n$ pg_restore -d shop_copy shop.dump"),
    points("<code>-Fc</code> — compressed custom format; <code>pg_restore</code> দিয়ে বাছাই করে restore করা যায়",
           "শুধু SQL চাইলে: <code>pg_dump shop &gt; shop.sql</code>", "শুধু গঠন: <code>pg_dump --schema-only</code>"))

c.finish("PostgreSQL 101 শেষ! 🎉",
         "Table, type আর CRUD হলো। এবার অনেক table জুড়ে কাজ — আর PostgreSQL-এর নিজস্ব কৌশল যেগুলো MySQL-এ নেই।",
         recap=["Identity column, <code>text</code>, <code>numeric</code>, আসল <code>boolean</code>",
                "<code>RETURNING</code> — INSERT/UPDATE/DELETE-এর ফল সাথে সাথে",
                "<code>LIKE</code> case-sensitive; <code>ILIKE</code> না",
                "কঠোর type, <code>::</code> দিয়ে cast", "<code>CHECK</code> দিয়ে নিজের নিয়ম",
                "<code>length()</code> অক্ষর গোনে; সময়ের জন্য <code>timestamptz</code>"])

if __name__ == "__main__":
    c.build()
