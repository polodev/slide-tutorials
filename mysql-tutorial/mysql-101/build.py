"""MySQL 101 — table, CRUD, filtering, functions. Every query runs on a real MySQL 8 database
(one fresh database per course; blocks run in order). Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402


def sql(src, **kw):
    return code(src, "mysql", **kw)


def laravel(src, label="Laravel-এ"):
    return code(src, "php", run=False, label=label)


c = Course(slug="mysql-101", title="MySQL 101 — শূন্য থেকে শুরু", folder=Path(__file__).parent,
           subtitle="Table বানানো, data রাখা, খোঁজা, বদলানো আর মোছা — Laravel-এর Eloquent পাশে রেখে",
           series="MySQL 101", sql_engine="mysql",
           next_course=("../mysql-102/index.html", "MySQL 102 — Relationship ও JOIN"))

c.cover("MySQL 101<br>শূন্য থেকে শুরু",
        "Laravel-এ Eloquent দিয়ে কাজ করেন, কিন্তু ভিতরে আসলে কী SQL চলে? এই কোর্সে একটা মোবাইল দোকানের database দিয়ে SQL হাতে-কলমে শিখব।",
        learn=["Database, table, row, column", "CREATE TABLE আর data type", "INSERT, SELECT, UPDATE, DELETE",
               "WHERE, LIKE, IN, BETWEEN, NULL", "ORDER BY আর LIMIT", "NOT NULL, UNIQUE, DEFAULT",
               "String, date আর number function", "বাংলা লেখা ঠিকভাবে রাখা (utf8mb4)"],
        need="কিছুই না। Laravel জানলে তুলনাগুলো বাড়তি সুবিধা।")

# ================================================================== start
c.section("শুরু")
c.lesson("Database আসলে কী?",
    say("Database হলো সাজানো data-র ভাণ্ডার। MySQL-এ data থাকে <b>table</b>-এ — Excel sheet-এর মতো: প্রতিটি <b>row</b> একটা জিনিস, প্রতিটি <b>column</b> একটা তথ্য।"),
    table(["id", "name", "phone", "district"], [
        ["1", "Karim", "01711000001", "Dhaka"], ["2", "Nusrat", "01811000002", "Sylhet"], ["3", "Rahim", "01911000003", "Khulna"]]),
    php_note("Laravel-এর একটা <b>Model</b> (<code>Customer</code>) মানে একটা <b>table</b> (<code>customers</code>), আর একটা object মানে একটা row।"))

c.lesson("MySQL install আর connect",
    points("<b>Windows:</b> Laragon বা XAMPP — MySQL সাথেই আসে", "<b>macOS:</b> <code>brew install mysql</code> অথবা Laravel Herd Pro / DBngin",
           "<b>Ubuntu:</b> <code>sudo apt install mysql-server</code>", "GUI চাইলে: TablePlus, DBeaver, phpMyAdmin"),
    shell("$ mysql -u root -p\nmysql> SELECT VERSION();", out="+-----------+\n| VERSION() |\n+-----------+\n| 8.0.43    |\n+-----------+"),
    tip("এই কোর্সের প্রতিটি query আসল MySQL 8-এ চালিয়ে ফলাফল বসানো হয়েছে। আপনিও terminal বা TablePlus-এ কপি করে চালান।"))

c.lesson("প্রথম query",
    say("SQL-এ <code>SELECT</code> মানে \"দেখাও\"। Table ছাড়াও হিসাব করা যায়। প্রতিটি statement-এর শেষে <code>;</code>।"),
    sql("SELECT 2 + 3 AS total, NOW() > '2020-01-01' AS is_after_2020, 'Hello, World!' AS greeting;"),
    points("<code>AS</code> দিয়ে column-এর নাম দেওয়া যায়", "SQL keyword ছোট-বড় হাতের যেকোনো অক্ষরে লেখা যায়; বড় হাতের অক্ষরে লেখা প্রচলিত"),
    php_note("Laravel-এ <code>DB::select('SELECT 2 + 3 AS total')</code> দিয়ে সরাসরি SQL চালানো যায়।"))

c.lesson("Database বানানো",
    say("একটা app-এর সব table একটা database-এ থাকে। বাংলা লেখার জন্য character set অবশ্যই <code>utf8mb4</code>।"),
    shell("mysql> CREATE DATABASE shop CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;\nmysql> SHOW DATABASES;\nmysql> USE shop;"),
    php_note("Laravel-এর <code>.env</code>-এ <code>DB_DATABASE=shop</code> — database আগে নিজে বানিয়ে নিতে হয়, তারপর <code>php artisan migrate</code>।"),
    warn("পুরনো <code>utf8</code> (utf8mb3) emoji রাখতে পারে না। সবসময় <code>utf8mb4</code> — Laravel-এর ডিফল্টও এটাই।"))

# ================================================================== table
c.section("Table")
c.lesson("CREATE TABLE: প্রথম table",
    say("প্রতিটি column-এর নাম আর type বলতে হয়। <code>id</code> হলো <b>PRIMARY KEY</b> — প্রতিটি row-এর আলাদা পরিচয়, <code>AUTO_INCREMENT</code> নিজেই ১, ২, ৩ বসায়।"),
    sql('''
CREATE TABLE customers (
    id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    phone      VARCHAR(15)  NOT NULL,
    district   VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
'''),
    laravel('''
Schema::create('customers', function (Blueprint $table) {
    $table->id();
    $table->string('name', 100);
    $table->string('phone', 15);
    $table->string('district', 50)->nullable();
    $table->timestamps();
});
''', "Laravel migration-এ"))

c.lesson("DESCRIBE: table-এর গঠন দেখা",
    sql("DESCRIBE customers;"),
    points("<code>Null</code> — খালি রাখা যাবে কিনা", "<code>Key: PRI</code> — primary key", "<code>Extra</code> — auto_increment ইত্যাদি"),
    tip("<code>SHOW CREATE TABLE customers;</code> দিলে পুরো CREATE statement দেখায় — অন্য জায়গায় একই table বানাতে কাজে লাগে।"))

c.lesson("Data type বেছে নেওয়া",
    table(["কী রাখবেন", "Type", "Laravel migration"], [
        ["id, পরিমাণ", "<code>INT</code> / <code>BIGINT UNSIGNED</code>", "<code>id()</code>, <code>integer()</code>"],
        ["টাকা", "<code>DECIMAL(12,2)</code> — কখনো FLOAT না", "<code>decimal('price', 12, 2)</code>"],
        ["নাম, ফোন", "<code>VARCHAR(n)</code>", "<code>string()</code>"],
        ["বড় লেখা", "<code>TEXT</code>", "<code>text()</code>"],
        ["হ্যাঁ/না", "<code>BOOLEAN</code> (আসলে <code>TINYINT(1)</code>)", "<code>boolean()</code>"],
        ["তারিখ / সময়", "<code>DATE</code>, <code>DATETIME</code>, <code>TIMESTAMP</code>", "<code>date()</code>, <code>timestamps()</code>"],
        ["নির্দিষ্ট কয়েকটা মান", "<code>ENUM('new','used')</code>", "<code>enum()</code>"]]),
    warn("ফোন নম্বর number না, <code>VARCHAR</code> — শুরুর <code>0</code> হারিয়ে যাবে নইলে (<code>01711...</code> → <code>1711...</code>)।"))

c.lesson("products table",
    say("এই table-টা পুরো কোর্সে ব্যবহার করব। দামের জন্য <code>DECIMAL</code>, অবস্থার জন্য <code>ENUM</code>।"),
    sql('''
CREATE TABLE products (
    id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    brand     VARCHAR(50)  NOT NULL,
    price     DECIMAL(10,2) NOT NULL,
    stock     INT UNSIGNED NOT NULL DEFAULT 0,
    condition_type ENUM('new', 'used') NOT NULL DEFAULT 'new'
);
'''))

# ================================================================== insert/select
c.section("INSERT ও SELECT")
c.lesson("INSERT: data রাখা",
    say("Column-এর নাম দিয়ে মান দিই। <code>id</code> দিতে হয় না — AUTO_INCREMENT নিজেই বসায়।"),
    sql('''
INSERT INTO customers (name, phone, district)
VALUES ('Karim Uddin', '01711000001', 'Dhaka');
'''),
    laravel("Customer::create(['name' => 'Karim Uddin', 'phone' => '01711000001', 'district' => 'Dhaka']);"))

c.lesson("একসাথে অনেক row",
    say("একটা <code>INSERT</code>-এ কমা দিয়ে অনেক row — অনেক দ্রুত।"),
    sql('''
INSERT INTO customers (name, phone, district) VALUES
    ('Nusrat Jahan', '01811000002', 'Sylhet'),
    ('Rahim Mia',    '01911000003', 'Khulna'),
    ('Sadia Islam',  '01611000004', 'Dhaka'),
    ('Tanvir Hasan', '01511000005', NULL);

INSERT INTO products (name, brand, price, stock, condition_type) VALUES
    ('Redmi 13',        'Xiaomi',  17500.00, 5, 'new'),
    ('Redmi Note 13',   'Xiaomi',  23500.00, 2, 'new'),
    ('Galaxy A15',      'Samsung', 21000.00, 0, 'new'),
    ('Galaxy S21',      'Samsung', 32000.00, 1, 'used'),
    ('iPhone 12',       'Apple',   48000.00, 2, 'used'),
    ('Vivo Y28',        'Vivo',    18000.00, 4, 'new'),
    ('Walton NEXG N9',  'Walton',   9990.00, 7, 'new'),
    ('Charger 20W',     'Anker',     650.00, 30, 'new');
'''),
    laravel("Product::insert([...]);   // অথবা DB::table('products')->insert([...])"))

c.lesson("SELECT: সব দেখা",
    sql("SELECT * FROM customers;"),
    php_note("<code>Customer::all()</code> ভিতরে ঠিক এই query-টাই চালায়।"))

c.lesson("শুধু দরকারি column",
    say("<code>*</code> না দিয়ে column-এর নাম দিন — কম data আসে, query দ্রুত হয়।"),
    sql("SELECT name, brand, price FROM products;"),
    php_note("<code>Product::select('name', 'brand', 'price')-&gt;get()</code>"))

# ================================================================== filter
c.section("খোঁজা ও সাজানো")
c.lesson("WHERE: শর্ত দিয়ে খোঁজা",
    say("<code>=</code>, <code>&lt;&gt;</code> (সমান না), <code>&gt;</code>, <code>&lt;=</code> — আর একাধিক শর্ত <code>AND</code> / <code>OR</code> দিয়ে।"),
    sql("SELECT name, price, stock FROM products\nWHERE brand = 'Xiaomi' AND price < 20000;"),
    sql("SELECT name, brand FROM products\nWHERE brand = 'Apple' OR condition_type = 'used';"),
    laravel("Product::where('brand', 'Xiaomi')->where('price', '<', 20000)->get();"))

c.lesson("LIKE: অংশ মিলিয়ে খোঁজা",
    say("<code>%</code> মানে \"যেকোনো কিছু\"। <code>'Redmi%'</code> = Redmi দিয়ে শুরু, <code>'%13'</code> = 13 দিয়ে শেষ, <code>'%Note%'</code> = মাঝে কোথাও।"),
    sql("SELECT name FROM products WHERE name LIKE 'Redmi%';"),
    sql("SELECT name, phone FROM customers WHERE phone LIKE '017%';"),
    tip("ডিফল্ট collation-এ (<code>_ai_ci</code>) ছোট-বড় হাতের অক্ষর আলাদা ধরে না — <code>'redmi%'</code> দিলেও মিলবে।"))

c.lesson("IN আর BETWEEN",
    say("<code>IN (...)</code> — তালিকার যেকোনো একটা। <code>BETWEEN a AND b</code> — a থেকে b (দুটোই সহ)।"),
    sql("SELECT name, brand FROM products WHERE brand IN ('Samsung', 'Vivo');"),
    sql("SELECT name, price FROM products WHERE price BETWEEN 15000 AND 25000;"),
    laravel("Product::whereIn('brand', ['Samsung', 'Vivo'])->get();\nProduct::whereBetween('price', [15000, 25000])->get();"))

c.lesson("NULL: \"জানা নেই\"",
    say("<code>NULL</code> মানে মান নেই। এটা <code>=</code> দিয়ে খোঁজা যায় না — লিখতে হয় <code>IS NULL</code> / <code>IS NOT NULL</code>।"),
    sql("SELECT name FROM customers WHERE district = NULL;   -- ভুল: কিছুই আসবে না"),
    sql("SELECT name FROM customers WHERE district IS NULL;"),
    sql("SELECT name, IFNULL(district, 'জানা নেই') AS district FROM customers;"),
    php_note("<code>IFNULL(district, '...')</code> হলো PHP-র <code>$district ?? '...'</code>। Laravel-এ <code>whereNull('district')</code>।"))

c.lesson("ORDER BY আর LIMIT",
    say("<code>ORDER BY</code> দিয়ে সাজাই (<code>ASC</code> ছোট→বড়, <code>DESC</code> বড়→ছোট)। <code>LIMIT</code> কয়টা দেখাবে, <code>OFFSET</code> কয়টা বাদ দিয়ে শুরু।"),
    sql("SELECT name, price FROM products ORDER BY price DESC LIMIT 3;"),
    sql("SELECT name, price FROM products ORDER BY price DESC LIMIT 3 OFFSET 3;   -- দ্বিতীয় পাতা"),
    laravel("Product::orderByDesc('price')->limit(3)->get();\nProduct::orderByDesc('price')->paginate(3);   // LIMIT/OFFSET নিজেই করে"))

c.lesson("হিসাব করা column",
    say("SELECT-এ সরাসরি হিসাব করা যায়। নতুন column-এর নাম দিই <code>AS</code> দিয়ে।"),
    sql('''
SELECT name,
       price,
       stock,
       price * stock               AS stock_value,
       ROUND(price * 1.15, 2)      AS price_with_vat,
       CONCAT(brand, ' — ', name)  AS label
FROM products
WHERE stock > 0
ORDER BY stock_value DESC;
'''))

c.lesson("DISTINCT আর COUNT",
    sql("SELECT DISTINCT brand FROM products ORDER BY brand;"),
    sql("SELECT COUNT(*) AS total_products, COUNT(DISTINCT brand) AS brands FROM products;"),
    php_note("<code>Product::distinct()-&gt;pluck('brand')</code> আর <code>Product::count()</code>। গ্রুপ ধরে গোনা (<code>GROUP BY</code>) আছে MySQL 102-এ।"))

c.lesson("CASE: শর্ত অনুযায়ী মান",
    say("<code>CASE WHEN ... THEN ... ELSE ... END</code> — SQL-এর if/else।"),
    sql('''
SELECT name, stock,
       CASE
           WHEN stock = 0 THEN 'শেষ'
           WHEN stock <= 2 THEN 'কম'
           ELSE 'আছে'
       END AS stock_status
FROM products
ORDER BY stock;
'''),
    php_note("PHP-র <code>match(true) { $stock === 0 =&gt; 'শেষ', ... }</code> এর মতো।"))

# ================================================================== change data
c.section("বদলানো ও মোছা")
c.lesson("UPDATE: মান বদলানো",
    say("<code>SET</code> দিয়ে নতুন মান, <code>WHERE</code> দিয়ে কোন row। আউটপুটে কয়টা row মিলল আর বদলাল দেখায়।"),
    sql("UPDATE products SET price = 16999.00 WHERE name = 'Redmi 13';"),
    sql("UPDATE products SET stock = stock + 10 WHERE brand = 'Xiaomi';"),
    sql("SELECT name, price, stock FROM products WHERE brand = 'Xiaomi';"),
    laravel("Product::where('brand', 'Xiaomi')->increment('stock', 10);"))

c.lesson("সাবধান: WHERE ছাড়া UPDATE",
    say("<code>WHERE</code> ভুলে গেলে <b>সব</b> row বদলে যায়। আগে একই <code>WHERE</code> দিয়ে <code>SELECT</code> চালিয়ে দেখে নিন কোন row বদলাবে।"),
    shell("mysql> UPDATE products SET price = 0;\nQuery OK, 8 rows affected   ← সব product-এর দাম ০ হয়ে গেল!"),
    tip("<code>mysql --safe-updates</code> (বা <code>SET SQL_SAFE_UPDATES = 1;</code>) চালু রাখলে key-ভিত্তিক WHERE ছাড়া UPDATE/DELETE MySQL নিজেই আটকে দেয়।"),
    warn("Production database-এ হাতে UPDATE চালানোর আগে backup নিন অথবা transaction-এর ভিতরে চালান (MySQL 103)।"))

c.lesson("DELETE: row মোছা",
    sql("DELETE FROM customers WHERE name = 'Tanvir Hasan';"),
    sql("SELECT COUNT(*) AS customers_left FROM customers;"),
    php_note("Laravel-এর <code>SoftDeletes</code> আসলে DELETE করে না — <code>deleted_at</code> column-এ সময় বসায় (UPDATE)। <code>forceDelete()</code> আসল DELETE চালায়।"),
    tip("<code>TRUNCATE TABLE customers;</code> সব row মুছে AUTO_INCREMENT আবার ১ থেকে শুরু করে — শুধু test data মুছতে।"))

# ================================================================== constraints
c.section("নিয়ম ও পরিবর্তন")
c.lesson("NOT NULL: খালি রাখা যাবে না",
    sql("INSERT INTO customers (name, phone) VALUES ('Mitu', NULL);", err="1048"),
    say("Database নিজেই ভুল data আটকায়। App-এ validation থাকলেও database-এর নিয়ম শেষ পাহারাদার।"))

c.lesson("UNIQUE: একই মান দুইবার না",
    say("একই ফোন নম্বর দিয়ে দুইজন customer যেন না হয়। <code>ALTER TABLE</code> দিয়ে পরে নিয়ম যোগ করা যায়।"),
    sql("ALTER TABLE customers ADD UNIQUE KEY customers_phone_unique (phone);"),
    sql("INSERT INTO customers (name, phone) VALUES ('Another Karim', '01711000001');", err="1062"),
    laravel("$table->string('phone')->unique();\n// validation-এ: 'phone' => 'unique:customers'"))

c.lesson("ALTER TABLE: column যোগ ও বদল",
    sql("ALTER TABLE customers ADD COLUMN due DECIMAL(10,2) NOT NULL DEFAULT 0 AFTER district;"),
    sql("ALTER TABLE customers MODIFY district VARCHAR(80);"),
    sql("UPDATE customers SET due = 1500 WHERE name = 'Rahim Mia';\nSELECT name, district, due FROM customers;"),
    laravel('''
Schema::table('customers', function (Blueprint $table) {
    $table->decimal('due', 10, 2)->default(0)->after('district');
});
''', "Laravel migration-এ"))

# ================================================================== functions
c.section("Function")
c.lesson("String function আর বাংলা",
    say("<code>LENGTH</code> byte গোনে, <code>CHAR_LENGTH</code> অক্ষর — বাংলায় পার্থক্য স্পষ্ট। (Terminal-এ বাংলা row-এর ঘর একটু বাঁকা দেখায় — client byte ধরে ফাঁকা দেয়, data ঠিকই আছে।)"),
    sql('''
INSERT INTO customers (name, phone, district) VALUES ('রাশেদ খান', '01311000006', 'রাজশাহী');

SELECT name,
       LENGTH(name)      AS bytes,
       CHAR_LENGTH(name) AS chars,
       UPPER(name)       AS upper_name,
       LEFT(phone, 3)    AS operator_code
FROM customers;
'''),
    php_note("<code>strlen()</code> বনাম <code>mb_strlen()</code> — PHP-তেও একই ব্যাপার।"))

c.lesson("Date function",
    sql('''
SELECT CURDATE()                                      AS today,
       DATE_FORMAT('2026-10-21', '%d/%m/%Y')          AS bd_format,
       DATE_ADD('2026-10-21', INTERVAL 7 DAY)         AS warranty_check,
       DATEDIFF('2026-12-16', '2026-10-21')           AS days_to_victory_day,
       DAYNAME('2026-10-23')                          AS day_name;
''', ),
    table(["MySQL", "Laravel / Carbon"], [["<code>CURDATE()</code>, <code>NOW()</code>", "<code>today()</code>, <code>now()</code>"],
        ["<code>DATE_ADD(d, INTERVAL 7 DAY)</code>", "<code>$d-&gt;addDays(7)</code>"], ["<code>DATEDIFF(a, b)</code>", "<code>$b-&gt;diffInDays($a)</code>"],
        ["<code>WHERE DATE(created_at) = ...</code>", "<code>whereDate('created_at', ...)</code>"]]))

c.lesson("Number function",
    sql('''
SELECT ROUND(17499.567, 2)  AS rounded,
       ROUND(17499.567)     AS whole,
       FLOOR(17499.9)       AS floor_value,
       CEIL(17499.1)        AS ceil_value,
       17500 DIV 3          AS int_div,
       17500 MOD 3          AS remainder,
       FORMAT(1234567.891, 2) AS formatted;
'''),
    tip("টাকার হিসাব <code>DECIMAL</code>-এ রাখলে <code>0.1 + 0.2</code> জাতীয় float-এর ভুল হয় না।"))

# ================================================================== project
c.section("Project")
c.lesson("Project: দোকানের প্রশ্নের উত্তর",
    say("মালিক জানতে চান: \"স্টকে আছে এমন ২০ হাজারের নিচের নতুন ফোন কোনগুলো, সস্তা থেকে দামি?\""),
    sql('''
SELECT CONCAT(brand, ' ', name) AS phone,
       price,
       stock
FROM products
WHERE condition_type = 'new'
  AND stock > 0
  AND price < 20000
  AND name NOT LIKE 'Charger%'
ORDER BY price;
'''),
    task("নিজে লিখুন: (১) used ফোনগুলোর মোট স্টকের দাম; (২) যে customer-দের district জানা নেই বা বাকি ১০০০-এর বেশি।"),
    laravel('''
Product::where('condition_type', 'new')
    ->where('stock', '>', 0)
    ->where('price', '<', 20000)
    ->where('name', 'not like', 'Charger%')
    ->orderBy('price')
    ->get();
'''))

c.lesson("Backup আর restore",
    shell("$ mysqldump -u root -p shop > shop-2026-10-21.sql\n$ mysql -u root -p shop_copy < shop-2026-10-21.sql"),
    points("<code>mysqldump</code> পুরো database-কে SQL file বানায় (CREATE + INSERT)", "নিয়মিত backup নিন, আর মাঝে মাঝে restore করে দেখুন সত্যি কাজ করে কিনা",
           "শুধু গঠন চাইলে: <code>mysqldump --no-data</code>"),
    php_note("<code>spatie/laravel-backup</code> ভিতরে এই <code>mysqldump</code>-ই চালায়।"))

c.finish("MySQL 101 শেষ! 🎉",
         "এক table-এর কাজ শেষ। কিন্তু আসল দোকানে customer, product, বিক্রি — সব আলাদা table, একে অপরের সাথে যুক্ত। সেটাই MySQL 102।",
         recap=["<code>CREATE TABLE</code>-এ ঠিক type: টাকা DECIMAL, ফোন VARCHAR",
                "<code>INSERT</code> / <code>SELECT</code> / <code>UPDATE</code> / <code>DELETE</code>",
                "<code>WHERE</code> + <code>LIKE</code>, <code>IN</code>, <code>BETWEEN</code>, <code>IS NULL</code>",
                "UPDATE/DELETE-এর আগে একই WHERE দিয়ে SELECT",
                "NOT NULL, UNIQUE — database-এর নিজের পাহারা",
                "বাংলার জন্য utf8mb4, অক্ষর গুনতে CHAR_LENGTH"])

if __name__ == "__main__":
    c.build()
