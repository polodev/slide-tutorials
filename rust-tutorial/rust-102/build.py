"""Rust 102 — Ownership, borrowing, struct, enum, Option/Result, Vec/HashMap, module.
Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, jargon, php_note, points, quiz, say, steps, table, task, tip, warn  # noqa: E402

c = Course(slug="rust-102", title="Rust 102 — Ownership ও Data", folder=Path(__file__).parent,
           subtitle="Rust-এর আসল শক্তি: ownership, borrowing, struct, enum, Option, Result, Vec আর HashMap",
           series="Rust 102", next_course=("../rust-103/index.html", "Rust 103 — Trait, Iterator ও Concurrency"))

c.cover("Rust 102<br>Ownership ও Data",
        "এই কোর্সটাই Rust-এর হৃদয়। Ownership বুঝলে বাকি Rust সহজ। তারপর struct আর enum দিয়ে নিজের data type বানাব।",
        learn=["Stack, heap আর ownership-এর ৩ নিয়ম", "Move, clone আর Copy", "Borrowing: & আর &mut",
               "String, &str আর বাংলা লেখা", "struct, impl আর method", "enum, Option (null নেই!)",
               "Vec আর HashMap", "Result আর ? দিয়ে error সামলানো"],
        need="Rust 101 (variable, function, if, loop, match)।")

# ================================================================== ownership
c.section("Ownership")
c.lesson("Stack আর Heap",
    say("Program-এর data দুই জায়গায় থাকে। কোনটা কোথায় থাকে বুঝলে ownership বোঝা সহজ।"),
    table(["", "Stack", "Heap"], [
        ["কী থাকে", "আকার জানা ছোট data: <code>i32</code>, <code>bool</code>, <code>char</code>", "আকার বদলায় এমন data: <code>String</code>, <code>Vec</code>"],
        ["গতি", "খুব দ্রুত", "একটু ধীর (খুঁজে জায়গা নিতে হয়)"],
        ["কে পরিষ্কার করে", "function শেষ হলেই", "যে variable \"মালিক\", সে scope-এর বাইরে গেলে"]]),
    php_note("PHP-তে garbage collector আর reference count এই কাজ করে, আপনি টেরই পান না। Rust-এ GC নেই — compiler <b>ownership</b> নিয়ম দেখে ঠিক করে কখন memory ছাড়বে।"))

c.lesson("Ownership-এর ৩ নিয়ম",
    steps("প্রতিটি মানের একজন <b>মালিক (owner)</b> variable থাকে",
          "একসাথে মালিক <b>একজনই</b>",
          "মালিক scope (<code>{ }</code>)-এর বাইরে গেলে মানটা <b>drop</b> হয়, memory ফেরত যায়"),
    code(r'''
fn main() {
    {
        let shop = String::from("Rahim Mobile");  // shop মালিক
        println!("ভিতরে: {shop}");
    }   // এখানে shop drop হলো, memory ফেরত

    // println!("{shop}");  // এখানে shop আর নেই
    println!("block শেষ");
}
'''),
    tip("এই তিনটা নিয়মই পুরো কোর্সের ভিত্তি। বাকি সব এগুলো থেকেই আসে।"))

c.lesson("Move: মালিকানা হাতবদল",
    say("<code>String</code> এক variable থেকে আরেকটায় দিলে কপি হয় না — <b>মালিকানা চলে যায় (move)</b>। আগের variable আর ব্যবহার করা যায় না।"),
    php_note("PHP-তে <code>$b = $a;</code> করলে string কপি হয়, দুটোই চলে। Rust-এ String-এর জন্য এটা move।"),
    code(r'''
fn main() {
    let s1 = String::from("Samsung A15");
    let s2 = s1;              // মালিকানা s2-তে গেল
    println!("{s2}");
    println!("{s1}");          // s1 এখন খালি
}
''', err="E0382"),
    quiz("কেন Rust দুটোকেই চলতে দেয় না?",
         "দুজন মালিক থাকলে scope শেষে দুজনই একই memory ছাড়তে চাইত (double free)। একজন মালিক মানে এই bug অসম্ভব।"))

c.lesson("clone: সত্যিকারের কপি",
    say("সত্যি দুটো আলাদা কপি চাইলে <code>.clone()</code>। এতে heap-এর data-ও কপি হয়, তাই বড় data-তে খরচ আছে।"),
    code(r'''
fn main() {
    let s1 = String::from("Samsung A15");
    let s2 = s1.clone();       // heap-এ নতুন কপি
    println!("s1 = {s1}, s2 = {s2}");
}
'''),
    tip("শুরুতে compile না হলে <code>clone()</code> দিয়ে চালিয়ে নেওয়া দোষের না। পরে borrowing শিখে অপ্রয়োজনীয় clone সরাবেন।"))

c.lesson("Copy type: সংখ্যা move হয় না",
    say("<code>i32</code>, <code>f64</code>, <code>bool</code>, <code>char</code> — এগুলো ছোট আর পুরোটাই stack-এ, তাই দিলে নিজে থেকেই কপি হয়। এদের বলে <b>Copy</b> type।"),
    code(r'''
fn main() {
    let price = 23500;
    let copy = price;          // কপি হলো, move না
    println!("{price} {copy}");

    let ok = true;
    let ok2 = ok;
    println!("{ok} {ok2}");
}
'''),
    table(["Copy (কপি হয়)", "Move (মালিকানা যায়)"], [
        ["<code>i32</code>, <code>u64</code>, <code>f64</code>, <code>bool</code>, <code>char</code>", "<code>String</code>, <code>Vec</code>, <code>HashMap</code>"],
        ["শুধু Copy দিয়ে বানানো tuple: <code>(i32, bool)</code>", "এগুলো থাকা struct"]]))

c.lesson("Function-এ দিলেও move",
    say("Function-এ String পাঠালে মালিকানা function-এ চলে যায়। Function শেষে সেটা drop হয়।"),
    code(r'''
fn print_invoice(customer: String) {
    println!("Invoice: {customer}");
}   // customer এখানে drop

fn main() {
    let name = String::from("Karim");
    print_invoice(name);
    println!("আবার: {name}");   // name তো চলে গেছে
}
''', err="E0382"),
    say("সমাধান: মালিকানা না দিয়ে শুধু <b>ধার (borrow)</b> দেওয়া। পরের পাঠ।"))

# ================================================================== borrowing
c.section("Borrowing")
c.lesson("& দিয়ে ধার দেওয়া",
    say("<code>&name</code> মানে \"দেখতে দিলাম, মালিকানা না\"। Function-এর parameter হয় <code>&String</code> বা ভালো হলো <code>&str</code>।"),
    php_note("PHP object যেমন handle হিসেবে যায়, অনেকটা সেরকম — কিন্তু Rust-এ ধার নেওয়া জিনিস বদলানো যায় না (যদি না &mut হয়)।"),
    code(r'''
fn print_invoice(customer: &str) {
    println!("Invoice: {customer}");
}

fn main() {
    let name = String::from("Karim");
    print_invoice(&name);       // ধার দিলাম
    print_invoice(&name);       // আবারও দেওয়া যায়
    println!("মালিক এখনো name: {name}");
}
'''))

c.lesson("&mut: বদলানোর জন্য ধার",
    say("Function-কে বদলানোর অনুমতি দিতে <code>&mut</code>। Variable-টাও <code>mut</code> হতে হবে।"),
    code(r'''
fn add_item(cart: &mut Vec<String>, item: &str) {
    cart.push(item.to_string());
}

fn main() {
    let mut cart = Vec::new();
    add_item(&mut cart, "Charger");
    add_item(&mut cart, "Earphone");
    println!("Cart: {:?}", cart);
}
'''),
    php_note("<code>function addItem(array &$cart, $item)</code> — PHP-র <code>&amp;</code> reference-এর মতো।"))

c.lesson("নিয়ম: একসাথে একটা &mut, অথবা অনেক &",
    say("একই সময়ে হয় <b>অনেকে শুধু দেখবে (&)</b>, নয়তো <b>একজন বদলাবে (&mut)</b>। দুটো একসাথে না। এভাবেই Rust data race আটকায়।"),
    code(r'''
fn main() {
    let mut stock = vec![5, 3, 8];
    let first = &stock[0];        // দেখছি
    stock.push(10);               // বদলাচ্ছি — অথচ first এখনো ব্যবহার হবে
    println!("প্রথম: {first}");
}
''', err="E0502"),
    tip("কেন? <code>push</code>-এ Vec নতুন জায়গায় সরে যেতে পারে, তখন <code>first</code> ভুল memory দেখাত। Compiler এটা আগেই আটকাল।"))

c.lesson("Reference ঝুলে থাকতে পারে না",
    say("যে মান মরে যাবে তার reference ফেরত দেওয়া যায় না। PHP বা C-তে এই ধরনের bug চলার সময় ধরা পড়ে; Rust compile-এর সময়েই আটকায়।"),
    code(r'''
fn make_name() -> &String {
    let s = String::from("Karim");
    &s
}   // s এখানে drop, অথচ তার reference ফেরত দিচ্ছি

fn main() {
    println!("{}", make_name());
}
''', err="E0106"),
    say("সমাধান সহজ: reference না দিয়ে মালিকানাসহ <code>String</code> ফেরত দিন: <code>fn make_name() -&gt; String</code>।"))

c.lesson("Memory safety: Rust কী আটকায়",
    say("Ownership নিয়ম আসলে কিছু পুরনো মারাত্মক bug আটকানোর জন্য। এই শব্দগুলো C/C++-এর দুনিয়ায় নিয়মিত শোনা যায়, Rust-এ এগুলো compile-এই ধরা পড়ে।"),
    jargon(("Memory safety", "নিজের memory-র ভুল ব্যবহার (ভুল জায়গা পড়া, দুইবার মুছা) থেকে সুরক্ষা"),
           ("Dangling pointer / reference", "যে জিনিসের দিকে নির্দেশ করছে সেটা আগেই মুছে গেছে — আগের lesson-এর error"),
           ("Use-after-free", "মুছে ফেলা memory আবার ব্যবহার"),
           ("Double free", "একই জিনিস দুইবার মুছতে যাওয়া — move নিয়ম এটা আটকায়"),
           ("Null pointer", "\"কিছু নেই\" কিন্তু ব্যবহার করতে গেলে crash — Rust-এ <code>Option</code> আছে, null নেই"),
           ("Garbage collector (GC)", "চলার সময় যে প্রক্রিয়া আর-লাগে-না memory পরিষ্কার করে (PHP-তে আছে); Rust-এ নেই, ownership compile-এই ঠিক করে")),
    php_note("PHP-তে memory আপনাকে ভাবতে হয় না, কারণ GC আছে — বিনিময়ে একটু ধীর আর বেশি memory। Rust GC ছাড়াই নিরাপদ।"))

c.lesson("Slice: পুরোটা না, একটা অংশ ধার",
    say("<code>&s[0..5]</code> হলো String-এর একটা অংশের reference (<code>&str</code>)। Array/Vec-এর অংশ হলো <code>&[T]</code>।"),
    code(r'''
fn first_word(s: &str) -> &str {
    match s.find(' ') {
        Some(i) => &s[..i],
        None => s,
    }
}

fn main() {
    let model = String::from("Xiaomi Redmi Note 13");
    println!("Brand: {}", first_word(&model));

    let sales = [1200, 3400, 2100, 5000];
    let last_two = &sales[2..];
    println!("শেষ দুই দিন: {:?}", last_two);
}
'''),
    tip("Function-এ text নিতে <code>&str</code> ব্যবহার করুন — তাহলে <code>String</code> আর <code>\"literal\"</code> দুটোই পাঠানো যায়।"))

c.lesson("বাংলা লেখা: byte বনাম অক্ষর",
    say("Rust-এর String হলো UTF-8 byte। বাংলা অক্ষর সাধারণত ৩ byte। তাই <code>len()</code> byte গোনে, অক্ষর গুনতে <code>chars().count()</code>।"),
    code(r'''
fn main() {
    let word = "ঢাকা";
    println!("byte: {}", word.len());
    println!("char: {}", word.chars().count());
    for ch in word.chars() {
        print!("[{ch}] ");
    }
    println!();
}
'''),
    php_note("PHP-তে <code>strlen()</code> byte গোনে, <code>mb_strlen()</code> অক্ষর — Rust-এ <code>len()</code> আর <code>chars().count()</code>।"))

c.lesson("বাংলা কাটতে সাবধান",
    say("Byte index দিয়ে কাটলে অক্ষরের মাঝখানে পড়লে program panic করে। বাংলায় <code>chars()</code> দিয়ে কাজ করুন।"),
    code(r'''
fn main() {
    let word = "ঢাকা";
    let first: String = word.chars().take(2).collect();
    println!("প্রথম ২ char: {first}");
    println!("{}", &word[0..2]);   // ২ byte = অক্ষরের মাঝখান
}
''', panic=True))

# ================================================================== struct
c.section("Struct")
c.lesson("struct: নিজের data type",
    say("কয়েকটা field একসাথে বেঁধে নতুন type বানাতে <code>struct</code>। PHP class-এর property অংশটুকুর মতো।"),
    code(r'''
struct Product {
    name: String,
    price: u32,
    stock: u32,
}

fn main() {
    let phone = Product {
        name: String::from("Redmi Note 13"),
        price: 23500,
        stock: 4,
    };
    println!("{} — {} টাকা — স্টক {}", phone.name, phone.price, phone.stock);
}
'''),
    php_note("<code>class Product { public string $name; public int $price; }</code> — Rust-এ data (struct) আর method (impl) আলাদা ব্লকে লেখা হয়।"))

c.lesson("impl: method যোগ করা",
    say("<code>impl</code> ব্লকে method লিখি। প্রথম parameter <code>&self</code> মানে \"এই product টা\" — PHP-র <code>$this</code>।"),
    code(r'''
struct Product {
    name: String,
    price: u32,
    stock: u32,
}

impl Product {
    fn stock_value(&self) -> u32 {
        self.price * self.stock
    }

    fn is_low(&self) -> bool {
        self.stock < 3
    }
}

fn main() {
    let p = Product { name: "Vivo Y28".to_string(), price: 18000, stock: 2 };
    println!("{}: স্টকের দাম {} টাকা", p.name, p.stock_value());
    println!("স্টক কম? {}", p.is_low());
}
'''))

c.lesson("new() আর &mut self",
    say("<code>self</code> ছাড়া function হলো associated function — <code>Product::new()</code> দিয়ে ডাকা হয়, PHP-র constructor বা static method-এর মতো। বদলাতে চাইলে <code>&mut self</code>।"),
    code(r'''
struct Product {
    name: String,
    stock: u32,
}

impl Product {
    fn new(name: &str) -> Self {
        Self { name: name.to_string(), stock: 0 }
    }

    fn restock(&mut self, qty: u32) {
        self.stock += qty;
    }
}

fn main() {
    let mut p = Product::new("Realme C67");
    p.restock(5);
    p.restock(2);
    println!("{}: {}টা", p.name, p.stock);
}
'''),
    php_note("<code>new Product('Realme')</code> → <code>Product::new(\"Realme\")</code>। Rust-এ <code>new</code> শুধু একটা নাম, বিশেষ keyword না।"))

c.lesson("Attribute: #[...] মানে কী?",
    say("Struct বা function-এর ঠিক উপরে <code>#[...]</code> লেখা দেখেছেন? একে বলে <b>attribute</b> — compiler-কে দেওয়া একটা নির্দেশ বা তথ্য। নিচে <code>Debug</code> চাওয়া হচ্ছে, কিন্তু struct-কে সেই ক্ষমতা দেওয়া হয়নি:"),
    code(r'''
struct Customer {
    name: String,
    due: i64,
}

fn main() {
    let c = Customer { name: "Nusrat".into(), due: 1500 };
    println!("{:?}", c);
}
''', err="E0277"),
    php_note("PHP 8-এও একই চিহ্ন: <code>#[Route('/home')]</code>, <code>#[Test]</code>। Laravel-এ attribute দিয়ে route/validation লেখা এখন চালু হচ্ছে। Rust-এ attribute এর চেয়েও গভীরে কাজ করে — compiler নিজে code বানিয়ে দেয়।"),
    jargon(("Attribute", "<code>#[...]</code> — নিচের item-এর (struct/function) জন্য compiler-কে নির্দেশ"),
           ("<code>#![...]</code>", "ভিতরের attribute — পুরো file বা crate-এর জন্য (শুরুতে লেখা হয়)"),
           ("Annotation", "অন্য ভাষায় একই ধারণার নাম (Java, PHP)")))

c.lesson("Attribute-এর পরিবার",
    say("এই কোর্স-সিরিজে যে attribute-গুলো দেখবেন, সব একসাথে। প্রতিটার কাজ আলাদা, কিন্তু লেখার ধরন এক।"),
    table(["Attribute", "কাজ", "কোথায়"], [
        ["<code>#[derive(Debug)]</code>", "compiler একটা trait-এর code নিজে লিখে দেয়", "এই কোর্স, Rust 103"],
        ["<code>#[test]</code>", "function-টা test হিসেবে চিহ্নিত", "Rust 103"],
        ["<code>#[cfg(test)]</code>", "শুধু শর্ত মিললে এই code compile হবে", "Rust 103"],
        ["<code>#[allow(dead_code)]</code>", "নির্দিষ্ট warning চুপ করানো", "—"],
        ["<code>#[tokio::main]</code>", "<code>async fn main</code>-কে চালানোর ব্যবস্থা বানায়", "Rust Web Development"],
        ["<code>#[serde(default)]</code>", "serde crate-কে নির্দেশ", "Rust Web Development"],
        ["<code>#[component]</code>, <code>#[page]</code>", "framework-এর function চিহ্নিত", "Leptos, Topcoat"]]),
    jargon(("Procedural macro", "attribute আর derive-এর ভিতরের শক্তি — Rust code পড়ে নতুন Rust code লেখে"),
           ("Boilerplate", "বারবার একই ছাঁচে লিখতে হয় এমন একঘেয়ে code — derive সেটা কমায়")),
    tip("পরের lesson-এ <code>#[derive(Debug)]</code> বসিয়ে ঠিক এই ভুলটাই সারাবেন।"))

c.lesson("#[derive(Debug)]: struct প্রিন্ট করা",
    say("<code>{:?}</code> দিয়ে struct প্রিন্ট করতে <code>#[derive(Debug)]</code> লাগে। <code>{:#?}</code> সুন্দর করে লাইন ভেঙে দেখায় — PHP-র <code>dd()</code>/<code>print_r</code>-এর মতো।"),
    code(r'''
#[derive(Debug)]
struct Customer {
    name: String,
    phone: String,
    due: i64,
}

fn main() {
    let c = Customer {
        name: "Nusrat".into(),
        phone: "01711000000".into(),
        due: 1500,
    };
    println!("{:?}", c);
    println!("{:#?}", c);
    println!("{} ({}) এর বাকি {} টাকা", c.name, c.phone, c.due);
}
'''))

# ================================================================== enum
c.section("Enum ও Option")
c.lesson("enum: কয়েকটার মধ্যে একটা",
    say("কোনো মান যদি নির্দিষ্ট কয়েকটার একটা হয় — যেমন payment-এর মাধ্যম — তাহলে <code>enum</code>।"),
    code(r'''
#[derive(Debug)]
enum PaymentMethod {
    Cash,
    Bkash,
    Nagad,
    Card,
}

fn fee_percent(m: &PaymentMethod) -> f64 {
    match m {
        PaymentMethod::Cash => 0.0,
        PaymentMethod::Bkash | PaymentMethod::Nagad => 1.5,
        PaymentMethod::Card => 2.0,
    }
}

fn main() {
    let all = [PaymentMethod::Cash, PaymentMethod::Bkash, PaymentMethod::Nagad, PaymentMethod::Card];
    for m in &all {
        println!("{:?}: চার্জ {}%", m, fee_percent(m));
    }
}
'''),
    php_note("PHP 8.1-এর <code>enum PaymentMethod { case Cash; case Bkash; }</code> — খুব কাছাকাছি।"))

c.lesson("enum-এর ভিতরে data",
    say("Rust enum-এর প্রতিটি রূপ নিজের data রাখতে পারে। PHP enum এটা পারে না — এটাই Rust enum-এর শক্তি।"),
    code(r'''
enum Payment {
    Cash,
    Bkash { number: String, trx_id: String },
    Card(String),   // card-এর শেষ ৪ সংখ্যা
}

fn describe(p: &Payment) -> String {
    match p {
        Payment::Cash => "নগদ টাকা".to_string(),
        Payment::Bkash { number, trx_id } => format!("bKash {number}, TrxID {trx_id}"),
        Payment::Card(last4) => format!("Card ****{last4}"),
    }
}

fn main() {
    let list = [
        Payment::Cash,
        Payment::Bkash { number: "01711000000".into(), trx_id: "BK7X9".into() },
        Payment::Card("4421".into()),
    ];
    for p in &list {
        println!("{}", describe(p));
    }
}
'''))

c.lesson("Option: Rust-এ null নেই",
    say("মান থাকতেও পারে, নাও থাকতে পারে — এর জন্য <code>Option&lt;T&gt;</code>: হয় <code>Some(মান)</code>, নয়তো <code>None</code>। Compiler বাধ্য করে <code>None</code> সামলাতে।"),
    php_note("PHP-তে <code>find()</code> null ফেরত দিলে <code>$user-&gt;name</code> লিখলেই error। Rust-এ <code>None</code> না সামলে ভিতরের মান ধরাই যায় না।"),
    code(r'''
fn find_price(model: &str) -> Option<u32> {
    match model {
        "Redmi 13" => Some(17500),
        "Galaxy A15" => Some(21000),
        _ => None,
    }
}

fn main() {
    for m in ["Redmi 13", "Nokia 3310"] {
        match find_price(m) {
            Some(price) => println!("{m}: {price} টাকা"),
            None => println!("{m}: দাম পাওয়া যায়নি"),
        }
    }
}
'''))

c.lesson("Option-এর ছোট শর্টকাট",
    points("<code>if let Some(x) = ...</code> — শুধু একটা ক্ষেত্র দরকার হলে",
           "<code>.unwrap_or(0)</code> — না থাকলে ডিফল্ট (PHP-র <code>?? 0</code>)",
           "<code>.unwrap()</code> — নিশ্চিত থাকলে; <code>None</code> হলে panic, তাই সাবধানে"),
    code(r'''
fn main() {
    let phones = vec!["Redmi", "Vivo", "Oppo"];

    if let Some(first) = phones.first() {
        println!("প্রথম: {first}");
    }

    let tenth = phones.get(9);
    println!("দশম: {:?}", tenth);
    println!("দশম: {}", tenth.unwrap_or(&"নেই"));

    let discount: Option<u32> = None;
    println!("ছাড়: {}", discount.unwrap_or(0));
}
'''))

# ================================================================== collections
c.section("Vec ও HashMap")
c.lesson("Vec: বাড়ানো-কমানো যায় এমন list",
    say("<code>Vec&lt;T&gt;</code> হলো PHP-র সাধারণ indexed array। <code>vec![]</code> macro দিয়ে সহজে বানানো যায়।"),
    code(r'''
fn main() {
    let mut sales: Vec<u32> = Vec::new();
    sales.push(1200);
    sales.push(3400);
    sales.push(2100);

    let mut brands = vec!["Samsung", "Xiaomi"];
    brands.push("Walton");

    println!("{:?} মোট {}টা", sales, sales.len());
    println!("{:?}", brands);
    println!("সরানো হলো: {:?}", brands.pop());
    println!("আছে Walton? {}", brands.contains(&"Walton"));
}
'''),
    php_note("<code>$sales[] = 1200;</code> → <code>sales.push(1200)</code>, <code>count($sales)</code> → <code>sales.len()</code>, <code>in_array()</code> → <code>contains()</code>"))

c.lesson("Vec-এ struct: Cart-এর মোট দাম",
    code(r'''
struct Item {
    name: String,
    price: u32,
    qty: u32,
}

fn main() {
    let cart = vec![
        Item { name: "Charger".into(), price: 650, qty: 1 },
        Item { name: "Cover".into(), price: 250, qty: 2 },
        Item { name: "Glass".into(), price: 150, qty: 3 },
    ];

    let mut total = 0;
    for item in &cart {
        let line = item.price * item.qty;
        println!("{:<8} {:>4} × {} = {:>5}", item.name, item.price, item.qty, line);
        total += line;
    }
    println!("মোট: {total} টাকা");
}
'''),
    say("<code>for item in &cart</code> — <code>&</code> দিয়ে ধার নিয়ে ঘুরলাম, তাই পরে <code>cart</code> আবার ব্যবহার করা যাবে।"),
    task("<code>qty</code> ৩ বা বেশি হলে ঐ লাইনে ১০% ছাড় দিন।"))

c.lesson("HashMap: key দিয়ে মান",
    say("PHP-র associative array (<code>['Redmi' =&gt; 5]</code>) হলো Rust-এর <code>HashMap</code>। <code>use std::collections::HashMap;</code> লাগে।"),
    code(r'''
use std::collections::HashMap;

fn main() {
    let mut stock: HashMap<String, u32> = HashMap::new();
    stock.insert("Redmi 13".to_string(), 5);
    stock.insert("Galaxy A15".to_string(), 2);

    stock.insert("Redmi 13".to_string(), 4);   // একই key: মান বদলায়

    match stock.get("Galaxy A15") {
        Some(qty) => println!("Galaxy A15 আছে {qty}টা"),
        None => println!("নেই"),
    }
    println!("মোট model: {}", stock.len());
}
'''),
    warn("HashMap-এ ক্রম (order) ঠিক থাকে না। ক্রম চাইলে <code>BTreeMap</code> নিন — key অনুযায়ী সাজানো থাকে।"))

c.lesson("entry(): গুনে গুনে যোগ",
    say("<code>entry(key).or_insert(0)</code> — key না থাকলে ০ বসায়, তারপর সেই মানের <code>&mut</code> দেয়। গণনার জন্য সবচেয়ে কাজের pattern।"),
    code(r'''
use std::collections::BTreeMap;

fn main() {
    let sales = ["Karim", "Rahim", "Karim", "Nusrat", "Karim", "Rahim"];

    let mut count: BTreeMap<&str, u32> = BTreeMap::new();
    for seller in sales {
        *count.entry(seller).or_insert(0) += 1;
    }

    for (seller, n) in &count {
        println!("{seller}: {n}টা বিক্রি");
    }
}
'''),
    php_note("<code>$count[$seller] = ($count[$seller] ?? 0) + 1;</code> এর Rust রূপ।"))

# ================================================================== errors
c.section("Error সামলানো")
c.lesson("Result: সফল অথবা ব্যর্থ",
    say("যে কাজ ব্যর্থ হতে পারে, সেটা <code>Result&lt;T, E&gt;</code> ফেরত দেয়: <code>Ok(মান)</code> অথবা <code>Err(কারণ)</code>।"),
    php_note("PHP-তে exception <code>throw</code> করে <code>try/catch</code>। Rust-এ exception নেই — error একটা সাধারণ ফেরত মান, তাই উপেক্ষা করা কঠিন।"),
    code(r'''
fn main() {
    for input in ["250", "দুইশো", "-5"] {
        match input.parse::<u32>() {
            Ok(n) => println!("{input} → সংখ্যা {n}"),
            Err(e) => println!("{input} → ভুল: {e}"),
        }
    }
}
'''))

c.lesson("নিজের function থেকে Result",
    code(r'''
fn withdraw(balance: u32, amount: u32) -> Result<u32, String> {
    if amount == 0 {
        return Err("০ টাকা তোলা যায় না".to_string());
    }
    if amount > balance {
        return Err(format!("ব্যালেন্স কম: আছে {balance}, চাইছেন {amount}"));
    }
    Ok(balance - amount)
}

fn main() {
    let balance = 1000;
    for amount in [300, 0, 5000] {
        match withdraw(balance, amount) {
            Ok(left) => println!("{amount} তোলা হলো, বাকি {left}"),
            Err(msg) => println!("ব্যর্থ: {msg}"),
        }
    }
}
'''),
    say("ব্যর্থ হলে কেন ব্যর্থ, সেটা <code>Err</code>-এর ভিতরে পাঠাচ্ছি। ডাকার জায়গায় <code>match</code> দিয়ে দুটো পথই সামলাতে হয়।"))

c.lesson("? : error উপরে পাঠিয়ে দেওয়া",
    say("<code>?</code> মানে: <code>Ok</code> হলে ভিতরের মান দাও, <code>Err</code> হলে এখনই এই function থেকে সেই error ফেরত দাও। অনেক <code>match</code> লেখা বাঁচে।"),
    code(r'''
use std::num::ParseIntError;

fn total(price: &str, qty: &str) -> Result<u32, ParseIntError> {
    let p: u32 = price.parse()?;   // ভুল হলে এখান থেকেই Err ফেরত
    let q: u32 = qty.parse()?;
    Ok(p * q)
}

fn main() {
    println!("{:?}", total("450", "3"));
    println!("{:?}", total("450", "তিন"));
}
'''),
    php_note("Laravel-এ exception নিজে থেকেই উপরে উঠে handler-এ যায়। Rust-এ <code>?</code> লিখে আপনি নিজে বলে দেন — কোথায় error উঠতে পারে, কোড পড়েই দেখা যায়।"))

c.lesson("panic নাকি Result?",
    table(["অবস্থা", "কী ব্যবহার করবেন"], [
        ["User-এর ভুল input, file নেই, network সমস্যা", "<code>Result</code> — আশা করা যায় এমন ব্যর্থতা"],
        ["Program-এর নিজের bug (\"এটা কখনো হওয়ার কথা না\")", "<code>panic!</code> / <code>expect</code>"],
        ["ছোট উদাহরণ, test, prototype", "<code>unwrap()</code> / <code>expect()</code> চলবে"],
        ["Library বা web server-এর কোড", "প্রায় সব সময় <code>Result</code>"]]),
    tip("<code>unwrap()</code> এর বদলে <code>expect(\"কেন ব্যর্থ হতে পারে না\")</code> লিখুন — panic হলে বার্তাটা খুঁজে পেতে সুবিধা।"))

# ================================================================== modules + project
c.section("Module ও Project")
c.lesson("mod আর pub: কোড ভাগ করা",
    say("<code>mod</code> দিয়ে কোড আলাদা অংশে ভাগ করি। ভিতরের সবকিছু ডিফল্টভাবে private — বাইরে থেকে ব্যবহার করতে <code>pub</code>।"),
    code(r'''
mod billing {
    pub const VAT: u32 = 15;

    pub fn with_vat(amount: u32) -> u32 {
        amount + vat_of(amount)
    }

    fn vat_of(amount: u32) -> u32 {   // private
        amount * VAT / 100
    }
}

fn main() {
    println!("VAT {}% সহ: {}", billing::VAT, billing::with_vat(2000));
}
'''),
    php_note("PHP-র <code>namespace App\\Billing;</code> আর <code>public/private</code>-এর মতো। বড় project-এ প্রতিটি <code>mod</code> আলাদা file হয়: <code>src/billing.rs</code>।"))

c.lesson("Module, API আর encapsulation",
    say("<code>pub</code> দিয়ে আপনি ঠিক করেন বাইরের কোড কী দেখতে পাবে। এটাই <b>encapsulation</b>: ভিতরের খুঁটিনাটি লুকিয়ে শুধু দরকারি অংশ খোলা রাখা।"),
    jargon(("Module", "কোড ভাগ করার একক; Rust-এ <code>mod</code>। PHP-র namespace-এর কাছাকাছি"),
           ("Encapsulation", "ভিতরের data/কাজ লুকানো, শুধু নির্দিষ্ট দরজা (public method) খোলা"),
           ("API (Application Programming Interface)", "একটা code যা অন্য code-কে কী কী করতে দেয় তার তালিকা — এখানে <code>pub</code> ফাংশনগুলো"),
           ("Public / private", "বাইরে থেকে দেখা যায় / যায় না (ডিফল্ট private)")),
    tip("\"API\" শব্দটা দুই অর্থে আসে: library-র pub function-এর তালিকা (এখানে), আর web server-এর endpoint-এর তালিকা (Rust Web Development-এ)।"))

c.lesson("Project: দোকানের Inventory",
    say("struct, enum, HashMap, Result আর <code>?</code> একসাথে। প্রতিটি লাইন একটা command: <code>add</code>, <code>sell</code>, <code>report</code>।"),
    code(r'''
use std::collections::BTreeMap;
use std::io::{self, BufRead};

enum Command { Add(String, u32), Sell(String, u32), Report }

fn parse(line: &str) -> Result<Command, String> {
    let parts: Vec<&str> = line.split_whitespace().collect();
    match parts.as_slice() {
        ["add", name, qty] => Ok(Command::Add(name.to_string(), qty.parse().map_err(|_| "qty ভুল")?)),
        ["sell", name, qty] => Ok(Command::Sell(name.to_string(), qty.parse().map_err(|_| "qty ভুল")?)),
        ["report"] => Ok(Command::Report),
        _ => Err(format!("বুঝিনি: {line}")),
    }
}

fn main() {
    let mut stock: BTreeMap<String, u32> = BTreeMap::new();
    for line in io::stdin().lock().lines() {
        let line = line.expect("পড়া গেল না");
        match parse(&line) {
            Ok(Command::Add(name, qty)) => *stock.entry(name).or_insert(0) += qty,
            Ok(Command::Sell(name, qty)) => match stock.get_mut(&name) {
                Some(have) if *have >= qty => *have -= qty,
                Some(have) => println!("✗ {name}: আছে {have}টা, চাইছেন {qty}টা"),
                None => println!("✗ {name} নামে কিছু নেই"),
            },
            Ok(Command::Report) => {
                for (name, qty) in &stock {
                    println!("  {name:<10} {qty:>3}টা");
                }
            }
            Err(msg) => println!("✗ {msg}"),
        }
    }
}
''', stdin="add Redmi13 5\nadd GalaxyA15 2\nsell Redmi13 3\nsell GalaxyA15 4\nsell Nokia 1\nhello\nreport\n"),
    task("<code>price</code> যোগ করুন: <code>add Redmi13 5 17500</code>, আর report-এ মোট স্টকের দাম দেখান।"))

c.lesson("Rust 102-এর জার্গন কার্ড",
    table(["শব্দ", "এক লাইনে"], [
        ["Ownership / Move / Borrow", "এক সময়ে একজন মালিক; হস্তান্তর; ধার নেওয়া (<code>&amp;</code>)"],
        ["Stack / Heap", "দ্রুত নির্দিষ্ট আকারের জায়গা / বড়, বাড়তে-পারা জায়গা"],
        ["Memory safety", "memory-র ভুল ব্যবহার compile-এই আটকানো"],
        ["Null / Option", "\"কিছু নেই\" — Rust-এ <code>Option</code> দিয়ে স্পষ্টভাবে"],
        ["Attribute (<code>#[...]</code>)", "compiler-কে নির্দেশ; derive দিয়ে code বানানো"],
        ["Boilerplate", "বারবার লেখার একঘেয়ে code"],
        ["Encapsulation / API", "ভিতরের তথ্য লুকানো / বাইরে খোলা দরজার তালিকা"],
        ["Error value", "<code>Result</code> — exception ছোঁড়ার বদলে মান হিসেবে ফেরত"]]))

c.finish("Rust 102 শেষ! 🎉",
         "Rust-এর সবচেয়ে কঠিন অংশ আপনি পার করে এসেছেন। এবার trait, generic, iterator আর একসাথে অনেক কাজ (concurrency)।",
         recap=["প্রতিটি মানের একজন মালিক; scope শেষে drop",
                "String move হয়, সংখ্যা Copy হয়",
                "অনেক <code>&</code> অথবা একটা <code>&mut</code>",
                "struct + impl = PHP class-এর মতো",
                "null নেই: <code>Option</code>; exception নেই: <code>Result</code> আর <code>?</code>",
                "<code>Vec</code> = list, <code>HashMap</code>/<code>BTreeMap</code> = key-value"])

if __name__ == "__main__":
    c.build()
