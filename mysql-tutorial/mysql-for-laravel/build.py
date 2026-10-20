"""MySQL for Laravel — what Eloquent sends to MySQL, N+1, writes, pagination, migrations, schema design.
Laravel snippets marked eloquent=True really run (illuminate/database 12 via Capsule) against the
course database, and print the SQL they sent. Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
from kit import Course, code, php_note, points, say, table, task, tip, warn  # noqa: E402
from shop_schema import SCHEMA, SEED  # noqa: E402


def sql(src, **kw):
    return code(src, "mysql", **kw)


def lara(src, **kw):
    """A Laravel snippet that runs against the course database."""
    return code(src, "php", eloquent=True, label=kw.pop("label", "Laravel"), **kw)


c = Course(slug="mysql-for-laravel", title="MySQL for Laravel — Eloquent-এর ভিতরে", folder=HERE,
           subtitle="Eloquent আসলে কোন SQL পাঠায়: N+1, eager loading, transaction, pagination, migration আর schema design — সব আসল query log সহ",
           series="MySQL for Laravel", sql_engine="mysql", models=HERE / "models.php")

c.cover("MySQL for Laravel<br>Eloquent-এর ভিতরে",
        "এই কোর্সের প্রতিটি Laravel কোড আসলেই চালানো হয়েছে, আর পাশে দেখানো হয়েছে MySQL-এ ঠিক কোন query গেল আর কয়টা। Debugbar যা দেখায়, সেটা বুঝতে শিখব।",
        learn=["toRawSql() আর query log", "where/orWhere-এর ফাঁদ", "whereHas, withCount-এর SQL", "N+1 আর with()",
               "create বনাম insert, increment-এর atomic UPDATE", "Transaction আর lockForUpdate", "paginate, simplePaginate, cursorPaginate",
               "Migration কোন SQL বানায়; টাকা, soft delete, index"],
        need="MySQL 102 (JOIN, GROUP BY) আর Laravel-এর Eloquent-এর সাধারণ ব্যবহার।")

# ================================================================== setup
c.section("প্রস্তুতি")
c.lesson("Database আর Model",
    say("MySQL 102-এর দোকানের database। Model-গুলো সাধারণ Laravel model — relationship সহ।"),
    sql(SCHEMA + SEED, show_output=False, label="MySQL — schema + seed (MySQL 102 থেকে)"),
    code((HERE / "models.php").read_text().split("class Branch", 1)[0].replace("// Eloquent models for the 'Rahim Mobile' schema (../shop_schema.py). Loaded before every Laravel snippet.\n", "")
         + "class Sale extends Model\n{\n    public $timestamps = false;\n"
         "    public function customer() { return $this->belongsTo(Customer::class); }\n"
         "    public function items() { return $this->hasMany(SaleItem::class); }\n    // branch(), employee() ...\n}",
         "php", run=False, label="app/Models (সংক্ষেপে)"),
    tip("এখানে Laravel-এর database অংশ (<code>illuminate/database</code>) আলাদাভাবে চালানো হয়েছে — একই Eloquent, একই SQL।"))

c.lesson("Eloquent কোন SQL বানাল? toRawSql()",
    say("<code>-&gt;toRawSql()</code> query না চালিয়ে SQL দেখায় (মান বসিয়ে)। <code>-&gt;toSql()</code> দেখায় <code>?</code> সহ। Debug করার প্রথম ধাপ।"),
    lara('''
echo Product::where('brand', 'Xiaomi')
    ->where('price', '<', 20000)
    ->orderByDesc('price')
    ->toRawSql();
'''),
    tip("<code>queries(fn () =&gt; ...)</code> হলো এই কোর্সের ছোট helper: ভিতরে যত query চলে, সব নম্বরসহ দেখায় — Debugbar-এর মতো। Laravel app-এ একই কাজ <code>DB::listen()</code> বা <code>DB::enableQueryLog()</code>।"))

# ================================================================== query builder
c.section("Query → SQL")
c.lesson("orWhere-এর ফাঁদ",
    say("\"Xiaomi অথবা Samsung, যাদের স্টক আছে\" — সরল লিখলে SQL-এ AND আগে বাঁধে, ফল ভুল।"),
    lara('''
$wrong = Product::where('brand', 'Xiaomi')->orWhere('brand', 'Samsung')->where('stock', '>', 2);
echo $wrong->toRawSql(), "\\n", $wrong->pluck('name')->join(', '), "\\n\\n";

$right = Product::where(fn ($q) => $q->where('brand', 'Xiaomi')->orWhere('brand', 'Samsung'))
    ->where('stock', '>', 2);
echo $right->toRawSql(), "\\n", $right->pluck('name')->join(', ');
'''),
    warn("প্রথমটায় Redmi Note 13 (স্টক ২) চলে এসেছে। <code>orWhere</code> থাকলে সবসময় closure দিয়ে bracket করুন।"))

c.lesson("whereHas = EXISTS subquery",
    lara('''
$q = Customer::whereHas('sales', fn ($s) => $s->where('total', '>', 20000));
echo $q->toRawSql(), "\\n\\n";
echo $q->pluck('name')->join(', ');
'''),
    say("<code>whereHas</code> প্রতিটি customer-এর জন্য <code>EXISTS</code> subquery চালায়। বড় table-এ <code>sales.customer_id</code>-এ index থাকা জরুরি (foreign key দিলে MySQL নিজেই বানায়)।"))

c.lesson("withCount আর withSum",
    say("সম্পর্কিত row গোনা বা যোগ করা — আলাদা query না, একই SELECT-এর ভিতরে subquery।"),
    lara('''
$customers = queries(fn () => Customer::withCount('sales')
    ->withSum('sales', 'total')
    ->orderByDesc('sales_sum_total')
    ->limit(3)
    ->get());

foreach ($customers as $c) {
    echo "{$c->name}: {$c->sales_count}টা, {$c->sales_sum_total} টাকা\\n";
}
'''))

c.lesson("GROUP BY: selectRaw দিয়ে",
    lara('''
$rows = Sale::query()
    ->join('branches', 'branches.id', '=', 'sales.branch_id')
    ->selectRaw('branches.name AS branch, COUNT(*) AS invoices, SUM(total) AS revenue')
    ->groupBy('branches.id', 'branches.name')
    ->orderByDesc('revenue')
    ->get();

foreach ($rows as $r) {
    echo str_pad($r->branch, 8), " {$r->invoices}  {$r->revenue}\\n";
}
'''),
    warn("<code>selectRaw</code>-এ কখনো user input সরাসরি জুড়বেন না। মান লাগলে দ্বিতীয় parameter-এ binding দিন: <code>selectRaw('price * ? AS with_vat', [1.15])</code>।"))

c.lesson("শুধু যা দরকার: pluck, value, exists",
    lara('''
queries(function () {
    $names  = Product::where('brand', 'Xiaomi')->pluck('name');   // শুধু name column
    $price  = Product::where('name', 'iPhone 12')->value('price'); // এক মান
    $exists = Customer::where('phone', '01711000001')->exists();  // SELECT EXISTS
    $count  = Sale::whereNull('customer_id')->count();
    echo "{$names->join(', ')} | {$price} | " . ($exists ? 'yes' : 'no') . " | walk-in: {$count}\\n";
});
'''),
    tip("শুধু আছে কিনা জানতে <code>-&gt;first()</code> বা <code>-&gt;get()-&gt;count()</code> না — <code>exists()</code> আর <code>count()</code> database-এই হিসাব করে।"))

# ================================================================== N+1
c.section("N+1 ও Eager loading")
c.lesson("N+1: চুপচাপ ৮টা query",
    say("প্রতিটি sale-এর customer-এর নাম দেখাতে loop — দেখতে নিরীহ, কিন্তু প্রতিটি <code>$sale-&gt;customer</code> একটা নতুন query।"),
    lara('''
queries(function () {
    foreach (Sale::all() as $sale) {
        $sale->customer?->name;
    }
});
'''),
    warn("১০টা sale-এ ৮টা query: ১টা sale-এর, আর customer আছে এমন ৭টার প্রতিটির জন্য একটা (walk-in-এ <code>customer_id</code> NULL, তাই query হয়নি — একই customer দুইবার এলেও দুইবার query!)। ১০০০টা sale-এ প্রায় ১০০১টা।"))

c.lesson("with(): ৮ থেকে ২",
    lara('''
queries(function () {
    foreach (Sale::with('customer')->get() as $sale) {
        $sale->customer?->name;
    }
});
'''),
    say("Laravel প্রথমে সব sale আনে, তারপর একটা <code>WHERE id IN (...)</code> query-তে সব customer — যত sale-ই থাকুক, query ২টা।"))

c.lesson("Nested eager loading",
    lara('''
$sales = queries(fn () => Sale::with(['customer:id,name', 'items.product:id,name'])
    ->whereIn('invoice_no', ['INV-1001', 'INV-1005'])
    ->get());

foreach ($sales as $s) {
    echo "{$s->invoice_no} {$s->customer->name}: ",
        $s->items->map(fn ($i) => $i->product->name)->join(', '), "\\n";
}
'''),
    points("<code>items.product</code> — items, তারপর তাদের product", "<code>customer:id,name</code> — শুধু দরকারি column (id অবশ্যই রাখুন)"))

c.lesson("preventLazyLoading: N+1 হলেই ধরা",
    say("<code>AppServiceProvider::boot()</code>-এ এক লাইন দিলে development-এ lazy loading হলেই exception — N+1 production-এ যাওয়ার আগেই ধরা পড়ে।"),
    lara('''
Illuminate\\Database\\Eloquent\\Model::preventLazyLoading();

try {
    foreach (Sale::limit(2)->get() as $sale) {
        echo $sale->customer->name;
    }
} catch (Illuminate\\Database\\LazyLoadingViolationException $e) {
    echo get_class($e), ":\\n", $e->getMessage();
}
'''),
    code("Model::preventLazyLoading(! app()->isProduction());", "php", run=False, label="app/Providers/AppServiceProvider.php"))

# ================================================================== writes
c.section("লেখা: create, update, upsert")
c.lesson("create বনাম insert",
    say("<code>create()</code> প্রতিটি row-এর জন্য একটা query (event, timestamp, cast সব চলে)। <code>insert()</code> এক query-তে সব, কিন্তু Eloquent-এর কোনো সুবিধা নেই।"),
    lara('''
queries(function () {
    foreach (['Jamal' => '01700000101', 'Kamal' => '01700000102'] as $name => $phone) {
        Customer::create(['name' => $name, 'phone' => $phone]);
    }
    Customer::insert([
        ['name' => 'Rina', 'phone' => '01700000103'],
        ['name' => 'Mina', 'phone' => '01700000104'],
    ]);
});
'''),
    tip("হাজার row import-এ <code>insert()</code> (বা <code>chunk</code> করে insert); সাধারণ form save-এ <code>create()</code>।"))

c.lesson("Loop-এ save বনাম এক UPDATE",
    lara('''
queries(function () {
    foreach (Product::where('brand', 'Walton')->get() as $p) {   // ১ SELECT + প্রতিটিতে UPDATE
        $p->price = $p->price + 50;
        $p->save();
    }
    Product::where('brand', 'Nokia')->update(['price' => DB::raw('price + 50')]);   // ১ UPDATE
});
'''),
    say("সব row-এ একই নিয়ম হলে query builder-এর <code>update()</code> — এক query। (তবে এতে model event চলে না।)"))

c.lesson("increment: race-free স্টক কমানো",
    say("<code>$p-&gt;stock = $p-&gt;stock - 1; $p-&gt;save();</code> — দুই কাউন্টার একসাথে করলে একটা বিক্রি হারিয়ে যেতে পারে। <code>decrement()</code> database-এই হিসাব করে: <code>stock = stock - 1</code>।"),
    lara('''
$p = Product::find(8);
queries(fn () => $p->decrement('stock', 2));
echo 'এখন স্টক: ', Product::whereKey(8)->value('stock');
'''))

c.lesson("upsert: থাকলে update, না থাকলে insert",
    say("Supplier-এর price list import: product নাম মিললে দাম বদলাও, নইলে নতুন যোগ করো — এক query-তে। MySQL-এ এটা <code>INSERT ... ON DUPLICATE KEY UPDATE</code>, তাই unique key লাগে।"),
    sql("ALTER TABLE products ADD UNIQUE KEY products_name_unique (name);"),
    lara('''
queries(fn () => Product::upsert([
    ['category_id' => 1, 'name' => 'Redmi 13',  'brand' => 'Xiaomi', 'cost' => 15500, 'price' => 17200, 'stock' => 5],
    ['category_id' => 1, 'name' => 'Redmi 14C', 'brand' => 'Xiaomi', 'cost' => 13000, 'price' => 14500, 'stock' => 6],
], uniqueBy: ['name'], update: ['cost', 'price']));

echo Product::where('name', 'like', 'Redmi 1%')->get(['name', 'price'])->toJson();
'''))

c.lesson("Transaction আর lockForUpdate",
    lara('''
queries(function () {
    DB::transaction(function () {
        $p = Product::lockForUpdate()->find(4);          // SELECT ... FOR UPDATE
        if ($p->stock < 1) {
            throw new RuntimeException('স্টক নেই');
        }
        $p->decrement('stock');
        $saleId = DB::table('sales')->insertGetId([
            'invoice_no' => 'INV-1012', 'branch_id' => 3, 'employee_id' => 4,
            'sold_at' => '2026-10-20 15:00:00', 'total' => 48000,
        ]);
        DB::table('sale_items')->insert(['sale_id' => $saleId, 'product_id' => 4, 'qty' => 1, 'unit_price' => 48000]);
    });
});
'''),
    say("Query log-এ <code>for update</code> দেখুন। Closure-এর ভিতরে exception হলে Laravel নিজেই ROLLBACK করে।"),
    tip("Transaction log-এ <code>START TRANSACTION</code>/<code>COMMIT</code> দেখায় না, কারণ Laravel সেগুলো PDO-র method দিয়ে চালায় — কিন্তু database-এ ঠিকই হয়।"))

# ================================================================== big data
c.section("অনেক data")
c.lesson("chunk আর lazy: memory বাঁচানো",
    say("<code>Sale::all()</code> সব row একবারে memory-তে আনে। লাখ row হলে PHP-র memory শেষ। <code>chunkById</code> অল্প অল্প করে আনে।"),
    lara('''
queries(function () {
    Sale::orderBy('id')->chunkById(4, function ($sales) {
        echo '  chunk: ', $sales->pluck('invoice_no')->join(', '), "\\n";
    });
});
'''),
    points("<code>chunkById</code> — <code>WHERE id &gt; শেষ_id</code>, loop-এর ভিতরে update করলেও নিরাপদ",
           "<code>lazyById()</code> — একই কাজ, কিন্তু সাধারণ foreach-এর মতো লেখা যায়",
           "সাধারণ <code>chunk()</code> OFFSET ব্যবহার করে — বড় table-এ ধীর আর loop-এ update করলে row বাদ পড়তে পারে"))

c.lesson("তিন ধরনের pagination",
    lara('''
echo "paginate():\\n";
queries(fn () => Sale::orderBy('id')->paginate(3, page: 2));

echo "\\nsimplePaginate():\\n";
queries(fn () => Sale::orderBy('id')->simplePaginate(3, page: 2));

echo "\\ncursorPaginate():\\n";
$first = Sale::orderBy('id')->cursorPaginate(3);
queries(fn () => Sale::orderBy('id')->cursorPaginate(3, cursor: $first->nextCursor()));
'''),
    table(["", "Query", "কখন"], [
        ["<code>paginate</code>", "COUNT + LIMIT/OFFSET", "পাতার নম্বর দরকার (admin table)"],
        ["<code>simplePaginate</code>", "শুধু LIMIT/OFFSET (একটা বেশি আনে)", "শুধু আগে/পরে বাটন"],
        ["<code>cursorPaginate</code>", "<code>WHERE id &gt; ?</code> LIMIT — OFFSET নেই", "Infinite scroll, API, বড় table"]]))

c.lesson("বড় OFFSET কেন ধীর",
    say("<code>LIMIT 20 OFFSET 200000</code> মানে MySQL ২ লাখ row পড়ে ফেলে দেয়, তারপর ২০টা দেয়। Cursor (keyset) pagination সরাসরি index দিয়ে শুরু জায়গায় যায়।"),
    sql('''
EXPLAIN FORMAT=TREE
SELECT id, invoice_no FROM sales ORDER BY id LIMIT 3 OFFSET 6;
'''),
    sql('''
EXPLAIN FORMAT=TREE
SELECT id, invoice_no FROM sales WHERE id > 6 ORDER BY id LIMIT 3;
'''),
    tip("প্রথমটায় index থেকে ৯টা row পড়ে ৬টা ফেলে দেয়; দ্বিতীয়টা সরাসরি <code>id &gt; 6</code> থেকে শুরু। ১০ row-এ পার্থক্য নেই, ১০ লাখে বিশাল।"))

c.lesson("whereDate-এর লুকানো খরচ",
    lara('''
echo Sale::whereDate('sold_at', '2026-10-16')->toRawSql(), "\\n\\n";
echo Sale::whereBetween('sold_at', ['2026-10-16 00:00:00', '2026-10-16 23:59:59'])->toRawSql();
'''),
    say("প্রথমটায় column-এর উপর <code>date()</code> function — index কাজ করে না (MySQL 103)। বড় table-এ দ্বিতীয়টা লিখুন, সাথে <code>sold_at</code>-এ index।"))

# ================================================================== schema
c.section("Migration ও Schema design")
c.lesson("Migration আসলে কোন SQL",
    say("<code>pretend()</code> দিয়ে migration না চালিয়ে শুধু SQL দেখা যায় — <code>php artisan migrate --pretend</code> এটাই করে।"),
    lara('''
use Illuminate\\Database\\Schema\\Blueprint;

$queries = DB::connection()->pretend(function () {
    DB::schema()->create('expenses', function (Blueprint $table) {
        $table->id();
        $table->foreignId('branch_id')->constrained()->cascadeOnDelete();
        $table->string('title');
        $table->decimal('amount', 12, 2);
        $table->timestamps();
        $table->softDeletes();
        $table->index(['branch_id', 'created_at']);
    });
});
foreach ($queries as $q) {
    echo $q['query'], ";\\n";
}
''', label="Laravel migration → SQL"),
    points("<code>id()</code> = <code>bigint unsigned auto_increment primary key</code>",
           "<code>foreignId()-&gt;constrained()</code> = column + foreign key", "<code>softDeletes()</code> = nullable <code>deleted_at</code>"))

c.lesson("টাকা কোন type-এ?",
    table(["উপায়", "ভালো", "সাবধান"], [
        ["<code>decimal(12, 2)</code>", "পড়তে সহজ, SQL-এ সঠিক যোগফল", "PHP-তে string হয়ে আসে; float-এ cast করবেন না"],
        ["<code>unsignedBigInteger</code> (পয়সায়)", "পূর্ণসংখ্যা — কোনো ভগ্নাংশের ভুল নেই", "দেখানোর সময় ১০০ দিয়ে ভাগ"],
        ["<code>float</code> / <code>double</code>", "—", "কখনো না: <code>0.1 + 0.2 ≠ 0.3</code>"]]),
    lara('''
$p = Product::find(1);
var_dump($p->price);            // decimal আসে string হিসেবে
echo bcadd($p->price, '0.10', 2), "\\n";   // নিখুঁত যোগ
'''),
    php_note("Model-এ <code>protected $casts = ['price' =&gt; 'decimal:2'];</code> দিলে সবসময় ২ ঘর দশমিকসহ string।"))

c.lesson("Soft delete আসলে কী করে",
    sql('''
CREATE TABLE expenses (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP NULL, updated_at TIMESTAMP NULL, deleted_at TIMESTAMP NULL
);
''', show_output=False),
    lara('''
queries(function () {
    $e = Expense::create(['title' => 'দোকান ভাড়া', 'amount' => 25000]);
    $e->delete();                                   // আসলে UPDATE
    echo '  দেখা যায়? ', Expense::count(), ' | সহ মোছা: ', Expense::withTrashed()->count(), "\\n";
});
'''),
    warn("Soft delete-এর সব query-তে <code>deleted_at is null</code> যোগ হয় — unique key আর index-এ এটা মাথায় রাখুন (মোছা row-ও unique key-তে জায়গা নেয়)।"))

c.lesson("DB::raw-এর বিপদ",
    say("<code>DB::raw()</code> আর <code>whereRaw()</code>-এ লেখা SQL যেমন আছে তেমনই যায়। User input জুড়লে SQL injection।"),
    lara('''
$search = "x' OR '1'='1";

$unsafe = Product::whereRaw("name = '$search'");
echo "ভুল: ", $unsafe->count(), " row — সব product বেরিয়ে গেল!\\n";

$safe = Product::whereRaw('name = ?', [$search]);
echo "ঠিক: ", $safe->count(), " row\\n";
'''),
    tip("নিয়ম: raw SQL-এ মান সবসময় <code>?</code> আর binding array দিয়ে। Column বা ক্রমের নাম user থেকে নিলে whitelist করুন।"))

c.lesson("Laravel + MySQL চেকলিস্ট",
    table(["করুন", "কেন"], [
        ["Development-এ <code>preventLazyLoading()</code>", "N+1 শুরুতেই ধরা পড়ে"],
        ["Foreign key: <code>foreignId()-&gt;constrained()</code>", "অনাথ data আটকায়, JOIN-এ index পায়"],
        ["WHERE + ORDER BY-এর column-এ composite index", "বড় table-এ পাতা দ্রুত"],
        ["টাকা <code>decimal</code> বা পয়সায় integer", "হিসাবে ভগ্নাংশের ভুল নেই"],
        ["স্টক বদলাতে <code>decrement()</code> + transaction + <code>lockForUpdate()</code>", "একসাথে বিক্রিতে ভুল হয় না"],
        ["Import-এ <code>insert</code>/<code>upsert</code> আর <code>chunkById</code>", "কম query, কম memory"],
        ["API list-এ <code>cursorPaginate</code>", "বড় OFFSET এড়ানো"],
        ["Raw SQL-এ সবসময় binding", "SQL injection নেই"]]),
    task("নিজের Laravel project-এ Debugbar বা Telescope চালু করে সবচেয়ে বেশি query হয় এমন পাতা খুঁজুন — N+1 আছে কিনা দেখুন।"))

c.finish("MySQL for Laravel শেষ! 🎉",
         "Eloquent এখন আর জাদু না — আপনি জানেন প্রতিটি লাইন MySQL-এ কী পাঠায়, আর কখন সেটা ধীর।",
         recap=["<code>toRawSql()</code> আর query log দিয়ে SQL দেখুন",
                "<code>orWhere</code> → closure দিয়ে bracket",
                "Loop-এ relationship → <code>with()</code>; <code>preventLazyLoading()</code>",
                "Bulk কাজে <code>insert</code>/<code>update</code>/<code>upsert</code>; স্টকে <code>decrement</code>",
                "বড় data: <code>chunkById</code>, <code>cursorPaginate</code>, range শর্ত",
                "Raw SQL-এ binding, টাকা decimal"])

if __name__ == "__main__":
    c.build()
