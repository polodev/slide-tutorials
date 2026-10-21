"""Rust 103 — Trait, generic, closure, iterator, lifetime, smart pointer, test, crate, concurrency, async.
Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, jargon, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402

SERDE = {"serde": '{ version = "1", features = ["derive"] }', "serde_json": "1"}
TOKIO = {"tokio": '{ version = "1", features = ["full"] }'}

c = Course(slug="rust-103", title="Rust 103 — Trait, Iterator ও Concurrency", folder=Path(__file__).parent,
           subtitle="Trait (interface), generic, closure, Laravel Collection-এর মতো iterator, test, crate, thread আর async",
           series="Rust 103", next_course=("../rust-web-development/index.html", "Rust Web Development"))

c.cover("Rust 103<br>Trait, Iterator ও Concurrency",
        "এখন আপনি Rust-এর ভাষা জানেন। এই কোর্সে শিখব কীভাবে বড়, পরিষ্কার আর দ্রুত কোড লেখা হয় — যা web development-এ সরাসরি লাগবে।",
        learn=["Trait — PHP interface-এর মতো", "Generic আর trait bound", "Closure (PHP-র fn() =>)",
               "Iterator — Laravel Collection-এর মতো", "Lifetime-এর মূল ধারণা", "Box, Rc, RefCell",
               "Test লেখা আর crate ব্যবহার (serde)", "Thread, channel, Arc/Mutex আর async"],
        need="Rust 102 (ownership, struct, enum, Option, Result)।")

# ================================================================== trait
c.section("Trait")
c.lesson("Trait: একটা চুক্তি",
    say("Trait বলে দেয় একটা type-এর কী কী method থাকতেই হবে। যে type trait <code>impl</code> করবে, তাকে সব method লিখতে হবে।"),
    php_note("<code>interface Payable { public function amount(): int; }</code> আর <code>class Invoice implements Payable</code> — Rust-এ <code>trait</code> আর <code>impl Payable for Invoice</code>।"),
    code(r'''
trait Payable {
    fn amount(&self) -> u32;
}

struct Invoice { total: u32 }
struct ServiceBill { parts: u32, labour: u32 }

impl Payable for Invoice {
    fn amount(&self) -> u32 { self.total }
}

impl Payable for ServiceBill {
    fn amount(&self) -> u32 { self.parts + self.labour }
}

fn main() {
    let a = Invoice { total: 23500 };
    let b = ServiceBill { parts: 1800, labour: 500 };
    println!("Invoice: {}, Service: {}", a.amount(), b.amount());
}
'''))

c.lesson("Default method",
    say("Trait-এর ভিতরে method-এর ডিফল্ট কোড লেখা যায়। যে type চায়, সে নিজের মতো বদলাতে (override) পারে।"),
    code(r'''
trait Payable {
    fn amount(&self) -> u32;

    fn with_vat(&self) -> u32 {          // ডিফল্ট কোড
        self.amount() * 115 / 100
    }
}

struct Invoice { total: u32 }
struct Donation { total: u32 }

impl Payable for Invoice {
    fn amount(&self) -> u32 { self.total }
}

impl Payable for Donation {
    fn amount(&self) -> u32 { self.total }
    fn with_vat(&self) -> u32 { self.total }   // দানে VAT নেই
}

fn main() {
    println!("{}", Invoice { total: 1000 }.with_vat());
    println!("{}", Donation { total: 1000 }.with_vat());
}
'''),
    php_note("PHP-তে interface-এ কোড থাকে না, তাই <code>trait</code> বা abstract class লাগে। Rust trait দুটো কাজই করে।"))

c.lesson("Trait দিয়ে যেকোনো type নেওয়া",
    say("<code>impl Payable</code> parameter মানে \"Payable হলেই চলবে\"। আলাদা type একই list-এ রাখতে <code>Box&lt;dyn Payable&gt;</code>।"),
    code(r'''
trait Payable {
    fn amount(&self) -> u32;
    fn label(&self) -> String;
}

struct Invoice { no: u32, total: u32 }
struct Expense { name: String, cost: u32 }

impl Payable for Invoice {
    fn amount(&self) -> u32 { self.total }
    fn label(&self) -> String { format!("Invoice #{}", self.no) }
}
impl Payable for Expense {
    fn amount(&self) -> u32 { self.cost }
    fn label(&self) -> String { format!("খরচ: {}", self.name) }
}

fn show(item: &impl Payable) {
    println!("{:<14} {:>6}", item.label(), item.amount());
}

fn main() {
    let items: Vec<Box<dyn Payable>> = vec![
        Box::new(Invoice { no: 101, total: 23500 }),
        Box::new(Expense { name: "ভাড়া".into(), cost: 15000 }),
    ];
    for it in &items {
        println!("{:<14} {:>6}", it.label(), it.amount());
    }
    show(&Invoice { no: 102, total: 900 });
}
'''))

c.lesson("Polymorphism: এক নামে অনেক রূপ",
    say("<code>Invoice</code> আর <code>ServiceBill</code> দুটো আলাদা type, কিন্তু দুটোই <code>Payable</code>। তাই একই list-এ রেখে একই method ডাকা যায় — প্রতিটা নিজের মতো উত্তর দেয়। এটাই <b>polymorphism</b>। <code>&amp;dyn Payable</code> মানে \"Payable চুক্তি মানে এমন যেকোনো কিছুর reference\"।"),
    code(r'''
trait Payable {
    fn amount(&self) -> u32;
}

struct Invoice { total: u32 }
struct ServiceBill { parts: u32, labour: u32 }

impl Payable for Invoice {
    fn amount(&self) -> u32 { self.total }
}
impl Payable for ServiceBill {
    fn amount(&self) -> u32 { self.parts + self.labour }
}

fn main() {
    let a = Invoice { total: 23500 };
    let b = ServiceBill { parts: 1800, labour: 500 };
    let all: [&dyn Payable; 2] = [&a, &b];   // আলাদা type, একই list

    let mut sum = 0;
    for item in all {
        sum += item.amount();                  // প্রতিটা নিজের amount() চালায়
    }
    println!("মোট: {sum}");
}
'''),
    jargon(("Abstraction", "খুঁটিনাটি লুকিয়ে শুধু \"কী করে\" দেখানো — trait সেটাই করে"),
           ("Interface", "চুক্তি: কী কী method থাকবে (PHP interface = Rust trait)"),
           ("Polymorphism", "আলাদা type-কে একই ভাবে ব্যবহার করা"),
           ("Static dispatch", "কোন function চলবে তা compile-এই ঠিক (generic) — দ্রুততম"),
           ("Dynamic dispatch", "চলার সময় ঠিক হয় (<code>dyn Trait</code>) — একটু ধীর, কিন্তু আলাদা type একই list-এ")))

c.lesson("derive: কাজের trait বিনা খরচে",
    say("অনেক সাধারণ trait compiler নিজেই লিখে দেয়। <code>#[derive(...)]</code> লিখলেই হলো।"),
    table(["Trait", "কী পাবেন"], [
        ["<code>Debug</code>", "<code>{:?}</code> দিয়ে প্রিন্ট"], ["<code>Clone</code>", "<code>.clone()</code>"],
        ["<code>PartialEq</code>", "<code>==</code> দিয়ে তুলনা"], ["<code>Default</code>", "<code>Type::default()</code> — সব field ডিফল্ট মানে"]]),
    code(r'''
#[derive(Debug, Clone, PartialEq, Default)]
struct Customer {
    name: String,
    due: u32,
}

fn main() {
    let a = Customer { name: "Karim".into(), due: 500 };
    let b = a.clone();
    println!("সমান? {}", a == b);
    println!("{:?}", Customer::default());
}
'''))

c.lesson("Display: নিজের মতো করে {} দিয়ে প্রিন্ট",
    say("<code>{}</code> দিয়ে প্রিন্ট করতে <code>std::fmt::Display</code> trait নিজে লিখতে হয়।"),
    php_note("PHP-র <code>__toString()</code> magic method-এর মতো।"),
    code(r'''
use std::fmt;

struct Taka(i64);   // পয়সায় রাখা টাকা

impl fmt::Display for Taka {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "৳{}.{:02}", self.0 / 100, self.0 % 100)
    }
}

fn main() {
    let price = Taka(2350050);
    println!("দাম: {price}");
    println!("ছাড়: {}", Taka(1999));
}
'''),
    tip("<code>struct Taka(i64)</code> হলো tuple struct — একটা মানকে নতুন নাম দেওয়া, যাতে ভুল করে পয়সা আর টাকা মিশে না যায়।"))

# ================================================================== generic
c.section("Generic")
c.lesson("Generic function",
    say("<code>&lt;T&gt;</code> মানে \"যেকোনো type\"। কিন্তু T নিয়ে কী করা যাবে, সেটা trait bound দিয়ে বলতে হয়: <code>T: PartialOrd</code> মানে তুলনা করা যায়।"),
    code(r'''
fn largest<T: PartialOrd + Copy>(list: &[T]) -> T {
    let mut big = list[0];
    for &item in list {
        if item > big {
            big = item;
        }
    }
    big
}

fn main() {
    println!("{}", largest(&[1200, 3400, 2100]));
    println!("{}", largest(&[4.5, 3.9, 4.8]));
    println!("{}", largest(&['ক', 'খ', 'গ']));
}
'''),
    php_note("PHP-তে type না দিলেই যেকোনো type চলে, কিন্তু ভুল type চলার সময় ধরা পড়ে। Rust generic compile-এর সময়েই নিশ্চিত করে।"))

c.lesson("Generic struct",
    code(r'''
#[derive(Debug)]
struct Paginated<T> {
    items: Vec<T>,
    page: u32,
    total: u32,
}

impl<T> Paginated<T> {
    fn has_next(&self, per_page: u32) -> bool {
        self.page * per_page < self.total
    }
}

fn main() {
    let phones = Paginated { items: vec!["Redmi", "Vivo"], page: 1, total: 5 };
    let prices = Paginated { items: vec![17500, 21000], page: 3, total: 6 };
    println!("{:?} → পরের পাতা? {}", phones.items, phones.has_next(2));
    println!("{:?} → পরের পাতা? {}", prices.items, prices.has_next(2));
}
'''),
    php_note("Laravel-এর <code>paginate()</code> যেকোনো model-এর জন্য একই — এখানে <code>Paginated&lt;T&gt;</code> যেকোনো type-এর জন্য।"))

c.lesson("where: লম্বা bound পরিষ্কার করে লেখা",
    code(r'''
use std::fmt::Display;

fn receipt<T, U>(item: T, price: U) -> String
where
    T: Display,
    U: Display + Copy,
{
    format!("{item} ........ {price} টাকা")
}

fn main() {
    println!("{}", receipt("Charger", 650));
    println!("{}", receipt(String::from("Cover"), 250.5));
}
'''),
    say("Bound অনেক হলে <code>where</code> ব্লকে লিখলে function-এর প্রথম লাইন পরিষ্কার থাকে।"))

# ================================================================== closure + iterator
c.section("Closure ও Iterator")
c.lesson("Closure: ছোট নামহীন function",
    say("<code>|x| x * 2</code> হলো closure। এটা চারপাশের variable ব্যবহার (capture) করতে পারে।"),
    php_note("PHP 7.4-এর arrow function <code>fn($x) =&gt; $x * $rate</code> একদম একই ধারণা — PHP-তেও বাইরের <code>$rate</code> নিজে থেকেই পায়।"),
    code(r'''
fn main() {
    let vat = 15;
    let with_vat = |amount: u32| amount + amount * vat / 100;   // vat capture করল

    println!("{}", with_vat(1000));
    println!("{}", with_vat(2400));

    let mut count = 0;
    let mut tick = || count += 1;   // বদলালে closure-ও mut
    tick();
    tick();
    println!("ডাকা হলো {count} বার");
}
'''))

c.lesson("Callback আর higher-order function",
    say("Closure-কে argument হিসেবে অন্য function-এ পাঠানো যায় — \"কাজটা তুমি করো, কীভাবে সেটা আমি পরে বলে দিচ্ছি\"। এই closure-কে বলে <b>callback</b>, আর যে function closure নেয় সেটা <b>higher-order function</b>।"),
    code(r'''
fn apply(price: u32, rule: impl Fn(u32) -> u32) -> u32 {
    rule(price)
}

fn main() {
    let vat = |p| p * 115 / 100;
    let eid_offer = |p| p - 500;

    println!("VAT সহ: {}", apply(18500, vat));
    println!("ঈদ অফার: {}", apply(18500, eid_offer));
}
'''),
    php_note("PHP-র <code>array_map(fn ($p) =&gt; $p * 2, $prices)</code> — <code>fn</code> আর <code>array_map</code> ঠিক এই দুই ধারণা।"),
    jargon(("Callback", "অন্য function-কে দিয়ে রাখা function, যা সে পরে ডাকবে"),
           ("Lambda / anonymous function", "নামহীন ছোট function — Rust-এ closure"),
           ("Higher-order function", "যে function অন্য function নেয় বা ফেরত দেয় (<code>map</code>, <code>filter</code> এমনই)")))

c.lesson("Iterator: Laravel Collection-এর মতো",
    say("<code>.iter()</code> থেকে শুরু করে <code>map</code>, <code>filter</code> জুড়ে শেষে <code>collect()</code> বা <code>sum()</code>। এটা lazy — শেষ ধাপ না ডাকা পর্যন্ত কিছুই চলে না।"),
    code(r'''
fn main() {
    let prices = vec![17500, 650, 21000, 250, 9900];

    let expensive: Vec<u32> = prices.iter()
        .filter(|&&p| p >= 5000)
        .map(|&p| p * 95 / 100)        // ৫% ছাড়
        .collect();

    println!("দামি ফোন (ছাড়সহ): {:?}", expensive);
    println!("মোট: {}", prices.iter().sum::<u32>());
}
'''),
    code(r'''
<?php
$prices = [17500, 650, 21000, 250, 9900];
$expensive = array_values(array_map(fn($p) => intdiv($p * 95, 100),
    array_filter($prices, fn($p) => $p >= 5000)));
echo json_encode($expensive), "\n";
echo array_sum($prices), "\n";
''', "php", label="PHP-তে একই কাজ"),
    tip("Laravel-এ: <code>collect($prices)-&gt;filter(...)-&gt;map(...)-&gt;values()</code>। Rust-এ একই ভাবনা, কিন্তু compile-এর পর সাধারণ loop-এর মতোই দ্রুত।"))

c.lesson("Lazy: iterator দেরিতে কাজ করে",
    say("<code>map</code> লিখলেই কাজ শুরু হয় না। শেষে <code>collect</code> বা <code>sum</code> না ডাকা পর্যন্ত কিছুই চলে না — একে বলে <b>lazy evaluation</b>। নিচের আউটপুটে দেখুন \"map\" লাইনগুলো \"তৈরি হলো\"-র <b>পরে</b> এসেছে:"),
    code(r'''
fn main() {
    let prices = [18500, 41500];

    let doubled = prices.iter().map(|p| {
        println!("map চলছে: {p}");
        p * 2
    });
    println!("pipeline তৈরি হলো, কিছুই চলেনি");

    let result: Vec<i32> = doubled.collect();   // এখন সত্যিকারের কাজ
    println!("{result:?}");
}
'''),
    jargon(("Lazy evaluation", "দরকার না পড়া পর্যন্ত হিসাব না করা"),
           ("Pipeline", "ধাপে ধাপে বদলানোর সারি: <code>iter().filter().map().sum()</code>"),
           ("Consumer", "যে method শেষে মান চায় ও pipeline চালায় (<code>collect</code>, <code>sum</code>, <code>count</code>)")),
    php_note("Laravel <code>LazyCollection</code> এই ধারণাই। সাধারণ <code>Collection</code> প্রতি ধাপে পুরো array বানায়; Rust iterator সবসময় lazy, আর অতিরিক্ত array তৈরি করে না।"))

c.lesson("struct-এর list-এ iterator",
    code(r'''
struct Sale { seller: &'static str, model: &'static str, price: u32 }

fn main() {
    let sales = vec![
        Sale { seller: "Karim", model: "Redmi 13", price: 17500 },
        Sale { seller: "Nusrat", model: "Galaxy A15", price: 21000 },
        Sale { seller: "Karim", model: "Charger", price: 650 },
        Sale { seller: "Rahim", model: "Vivo Y28", price: 18000 },
    ];

    let karim: u32 = sales.iter().filter(|s| s.seller == "Karim").map(|s| s.price).sum();
    let top = sales.iter().max_by_key(|s| s.price).unwrap();
    let cheap = sales.iter().find(|s| s.price < 1000);
    let models: Vec<&str> = sales.iter().map(|s| s.model).collect();

    println!("Karim-এর বিক্রি: {karim}");
    println!("সবচেয়ে দামি: {} ({})", top.model, top.price);
    println!("১০০০-এর কম: {:?}", cheap.map(|s| s.model));
    println!("সব model: {}", models.join(", "));
}
'''),
    table(["Laravel Collection", "Rust iterator"], [
        ["<code>where()</code> / <code>filter()</code>", "<code>filter()</code>"], ["<code>pluck('model')</code>", "<code>map(|s| s.model)</code>"],
        ["<code>sum('price')</code>", "<code>map(..).sum()</code>"], ["<code>sortByDesc()->first()</code>", "<code>max_by_key()</code>"],
        ["<code>first(fn)</code>", "<code>find()</code>"]]))

c.lesson("enumerate, zip আর sort",
    code(r'''
fn main() {
    let names = ["Karim", "Nusrat", "Rahim"];
    let sales = [52000, 87000, 61000];

    let mut board: Vec<(&str, u32)> = names.iter().copied().zip(sales).collect();
    board.sort_by(|a, b| b.1.cmp(&a.1));      // বেশি থেকে কম

    for (i, (name, amount)) in board.iter().enumerate() {
        println!("{}. {name:<7} {amount:>6}", i + 1);
    }
}
'''),
    points("<code>zip</code> — দুই list জোড়া লাগায়", "<code>enumerate</code> — সাথে index দেয় (০ থেকে)",
           "<code>sort_by</code> — নিজের তুলনা; <code>b.cmp(a)</code> মানে উল্টো ক্রম"))

# ================================================================== lifetime
c.section("Lifetime")
c.lesson("Lifetime: reference কতক্ষণ বাঁচবে",
    say("দুটো reference নিয়ে একটা ফেরত দিলে compiler জানতে চায়: ফেরত দেওয়া reference কোনটার সাথে বাঁচবে?"),
    code(r'''
fn longer(a: &str, b: &str) -> &str {
    if a.len() >= b.len() { a } else { b }
}

fn main() {
    println!("{}", longer("Dhaka", "Chattogram"));
}
''', err="E0106"))

c.lesson("'a দিয়ে সম্পর্ক বলে দেওয়া",
    say("<code>'a</code> একটা নাম মাত্র। এর মানে: \"ফেরত দেওয়া reference ততক্ষণ ঠিক থাকবে, যতক্ষণ a আর b দুটোই ঠিক থাকে\"। এটা memory বদলায় না, শুধু compiler-কে সম্পর্কটা জানায়।"),
    code(r'''
fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() { a } else { b }
}

fn main() {
    let city1 = String::from("Dhaka");
    let city2 = String::from("Chattogram");
    println!("লম্বা নাম: {}", longer(&city1, &city2));
}
'''),
    tip("বেশিরভাগ সময় lifetime লিখতে হয় না, compiler নিজেই বুঝে নেয়। শুধু compiler জিজ্ঞেস করলে লিখুন।"),
    quiz("<code>&'static str</code> মানে কী?", "এমন লেখা যা পুরো program জুড়ে বেঁচে থাকে — যেমন code-এর ভিতরের <code>\"literal\"</code>।"))

# ================================================================== smart pointers
c.section("Smart pointer")
c.lesson("Box: heap-এ রাখা",
    say("<code>Box&lt;T&gt;</code> মানটা heap-এ রাখে। দরকার হয় যখন আকার compile-এর সময় জানা নেই — যেমন নিজের ভিতরে নিজেকে রাখা (tree)।"),
    code(r'''
enum Category {
    Leaf(&'static str),
    Group(&'static str, Vec<Box<Category>>),
}

fn count(c: &Category, depth: usize) -> usize {
    match c {
        Category::Leaf(name) => {
            println!("{}- {name}", "  ".repeat(depth));
            1
        }
        Category::Group(name, kids) => {
            println!("{}+ {name}", "  ".repeat(depth));
            kids.iter().map(|k| count(k, depth + 1)).sum()
        }
    }
}

fn main() {
    let tree = Category::Group("Mobile", vec![
        Box::new(Category::Leaf("Smartphone")),
        Box::new(Category::Group("Accessories", vec![
            Box::new(Category::Leaf("Charger")),
            Box::new(Category::Leaf("Cover")),
        ])),
    ]);
    println!("মোট পাতা-category: {}", count(&tree, 0));
}
'''))

c.lesson("Rc: একাধিক মালিক",
    say("Ownership-এ মালিক একজন। কিন্তু কখনো কয়েকজনকে একই data-র মালিক হতে হয় — তখন <code>Rc</code> (reference counted)। শেষ মালিক চলে গেলে data drop হয়।"),
    code(r'''
use std::rc::Rc;

struct Shop { name: String }

fn main() {
    let shop = Rc::new(Shop { name: "Rahim Mobile".into() });
    let for_pos = Rc::clone(&shop);      // কপি না, শুধু গণনা বাড়ল
    let for_report = Rc::clone(&shop);

    println!("{} — মালিক {} জন", for_pos.name, Rc::strong_count(&shop));
    drop(for_report);
    println!("একজন গেল — মালিক {} জন", Rc::strong_count(&shop));
}
'''),
    php_note("PHP-তে সব object এভাবেই চলে (refcount)। Rust-এ এটা আপনি নিজে বেছে নেন, তাই খরচটা চোখে পড়ে।"))

c.lesson("RefCell: ধার নিয়মের হিসাব চলার সময়",
    say("<code>Rc</code>-এর ভিতরের মান বদলানো যায় না। বদলাতে <code>Rc&lt;RefCell&lt;T&gt;&gt;</code>। নিয়ম ভাঙলে compile error না, চলার সময় panic।"),
    code(r'''
use std::cell::RefCell;
use std::rc::Rc;

fn main() {
    let cart = Rc::new(RefCell::new(Vec::<&str>::new()));
    let pos = Rc::clone(&cart);
    let app = Rc::clone(&cart);

    pos.borrow_mut().push("Charger");
    app.borrow_mut().push("Cover");
    println!("Cart: {:?}", cart.borrow());
}
'''),
    warn("RefCell সহজ মনে হলেও আগে সাধারণ <code>&mut</code> দিয়ে চেষ্টা করুন। Web server-এ thread-এর মধ্যে ভাগ করতে <code>Arc&lt;Mutex&gt;</code> লাগবে (এই কোর্সেই সামনে)।"))

# ================================================================== tests + crates
c.section("Test ও Crate")
c.lesson("Test-এর জার্গন",
    say("Test লেখার আগে কয়েকটা শব্দ চেনা ভালো — job interview আর team-এর কথাবার্তায় বারবার আসে।"),
    jargon(("Unit test", "একটা ছোট function/অংশের আলাদা পরীক্ষা (<code>#[test]</code>)"),
           ("Integration test", "অনেক অংশ একসাথে জুড়ে পরীক্ষা (যেমন database সহ API)"),
           ("Assertion", "\"এটা অবশ্যই সত্য\" দাবি — <code>assert_eq!</code>; মিথ্যা হলে test ব্যর্থ"),
           ("Regression", "আগে ঠিক ছিল, নতুন বদলে ভেঙে গেছে এমন bug — test এটা ধরে"),
           ("TDD (Test-Driven Development)", "আগে test লিখে (ব্যর্থ), তারপর পাস করার মতো code লেখা"),
           ("Coverage", "test কতটুকু code ছুঁয়ে দেখেছে তার শতাংশ")),
    php_note("PHPUnit-এর <code>$this-&gt;assertEquals()</code> আর Pest-এর <code>expect()</code>; Rust-এ <code>assert_eq!</code> macro আর test সরাসরি <code>cargo test</code>।"))

c.lesson("Test লেখা",
    say("Function-এর উপরে <code>#[test]</code>, ভিতরে <code>assert_eq!</code>। <code>cargo test</code> সব test চালায় — আলাদা package লাগে না।"),
    php_note("PHPUnit/Pest-এর <code>expect($x)-&gt;toBe(5)</code> এর মতো। Rust-এ test সাধারণত একই file-এর নিচে <code>mod tests</code>-এ থাকে।"),
    code(r'''
fn vat(amount: u32) -> u32 {
    amount * 15 / 100
}

fn discount(amount: u32) -> u32 {
    if amount >= 10_000 { amount / 10 } else { 0 }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn vat_is_15_percent() {
        assert_eq!(vat(1000), 150);
    }

    #[test]
    fn no_discount_below_10k() {
        assert_eq!(discount(9_999), 0);
    }

    #[test]
    fn ten_percent_from_10k() {
        assert_eq!(discount(20_000), 2_000);
    }
}
''', test=True),
    shell("$ cargo test"))

c.lesson("Test ব্যর্থ হলে",
    say("কোডে bug থাকলে test ঠিক কোন মান আশা করেছিল আর কী পেয়েছে, দুটোই দেখায়।"),
    code(r'''
fn delivery_charge(district: &str) -> u32 {
    if district == "Dhaka" { 60 } else { 120 }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dhaka_is_60() {
        assert_eq!(delivery_charge("Dhaka"), 60);
    }

    #[test]
    fn gazipur_is_also_inside_dhaka_rate() {
        assert_eq!(delivery_charge("Gazipur"), 60);   // নতুন নিয়ম, কোড এখনো পুরনো
    }
}
''', test=True, panic=True))

c.lesson("Library, framework আর crate",
    say("তিনটা শব্দ প্রায়ই গুলিয়ে যায়। মূল পার্থক্য: <b>নিয়ন্ত্রণ কার হাতে</b>।"),
    table(["", "মানে", "উদাহরণ"], [
        ["<b>Library</b>", "আপনি যখন চান তখন ডাকেন", "serde, chrono"],
        ["<b>Framework</b>", "কাঠামো দেয়; সে আপনার code ডাকে", "axum, Leptos, Topcoat; Laravel"],
        ["<b>Crate</b>", "Rust-এ যেকোনো package (library বা program)", "crates.io-তে আছে"],
        ["<b>Registry</b>", "package রাখার দোকান", "crates.io (PHP-তে Packagist)"]]),
    jargon(("Semantic versioning", "<code>1.2.3</code> = major.minor.patch; major বদলালে পুরনো code ভাঙতে পারে"),
           ("Lock file", "<code>Cargo.lock</code> — ঠিক কোন version ব্যবহার হয়েছে তার তালিকা (<code>composer.lock</code>-এর মতো)"),
           ("Dependency", "আপনার code যে crate-এর উপর নির্ভর করে")))

c.lesson("Crate ব্যবহার: serde দিয়ে JSON",
    say("<code>cargo add</code> দিয়ে crate যোগ করি। JSON-এর জন্য সবাই <code>serde</code> + <code>serde_json</code> ব্যবহার করে।"),
    shell("$ cargo add serde --features derive\n$ cargo add serde_json"),
    code(r'''
use serde::Serialize;

#[derive(Serialize)]
struct Product {
    id: u32,
    name: String,
    price: u32,
    in_stock: bool,
}

fn main() {
    let p = Product { id: 7, name: "Redmi 13".into(), price: 17500, in_stock: true };
    println!("{}", serde_json::to_string(&p).unwrap());
    println!("{}", serde_json::to_string_pretty(&p).unwrap());
}
''', deps=SERDE),
    php_note("<code>json_encode($product)</code> বা Laravel-এর <code>return $product;</code> — Rust-এ <code>#[derive(Serialize)]</code>।"))

c.lesson("JSON থেকে struct",
    say("<code>Deserialize</code> করলে JSON পড়ে struct বানায়। কোনো field না মিললে বা type ভুল হলে <code>Err</code> দেয় — ভুল data ভিতরে ঢোকে না।"),
    code(r'''
use serde::Deserialize;

#[derive(Deserialize)]
struct Order {
    customer: String,
    items: Vec<String>,
    paid: bool,
}

fn main() {
    let good = r#"{"customer":"Nusrat","items":["Charger","Cover"],"paid":true}"#;
    let bad = r#"{"customer":"Karim","items":"Charger","paid":true}"#;

    let order: Order = serde_json::from_str(good).unwrap();
    println!("{} — {} আইটেম — paid: {}", order.customer, order.items.len(), order.paid);

    match serde_json::from_str::<Order>(bad) {
        Ok(o) => println!("{}", o.customer),
        Err(e) => println!("ভুল JSON: {e}"),
    }
}
''', deps=SERDE),
    tip("Laravel-এ <code>$request-&gt;validate()</code> যে কাজ করে, Rust web-এ অনেকটা সেটাই হয় শুধু type দিয়ে।"))

# ================================================================== concurrency
c.section("Concurrency")
c.lesson("Concurrency-র জার্গন",
    say("একসাথে অনেক কাজের জগতে শব্দগুলো ভয়ংকর শোনায়, কিন্তু ধারণা সোজা। Rust-এর বিশেষত্ব: এই bug-গুলোর বেশিরভাগ compile-এই ধরা পড়ে।"),
    jargon(("Concurrency", "অনেক কাজ একসাথে <b>চলমান</b> (পালা করে হতে পারে)"),
           ("Parallelism", "অনেক কাজ আক্ষরিক <b>একই মুহূর্তে</b> (একাধিক CPU core-এ)"),
           ("Race condition", "দুই thread একই data একসাথে বদলাচ্ছে, ফল নির্ভর করছে কে আগে — এলোমেলো bug"),
           ("Deadlock", "দুজন একে অপরের জন্য অপেক্ষা করছে, কেউ এগোয় না"),
           ("Thread-safe", "একাধিক thread-এ নিরাপদে ব্যবহার করা যায়"),
           ("Mutex", "তালা — একবারে একজনই ভিতরে ঢুকতে পারে"),
           ("Atomic", "মাঝপথে ভাঙা যায় না এমন ছোট ক্রিয়া")),
    php_note("PHP-র প্রতি request আলাদা process, তাই এই সমস্যা কম। Rust server-এ একটাই process-এ হাজারো request — তাই এই শব্দগুলো জানা জরুরি।"))

c.lesson("Thread: একসাথে কয়েকটা কাজ",
    say("<code>thread::spawn</code> নতুন thread চালায়। <code>join()</code> দিয়ে শেষ হওয়া পর্যন্ত অপেক্ষা করি। <code>move</code> দিয়ে data thread-এ পাঠাই।"),
    code(r'''
use std::thread;

fn main() {
    let branches = vec!["Mirpur", "Uttara", "Gulshan"];
    let mut handles = Vec::new();

    for (i, branch) in branches.into_iter().enumerate() {
        handles.push(thread::spawn(move || {
            let total = (i as u32 + 1) * 10_000;   // ধরি হিসাব করতে সময় লাগে
            (branch, total)
        }));
    }

    for h in handles {
        let (branch, total) = h.join().unwrap();
        println!("{branch}: {total}");
    }
}
'''),
    php_note("সাধারণ PHP একটা request-এ একটা কাজ করে। একসাথে কাজ চালাতে Laravel queue বা আলাদা process লাগে। Rust এক program-এর ভিতরেই নিরাপদে পারে।"))

c.lesson("Channel: thread থেকে বার্তা পাঠানো",
    say("<code>mpsc::channel()</code> একটা পাইপ: অনেকে পাঠাতে (<code>tx</code>) পারে, একজন নেয় (<code>rx</code>)।"),
    code(r'''
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();

    for branch in ["Mirpur", "Uttara", "Gulshan"] {
        let tx = tx.clone();
        thread::spawn(move || {
            let sale = branch.len() as u32 * 1000;
            tx.send((branch, sale)).unwrap();
        });
    }
    drop(tx);   // মূল tx বন্ধ, নইলে rx চিরকাল অপেক্ষা করবে

    let mut total = 0;
    for (branch, sale) in rx {
        total += sale;
        println!("পেলাম {branch}");
    }
    println!("সব শাখা মিলে: {total}");
}
'''),
    warn("Thread কোনটা আগে শেষ করবে তার ঠিক নেই — \"পেলাম\" লাইনের ক্রম প্রতিবার বদলাতে পারে, কিন্তু মোট সবসময় একই।"))

c.lesson("Arc + Mutex: ভাগ করা data নিরাপদে বদলানো",
    say("অনেক thread একটা মান বদলাতে চাইলে: <code>Arc</code> (thread-safe Rc) দিয়ে ভাগ, <code>Mutex</code> দিয়ে একবারে একজন। Web server-এর shared state ঠিক এভাবেই।"),
    code(r'''
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let stock = Arc::new(Mutex::new(100));
    let mut handles = vec![];

    for _ in 0..10 {
        let stock = Arc::clone(&stock);
        handles.push(thread::spawn(move || {
            let mut s = stock.lock().unwrap();   // তালা দিলাম
            *s -= 3;                              // ৩টা বিক্রি
        }));                                      // scope শেষে তালা খুলল
    }
    for h in handles {
        h.join().unwrap();
    }
    println!("বাকি স্টক: {}", stock.lock().unwrap());
}
'''),
    quiz("Mutex ছাড়া শুধু <code>Arc&lt;i32&gt;</code> দিয়ে বদলাতে চাইলে কী হবে?",
         "Compile হবে না। Rust data race-কে compile error বানায় — এটাই \"fearless concurrency\"।"))

c.lesson("Async-এর জার্গন",
    say("<code>async/await</code>-এর চারপাশের শব্দ — web server আর Leptos/Topcoat-এ বারবার আসবে।"),
    jargon(("Blocking", "অপেক্ষার সময় thread আটকে বসে থাকে"),
           ("Non-blocking", "অপেক্ষার সময় thread অন্য কাজ করে"),
           ("I/O-bound", "বেশিরভাগ সময় কাটে অপেক্ষায় (network, database, file) — async এখানে কার্যকর"),
           ("CPU-bound", "বেশিরভাগ সময় হিসাব কষতে যায় — async নয়, thread দরকার"),
           ("Runtime / executor", "async code চালানোর ব্যবস্থা (tokio); Rust নিজে দেয় না"),
           ("Future", "\"এখনো হয়নি, পরে হবে\" এমন একটা মান; <code>.await</code> দিয়ে ফল নেওয়া")))

c.lesson("async/await: অপেক্ষার সময় অন্য কাজ",
    say("Network বা database-এর জন্য অপেক্ষায় thread বসিয়ে রাখা অপচয়। <code>async</code> function অপেক্ষার সময় অন্য কাজ চালাতে দেয়। চালাতে runtime লাগে — সবচেয়ে জনপ্রিয় <b>tokio</b>।"),
    code(r'''
use std::time::Duration;
use tokio::time::sleep;

async fn fetch_price(model: &str, ms: u64) -> (String, u32) {
    sleep(Duration::from_millis(ms)).await;   // ধরি API call
    (model.to_string(), ms as u32 * 100)
}

#[tokio::main]
async fn main() {
    let start = std::time::Instant::now();
    let (a, b) = tokio::join!(fetch_price("Redmi 13", 200), fetch_price("Galaxy A15", 300));
    println!("{a:?}\n{b:?}");
    println!("সময় লাগল ~{} ms (২০০ + ৩০০ না!)", start.elapsed().as_millis() / 100 * 100);
}
''', deps=TOKIO),
    php_note("PHP request সাধারণত একটার পর একটা অপেক্ষা করে। Rust web framework (axum) পুরোটাই async — হাজার request একসাথে অল্প thread-এ।"))

# ================================================================== project
c.section("Project")
c.lesson("Project: বিক্রির CSV থেকে রিপোর্ট",
    say("CSV লাইন পড়া, ভুল লাইন বাদ দেওয়া, শাখা ধরে যোগফল আর সেরা model — struct, Result, iterator আর BTreeMap একসাথে।"),
    code(r'''
use std::collections::BTreeMap;

#[derive(Debug)]
struct Sale { branch: String, model: String, price: u32 }

fn parse(line: &str) -> Result<Sale, String> {
    let f: Vec<&str> = line.split(',').map(|x| x.trim()).collect();
    let [branch, model, price] = f.as_slice() else {
        return Err(format!("৩টা ঘর নেই: {line}"));
    };
    let price = price.parse().map_err(|_| format!("দাম ভুল: {line}"))?;
    Ok(Sale { branch: branch.to_string(), model: model.to_string(), price })
}

fn main() {
    let csv = "Mirpur, Redmi 13, 17500
Uttara, Galaxy A15, 21000
Mirpur, Charger, 650
Uttara, Vivo Y28, 18OOO
Gulshan, iPhone 15
Gulshan, Galaxy A15, 21000";

    let (ok, bad): (Vec<_>, Vec<_>) = csv.lines().map(parse).partition(|r| r.is_ok());
    let sales: Vec<Sale> = ok.into_iter().map(Result::unwrap).collect();

    let mut by_branch: BTreeMap<&str, u32> = BTreeMap::new();
    for s in &sales {
        *by_branch.entry(&s.branch).or_insert(0) += s.price;
    }
    for (b, total) in &by_branch {
        println!("{b:<8} {total:>6}");
    }
    let best = sales.iter().max_by_key(|s| s.price).unwrap();
    println!("সবচেয়ে দামি বিক্রি: {} ({})", best.model, best.branch);
    for e in bad {
        println!("বাদ: {}", e.unwrap_err());
    }
}
'''),
    task("রিপোর্টের জন্য একটা <code>#[test]</code> লিখুন: ভুল দামের লাইন <code>Err</code> দেয় কিনা।"))

c.lesson("Rust 103-এর জার্গন কার্ড",
    table(["শব্দ", "এক লাইনে"], [
        ["Trait / Interface", "type-এর কাছে কী কী থাকতে হবে তার চুক্তি"],
        ["Polymorphism", "আলাদা type একই চুক্তিতে ব্যবহার"],
        ["Static / dynamic dispatch", "কোন method চলবে compile-এ ঠিক / চলার সময় ঠিক"],
        ["Callback / lambda", "অন্যকে দেওয়া নামহীন function"],
        ["Lazy evaluation", "দরকার না হওয়া পর্যন্ত কাজ না করা"],
        ["Unit test / Assertion", "ছোট অংশের পরীক্ষা / \"এটা সত্য হতেই হবে\" দাবি"],
        ["Library / Framework", "আপনি ডাকেন / সে আপনাকে ডাকে"],
        ["Race condition / Deadlock", "একসাথে বদলানোর গোলমাল / পরস্পরের জন্য অপেক্ষা"],
        ["Blocking / Non-blocking", "বসে থাকা / অপেক্ষায় অন্য কাজ"]]))

c.finish("Rust 103 শেষ! 🎉",
         "Trait, iterator, test, crate আর concurrency — web server বানানোর সব উপকরণ এখন হাতে। চলুন Laravel-এর মতো একটা API বানাই।",
         recap=["Trait = interface; <code>derive</code> দিয়ে সাধারণ trait বিনা খরচে",
                "Generic + trait bound = নিরাপদ, পুনঃব্যবহারযোগ্য কোড",
                "Iterator chain = Laravel Collection, কিন্তু loop-এর মতো দ্রুত",
                "<code>#[test]</code> আর <code>cargo test</code> সাথেই আসে",
                "serde = JSON; tokio = async runtime",
                "Thread-এ ভাগ করা data: <code>Arc&lt;Mutex&lt;T&gt;&gt;</code>"])

if __name__ == "__main__":
    c.build()
