"""PostgreSQL for Laravel — what changes when a Laravel app runs on PostgreSQL. Laravel snippets run for real
(illuminate/database 12 via Capsule, pdo_pgsql) against the private PostgreSQL cluster. Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
from kit import Course, code, php_note, points, say, table, task, tip, warn  # noqa: E402
from pg_shop_schema import SCHEMA, SEED  # noqa: E402


def sql(src, **kw):
    return code(src, "postgresql", **kw)


def lara(src, **kw):
    return code(src, "php", eloquent=True, label=kw.pop("label", "Laravel"), **kw)


c = Course(slug="postgresql-for-laravel", title="PostgreSQL for Laravel", folder=HERE,
           subtitle="Laravel app PostgreSQL-এ: migration কোন SQL বানায়, LIKE/GROUP BY-এর ফাঁদ, RETURNING, JSONB, sequence আর aborted transaction",
           series="PostgreSQL for Laravel", sql_engine="postgresql",
           models=ROOT / "mysql-tutorial/mysql-for-laravel/models.php")

c.cover("PostgreSQL for Laravel",
        "একই Laravel কোড, ভিন্ন database। কোথায় কোড বদলাতে হয় না, কোথায় চুপচাপ ভুল ফল আসে, আর কোথায় PostgreSQL আপনাকে বাড়তি শক্তি দেয় — সব আসল কোড চালিয়ে।",
        learn=["<code>.env</code> আর connection", "Migration → PostgreSQL SQL", "LIKE case-sensitive: whereLike",
               "কঠোর GROUP BY", "RETURNING আর upsert", "JSONB আর full-text Eloquent দিয়ে",
               "Sequence-এর ফাঁদ", "Aborted transaction"],
        need="PostgreSQL 102 আর Laravel Eloquent। MySQL for Laravel করা থাকলে আরও ভালো।")

c.section("প্রস্তুতি")
c.lesson("Connection আর data",
    code("DB_CONNECTION=pgsql\nDB_HOST=127.0.0.1\nDB_PORT=5432\nDB_DATABASE=shop\nDB_USERNAME=shop_app\nDB_PASSWORD=secret",
         "ini", run=False, file=".env"),
    sql(SCHEMA + SEED, show_output=False, label="PostgreSQL — schema + seed"),
    lara('''
echo DB::connection()->getDriverName(), ' ', DB::scalar('select version()'), "\\n\\n";
echo Product::where('brand', 'Xiaomi')->orderBy('price')->toRawSql();
'''),
    tip("Identifier quote এখন <code>\"double quote\"</code> (MySQL-এ ছিল <code>`backtick`</code>) — Laravel নিজেই সামলায়। Raw SQL লিখলে মনে রাখুন।"))

c.lesson("Migration কোন SQL বানায়",
    lara('''
use Illuminate\\Database\\Schema\\Blueprint;

$queries = DB::connection()->pretend(fn () => DB::schema()->create('repairs', function (Blueprint $t) {
    $t->id();
    $t->foreignId('customer_id')->constrained();
    $t->string('device');
    $t->enum('status', ['received', 'repairing', 'delivered'])->default('received');
    $t->boolean('warranty')->default(false);
    $t->jsonb('parts')->nullable();
    $t->decimal('charge', 10, 2);
    $t->timestampsTz();
}));
foreach ($queries as $q) echo $q['query'], ";\\n";
''', label="Laravel migration → PostgreSQL"),
    points("<code>id()</code> → <code>bigserial primary key</code>", "<code>enum()</code> → <code>varchar</code> + <code>CHECK</code> (আসল enum type না)",
           "<code>jsonb()</code> → আসল <code>jsonb</code>; <code>json()</code> দিলে শুধু <code>json</code>", "<code>timestampsTz()</code> → <code>timestamp(0) with time zone</code>"))

c.section("ফাঁদ")
c.lesson("LIKE এখন case-sensitive",
    lara('''
echo "like:  ", Product::where('name', 'like', 'redmi%')->count(), "\\n";
echo "ilike: ", Product::where('name', 'ilike', 'redmi%')->count(), "\\n";

$q = Product::whereLike('name', 'redmi%');                       // Laravel 11+
echo "whereLike: ", $q->count(), "  →  ", $q->toRawSql(), "\\n";
$q = Product::whereLike('name', 'redmi%', caseSensitive: true);
echo "caseSensitive: ", $q->count(), "  →  ", $q->toRawSql();
'''),
    warn("MySQL থেকে আসা app-এ search box হঠাৎ কিছু খুঁজে না পেলে প্রথমে এটা দেখুন। <code>whereLike()</code> দুই database-এই ঠিক আচরণ করে।"))

c.lesson("GROUP BY: MySQL-এ চলত, এখানে চলে না",
    lara('''
try {
    Sale::selectRaw('branch_id, invoice_no, sum(total) as revenue')->groupBy('branch_id')->get();
} catch (Illuminate\\Database\\QueryException $e) {
    echo "SQLSTATE ", $e->errorInfo[0], ":\\n", explode("\\n", $e->errorInfo[2])[0], "\\n\\n";
}

$rows = Sale::selectRaw('branch_id, count(*) as invoices, sum(total) as revenue')
    ->groupBy('branch_id')->orderBy('branch_id')->get();
echo $rows->toJson();
'''),
    tip("ফলাফলে <code>revenue</code> string (<code>\"60850.00\"</code>) — PostgreSQL-এর <code>numeric</code> PHP-তে string আসে। দরকারে model-এ <code>decimal:2</code> cast।"))

c.lesson("Sequence-এর ফাঁদ: seed-এর পর duplicate key",
    say("Laravel-এর <code>id()</code> হলো <code>bigserial</code> — একটা sequence থেকে পরের নম্বর নেয়। Seeder-এ id হাতে দিলে sequence জানে না, পরের <code>create()</code> একই id নিতে চায়।"),
    lara('''
use Illuminate\\Database\\Schema\\Blueprint;
DB::schema()->create('brands', fn (Blueprint $t) => [$t->id(), $t->string('name')]);

DB::table('brands')->insert([['id' => 1, 'name' => 'Xiaomi'], ['id' => 2, 'name' => 'Samsung']]);
try {
    DB::table('brands')->insert(['name' => 'Vivo']);
} catch (Illuminate\\Database\\QueryException $e) {
    echo explode("\\n", $e->errorInfo[2])[0], "\\n";
}

DB::statement("SELECT setval(pg_get_serial_sequence('brands', 'id'), (SELECT max(id) FROM brands))");
$id = DB::table('brands')->insertGetId(['name' => 'Vivo']);
echo "setval-এর পর নতুন id: {$id}";
'''),
    tip("সমাধান: seeder-এ id দেবেন না; অথবা import-এর পর <code>setval</code> চালান। MySQL-এর AUTO_INCREMENT নিজেই এগিয়ে যায়, তাই এই সমস্যা সেখানে নেই।"))

c.lesson("Aborted transaction",
    say("PostgreSQL-এ transaction-এর ভিতরে একটা query ব্যর্থ হলে, exception <code>catch</code> করে চালিয়ে গেলেও পরের সব query ব্যর্থ হয় — যতক্ষণ না rollback।"),
    lara('''
try {
    DB::transaction(function () {
        try {
            DB::insert("insert into customers (name, phone) values ('Dup', '01711000001')");   // duplicate phone
        } catch (Illuminate\\Database\\QueryException $e) {
            echo "১ম ব্যর্থ, catch করে চালিয়ে গেলাম...\\n";
        }
        DB::table('customers')->count();                                                     // এটাও ব্যর্থ!
    });
} catch (Illuminate\\Database\\QueryException $e) {
    echo "২য়: SQLSTATE ", $e->errorInfo[0], " — ", explode("\\n", $e->errorInfo[2])[0];
}
'''),
    tip("Transaction-এর ভিতরে ভুল হওয়া স্বাভাবিক হলে (যেমন duplicate) আগেই যাচাই করুন, <code>insertOrIgnore()</code>/<code>upsert()</code> দিন, অথবা ভিতরে nested <code>DB::transaction()</code> (SAVEPOINT) ব্যবহার করুন।"))

c.section("বাড়তি শক্তি")
c.lesson("RETURNING: create আর insertGetId",
    lara('''
queries(function () {
    Customer::create(['name' => 'Jamal', 'phone' => '01700000101']);
    DB::table('customers')->insertGetId(['name' => 'Kamal', 'phone' => '01700000102']);
});
'''),
    say("PostgreSQL-এ নতুন id আসে একই query-র <code>returning \"id\"</code> থেকে — আলাদা <code>LAST_INSERT_ID()</code> লাগে না।"))

c.lesson("upsert → ON CONFLICT",
    sql("CREATE UNIQUE INDEX products_name_unique ON products (name);", show_output=False),
    lara('''
queries(fn () => Product::upsert([
    ['category_id' => 1, 'name' => 'Redmi 13',  'brand' => 'Xiaomi', 'cost' => 15500, 'price' => 17200, 'stock' => 5],
    ['category_id' => 1, 'name' => 'Redmi 14C', 'brand' => 'Xiaomi', 'cost' => 13000, 'price' => 14500, 'stock' => 6],
], uniqueBy: ['name'], update: ['cost', 'price']));

queries(fn () => Customer::insertOrIgnore(['name' => 'Karim again', 'phone' => '01711000001']));
'''),
    warn("PostgreSQL-এ <code>uniqueBy</code>-এর column-এ সত্যিকারের unique index থাকতেই হবে, নইলে error। MySQL কোনো unique key পেলেই চলে।"))

c.lesson("JSONB Eloquent দিয়ে",
    sql('''
ALTER TABLE products ADD COLUMN specs jsonb NOT NULL DEFAULT '{}';
UPDATE products SET specs = '{"ram": 8, "colors": ["Black", "Green"], "5g": false}' WHERE name = 'Redmi Note 13';
UPDATE products SET specs = '{"ram": 4, "colors": ["Black"], "5g": true}'          WHERE name = 'iPhone 12';
CREATE INDEX products_specs_gin ON products USING gin (specs);
''', show_output=False),
    lara('''
$q = Product::whereJsonContains('specs->colors', 'Black');
echo $q->toRawSql(), "\\n", $q->pluck('name')->join(', '), "\\n\\n";

$q = Product::where('specs->5g', true);
echo $q->toRawSql(), "\\n", $q->pluck('name')->join(', '), "\\n\\n";

$q = Product::where('specs->ram', '>=', 8);
echo $q->toRawSql(), "\\n", $q->pluck('name')->join(', ');
'''),
    warn("শেষ query-তে <code>-&gt;&gt;</code> লেখা (text) ফেরত দেয়, তাই তুলনা হয় অক্ষর ধরে: <code>'10' &gt;= '8'</code> মিথ্যা! সংখ্যায় তুলনা করতে cast দিন: <code>whereRaw(\"(specs-&gt;&gt;'ram')::int &gt;= ?\", [8])</code>।"),
    tip("<code>whereJsonContains</code> → <code>@&gt;</code>, যেটা GIN index ব্যবহার করে। <code>-&gt;&gt;</code> দিয়ে তুলনা index পায় না — বারবার লাগলে expression index দিন।"))

c.lesson("Full-text: whereFullText",
    lara('''
$q = Product::whereFullText(['name', 'brand'], 'galaxy');
echo $q->toRawSql(), "\\n", $q->pluck('name')->join(', ');
'''),
    php_note("Migration-এ <code>$table-&gt;fullText(['name', 'brand']);</code> দিলে pgsql-এ GIN index বানায় একই <code>to_tsvector</code> expression-এ — তাই query index পায়।"))

c.lesson("lockForUpdate আর queue",
    lara('''
queries(fn () => DB::transaction(function () {
    $p = Product::lockForUpdate()->find(4);
    $p->decrement('stock');
}));

echo "\\nlock + skip locked:\\n";
echo DB::table('jobs_demo')->lock('for update skip locked')->limit(1)->toRawSql();
'''),
    php_note("Laravel-এর database queue PostgreSQL-এ <code>for update skip locked</code> দিয়ে job নেয় — একাধিক worker নিরাপদে।"))

c.lesson("MySQL থেকে PostgreSQL-এ সরানোর চেকলিস্ট",
    table(["দেখুন", "কেন"], [
        ["<code>like</code> দিয়ে search", "Case-sensitive → <code>whereLike()</code> বা <code>ilike</code>"],
        ["<code>groupBy</code> + selectRaw", "SELECT-এর সব column GROUP BY-তে"],
        ["Raw SQL-এ backtick, <code>IFNULL</code>, <code>DATE_FORMAT</code>", "→ double quote, <code>COALESCE</code>, <code>to_char</code>"],
        ["Seeder-এ হাতে id", "শেষে <code>setval</code>"],
        ["Transaction-এ catch করে চালিয়ে যাওয়া", "Aborted transaction → SAVEPOINT/আগাম যাচাই"],
        ["<code>upsert</code>", "uniqueBy column-এ unique index"],
        ["<code>boolean</code>, <code>numeric</code>", "Cast ঠিক আছে কিনা (string/bool)"],
        ["<code>json</code> column", "<code>jsonb</code> + GIN index"]]),
    task("নিজের Laravel project PostgreSQL-এ চালান (Docker দিয়ে), test suite চালিয়ে দেখুন কোন query ভাঙে — উপরের তালিকা মিলিয়ে ঠিক করুন।"))

c.finish("PostgreSQL for Laravel শেষ! 🎉",
         "এখন আপনি জানেন Laravel app PostgreSQL-এ চালালে কী বদলায়, আর কীভাবে এর বাড়তি শক্তি কাজে লাগাতে হয়।",
         recap=["LIKE case-sensitive → <code>whereLike()</code>", "কঠোর GROUP BY, numeric আসে string",
                "Seeder-এ id দিলে <code>setval</code>", "ভিতরের error-এ পুরো transaction aborted",
                "<code>RETURNING</code>, <code>ON CONFLICT</code>, JSONB <code>@&gt;</code> + GIN", "<code>for update skip locked</code> queue"])

if __name__ == "__main__":
    c.build()
