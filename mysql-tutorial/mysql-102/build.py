"""MySQL 102 — relationship, foreign key, GROUP BY, JOIN, subquery, view.
Runs on the shared 'Rahim Mobile' schema (../shop_schema.py). Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
from kit import Course, code, php_note, points, quiz, say, table, task, tip, warn  # noqa: E402
from shop_schema import SCHEMA, SEED  # noqa: E402


def sql(src, **kw):
    return code(src, "mysql", **kw)


def laravel(src, label="Laravel-এ"):
    return code(src, "php", run=False, label=label)


c = Course(slug="mysql-102", title="MySQL 102 — Relationship ও JOIN", folder=HERE,
           subtitle="অনেক table একসাথে: foreign key, GROUP BY, JOIN, subquery আর view — Eloquent relationship-এর পিছনের SQL",
           series="MySQL 102", sql_engine="mysql",
           next_course=("../mysql-103/index.html", "MySQL 103 — Index, Transaction ও Window function"))

c.cover("MySQL 102<br>Relationship ও JOIN",
        "আসল দোকানের data এক table-এ থাকে না। শাখা, কর্মচারী, customer, product, বিক্রি — সব আলাদা table, id দিয়ে যুক্ত। এগুলো জোড়া লাগিয়ে রিপোর্ট বানানোই এই কোর্স।",
        learn=["কেন table ভাগ করি", "Primary key আর foreign key", "COUNT, SUM, AVG আর GROUP BY", "HAVING আর WITH ROLLUP",
               "INNER JOIN আর LEFT JOIN", "কখনো বিক্রি হয়নি এমন product খোঁজা", "Subquery, EXISTS, UNION", "VIEW আর Eloquent relationship-এর SQL"],
        need="MySQL 101 (SELECT, WHERE, ORDER BY, INSERT)।")

# ================================================================== setup
c.section("আজকের Database")
c.lesson("কেন একাধিক table?",
    say("সব কিছু এক table-এ রাখলে একই তথ্য বারবার লিখতে হয়, আর একটা বদলালে সব জায়গায় বদলাতে হয়।"),
    table(["invoice", "customer", "customer_phone", "branch", "product"], [
        ["INV-1001", "Karim Uddin", "01711000001", "Mirpur", "Redmi 13"],
        ["INV-1007", "Karim Uddin", "01711000001", "Mirpur", "Vivo Y28"],
        ["INV-1003", "Nusrat Jahan", "01811000002", "Uttara", "Redmi Note 13"]]),
    points("Karim-এর ফোন বদলালে সব row খুঁজে বদলাতে হবে — একটা ভুললেই অমিল",
           "সমাধান: customer আলাদা table-এ একবার, বিক্রিতে শুধু <code>customer_id</code>",
           "এটাকে বলে <b>normalization</b>"),
    php_note("Laravel-এ <code>Sale belongsTo Customer</code> — ঠিক এই <code>customer_id</code> column-টাই সম্পর্ক।"))

c.lesson("Table গুলো: Rahim Mobile",
    say("ছয়টা table। <code>FOREIGN KEY</code> লাইনগুলো বলছে কোন column অন্য কোন table-এর <code>id</code>-কে নির্দেশ করে।"),
    sql(SCHEMA, show_output=False, label="MySQL — schema"),
    table(["সম্পর্ক", "ধরন", "Eloquent"], [
        ["branch → employees", "এক শাখায় অনেক কর্মচারী", "<code>hasMany</code>"],
        ["sale → customer", "প্রতিটি বিক্রি একজন customer-এর (বা walk-in)", "<code>belongsTo</code>"],
        ["sale → sale_items → product", "এক বিক্রিতে অনেক product, এক product অনেক বিক্রিতে", "<code>belongsToMany</code> (pivot)"]]))

c.lesson("Data ঢোকানো",
    say("৩টা শাখা, ৬ জন customer, ১১টা product, ১০টা বিক্রি। পুরো কোর্স এই data নিয়ে।"),
    sql(SEED, show_output=False, label="MySQL — seed data"),
    sql('''
SELECT (SELECT COUNT(*) FROM branches)   AS branches,
       (SELECT COUNT(*) FROM customers)  AS customers,
       (SELECT COUNT(*) FROM products)   AS products,
       (SELECT COUNT(*) FROM sales)      AS sales,
       (SELECT COUNT(*) FROM sale_items) AS sale_items;
'''),
    php_note("Laravel-এ এটাই <code>DatabaseSeeder</code> — <code>php artisan db:seed</code>।"))

# ================================================================== aggregate
c.section("হিসাব: GROUP BY")
c.lesson("COUNT, SUM, AVG, MIN, MAX",
    say("Aggregate function অনেক row থেকে একটা মান বানায়।"),
    sql('''
SELECT COUNT(*)            AS invoices,
       SUM(total)          AS revenue,
       ROUND(AVG(total))   AS avg_invoice,
       MIN(total)          AS smallest,
       MAX(total)          AS biggest
FROM sales;
'''),
    laravel("Sale::count();  Sale::sum('total');  Sale::avg('total');  Sale::max('total');"))

c.lesson("GROUP BY: শাখা ধরে",
    say("<code>GROUP BY branch_id</code> — প্রতিটি শাখার row আলাদা দলে, তারপর প্রতিটি দলের হিসাব।"),
    sql('''
SELECT branch_id,
       COUNT(*)   AS invoices,
       SUM(total) AS revenue
FROM sales
GROUP BY branch_id
ORDER BY revenue DESC;
'''),
    warn("SELECT-এ যে column থাকবে তা হয় <code>GROUP BY</code>-এ থাকবে, নয়তো aggregate-এর ভিতরে। নইলে MySQL error দেয় (ONLY_FULL_GROUP_BY)।"),
    laravel("Sale::selectRaw('branch_id, COUNT(*) AS invoices, SUM(total) AS revenue')\n    ->groupBy('branch_id')->orderByDesc('revenue')->get();"))

c.lesson("তারিখ ধরে: দৈনিক বিক্রি",
    sql('''
SELECT DATE(sold_at)                AS day,
       DAYNAME(sold_at)             AS weekday,
       COUNT(*)                     AS invoices,
       SUM(total)                   AS revenue
FROM sales
GROUP BY DATE(sold_at), DAYNAME(sold_at)
ORDER BY day;
'''),
    tip("মাসিক চাইলে <code>DATE_FORMAT(sold_at, '%Y-%m')</code> দিয়ে GROUP BY করুন।"))

c.lesson("HAVING: দলের উপর শর্ত",
    say("<code>WHERE</code> row বাছাই করে দল বানানোর <b>আগে</b>। <code>HAVING</code> দল বানানোর <b>পরে</b> — aggregate-এর উপর শর্ত।"),
    sql('''
SELECT customer_id,
       COUNT(*)   AS visits,
       SUM(total) AS spent
FROM sales
WHERE customer_id IS NOT NULL
GROUP BY customer_id
HAVING COUNT(*) >= 2;
'''),
    quiz("\"৫০ হাজারের বেশি বিক্রি করেছে এমন শাখা\" — WHERE না HAVING?", "HAVING SUM(total) &gt; 50000 — কারণ শর্তটা যোগফলের উপর।"))

c.lesson("WITH ROLLUP: মোট যোগফল সহ",
    sql('''
SELECT IFNULL(branch_id, 'মোট') AS branch,
       SUM(total)               AS revenue
FROM sales
GROUP BY branch_id WITH ROLLUP;
'''),
    say("শেষ লাইনে সব দলের যোগফল। Excel-এর subtotal-এর মতো।"))

# ================================================================== keys
c.section("Foreign key")
c.lesson("Foreign key: ভুল id ঢুকতে দেয় না",
    say("<code>sales.branch_id</code> অবশ্যই <code>branches</code>-এ থাকা কোনো id হতে হবে। নেই এমন শাখা দিলে MySQL আটকায়।"),
    sql("INSERT INTO sales (invoice_no, branch_id, employee_id, sold_at, total)\nVALUES ('INV-9999', 99, 1, NOW(), 500);", err="1452"),
    php_note("Laravel-এ <code>$table-&gt;foreignId('branch_id')-&gt;constrained();</code> এই নিয়মটাই বানায়।"))

c.lesson("Parent মুছতে বাধা",
    say("Gulshan শাখার কর্মচারী আর বিক্রি আছে, তাই শাখাটা মোছা যায় না — নইলে সেগুলো \"অনাথ\" হয়ে যেত। Error-এ দেখুন কোন constraint আটকাল (<code>employees_ibfk_1</code>)।"),
    sql("DELETE FROM branches WHERE name = 'Gulshan';", err="1451"),
    table(["নিয়ম", "Parent মুছলে child-এর কী হয়", "Laravel"], [
        ["<code>RESTRICT</code> (ডিফল্ট)", "মোছা আটকায়", "<code>-&gt;restrictOnDelete()</code>"],
        ["<code>CASCADE</code>", "child-ও মুছে যায়", "<code>-&gt;cascadeOnDelete()</code>"],
        ["<code>SET NULL</code>", "child-এ id NULL হয়", "<code>-&gt;nullOnDelete()</code>"]]))

c.lesson("ON DELETE CASCADE",
    say("<code>sale_items</code> বানানো হয়েছে <code>ON DELETE CASCADE</code> দিয়ে: বিক্রি মুছলে তার লাইনগুলোও যায়। একটা পরীক্ষামূলক বিক্রি দিয়ে দেখি।"),
    sql('''
INSERT INTO sales (invoice_no, branch_id, employee_id, sold_at, total)
VALUES ('INV-TEST', 1, 1, '2026-10-19 21:00:00', 650);
INSERT INTO sale_items (sale_id, product_id, qty, unit_price)
VALUES (LAST_INSERT_ID(), 8, 1, 650);

SELECT COUNT(*) AS items_before FROM sale_items;
DELETE FROM sales WHERE invoice_no = 'INV-TEST';
SELECT COUNT(*) AS items_after FROM sale_items;
'''))

# ================================================================== join
c.section("JOIN")
c.lesson("INNER JOIN: দুই table জোড়া",
    say("<code>JOIN ... ON</code> দিয়ে বলি কোন column মিলিয়ে জোড়া হবে। এখন branch_id-এর বদলে শাখার নাম দেখাতে পারি।"),
    sql('''
SELECT s.invoice_no, b.name AS branch, s.total
FROM sales AS s
JOIN branches AS b ON b.id = s.branch_id
ORDER BY s.sold_at
LIMIT 5;
'''),
    tip("<code>sales AS s</code> — ছোট নাম (alias) দিলে লম্বা query পড়তে সহজ।"))

c.lesson("শাখার নাম দিয়ে রিপোর্ট",
    sql('''
SELECT b.name     AS branch,
       COUNT(*)   AS invoices,
       SUM(s.total) AS revenue
FROM sales s
JOIN branches b ON b.id = s.branch_id
GROUP BY b.id, b.name
ORDER BY revenue DESC;
'''),
    laravel('''
Sale::join('branches', 'branches.id', '=', 'sales.branch_id')
    ->selectRaw('branches.name AS branch, COUNT(*) AS invoices, SUM(sales.total) AS revenue')
    ->groupBy('branches.id', 'branches.name')
    ->orderByDesc('revenue')->get();
'''))

c.lesson("অনেক table: পুরো invoice",
    say("একটা invoice-এর সব লাইন: sale → items → product, সাথে customer আর কর্মচারী।"),
    sql('''
SELECT s.invoice_no,
       c.name  AS customer,
       e.name  AS sold_by,
       p.name  AS product,
       si.qty,
       si.unit_price,
       si.qty * si.unit_price AS line_total
FROM sales s
JOIN employees  e  ON e.id = s.employee_id
JOIN customers  c  ON c.id = s.customer_id
JOIN sale_items si ON si.sale_id = s.id
JOIN products   p  ON p.id = si.product_id
WHERE s.invoice_no IN ('INV-1001', 'INV-1005');
'''))

c.lesson("INNER JOIN কী বাদ দেয়?",
    say("INNER JOIN শুধু দুই দিকে মিল আছে এমন row রাখে। walk-in বিক্রির <code>customer_id</code> NULL — তাই নিচের query-তে সেগুলো <b>হারিয়ে গেছে</b>।"),
    sql('''
SELECT COUNT(*) AS all_sales FROM sales;

SELECT COUNT(*) AS sales_with_customer_join
FROM sales s
JOIN customers c ON c.id = s.customer_id;
'''),
    warn("রিপোর্টে মোট মেলে না? প্রথমে দেখুন কোনো INNER JOIN নীরবে row বাদ দিচ্ছে কিনা।"))

c.lesson("LEFT JOIN: বাম দিকের সব রাখা",
    say("<code>LEFT JOIN</code> বাম table-এর সব row রাখে; ডানে মিল না থাকলে সেখানে <code>NULL</code>।"),
    sql('''
SELECT s.invoice_no,
       IFNULL(c.name, 'Walk-in') AS customer,
       s.total
FROM sales s
LEFT JOIN customers c ON c.id = s.customer_id
ORDER BY s.id;
'''))

c.lesson("কখনো কেনেনি এমন customer",
    say("LEFT JOIN করে ডান দিক <code>IS NULL</code> খুঁজলে পাই \"মিল নেই\" এমন row — একে বলে anti-join।"),
    sql('''
SELECT c.name, c.phone
FROM customers c
LEFT JOIN sales s ON s.customer_id = c.id
WHERE s.id IS NULL;
'''),
    laravel("Customer::doesntHave('sales')->get();"))

c.lesson("কখনো বিক্রি হয়নি এমন product",
    sql('''
SELECT p.name, p.brand, p.stock
FROM products p
LEFT JOIN sale_items si ON si.product_id = p.id
WHERE si.id IS NULL;
'''),
    sql('''
SELECT cat.name AS category, COUNT(p.id) AS products
FROM categories cat
LEFT JOIN products p ON p.category_id = cat.id
GROUP BY cat.id, cat.name;
'''),
    tip("দ্বিতীয় query-তে <code>COUNT(p.id)</code> — <code>COUNT(*)</code> দিলে খালি category-ও ১ দেখাত, কারণ LEFT JOIN-এ একটা NULL row থাকে।"))

c.lesson("Leaderboard: কে কত বিক্রি করল",
    sql('''
SELECT e.name      AS employee,
       b.name      AS branch,
       COUNT(s.id) AS invoices,
       IFNULL(SUM(s.total), 0) AS revenue
FROM employees e
JOIN branches b ON b.id = e.branch_id
LEFT JOIN sales s ON s.employee_id = e.id
GROUP BY e.id, e.name, b.name
ORDER BY revenue DESC;
'''),
    task("Product ধরে leaderboard বানান: কোন product মোট কয়টা বিক্রি হয়েছে আর কত টাকার (<code>sale_items</code> + <code>products</code>)।"))

c.lesson("লাভ: বিক্রির দাম − কেনার দাম",
    sql('''
SELECT p.name,
       SUM(si.qty)                              AS sold,
       SUM(si.qty * si.unit_price)              AS revenue,
       SUM(si.qty * (si.unit_price - p.cost))   AS profit
FROM sale_items si
JOIN products p ON p.id = si.product_id
GROUP BY p.id, p.name
ORDER BY profit DESC
LIMIT 5;
'''),
    tip("আসল app-এ বিক্রির সময়কার কেনা দাম <code>sale_items</code>-এ কপি করে রাখুন — পরে product-এর cost বদলালে পুরনো লাভ যেন না বদলায়।"))

c.lesson("JOIN-এর ধরন এক নজরে",
    table(["JOIN", "কী ফেরত দেয়", "কখন"], [
        ["<code>INNER JOIN</code> (<code>JOIN</code>)", "দুই দিকে মিল আছে এমন row", "বেশিরভাগ রিপোর্ট"],
        ["<code>LEFT JOIN</code>", "বাম দিকের সব + ডানের মিল", "\"যাদের নেই\" তাদেরও দেখাতে"],
        ["<code>RIGHT JOIN</code>", "ডান দিকের সব + বামের মিল", "কম ব্যবহার; LEFT উল্টে লিখুন"],
        ["<code>CROSS JOIN</code>", "সব জোড়া (গুণফল)", "তারিখ × শাখা grid বানাতে"]]),
    php_note("Laravel: <code>join()</code>, <code>leftJoin()</code>, <code>rightJoin()</code>, <code>crossJoin()</code>।"))

# ================================================================== subquery
c.section("Subquery ও View")
c.lesson("Subquery: query-র ভিতরে query",
    sql('''
SELECT name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC;
'''),
    say("ভিতরের query আগে চলে (গড় দাম), তারপর বাইরের query সেটা ব্যবহার করে।"))

c.lesson("IN আর EXISTS",
    sql('''
-- Mirpur শাখা থেকে কিনেছেন এমন customer
SELECT name FROM customers
WHERE id IN (SELECT customer_id FROM sales WHERE branch_id = 1);
'''),
    sql('''
SELECT c.name FROM customers c
WHERE EXISTS (
    SELECT 1 FROM sales s WHERE s.customer_id = c.id AND s.total > 20000
);
'''),
    laravel("Customer::whereHas('sales', fn ($q) => $q->where('total', '>', 20000))->get();", "Laravel whereHas — ভিতরে এই EXISTS-ই"))

c.lesson("Derived table: subquery-কে table বানানো",
    sql('''
SELECT ROUND(AVG(daily.revenue)) AS avg_daily_revenue,
       MAX(daily.revenue)        AS best_day
FROM (
    SELECT DATE(sold_at) AS day, SUM(total) AS revenue
    FROM sales
    GROUP BY DATE(sold_at)
) AS daily;
'''),
    say("প্রথমে দৈনিক যোগফল, তারপর সেই ফলাফলের গড় — দুই ধাপের হিসাব এক query-তে।"))

c.lesson("UNION: দুই ফলাফল এক তালিকায়",
    sql('''
SELECT name, 'customer' AS type FROM customers WHERE district = 'Dhaka'
UNION ALL
SELECT name, 'employee' AS type FROM employees WHERE branch_id = 1;
'''),
    points("<code>UNION</code> — duplicate বাদ দেয়", "<code>UNION ALL</code> — সব রাখে, দ্রুত",
           "দুই দিকে column-এর সংখ্যা ও ক্রম একই হতে হবে"))

c.lesson("VIEW: query-কে নাম দিয়ে রাখা",
    say("বারবার লাগে এমন জটিল query <code>VIEW</code> বানিয়ে রাখলে table-এর মতো ব্যবহার করা যায়।"),
    sql('''
CREATE VIEW branch_daily_sales AS
SELECT b.name AS branch, DATE(s.sold_at) AS day, SUM(s.total) AS revenue
FROM sales s
JOIN branches b ON b.id = s.branch_id
GROUP BY b.name, DATE(s.sold_at);

SELECT * FROM branch_daily_sales WHERE branch = 'Mirpur' ORDER BY day;
'''),
    php_note("View-এর জন্যও Eloquent model বানানো যায় (<code>protected $table = 'branch_daily_sales';</code>) — শুধু পড়ার জন্য।"))

# ================================================================== laravel
c.section("Eloquent-এর পিছনে")
c.lesson("Eloquent relationship আসলে কোন SQL",
    laravel('''
class Sale extends Model {
    public function customer() { return $this->belongsTo(Customer::class); }
    public function items()    { return $this->hasMany(SaleItem::class); }
}

$sale = Sale::find(1);
$sale->customer;   // select * from customers where id = ? limit 1
$sale->items;      // select * from sale_items where sale_id = ?
''', "Laravel model"),
    say("প্রতিটি relationship property ধরলেই একটা আলাদা query চলে। একটা sale-এর জন্য সমস্যা নেই — কিন্তু ১০০টা sale-এর loop-এ?"))

c.lesson("N+1 সমস্যা আর with()",
    say("Loop-এ <code>$sale-&gt;customer</code> দিলে প্রতিটি sale-এর জন্য একটা করে query (customer থাকলে): N টা sale = ১ + N query। <code>with('customer')</code> দিলে মাত্র ২টা। আসল query log দেখুন MySQL for Laravel কোর্সে।"),
    laravel('''
// N+1: 1 + N queries
foreach (Sale::all() as $sale) { echo $sale->customer?->name; }

// Eager loading: 2 queries (যত sale-ই হোক)
foreach (Sale::with('customer')->get() as $sale) { echo $sale->customer?->name; }
'''),
    sql('''
-- with('customer') এর দ্বিতীয় query দেখতে এরকম:
SELECT * FROM customers WHERE id IN (1, 2, 3, 4, 5);
'''),
    tip("<code>Model::preventLazyLoading()</code> development-এ চালু রাখুন — N+1 হলে Laravel নিজেই exception দেবে। বিস্তারিত MySQL for Laravel-এ।"))

c.lesson("Project: সপ্তাহের রিপোর্ট",
    say("মালিকের জন্য এক query-তে: শাখা, কর্মচারী, invoice সংখ্যা, বিক্রি আর লাভ — বেশি লাভ আগে।"),
    sql('''
SELECT b.name AS branch,
       e.name AS employee,
       COUNT(DISTINCT s.id)                      AS invoices,
       SUM(si.qty * si.unit_price)               AS revenue,
       SUM(si.qty * (si.unit_price - p.cost))    AS profit
FROM sales s
JOIN branches   b  ON b.id = s.branch_id
JOIN employees  e  ON e.id = s.employee_id
JOIN sale_items si ON si.sale_id = s.id
JOIN products   p  ON p.id = si.product_id
WHERE s.sold_at >= '2026-10-15' AND s.sold_at < '2026-10-20'
GROUP BY b.name, e.name
ORDER BY profit DESC;
'''),
    task("একই রিপোর্টে customer-এর district ধরে ভাগ করুন — walk-in বিক্রি যেন বাদ না পড়ে (কোন JOIN লাগবে?)।"))

c.finish("MySQL 102 শেষ! 🎉",
         "এখন আপনি অনেক table জুড়ে রিপোর্ট বানাতে পারেন। এরপর: বড় data-তে দ্রুত চালানো (index), ভুল হলে ফিরিয়ে আনা (transaction) আর window function।",
         recap=["Table ভাগ করে id দিয়ে যুক্ত — normalization",
                "Foreign key: ভুল id আর অনাথ row আটকায়",
                "<code>GROUP BY</code> + aggregate; দলের শর্ত <code>HAVING</code>",
                "<code>JOIN</code> মিল রাখে, <code>LEFT JOIN</code> সব রাখে",
                "<code>LEFT JOIN ... IS NULL</code> = যাদের নেই",
                "Eloquent relationship = আলাদা query; loop-এ <code>with()</code>"])

if __name__ == "__main__":
    c.build()
