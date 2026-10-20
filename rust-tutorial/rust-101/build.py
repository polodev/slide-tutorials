"""Rust 101 — শূন্য থেকে Rust: variables, types, functions, control flow, input.
Run: python3 build.py   (every Rust/PHP block is compiled and run; real output goes on the slide)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, steps, table, task, tip, warn  # noqa: E402

c = Course(slug="rust-101", title="Rust 101 — শূন্য থেকে শুরু", folder=Path(__file__).parent,
           subtitle="Install, variables, types, function, if/loop/match আর keyboard input — PHP জানা থাকলেই যথেষ্ট",
           series="Rust 101", next_course=("../rust-102/index.html", "Rust 102 — Ownership ও Data"))

c.cover("Rust 101<br>শূন্য থেকে শুরু",
        "PHP/Laravel জানেন? তাহলে Rust শেখা অনেক সহজ হবে। প্রতিটি স্লাইডে একটা ছোট ধারণা, একটা ছোট কোড আর তার আসল আউটপুট।",
        learn=["Rust install আর Cargo", "Variable, mut, shadowing, const", "Number, bool, char, String",
               "Function আর return", "if, loop, while, for, match", "Keyboard থেকে input নেওয়া",
               "Compiler error পড়তে শেখা", "ছোট project: টাকার নোট ভাঙানো"],
        need="সাধারণ programming (PHP যথেষ্ট)। প্রতিটি পাঠ ২–৩ মিনিটের।")

# ================================================================== শুরু
c.section("শুরু")
c.lesson("Rust কেন শিখবেন?",
    points("<b>দ্রুত:</b> সরাসরি machine code-এ compile হয়, C/C++-এর কাছাকাছি গতি",
           "<b>নিরাপদ:</b> null pointer, memory leak, data race — compile করার সময়ই ধরা পড়ে",
           "<b>Garbage collector নেই:</b> memory কখন ছাড়বে, সেটা compiler নিজেই ঠিক করে",
           "<b>কোথায় চলে:</b> web server, CLI tool, WebAssembly, embedded, এমনকি PHP extension"),
    table(["", "PHP", "Rust"], [
        ["চলে কীভাবে", "Interpreter (প্রতি request-এ)", "আগে compile, তারপর binary"],
        ["Type", "Dynamic (চলার সময় ঠিক হয়)", "Static (compile-এর সময় ঠিক হয়)"],
        ["ভুল ধরা পড়ে", "অনেক সময় production-এ", "বেশিরভাগ compile-এর সময়েই"],
        ["Package manager", "Composer", "Cargo"]]),
    tip("Rust শিখতে একটু সময় লাগে, কারণ compiler কড়া। কিন্তু compile হয়ে গেলে program সাধারণত ঠিকঠাক চলে।"))

c.lesson("Install করুন (rustup)",
    say("Rust install করার official উপায় হলো <code>rustup</code>। এটা compiler (<code>rustc</code>), <code>cargo</code> আর standard library একসাথে দেয়।"),
    points("<b>macOS / Linux:</b> ডানের command চালান, তারপর terminal বন্ধ করে আবার খুলুন",
           "<b>Windows:</b> rustup.rs থেকে <code>rustup-init.exe</code> নামিয়ে চালান। Visual Studio C++ Build Tools চাইলে সেটাও install করুন",
           "Update করতে: <code>rustup update</code>"),
    shell("$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh\n$ rustc --version\n$ cargo --version",
          out="rustc 1.99.1 (58cf8f9c3 2026-10-13)\ncargo 1.99.1 (5f94df478 2026-08-27)"),
    tip("Editor হিসেবে VS Code + <b>rust-analyzer</b> extension নিন। Type, error আর auto-complete সাথে সাথে দেখাবে।"))

c.lesson("প্রথম program",
    say("প্রতিটি Rust program চলে <code>main</code> function থেকে। <code>println!</code> লেখা প্রিন্ট করে নতুন লাইনে যায়।"),
    points("<code>fn</code> দিয়ে function বানানো হয়",
           "<code>println!</code>-এর শেষে <code>!</code> মানে এটা একটা <b>macro</b> (সাধারণ function না)",
           "প্রতিটি statement-এর শেষে <code>;</code>"),
    php_note("<code>echo \"Hello, World!\\n\";</code> — Rust-এ এর জন্য পুরো <code>main</code> function লাগে।"),
    code(r'''
fn main() {
    println!("Hello, World!");
    println!("Rust শেখা শুরু হলো 🚀");
}
'''),
    task("নিজের নাম আর জেলার নাম দুই লাইনে প্রিন্ট করুন।"))

c.lesson("Cargo: Rust-এর Composer",
    say("বাস্তব project-এ আমরা <code>rustc</code> সরাসরি না চালিয়ে <code>cargo</code> ব্যবহার করি। এটা project বানায়, build করে, চালায়, আর package (crate) নামায়।"),
    table(["Cargo", "কাজ", "Composer/Laravel-এ"], [
        ["<code>cargo new hello</code>", "নতুন project", "<code>composer create-project</code>"],
        ["<code>cargo run</code>", "build করে চালায়", "<code>php artisan serve</code> এর মতো"],
        ["<code>cargo build --release</code>", "দ্রুত, optimize করা binary", "—"],
        ["<code>cargo add serde</code>", "crate যোগ", "<code>composer require</code>"],
        ["<code>Cargo.toml</code>", "project-এর তথ্য ও dependency", "<code>composer.json</code>"]]),
    shell("$ cargo new hello\n$ cd hello\n$ cargo run",
          out="   Compiling hello v0.1.0 (/home/rahim/hello)\n    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.52s\n     Running `target/debug/hello`\nHello, world!"),
    code('''
[package]
name = "hello"
version = "0.1.0"
edition = "2024"

[dependencies]
''', "toml", file="Cargo.toml"))

c.lesson("println! দিয়ে সুন্দর করে প্রিন্ট",
    say("<code>{}</code> জায়গায় মান বসে। Variable-এর নাম সরাসরি <code>{name}</code> লেখা যায়।"),
    points("<code>{:.2}</code> — দশমিকের পর ২ ঘর", "<code>{:>8}</code> — ডানে সাজিয়ে ৮ ঘর জায়গা",
           "<code>{:?}</code> — debug আকারে (পরে কাজে লাগবে)"),
    tip("<code>f64</code> = দশমিক সংখ্যা (৬৪-bit, PHP-র <code>float</code>)। <code>price * qty as f64</code> — <code>qty</code> পূর্ণসংখ্যা, তাই <code>as f64</code> দিয়ে দশমিক বানিয়ে <code>price</code>-এর সাথে গুণ; <code>{:.2}</code> ফলটা ২ ঘর দশমিকে দেখায় (3751.50)।"),
    php_note("<code>printf(\"%.2f\", $price)</code> বা <code>\"Hello {$name}\"</code> — Rust-এ সব <code>{}</code> দিয়ে।"),
    code(r'''
fn main() {
    let name = "Rahim";
    let price = 1250.5;
    let qty = 3;

    println!("Customer: {}", name);
    println!("Customer: {name}");
    println!("Total: {:.2} টাকা", price * qty as f64);
    println!("[{:>8}] [{:<8}]", "ডানে", "বামে");
    println!("{:?}", (name, qty));
}
'''))

# ================================================================== variables
c.section("Variables ও Types")
c.lesson("let: variable সাধারণত বদলানো যায় না",
    say("Rust-এ <code>let</code> দিয়ে variable বানাই। ডিফল্টভাবে এটা <b>immutable</b> — একবার মান দিলে আর বদলানো যায় না।"),
    php_note("PHP-তে <code>$x = 5; $x = 6;</code> চলে। Rust-এ বদলাতে চাইলে আগে থেকে বলে দিতে হয়।"),
    code(r'''
fn main() {
    let balance = 500;
    println!("Balance: {balance}");
    balance = 700;
    println!("Balance: {balance}");
}
''', err="E0384"),
    tip("Error message-এর শেষে compiler নিজেই সমাধান বলে দিচ্ছে: <code>let mut balance</code>। Rust compiler-এর error পড়তে শিখলে অর্ধেক কাজ শেষ।"))

c.lesson("mut: বদলানোর অনুমতি",
    say("বদলাতে চাইলে <code>let mut</code> লিখুন। এতে কোড পড়েই বোঝা যায় কোন মান বদলাবে আর কোনটা বদলাবে না।"),
    code(r'''
fn main() {
    let mut balance = 500;
    println!("শুরুতে: {balance} টাকা");

    balance = balance + 200;   // bKash থেকে এলো
    balance -= 50;             // রিকশা ভাড়া
    println!("এখন: {balance} টাকা");
}
'''),
    quiz("<code>let x = 1;</code> লিখে পরে <code>x += 1;</code> করলে কী হবে?",
         "Compile হবে না (E0384)। <code>let mut x = 1;</code> লিখতে হবে।"))

c.lesson("Shadowing: একই নামে নতুন variable",
    say("একই নামে আবার <code>let</code> লিখলে আগের variable ঢাকা পড়ে যায় (shadow)। এতে type-ও বদলানো যায়।"),
    points("<code>mut</code> একই variable-এর মান বদলায়, type বদলাতে পারে না",
           "Shadowing নতুন variable বানায়, তাই type বদলানো যায়",
           "ইনপুট পরিষ্কার করতে খুব কাজে লাগে: text → number"),
    code(r'''
fn main() {
    let phone = "  01711-000000  ";
    let phone = phone.trim();          // একই নাম, নতুন মান
    println!("[{phone}]");

    let qty = "12";                    // এটা text (&str)
    let qty: i32 = qty.parse().unwrap(); // এখন number
    println!("দ্বিগুণ: {}", qty * 2);
}
'''))

c.lesson("const: কখনো না বদলানো মান",
    say("<code>const</code> সব সময় immutable, type লিখতেই হবে, আর নাম সাধারণত বড় হাতের অক্ষরে।"),
    php_note("Laravel-এর <code>config()</code> বা PHP-র <code>const VAT = 15;</code> এর মতো।"),
    code(r'''
const VAT_PERCENT: f64 = 15.0;
const SHOP_NAME: &str = "Rahim Mobile";

fn main() {
    let price = 1000.0;
    let vat = price * VAT_PERCENT / 100.0;
    println!("{SHOP_NAME}");
    println!("দাম {price}, VAT {vat}, মোট {}", price + vat);
}
'''))

c.lesson("Integer: পূর্ণ সংখ্যা",
    say("Rust-এ number-এর আকার আপনি ঠিক করেন। <code>i</code> = চিহ্নসহ (ঋণাত্মক হতে পারে), <code>u</code> = শুধু ধনাত্মক।"),
    table(["Type", "সীমা", "কখন"], [
        ["<code>i32</code>", "প্রায় ±২১৪ কোটি", "ডিফল্ট, সাধারণ কাজে"],
        ["<code>i64</code>", "অনেক বড়", "টাকার হিসাব (পয়সায়), id"],
        ["<code>u8</code>", "০ – ২৫৫", "বয়স, byte"],
        ["<code>usize</code>", "machine অনুযায়ী", "index, length"]]),
    code(r'''
fn main() {
    let age: u8 = 25;
    let population: i64 = 17_00_00_000;  // _ শুধু পড়ার সুবিধার জন্য
    let temp = -3;                        // ধরে নেয় i32

    println!("বয়স {age}, জনসংখ্যা {population}, তাপমাত্রা {temp}");
    println!("u8 সর্বোচ্চ: {}", u8::MAX);
    println!("i32 সর্বোচ্চ: {}", i32::MAX);
}
'''),
    tip("টাকার হিসাব কখনো float-এ রাখবেন না। পয়সায় (<code>i64</code>) রাখুন: ১২.৫০ টাকা = ১২৫০ পয়সা।"))

c.lesson("Float আর ভাগের ফাঁদ",
    say("দশমিক সংখ্যার জন্য <code>f64</code>। দুইটা integer ভাগ করলে ফলও integer হয় — দশমিক বাদ যায়।"),
    points("<code>7 / 2</code> = <code>3</code> (integer ভাগ)", "<code>7.0 / 2.0</code> = <code>3.5</code>",
           "Type বদলাতে <code>as</code>: <code>7 as f64</code>", "<code>%</code> = ভাগশেষ"),
    code(r'''
fn main() {
    let a = 7;
    let b = 2;
    println!("{} / {} = {}", a, b, a / b);
    println!("ভাগশেষ = {}", a % b);
    println!("দশমিকসহ = {}", a as f64 / b as f64);
    println!("পাই ≈ {:.3}", std::f64::consts::PI);
}
'''),
    code(r'''
<?php
echo 7 / 2, "\n";        // PHP দশমিক দেয়
echo intdiv(7, 2), "\n";  // integer ভাগ আলাদা function
''', "php", label="PHP-তে তুলনা"))

c.lesson("bool আর char",
    say("<code>bool</code> হয় <code>true</code> নয়তো <code>false</code>। <code>char</code> একটা অক্ষর, single quote দিয়ে — বাংলা অক্ষরও চলে।"),
    code(r'''
fn main() {
    let is_open = true;
    let has_stock = false;
    println!("দোকান খোলা? {is_open}, স্টক আছে? {has_stock}");
    println!("দুটোই? {}", is_open && has_stock);

    let letter = 'অ';
    let emoji = '📱';
    println!("{letter} {emoji}");
    println!("'অ' এর memory: {} byte", std::mem::size_of::<char>());
}
'''),
    php_note("PHP-তে <code>'অ'</code> একটা string। Rust-এ <code>'অ'</code> হলো <code>char</code>, আর <code>\"অ\"</code> হলো string।"))

c.lesson("String: দুই ধরনের লেখা",
    say("আপাতত মনে রাখুন: <code>\"Dhaka\"</code> লিখলে পাই <code>&str</code> (স্থির লেখা)। বদলানো বা বাড়ানো যায় এমন লেখার জন্য <code>String</code>।"),
    points("<code>String::from(\"..\")</code> বা <code>\"..\".to_string()</code> দিয়ে String",
           "<code>push_str</code> দিয়ে শেষে যোগ", "<code>format!</code> — println!-এর মতো, কিন্তু String ফেরত দেয়"),
    php_note("PHP-তে <code>$a . $b</code>। Rust-এ সবচেয়ে সহজ <code>format!(\"{a}{b}\")</code>।"),
    code(r'''
fn main() {
    let city = "Dhaka";                    // &str
    let mut address = String::from("Mirpur 10");
    address.push_str(", ");
    address.push_str(city);
    println!("{address}");

    let line = format!("{} — {} অক্ষর", address, address.len());
    println!("{line}");
}
'''),
    warn("<code>len()</code> অক্ষর না, <b>byte</b> গোনে। বাংলা অক্ষর ৩ byte করে, তাই বাংলায় সংখ্যা বড় দেখাবে। ১০২-এ বিস্তারিত।"))

c.lesson("Tuple: কয়েকটা মান একসাথে",
    say("আলাদা type-এর কয়েকটা মান একসাথে রাখতে tuple। <code>.0</code>, <code>.1</code> দিয়ে নেওয়া যায়, অথবা ভেঙে আলাদা variable-এ।"),
    code(r'''
fn main() {
    let product = ("Redmi Note 13", 23500, true);
    println!("নাম: {}", product.0);
    println!("দাম: {}", product.1);

    let (name, price, in_stock) = product;   // ভেঙে নেওয়া
    println!("{name} — {price} টাকা — স্টকে: {in_stock}");
}
'''),
    php_note("PHP-র <code>[$name, $price] = ['Redmi', 23500];</code> এর মতো।"))

c.lesson("Array: একই type-এর নির্দিষ্ট সংখ্যক মান",
    say("Array-এর দৈর্ঘ্য স্থির। দৈর্ঘ্য বাড়াতে-কমাতে হলে <code>Vec</code> লাগে (১০২-এ)।"),
    code(r'''
fn main() {
    let days = ["শনি", "রবি", "সোম", "মঙ্গল", "বুধ", "বৃহস্পতি", "শুক্র"];
    let sales = [1200, 3400, 2100];

    println!("প্রথম দিন: {}", days[0]);
    println!("মোট দিন: {}", days.len());
    println!("সব বিক্রি: {:?}", sales);

    let zeros = [0; 5];       // ৫টা শূন্য
    println!("{:?}", zeros);
}
'''),
    php_note("PHP array একসাথে list আর map। Rust-এ এগুলো আলাদা: array/<code>Vec</code> (list) আর <code>HashMap</code> (key-value)।"))

c.lesson("Array-এর বাইরে গেলে কী হয়?",
    say("PHP-তে ভুল index দিলে শুধু warning আর <code>null</code>। Rust সাথে সাথে program থামিয়ে দেয় (<b>panic</b>), ভুল মান নিয়ে চলতে দেয় না।"),
    code(r'''
fn main() {
    let sales = [1200, 3400, 2100];
    let index = sales.len() + 2;   // ইচ্ছা করে ভুল index
    println!("চেষ্টা করছি index {index}...");
    println!("{}", sales[index]);
}
''', panic=True),
    tip("নিরাপদে নিতে <code>sales.get(5)</code> — এটা panic না করে \"নেই\" (<code>None</code>) ফেরত দেয়। ১০২-এ <code>Option</code> শিখব।"))

# ================================================================== functions
c.section("Function")
c.lesson("Function বানানো",
    say("<code>fn</code> দিয়ে function। Parameter-এর type অবশ্যই লিখতে হবে — Rust এখানে অনুমান করে না।"),
    php_note("<code>function greet(string $name): void</code> — PHP-তে type ঐচ্ছিক, Rust-এ বাধ্যতামূলক।"),
    code(r'''
fn greet(name: &str, district: &str) {
    println!("স্বাগতম {name}, {district} থেকে!");
}

fn main() {
    greet("Karim", "Sylhet");
    greet("Nusrat", "Rajshahi");
}
'''))

c.lesson("Return: শেষ লাইনই ফলাফল",
    say("<code>-> i64</code> দিয়ে return type বলি। শেষ লাইনে <b>semicolon না দিলে</b> সেটাই ফেরত যায়। আগে ফেরত দিতে <code>return</code> লেখা যায়।"),
    code(r'''
fn total_price(price: i64, qty: i64) -> i64 {
    price * qty            // ; নেই, তাই এটাই return
}

fn discount(amount: i64) -> i64 {
    if amount < 1000 {
        return 0;          // আগে ফেরত দেওয়া
    }
    amount * 5 / 100
}

fn main() {
    let t = total_price(450, 4);
    println!("মোট {t}, ছাড় {}, দেবেন {}", discount(t), t - discount(t));
}
'''))

c.lesson("একটা ; দিলেই error",
    say("শেষ লাইনে ভুল করে <code>;</code> দিলে সেটা আর মান থাকে না, হয়ে যায় statement — ফলে কিছুই ফেরত যায় না (<code>()</code>)। Compiler ধরে ফেলে।"),
    code(r'''
fn square(x: i32) -> i32 {
    x * x;
}

fn main() {
    println!("{}", square(4));
}
''', err="E0308"),
    tip("Error-এর <code>help: remove this semicolon</code> লাইনটা দেখুন — compiler ঠিক জায়গা দেখিয়ে দিচ্ছে।"))

c.lesson("Block-ও একটা মান",
    say("<code>{ }</code> block-এর শেষ লাইন (semicolon ছাড়া) পুরো block-এর মান হয়। তাই block দিয়ে variable-এ মান বসানো যায়।"),
    code(r'''
fn main() {
    let bill = {
        let rice = 75 * 10;     // ১০ কেজি চাল
        let oil = 190 * 2;      // ২ লিটার তেল
        rice + oil              // block-এর মান
    };
    println!("বাজারের বিল: {bill} টাকা");
}
'''),
    quiz("<code>let x = { 5; };</code> হলে <code>x</code> কী?", "<code>()</code> — খালি মান, কারণ <code>5;</code> statement।"))

# ================================================================== control flow
c.section("if, loop, match")
c.lesson("if/else: শর্ত অবশ্যই bool",
    say("শর্তের চারপাশে bracket লাগে না। কিন্তু শর্ত অবশ্যই <code>bool</code> হতে হবে।"),
    php_note("PHP-তে <code>if ($count)</code> চলে (0 মানে false)। Rust-এ এটা error — লিখতে হবে <code>if count &gt; 0</code>।"),
    code(r'''
fn main() {
    let stock = 3;
    if stock {
        println!("স্টক আছে");
    }
}
''', err="E0308"),
    code(r'''
fn main() {
    let stock = 3;
    if stock > 0 {
        println!("স্টক আছে: {stock}টা");
    } else {
        println!("স্টক শেষ");
    }
}
'''))

c.lesson("if একটা মান দেয়",
    say("<code>if</code> নিজেই একটা expression, তাই সরাসরি variable-এ রাখা যায়। দুই দিকের type একই হতে হবে।"),
    php_note("PHP-র ternary <code>$x = $a &gt; 0 ? 'হ্যাঁ' : 'না';</code> — Rust-এ আলাদা ternary নেই, <code>if</code>-ই সেই কাজ করে।"),
    code(r'''
fn main() {
    let amount = 1800;
    let delivery = if amount >= 1500 { 0 } else { 60 };
    let label = if delivery == 0 { "ফ্রি ডেলিভারি" } else { "ডেলিভারি চার্জ" };
    println!("{label}: {delivery} টাকা");
}
'''))

c.lesson("else if: GPA বের করি",
    code(r'''
fn grade(marks: u32) -> &'static str {
    if marks >= 80 {
        "A+"
    } else if marks >= 70 {
        "A"
    } else if marks >= 60 {
        "A-"
    } else if marks >= 50 {
        "B"
    } else if marks >= 33 {
        "C/D"
    } else {
        "F"
    }
}

fn main() {
    for m in [95, 72, 48, 20] {
        println!("{m} নম্বর → {}", grade(m));
    }
}
'''),
    say("প্রতিটি শাখা একটা <code>&str</code> ফেরত দিচ্ছে, তাই পুরো <code>if</code> function-এর return মান।"),
    tip("<code>&'static str</code> মানে লেখাটা পুরো program জুড়ে থাকবে। <code>'static</code> নিয়ে ১০৩-এ বিস্তারিত।"))

c.lesson("loop: থামতে বলা পর্যন্ত চলে",
    say("<code>loop</code> চিরকাল চলে, <code>break</code> দিয়ে থামাতে হয়। <code>break</code>-এর সাথে একটা মানও ফেরত দেওয়া যায়।"),
    code(r'''
fn main() {
    let mut savings = 1000;
    let mut month = 0;

    let months_needed = loop {
        month += 1;
        savings += savings * 10 / 100;   // মাসে ১০% বাড়ে
        if savings >= 2000 {
            break month;                 // মান সহ বের হলাম
        }
    };
    println!("{months_needed} মাসে দ্বিগুণ, এখন {savings} টাকা");
}
'''))

c.lesson("while: শর্ত সত্য থাকা পর্যন্ত",
    code(r'''
fn main() {
    let mut seconds = 5;
    while seconds > 0 {
        println!("{seconds}...");
        seconds -= 1;
    }
    println!("রকেট উড়ল! 🚀");
}
'''),
    php_note("PHP-র <code>while ($s &gt; 0) { ... }</code> একদম একই, শুধু bracket আর <code>$</code> নেই।"))

c.lesson("for আর range: নামতা",
    say("<code>1..=10</code> মানে ১ থেকে ১০ (১০ সহ)। <code>1..10</code> মানে ১০ বাদ। উল্টো দিকে যেতে <code>.rev()</code>।"),
    code(r'''
fn main() {
    let n = 7;
    for i in 1..=5 {
        println!("{n} × {i} = {}", n * i);
    }

    for i in (1..=3).rev() {
        print!("{i} ");
    }
    println!();

    for city in ["Dhaka", "Khulna", "Barishal"] {
        print!("{city} | ");
    }
    println!();
}
'''),
    php_note("<code>for ($i = 1; $i &lt;= 5; $i++)</code> আর <code>foreach ($cities as $city)</code> — Rust-এ দুটোই <code>for ... in</code>।"))

c.lesson("match: PHP 8-এর match-এর বড় ভাই",
    say("<code>match</code> একটা মানকে কয়েকটা pattern-এর সাথে মিলিয়ে দেখে। <b>সব সম্ভাবনা</b> ধরতেই হবে — বাকি সবকিছুর জন্য <code>_</code>।"),
    points("<code>1 | 7</code> — এটা বা ওটা", "<code>2..=6</code> — range", "<code>_</code> — বাকি সব"),
    code(r'''
fn day_type(day: u8) -> &'static str {
    match day {
        6 => "ছুটি (শুক্রবার)",
        7 => "হাফ ডে (শনিবার)",
        1..=5 => "কাজের দিন",
        _ => "ভুল দিন",
    }
}

fn main() {
    for d in [1, 6, 7, 9] {
        println!("দিন {d}: {}", day_type(d));
    }
}
'''),
    code(r'''
<?php
$day = 6;
echo match (true) {
    $day === 6 => "ছুটি",
    $day >= 1 && $day <= 5 => "কাজের দিন",
    default => "অন্য",
}, "\n";
''', "php", label="PHP 8-এ তুলনা"))

c.lesson("match ভুলে গেলে compiler মনে করিয়ে দেয়",
    say("<code>_</code> বাদ দিলে compiler বলবে কোন মানগুলো ধরা হয়নি। একে বলে <b>exhaustive</b> check — বড় project-এ অনেক bug আটকায়।"),
    code(r'''
fn main() {
    let rating: u8 = 4;
    let text = match rating {
        1 => "খারাপ",
        2..=3 => "মোটামুটি",
        4..=5 => "ভালো",
    };
    println!("{text}");
}
''', err="E0004"))

# ================================================================== input
c.section("Input ও Project")
c.lesson("Keyboard থেকে input",
    say("<code>std::io::stdin().read_line()</code> একটা লাইন পড়ে String-এ রাখে। তারপর <code>trim()</code> করে <code>parse()</code> দিয়ে number বানাই।"),
    points("<code>use std::io;</code> — library থেকে <code>io</code> আনলাম (PHP-র <code>use</code>-এর মতো)",
           "<code>&mut input</code> — function-কে আমাদের String বদলানোর অনুমতি দিলাম",
           "<code>.expect(\"...\")</code> — ভুল হলে এই বার্তা দিয়ে থামবে"),
    code(r'''
use std::io;

fn main() {
    println!("কত কেজি চাল কিনবেন?");
    let mut input = String::new();
    io::stdin().read_line(&mut input).expect("পড়া গেল না");

    let kg: u32 = input.trim().parse().expect("সংখ্যা লিখুন");
    println!("{kg} কেজি × ৭৫ টাকা = {} টাকা", kg * 75);
}
''', stdin="12\n"),
    php_note("PHP CLI-তে <code>$kg = (int) trim(fgets(STDIN));</code>"))

c.lesson("ভুল input-এ কী হয়?",
    say("<code>parse()</code> ব্যর্থ হলে <code>expect</code> program থামায়। আপাতত এটাই যথেষ্ট — ১০২-এ <code>Result</code> দিয়ে সুন্দরভাবে সামলানো শিখব।"),
    code(r'''
use std::io;

fn main() {
    let mut input = String::new();
    io::stdin().read_line(&mut input).expect("পড়া গেল না");
    let kg: u32 = input.trim().parse().expect("সংখ্যা লিখুন");
    println!("{kg}");
}
''', stdin="বারো\n", panic=True))

c.lesson("Project: টাকার নোট ভাঙানো",
    say("ক্যাশ কাউন্টারে ফেরত দিতে কোন নোট কয়টা লাগবে? Array, for, integer ভাগ আর ভাগশেষ — সব একসাথে।"),
    code(r'''
use std::io;

fn main() {
    let notes = [1000, 500, 200, 100, 50, 20, 10, 5, 2, 1];

    println!("কত টাকা ফেরত দিতে হবে?");
    let mut input = String::new();
    io::stdin().read_line(&mut input).expect("পড়া গেল না");
    let mut amount: u32 = input.trim().parse().expect("সংখ্যা লিখুন");

    for note in notes {
        let count = amount / note;
        if count > 0 {
            println!("{note:>5} টাকার নোট × {count}");
            amount %= note;
        }
    }
}
''', stdin="2785\n"),
    task("শেষে মোট কয়টা নোট লাগল সেটাও প্রিন্ট করুন (একটা <code>let mut total = 0;</code> লাগবে)।"))

c.lesson("Compiler-কে বন্ধু বানান",
    say("প্রতিদিন কাজে লাগে এমন কয়েকটা command:"),
    table(["Command", "কী করে"], [
        ["<code>cargo check</code>", "binary না বানিয়ে শুধু error খোঁজে — সবচেয়ে দ্রুত"],
        ["<code>cargo fmt</code>", "কোড সুন্দর করে সাজায় (PHP-র Pint-এর মতো)"],
        ["<code>cargo clippy</code>", "ভালো অভ্যাসের পরামর্শ দেয় (PHPStan-এর মতো)"],
        ["<code>rustc --explain E0384</code>", "Error code-এর পুরো ব্যাখ্যা উদাহরণসহ"]]),
    steps("Error-এর প্রথম লাইন পড়ুন: <code>error[E0384]</code> আর ছোট বর্ণনা",
          "<code>--&gt;</code> লাইনে file আর line নম্বর", "<code>help:</code> লাইনে প্রায়ই সমাধান লেখা থাকে"),
    tip("একবারে সব error ঠিক করতে যাবেন না। প্রথমটা ঠিক করুন, আবার <code>cargo check</code> চালান।"))

c.finish("Rust 101 শেষ! 🎉",
         "আপনি এখন ছোট Rust program লিখতে পারেন। পরের কোর্সে Rust-এর সবচেয়ে গুরুত্বপূর্ণ ধারণা: Ownership।",
         recap=["<code>let</code> ডিফল্টে immutable, বদলাতে <code>mut</code>",
                "Integer ভাগে দশমিক বাদ যায়, টাকা রাখুন পয়সায়",
                "শেষ লাইনে <code>;</code> না দিলে সেটাই return",
                "<code>if</code> শর্ত শুধু <code>bool</code>, আর <code>if</code> একটা মান দেয়",
                "<code>match</code>-এ সব সম্ভাবনা ধরতে হয়",
                "Compiler error-এর <code>help:</code> লাইন পড়ুন"])

if __name__ == "__main__":
    c.build()
