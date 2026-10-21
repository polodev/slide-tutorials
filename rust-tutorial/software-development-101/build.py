"""Software Development 101 — প্রোগ্রামিং ও software engineering-এর জার্গন, Laravel developer-এর জন্য, Rust শেখার আগের ভিত।
C, C++, Rust, PHP উদাহরণ আসলেই compile/চালানো; আউটপুট আসল।  Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
from kit import Course, code, jargon, php_note, points, quiz, say, shell, steps, table, task, tip, warn  # noqa: E402

c = Course(slug="software-development-101", title="Software Development 101", folder=HERE,
           subtitle="Laravel জানেন, কিন্তু \"vector\", \"macro\", \"heap\", \"compiler\", \"CI/CD\" শুনে আটকে যান? Rust শেখার আগে software engineering-এর ভিত — সহজ ভাষায়, আসল কোড চালিয়ে",
           series="Software Development 101", next_course=("../rust-101/index.html", "Rust 101 — শূন্য থেকে Rust"))

c.cover("Software Development 101<br>Rust-এর আগের ভিত",
        "আপনি Laravel দিয়ে website বানাতে পারেন, কিন্তু কোনো কিছু \"কেন এই নামে\" বা \"ভিতরে কী হয়\" জানেন না — এটা স্বাভাবিক। এই কোর্সে ৫০+ বিষয়: computer কীভাবে কোড বোঝে, C/C++/Rust, memory, vector, algorithm, Git, API, database, DevOps — আর শেষে আপনার Laravel app Rust-এ নেওয়ার পথ।",
        learn=["Computer, compiler, interpreter — কোড কীভাবে চলে", "C, C++, Rust: কে কেন এল", "Memory: stack, heap, GC, ownership",
               "Vector, array, hash map, algorithm, Big-O", "Type, macro, runtime, concurrency, error handling",
               "Rust কেন ভালো — আর কোথায় নয়", "Git, API, database, test, CI/CD, security, DevOps",
               "Laravel → Rust রূপান্তরের roadmap"],
        need="কিছুই না। শুধু Laravel/PHP-এর সাধারণ অভিজ্ঞতা হলেই চলবে। কোনো CS ডিগ্রি লাগবে না।")


# ================================================================== ১. ভিত
c.section("ভিত")
c.lesson("Software engineering মানে কী?",
    say("Laravel-এ <code>php artisan make:controller</code> চালিয়ে page বানানো <b>application development</b>। Software engineering তার চেয়ে বড়: কোড লেখা, <b>বোঝা, বদলানো, নিরাপদ রাখা, দ্রুত চালানো</b> আর দলের সাথে কাজ করা।"),
    points("কোড একবার লেখা হয়, কিন্তু <b>বছরের পর বছর পড়া ও বদলানো</b> হয়",
           "ভালো software = ঠিকঠাক চলে + বোঝা যায় + বদলানো সহজ + নিরাপদ + দ্রুত",
           "Rust এই শেষের দুটো (নিরাপদ, দ্রুত) নিয়ে জন্মেছে — কিন্তু তার দাম হিসেবে নিচের স্তরের ধারণা জানতে চায়"),
    php_note("Laravel অনেক কিছু আপনার হয়ে করে দেয় (memory, security, routing)। Rust অনেকটা নিজের হাতে করতে দেয় — তাই আপনাকে জানতে হবে \"নিচে কী হচ্ছে\"। এই কোর্স সেটাই।"))

c.lesson("Computer আসলে কী বোঝে?",
    say("Computer শুধু বোঝে <b>0 আর 1</b> — বিদ্যুৎ আছে বা নেই। আপনার লেখা <code>echo \"Hello\"</code> শেষ পর্যন্ত বহু 0-1 হয়ে CPU-তে যায়। নিচে আসল সংখ্যায় দেখুন:"),
    code(r'''
fn main() {
    println!("18 binary-তে:  {:08b}", 18);
    println!("'A' এর কোড:      {}", 'A' as u8);
    println!("'ক' কত byte:    {}", "ক".len());
    println!("1 KB = {} byte", 1024);
}
'''),
    jargon(("Bit", "একটা 0 অথবা 1 — তথ্যের সবচেয়ে ছোট একক"),
           ("Byte", "৮ bit; ইংরেজি একটা অক্ষর = ১ byte, বাংলা একটা অক্ষর = সাধারণত ৩ byte (UTF-8)"),
           ("Binary", "শুধু 0 আর 1 দিয়ে লেখা সংখ্যা"),
           ("Machine code", "CPU সরাসরি যে 0-1 নির্দেশ বোঝে")))

c.lesson("Hardware-এর চার সদস্য",
    table(["অংশ", "কাজ", "উপমা (দোকান)"], [
        ["<b>CPU</b>", "হিসাব ও নির্দেশ চালায়", "ক্যাশিয়ার — যা বলা হয় করে, খুব দ্রুত"],
        ["<b>RAM (memory)</b>", "চলমান program-এর অস্থায়ী তথ্য; বন্ধ করলে মুছে যায়", "কাউন্টারের টেবিল"],
        ["<b>Disk (SSD)</b>", "স্থায়ী ফাইল ও database", "পেছনের গুদাম — বড় কিন্তু ধীর"],
        ["<b>Network</b>", "অন্য computer-এর সাথে কথা", "ফোন লাইন"]]),
    tip("\"Memory\" শব্দটা programming-এ প্রায় সবসময় <b>RAM</b> বোঝায়, disk নয়। Rust-এর ownership, stack, heap — সব RAM নিয়ে।"),
    jargon(("Core", "CPU-র ভিতরে একটা কাজের একক; ৮ core মানে একসাথে ৮টা কাজ"),
           ("Latency", "এক কাজ শুরু থেকে শেষ হতে সময়"),
           ("OS (Operating System)", "macOS/Linux/Windows — hardware আর আপনার program-এর মাঝের ব্যবস্থাপক")))

c.lesson("স্তরের মানচিত্র: আপনি কোথায়?",
    say("Software-এর জগৎ পেঁয়াজের মতো স্তরে স্তরে। Laravel developer হিসেবে আপনি একদম উপরে বসে কাজ করেন:"),
    table(["স্তর", "উদাহরণ", "কে সামলায়"], [
        ["৫. আপনার application", "Rahim Mobile-এর invoice page", "আপনি"],
        ["৪. Framework", "Laravel, axum, Leptos", "framework-এর লেখক"],
        ["৩. ভাষা ও runtime", "PHP + Zend Engine, Rust + std", "ভাষার টিম"],
        ["২. Operating system", "Linux, macOS", "OS-এর টিম (বেশিরভাগ C/C++/Rust-এ লেখা)"],
        ["১. Hardware", "CPU, RAM, disk", "নির্মাতা"]]),
    php_note("PHP-তে আপনাকে ৩ ও ২ স্তর নিয়ে ভাবতে হয় না। Rust-এ সেই স্তরগুলো আপনার সামনে খোলা — সুবিধা: গতি আর নিয়ন্ত্রণ; দাম: বেশি ধারণা শেখা।"))

c.section("কোড কীভাবে চলে")
c.lesson("Compiler আর interpreter",
    say("মানুষের লেখা কোড (<b>source code</b>) CPU সরাসরি বোঝে না — অনুবাদ লাগে। অনুবাদের দুটো পথ:"),
    table(["", "Compiler (Rust, C, C++, Go)", "Interpreter (PHP, Python, JS-এর অনেকটা)"], [
        ["কখন অনুবাদ", "চালানোর <b>আগে</b>, পুরোটা একবারে", "চলার <b>সময়</b>, লাইন/অংশ ধরে"],
        ["ফল", "একটা চালানো-যায় এমন ফাইল (binary)", "কোনো আলাদা ফাইল নেই; interpreter রোজ পড়ে"],
        ["ভুল ধরা পড়ে", "<b>compile-এ</b>, user দেখার আগেই", "অনেক ভুল <b>চলার সময়</b>, user-এর সামনে"],
        ["গতি", "সাধারণত অনেক দ্রুত", "ধীর (JIT থাকলে কিছুটা দ্রুত)"]]),
    jargon(("Source code", "মানুষের লেখা কোড (<code>.php</code>, <code>.rs</code> ফাইল)"),
           ("Compile", "source code-কে machine code-এ বদলানো"),
           ("Binary / executable", "compile-এর ফল, সরাসরি চালানো যায়"),
           ("Interpreter", "source code পড়ে সাথে সাথে চালায়"),
           ("Ahead-of-time (AOT)", "আগেই compile — Rust এমন")),
    php_note("PHP আসলে অর্ধেক-compiler: Zend Engine আপনার কোডকে <b>bytecode</b>-এ বদলে নেয়, তারপর একটা virtual machine সেটা চালায়। তবে প্রতিটা request-এ এই কাজ নতুন করে (OPcache থাকলে cache থেকে)।"))

c.lesson("একই কাজ, দুই পদ্ধতি",
    say("নিচে PHP আর Rust দুটোই একই জিনিস করছে। Rust-এর বেলায় চালানোর আগে compile হয়েছে; PHP সরাসরি চলেছে।"),
    code('''<?php
$prices = [18500, 41500, 112000];
echo "মোট: " . array_sum($prices) . " টাকা\\n";
''', "php"),
    code(r'''
fn main() {
    let prices = [18500, 41500, 112000];
    let total: i32 = prices.iter().sum();
    println!("মোট: {total} টাকা");
}
'''))

c.lesson("High-level বনাম low-level ভাষা",
    say("\"Level\" মানে machine থেকে কত দূরে। যত নিচে, তত নিয়ন্ত্রণ — কিন্তু তত বেশি কাজ আপনার ঘাড়ে।"),
    table(["ভাষা", "Level", "আপনাকে সামলাতে হয়", "উদাহরণ"], [
        ["Assembly", "সবচেয়ে নিচু", "প্রতিটা CPU নির্দেশ", "—"],
        ["<b>C</b>", "নিচু", "memory নিজে", "Linux kernel, database engine"],
        ["<b>C++</b>", "নিচু-মাঝারি", "memory (কিছু সাহায্য সহ)", "Chrome, game engine"],
        ["<b>Rust</b>", "নিচু-মাঝারি", "memory নিয়ম মেনে — compiler পাহারা দেয়", "Firefox-এর অংশ, Linux kernel-এর নতুন অংশ"],
        ["<b>Go</b>, Java, C#", "মাঝারি", "প্রায় কিছুই না (GC আছে)", "Docker, Kubernetes (Go)"],
        ["<b>PHP</b>, Python, JS", "উঁচু", "কিছুই না", "Laravel, WordPress"]]),
    tip("Low-level মানে \"খারাপ\" না, \"উঁচু\" মানে \"ভালো\" না। প্রতিটা ভাষা নিজের কাজের জন্য ভালো — পরের section-এ দেখুন কেন।"))


# ================================================================== ২. C, C++, Rust
c.section("C, C++, Rust")
c.lesson("C: সবকিছুর দাদু",
    say("<b>C</b> বানিয়েছিলেন Dennis Ritchie, Bell Labs-এ, ১৯৭০-এর দশকের শুরুতে — Unix operating system লেখার জন্য। আজও Linux kernel, database engine, আর অসংখ্য device-এর ভিতরে C চলছে। PHP-র interpreter-ও C-তে লেখা!"),
    code(r'''
#include <stdio.h>

int main(void) {
    int price = 18500;
    int qty = 3;
    printf("Hello, World!\n");
    printf("মোট: %d টাকা\n", price * qty);
    return 0;
}
''', "c"),
    php_note("আপনি যে <code>php</code> command চালান, সেটা C দিয়ে লেখা program। অর্থাৎ PHP-র নিচেই C।"),
    jargon(("Kernel", "operating system-এর কেন্দ্র — hardware-কে সরাসরি সামলায়"),
           ("Standard library", "ভাষার সাথে আসা তৈরি function (<code>printf</code>)"),
           ("Header (<code>#include</code>)", "অন্য file-এর function ব্যবহারের ঘোষণা আনা")))

c.lesson("C-তে memory নিজের হাতে",
    say("C-তে চাইলে RAM থেকে জায়গা চেয়ে নিতে হয় (<code>malloc</code>) আর কাজ শেষে নিজে ফেরত দিতে হয় (<code>free</code>)। ভুলে গেলে আর কেউ মনে করিয়ে দেবে না।"),
    code(r'''
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *prices = malloc(3 * sizeof(int));   // ৩টা সংখ্যার জায়গা চাইলাম
    if (prices == NULL) return 1;

    prices[0] = 18500;
    prices[1] = 41500;
    prices[2] = 112000;

    int sum = 0;
    for (int i = 0; i < 3; i++) sum += prices[i];
    printf("মোট: %d\n", sum);

    free(prices);                            // জায়গা ফেরত — ভুলে গেলে "leak"
    return 0;
}
''', "c"),
    warn("<code>free</code> ভুলে গেলে memory leak; দুইবার করলে crash; <code>free</code>-এর পর ব্যবহার করলে অজানা আচরণ। C compiler এসব আটকায় না — এই কারণেই বহু বড় security bug C/C++-এ।"),
    jargon(("malloc / free", "memory চাওয়া / ফেরত দেওয়া"),
           ("Pointer (<code>*</code>)", "একটা জায়গার <b>ঠিকানা</b> — মানটা নয়, কোথায় আছে সেটা"),
           ("Memory leak", "জায়গা নিয়ে ফেরত না দেওয়া; program ধীরে ধীরে RAM খেয়ে ফেলে"),
           ("Undefined behavior (UB)", "নিয়ম ভাঙলে ভাষা কিছুই গ্যারান্টি দেয় না — crash, ভুল মান, বা চুপচাপ ভুল")))

c.lesson("C++: C + অনেক কিছু",
    say("<b>C++</b> বানান Bjarne Stroustrup, ১৯৮০-র দশকে — C-র গতি রেখে তার উপর <b>class, object, template</b> যোগ করে। Chrome, game engine, Photoshop, অনেক trading system C++-এ। শক্তিশালী, কিন্তু অনেক জটিল — আর C-র memory-র ঝুঁকি অনেকটা রয়ে গেছে।"),
    code(r'''
#include <iostream>
#include <vector>

int main() {
    std::vector<int> prices = {18500, 41500};   // vector: বাড়তে-পারা list
    prices.push_back(112000);                   // শেষে যোগ

    int sum = 0;
    for (int p : prices) sum += p;
    std::cout << "দাম " << prices.size() << " টি, মোট " << sum << " টাকা\n";
    return 0;
}
''', "cpp"),
    jargon(("Class / Object", "ছাঁচ / ছাঁচ থেকে বানানো জিনিস (PHP-র মতোই)"),
           ("Template", "যেকোনো type-এর জন্য একবার লেখা code — Rust-এর generic-এর পূর্বসূরি"),
           ("<code>std::vector</code>", "<b>vector</b> নামটা এখান থেকেই জনপ্রিয় — পরে আলাদা lesson")))

c.lesson("Rust: গতি, কিন্তু নিরাপদ",
    say("<b>Rust</b> শুরু হয় ২০০৬ সালে Graydon Hoare-র ব্যক্তিগত প্রজেক্ট হিসেবে; পরে Mozilla (Firefox-এর নির্মাতা) সমর্থন করে। প্রথম স্থিতিশীল সংস্করণ <b>Rust 1.0 — ২০১৫ সালে</b>। লক্ষ্য একটাই: <b>C/C++-এর গতি, কিন্তু memory-র ভুল compile-এই ধরা</b>।"),
    code(r'''
fn main() {
    let price = 18500;
    let qty = 3;
    println!("Hello, World!");
    println!("মোট: {} টাকা", price * qty);
}
'''),
    points("C/C++-এর মতোই compile হয়ে machine code, কোনো garbage collector নেই",
           "কিন্তু <b>ownership</b> নিয়মে memory-র বেশিরভাগ বিপজ্জনক ভুল compile-এ আটকে যায়",
           "একই ভাষায় low-level কাজও, আবার web-ও (axum, Leptos, Topcoat)"),
    jargon(("Foundation", "২০২১ সালে Rust Foundation বানানো হয় — ভাষাটা এখন কোনো এক কোম্পানির নয়"),
           ("Stable release", "পুরনো কোড ভাঙবে না এমন প্রতিশ্রুতির সংস্করণ")))

c.lesson("ভাষা তুলনা: এক নজরে",
    table(["", "PHP", "JavaScript", "C", "C++", "Go", "Rust"], [
        ["চলে", "interpreter", "interpreter + JIT", "compiled", "compiled", "compiled", "compiled"],
        ["Memory", "automatic (GC)", "automatic (GC)", "নিজে", "নিজে + সাহায্য", "automatic (GC)", "ownership নিয়ম"],
        ["গতি", "মাঝারি", "মাঝারি–ভালো", "দ্রুততম", "দ্রুততম", "দ্রুত", "দ্রুততম"],
        ["Memory-র ভুল", "প্রায় নেই", "প্রায় নেই", "<b>প্রচুর</b>", "<b>প্রচুর</b>", "প্রায় নেই", "<b>compile-এ আটকায়</b>"],
        ["শেখা", "সহজ", "সহজ", "কঠিন", "অনেক কঠিন", "সহজ", "কঠিন (প্রথমে)"],
        ["সাধারণ কাজ", "web", "web/browser", "OS, embedded", "game, browser", "cloud, DevOps", "সব ধরন"]]),
    tip("Rust-এর আসল জয়গা: C/C++-এর গতি + Go/PHP-র নিরাপত্তা। দাম: শেখার ঢাল আর compile-এর সময়।"))

c.lesson("Programming paradigm: ভাবনার ধরন",
    say("ভাষাগুলো সমস্যা ভাবার আলাদা আলাদা ধরন (paradigm) দেয়। বেশিরভাগ ভাষা কয়েকটা মিশিয়ে।"),
    table(["Paradigm", "মূল ধারণা", "উদাহরণ"], [
        ["<b>Procedural</b>", "ধাপে ধাপে নির্দেশ, function ডাকা", "C, পুরনো PHP"],
        ["<b>Object-oriented (OOP)</b>", "data + কাজ একসাথে object-এ; class, inheritance", "Java, C++, Laravel-এর Eloquent model"],
        ["<b>Functional</b>", "function-ই মূল; data বদলায় না; <code>map/filter</code>", "Haskell, Laravel Collection-এর <code>map</code>"],
        ["<b>Rust</b>", "struct + trait (OOP-এর অংশ) + closure/iterator (functional) + procedural", "—"]]),
    jargon(("Inheritance", "এক class আরেক class-এর সবকিছু পায় (<code>extends</code>) — Rust-এ <b>নেই</b>, তার বদলে trait আর composition"),
           ("Composition", "বড় জিনিস ছোট জিনিস জুড়ে বানানো — \"class extends\" না, \"struct-এর ভিতরে struct\""),
           ("Immutable", "একবার বানালে বদলায় না — functional ভাবনা, Rust-এ ডিফল্ট")),
    php_note("PHP-তে <code>class Product extends Model</code> খুব স্বাভাবিক। Rust-এ inheritance নেই — প্রথমে অস্বস্তিকর, কিন্তু trait দিয়ে একই কাজ হয় (Rust 103-এ)।"))

# ================================================================== ৩. Memory
c.section("Memory")
c.lesson("Memory (RAM) আর variable",
    say("Variable আসলে RAM-এর একটা <b>নাম-দেওয়া বাক্স</b>। <code>$price = 18500;</code> মানে \"একটা বাক্স নাও, নাম price, ভিতরে 18500\"। প্রতিটা বাক্সের একটা <b>ঠিকানা (address)</b> আছে, আর বাক্সের <b>আকার</b> আছে।"),
    code(r'''
use std::mem::size_of;

fn main() {
    println!("i32 (ছোট পূর্ণ সংখ্যা):  {} byte", size_of::<i32>());
    println!("i64 (বড় পূর্ণ সংখ্যা):   {} byte", size_of::<i64>());
    println!("f64 (দশমিক সংখ্যা):     {} byte", size_of::<f64>());
    println!("bool:                    {} byte", size_of::<bool>());
    println!("[i32; 3] (তিনটা সংখ্যা): {} byte", size_of::<[i32; 3]>());
}
'''),
    php_note("PHP-তে <code>$x = 5</code> আর <code>$x = 'five'</code> একই variable-এ চলে, কারণ PHP পেছনে বাক্সের আকার নিজে ঠিক করে। Rust-এ আপনি (বা compiler) আগে থেকে জানে আকার — সেটাই গতির রহস্য।"),
    jargon(("Address", "RAM-এ একটা বাক্সের ঠিকানা (একটা সংখ্যা)"),
           ("Type", "বাক্সের আকার আর ভিতরের জিনিসের ধরন"),
           ("Allocation", "বাক্সের জন্য জায়গা নেওয়া")))

c.lesson("Stack আর heap: দুই রকম জায়গা",
    say("RAM-এর দুটো এলাকা (দোকানের উপমা):"),
    table(["", "Stack", "Heap"], [
        ["উপমা", "ক্যাশিয়ারের টেবিলের উপর সাজানো থালা — উপরেরটাই আগে নাও, রাখো", "পেছনের গুদাম — বড় জায়গা, কিন্তু খুঁজে নিতে সময়"],
        ["আকার", "ছোট, <b>আগে থেকে জানা</b> (সংখ্যা, bool)", "বড়, <b>বাড়তে-পারা</b> (লেখা, list)"],
        ["গতি", "খুব দ্রুত", "ধীর"],
        ["পরিষ্কার", "function শেষ হলে নিজে নিজে", "কেউ একজনকে পরিষ্কার করতে হয় (C: আপনি; PHP: GC; Rust: ownership)"]]),
    code(r'''
fn main() {
    let qty = 3;                                // stack: ছোট, নির্দিষ্ট আকার
    let mut name = String::from("Rahim");       // heap: লেখা বাড়তে পারে
    println!("শুরুতে:  {} অক্ষর, জায়গা আছে {}", name.len(), name.capacity());
    name.push_str(" Mobile Mirpur Branch");
    println!("পরে:    {} অক্ষর, জায়গা আছে {}", name.len(), name.capacity());
    println!("qty = {qty}");
}
'''),
    tip("উপরের <code>capacity</code> দেখুন: লেখা বাড়তে গিয়ে heap-এ আরও বড় জায়গা নিতে হয়েছে। এটাই heap-এর দাম।"),
    warn("\"Stack\" শব্দটার দুটো অর্থ — এখানে memory-র এলাকা। Data structure হিসেবেও \"stack\" আছে (শেষেরটা আগে বেরোয়), পরে দেখব। দুটো আলাদা জিনিস!"))

c.lesson("Memory management: তিন পদ্ধতি",
    say("Heap-এর জায়গা কে ফেরত নেবে — এই প্রশ্নের উত্তরেই ভাষাগুলো আলাদা:"),
    table(["পদ্ধতি", "কে পরিষ্কার করে", "ভাষা", "সুবিধা", "অসুবিধা"], [
        ["<b>Manual</b>", "প্রোগ্রামার (<code>free</code>)", "C, C++ (আংশিক)", "পূর্ণ নিয়ন্ত্রণ, দ্রুত", "ভুল হয়: leak, crash, security hole"],
        ["<b>Garbage Collector (GC)</b>", "ভাষার runtime, চলার সময়", "PHP, Java, Go, JS, Python", "সহজ, ভুল কম", "একটু বেশি memory, মাঝেমধ্যে ছোট বিরতি"],
        ["<b>Ownership</b>", "compiler, <b>compile-এ</b> নিয়ম দিয়ে", "Rust", "দ্রুত + নিরাপদ, কোনো বিরতি নেই", "নিয়ম শিখতে সময়"]]),
    jargon(("Garbage collector", "পেছনে চলা প্রক্রিয়া যে আর-লাগে-না memory খুঁজে খালি করে"),
           ("Ownership", "প্রতিটা মানের একজন মালিক; মালিক চলে গেলে মান মুছে যায় — compile-এ যাচাই"),
           ("Pause", "GC চলার সময় program-এর ক্ষণিক থেমে যাওয়া — real-time কাজে সমস্যা")),
    php_note("PHP প্রতি request-এ শুরু হয়ে শেষ হলে সব memory ফেলে দেয় — তাই leak ধরা পড়ে না। Rust server একবার চালু হয়ে দিনের পর দিন চলে, তাই memory-র হিসাব জরুরি।"))

c.lesson("Rust-এর পরিষ্কার: GC ছাড়াই নিজে নিজে",
    say("Rust-এ কেউ <code>free</code> লেখে না, GC-ও নেই। Compiler জানে কোন variable কোথায় শেষ হবে — ঠিক সেখানেই পরিষ্কার-করার code বসিয়ে দেয়। <code>Drop</code> দিয়ে সেটা দেখা যায়:"),
    code(r'''
struct Invoice {
    no: u32,
}

impl Drop for Invoice {
    fn drop(&mut self) {
        println!("Invoice {} পরিষ্কার হলো", self.no);
    }
}

fn main() {
    let _a = Invoice { no: 1001 };
    {
        let _b = Invoice { no: 1002 };
        println!("ভিতরের block চলছে");
    }   // ← এখানে _b-র মালিক শেষ, তাই এখনই পরিষ্কার
    println!("বাইরের block চলছে");
}   // ← এখানে _a শেষ
'''),
    tip("পরিষ্কারের সময় <b>আগে থেকে ঠিক জানা</b> — GC-র মতো \"কখনো একসময়\" না। এই নিশ্চয়তাই Rust-কে real-time আর server-এর জন্য আদর্শ করে।"))

c.lesson("Garbage collection কীভাবে কাজ করে",
    say("GC-র দুটো প্রধান কৌশল। <b>Reference counting</b>: প্রতিটা জিনিসের গায়ে লেখা থাকে \"কয়জন আমাকে ধরে আছে\"; সংখ্যা ০ হলেই মুছে। <b>Tracing</b>: মাঝে মাঝে \"মূল\" জিনিস থেকে ধরে ধরে যা পৌঁছানো যায় সেগুলো রেখে বাকি সব ফেলে দেয়। PHP প্রথমটা ব্যবহার করে, সাথে একটা ছোট cycle-খোঁজা অংশ।"),
    code('''<?php
class Node { public $other; }
$a = new Node(); $b = new Node();
$a->other = $b; $b->other = $a;     // দুজন একে অপরকে ধরে আছে
unset($a, $b);                       // নাম মুছলাম, কিন্তু object দুটো একে অপরকে ধরে বেঁচে আছে
echo "GC-র cycle collector মুছল: ", gc_collect_cycles(), " টি\\n";
''', "php"),
    say("উপরে দুই object একে অপরকে ধরে থাকায় count কখনো ০ হতো না — শুধু refcount থাকলে leak হতো। PHP-র আলাদা cycle collector সেটা ধরেছে।"),
    jargon(("Reference counting", "কয়জন ধরে আছে তার সংখ্যা রেখে, ০ হলে মোছা"),
           ("Cycle", "A → B → A — একে অপরকে ধরে থাকার চক্র; refcount একা পারে না"),
           ("Tracing GC", "মূল থেকে পৌঁছানো যায় এমন সব খুঁজে বাকিটা মোছে (Java, Go, JS)"),
           ("Stop-the-world pause", "GC চলার সময় program-এর ক্ষণিক থামা")),
    tip("GC-র দাম: (১) অতিরিক্ত memory, (২) চলার সময় অতিরিক্ত কাজ, (৩) অনির্দিষ্ট সময়ে ছোট বিরতি। Rust এই তিনটাই বাদ দেয় — কিন্তু বিনিময়ে নিয়ম শেখায়।"))

c.lesson("Memory safe মানে কী?",
    say("একটা ভাষা <b>memory safe</b> যদি তার সাধারণ (safe) কোড দিয়ে memory-র বিপজ্জনক ভুল — ভুল জায়গা পড়া, মুছে-ফেলা জিনিস ব্যবহার, দুইবার মোছা — করাই সম্ভব না হয়।"),
    table(["ভাষা", "Memory safe?", "কীভাবে"], [
        ["C, C++", "না", "programmer-এর দায়িত্ব; compiler চুপ"],
        ["PHP, Java, Go, Python, JS", "হ্যাঁ", "GC আর runtime-এর পাহারা (চলার সময়)"],
        ["<b>Rust</b>", "<b>হ্যাঁ</b>", "<b>ownership + borrow checker (compile-এ)</b>, GC ছাড়া"]]),
    points("বড় tech কোম্পানিদের হিসাবে প্রায় ৭০% security bug-ই ছিল memory-সংক্রান্ত — তাই সরকারি নিরাপত্তা সংস্থাগুলোও memory-safe ভাষায় যেতে বলছে",
           "Rust-এর <b>বিশেষত্ব</b>: GC-র মতো নিরাপদ, আবার C-র মতো দ্রুত"),
    jargon(("Safe Rust", "সাধারণ Rust code — memory-র ভুল করাই যায় না"),
           ("<code>unsafe</code>", "compiler-কে বলা \"এই অংশটুকু আমি নিজে দেখছি\" — খুব সীমিত জায়গায়, শেষ উপায়"),
           ("Security vulnerability", "hacker কাজে লাগাতে পারে এমন ফাঁক")),
    warn("\"Memory safe\" মানে \"সব bug-মুক্ত\" না! logic-এর ভুল (ভুল দাম হিসাব), SQL injection, দুর্বল password — এগুলো যেকোনো ভাষায় সম্ভব।"))

c.lesson("Borrow checker: compiler-এর পাহারাদার",
    say("Rust-এর compiler-এর যে অংশ ownership আর ধার (borrow) নিয়ম যাচাই করে, তার নাম <b>borrow checker</b>। নিয়ম মাত্র দুটো: <b>(১)</b> একবারে একজনই বদলাতে পারে (<code>&amp;mut</code>), <b>অথবা (২)</b> যত খুশি লোক শুধু পড়তে পারে (<code>&amp;</code>) — দুটো একসাথে নয়।"),
    code(r'''
fn main() {
    let mut cart = vec![18500, 41500];

    let first = &cart[0];          // পড়ার জন্য ধার নিলাম
    cart.push(112000);             // কিন্তু এদিকে বদলাতে চাইছি!
    println!("প্রথম দাম: {first}");
}
''', err="E0502"),
    say("কেন নিষিদ্ধ? <code>push</code>-এ vector বড় হয়ে নতুন জায়গায় সরে যেতে পারে — তখন <code>first</code> ঝুলে থাকা ঠিকানা হতো। C++-এ এটা চুপচাপ crash/ভুল ফল দেয়; Rust compile-এ থামায়।"),
    jargon(("Borrow", "মালিকানা না দিয়ে অস্থায়ীভাবে ব্যবহার করতে দেওয়া"),
           ("Borrow checker", "ধার-নিয়ম compile-এ যাচাই করে"),
           ("Data race", "একাধিক জন একসাথে একই data বদলানো/পড়া — borrow নিয়মই এটা অসম্ভব করে")),
    php_note("PHP-তে <code>$first = $cart[0]; $cart[] = 112000;</code> নির্বিঘ্নে চলে, কারণ <code>$first</code> একটা কপি। Rust-এ <code>&amp;</code> মানে কপি না, <b>সরাসরি ঠিকানা</b> — তাই নিয়ম কড়া।"))

c.lesson("Borrow checker: আরও দুই দৃশ্য",
    say("একসাথে দুজন লেখক (<code>&amp;mut</code>) নিষিদ্ধ, আর মালিকানা চলে গেলে পুরনো নাম অচল।"),
    code(r'''
fn main() {
    let mut stock = 10;
    let a = &mut stock;
    let b = &mut stock;      // দ্বিতীয় লেখক!
    *a -= 1;
    *b -= 1;
    println!("{stock}");
}
''', err="E0499"),
    code(r'''
fn main() {
    let invoice = String::from("INV-1001");
    let moved = invoice;                 // মালিকানা moved-এ চলে গেল
    println!("{invoice} {moved}");       // invoice এখন আর নেই
}
''', err="E0382"),
    tip("Borrow checker প্রথমে বিরক্তিকর লাগে — সবাই এটাকে \"fighting the borrow checker\" বলে। কিন্তু প্রতিটা error আসলে একটা সম্ভাব্য production bug, যা আপনার user কখনো দেখবে না।"))

c.lesson("Compile: ভিতরে কী কী ধাপ?",
    say("Rust compile করার সময় কয়েকটা ধাপ পরপর হয়। ভুলের ধরন দেখেই বোঝা যায় কোন ধাপে আটকেছে:"),
    steps("<b>Parse</b> — লেখা ব্যাকরণ মানছে কিনা (syntax)",
          "<b>Type check</b> — সংখ্যায় text যোগ করার মতো ভুল আছে কিনা",
          "<b>Borrow check</b> — ownership আর ধার নিয়ম ঠিক কিনা",
          "<b>Optimize</b> — কোড ছোট ও দ্রুত করা (release build-এ বেশি)",
          "<b>Machine code বানানো ও link</b> — সবকিছু জুড়ে একটা binary"),
    code(r'''
fn main() {
    let total = 18500 + 41500
    println!("{total}");
}
''', err="expected `;`"),
    say("উপরে প্রথম ধাপ (syntax) ব্যর্থ। নিচে দ্বিতীয় ধাপ:"),
    code(r'''
fn main() {
    let total: i32 = 18500 + "41500";
    println!("{total}");
}
''', err="E0277"),
    jargon(("Syntax error", "ভাষার ব্যাকরণ ভুল (<code>;</code> বাদ)"),
           ("Type error", "ভুল ধরনের মান মেশানো"),
           ("Link", "আলাদা আলাদা compile-করা অংশ আর library জুড়ে একটাই binary বানানো"),
           ("Debug vs release build", "debug: দ্রুত compile, ধীর program; release: ধীর compile, <b>অনেক</b> দ্রুত program (<code>cargo build --release</code>)")))

c.lesson("unsafe: শেষ উপায়",
    say("কখনো compiler-এর পাহারা সরিয়ে hardware বা C library-র সাথে সরাসরি কথা বলতে হয়। তখন <code>unsafe</code> block। ভিতরের দায়িত্ব আপনার; বাইরের সবকিছু safe থাকে — তাই বিপদ খোঁজার জায়গা ছোট হয়ে আসে।"),
    code(r'''
fn main() {
    let stock = 42;
    let ptr = &stock as *const i32;        // raw pointer: ঠিকানা, কোনো পাহারা নেই

    let value = unsafe { *ptr };           // ঠিকানা ধরে পড়া — compiler-কে বিশ্বাস করতে বলছি
    println!("ঠিকানা ধরে পাওয়া: {value}");
}
'''),
    tip("সাধারণ Laravel-style application-এ আপনার কখনো <code>unsafe</code> লাগবে না। Rust-এর standard library নিজেই ভিতরে <code>unsafe</code> ব্যবহার করে আপনাকে safe API দেয় — যেমন <code>Vec</code>।"))

c.lesson("Memory-র বিখ্যাত bug",
    say("C/C++-এর বড় security bug-গুলোর বেশিরভাগ এই কয়েকটা কারণে। Rust এগুলো compile-এ বা নিরাপদভাবে আটকায়।"),
    jargon(("Buffer overflow", "list-এর শেষের বাইরে লিখে অন্য data নষ্ট করা — বহু hacker-এর প্রিয় ফাঁক"),
           ("Use-after-free", "ফেরত দেওয়া জায়গা আবার ব্যবহার"),
           ("Dangling pointer", "যে জায়গার দিকে নির্দেশ করছে সেটা আর নেই"),
           ("Double free", "একই জায়গা দুইবার ফেরত"),
           ("Memory leak", "ফেরত না দেওয়া জায়গা জমতে থাকা"),
           ("Null pointer", "\"কিছুই নেই\" ঠিকানা ধরে ব্যবহার — crash")),
    code(r'''
fn main() {
    let prices = [18500, 41500, 112000];
    let index = prices.len() + 2;       // ভুল index
    println!("{}", prices[index]);      // C-তে এটা অজানা memory পড়ত; Rust থামিয়ে দেয়
}
''', panic=True),
    tip("C-তে এই ভুল চুপচাপ অন্য data পড়ে নিত। Rust নিরাপদে থেমে যায় আর ঠিক কোন লাইনে ভুল সেটা বলে — hacker-এর ঢোকার ফাঁক বন্ধ।"))


# ================================================================== ৪. Data
c.section("ডেটা ও algorithm")
c.lesson("Array আর vector",
    say("<b>Array</b> = সমান আকারের কয়েকটা বাক্স পরপর, <b>সংখ্যা নির্দিষ্ট</b> (৩টা বললে ৩টাই)। <b>Vector</b> = বাড়তে-কমতে-পারা list; ভিতরে লুকিয়ে একটা array, ভরে গেলে বড় জায়গায় সরে যায়। নিচে দেখুন কখন জায়গা বাড়ছে:"),
    code(r'''
fn main() {
    let mut cart: Vec<i32> = Vec::new();     // vector
    for price in [18500, 41500, 112000, 1200, 800, 2500, 9000, 600, 300] {
        cart.push(price);
        println!("আছে {} টা, জায়গা আছে {} টার", cart.len(), cart.capacity());
    }
}
'''),
    jargon(("Array", "নির্দিষ্ট সংখ্যক, পরপর সাজানো, একই ধরনের মান"),
           ("Vector (<code>Vec</code>)", "বাড়তে-পারা array; length আর <b>capacity</b> আলাদা"),
           ("Index", "কত নম্বর বাক্স — Rust-এ শুরু <b>০</b> থেকে"),
           ("Capacity", "এখন যত জায়গা নেওয়া আছে; পূর্ণ হলে বড় জায়গায় সরে যায় (উপরে ৪ → ৮ → ১৬)")))

c.lesson("\"Vector\" নামটা কেন?",
    say("গণিতে <b>vector</b> মানে কয়েকটা সংখ্যার সারি, যেমন (৩, ৫, ২) — একটা তীরের দিক ও দৈর্ঘ্য। কম্পিউটার বিজ্ঞানীরা \"সংখ্যার সারি\" অর্থে শব্দটা নিয়ে নেন। C++-এর <code>std::vector</code> থেকে এটা জনপ্রিয়; Rust-ও সেই নামই নিয়েছে (<code>Vec</code>)।"),
    table(["নাম", "মানে", "কোথায়"], [
        ["Vector (গণিত)", "দিক+মান সহ সংখ্যার সারি", "পদার্থবিদ্যা, graphics"],
        ["Vector (C++/Rust)", "বাড়তে-পারা list", "<code>std::vector</code>, <code>Vec&lt;T&gt;</code>"],
        ["List / array (PHP)", "<b>সব কাজের</b> একটাই জিনিস", "<code>$prices = [..]</code>"]]),
    code('''<?php
$a = [18500, 41500];
$a[] = 112000;        // vector-এর মতো
$a['special'] = 999;  // map-এর মতো! একই array-তে
echo json_encode($a), "\\n";
''', "php"),
    php_note("PHP-র array আসলে <b>hash map</b> (key→value), যেটা list-এর মতোও কাজ করে — তাই সুবিধাজনক, কিন্তু ধীর। Rust-এ আলাদা জিনিস: <code>Vec</code> list-এর জন্য, <code>HashMap</code> key-value-র জন্য — দ্রুত, কারণ আকার জানা।"))

c.lesson("vec! আর Vec::new(): macro আবার",
    say("ভিডিওতে বলা \"vec macro না Vec\" প্রশ্নটা আসলে সহজ: দুটো একই জিনিস বানায়, লেখার সুবিধা আলাদা। <code>vec![...]</code> macro (নামের শেষে <code>!</code>) শুরুর মানগুলোসহ বানায়; <code>Vec::new()</code> খালি বানায়।"),
    code(r'''
fn main() {
    let a = vec![18500, 41500, 112000];   // macro: মান দিয়ে বানানো
    let mut b = Vec::new();               // খালি, পরে ভরব
    b.push(18500);
    b.push(41500);
    b.push(112000);
    println!("{a:?} == {b:?} ? {}", a == b);
}
'''))

c.lesson("Hash map, tuple, struct, enum",
    say("PHP-র একটা array দিয়ে সব হতো। Rust-এ কাজ ভাগ — প্রতিটার নাম আর উদ্দেশ্য আলাদা:"),
    table(["জিনিস", "কী", "PHP-তে কাছাকাছি"], [
        ["<b>HashMap</b>", "key → value খোঁজা দ্রুত", "<code>['Mirpur' =&gt; 5]</code>"],
        ["<b>Tuple</b>", "কয়েকটা (আলাদা ধরনের) মান একসাথে", "<code>[$name, $price]</code>"],
        ["<b>Struct</b>", "নামওয়ালা field-সহ নিজের type", "class (শুধু property)"],
        ["<b>Enum</b>", "কয়েকটার <b>একটা</b> (ভিতরে data-সহ হতে পারে)", "constant-এর তালিকা, কিন্তু অনেক শক্তিশালী"],
        ["<b>Set</b>", "শুধু unique মান", "<code>array_unique</code>"]]),
    code(r'''
use std::collections::HashMap;

enum Payment { Cash, Bkash(String) }

fn main() {
    let mut stock = HashMap::new();                 // map: শাখা → পরিমাণ
    stock.insert("Mirpur", 5);
    stock.insert("Uttara", 2);
    println!("Mirpur: {:?}, Gulshan: {:?}", stock.get("Mirpur"), stock.get("Gulshan"));

    let item = ("Redmi 13", 18500);                 // tuple
    println!("{} — {}", item.0, item.1);

    let p = Payment::Bkash("01711-000000".into());  // enum, ভিতরে data
    match p {
        Payment::Cash => println!("নগদ"),
        Payment::Bkash(number) => println!("bKash: {number}"),
    }
}
'''),
    tip("ওপরে <code>Gulshan</code> খুঁজে না পেয়ে <code>None</code> — PHP-র <code>null</code>-এর মতো, কিন্তু Rust-এ <code>Option</code> type দিয়ে আগেই বলতে বাধ্য করে \"এটা না-ও থাকতে পারে\"।"))

c.lesson("Stack আর queue (data structure)",
    say("মনে আছে \"stack\"-এর দুই অর্থ? Memory-র এলাকা আর <b>data structure</b>। এখানে দ্বিতীয়টা: <b>stack</b> = শেষে-ঢুকেছে-আগে-বেরোয় (LIFO, থালার স্তূপ), <b>queue</b> = আগে-ঢুকেছে-আগে-বেরোয় (FIFO, লাইনে দাঁড়ানো)।"),
    code(r'''
use std::collections::VecDeque;

fn main() {
    let mut stack = vec!["INV-1", "INV-2", "INV-3"];
    println!("stack থেকে: {:?}", stack.pop());    // শেষেরটা আগে

    let mut queue = VecDeque::from(["INV-1", "INV-2", "INV-3"]);
    println!("queue থেকে: {:?}", queue.pop_front());  // প্রথমটা আগে
}
'''),
    jargon(("LIFO / FIFO", "Last-In-First-Out (stack) / First-In-First-Out (queue)"),
           ("Queue (job queue)", "Laravel-এর <code>Queue::push()</code>-ও এই ধারণা: কাজ লাইনে দাঁড়ায়, worker একটা একটা করে নেয়")))

c.lesson("Algorithm আর Big-O",
    say("<b>Algorithm</b> = একটা কাজ করার ধাপের তালিকা। একই কাজের একাধিক পথ থাকে; কোনটা কত ধাপ নেয় — সেটা মাপার ভাষা <b>Big-O</b>। ধরুন ফোনের তালিকায় একটা নাম খুঁজছেন: প্রথম থেকে একটা একটা করে (linear), না মাঝখান থেকে আধা আধা করে (binary, শর্ত: তালিকা সাজানো)?"),
    code(r'''
fn linear(list: &[u32], target: u32) -> u32 {
    let mut steps = 0;
    for &x in list {
        steps += 1;
        if x == target { break; }
    }
    steps
}

fn binary(list: &[u32], target: u32) -> u32 {
    let (mut lo, mut hi) = (0usize, list.len());
    let mut steps = 0;
    while lo < hi {
        steps += 1;
        let mid = (lo + hi) / 2;
        if list[mid] == target { break; }
        else if list[mid] < target { lo = mid + 1; }
        else { hi = mid; }
    }
    steps
}

fn main() {
    for n in [10u32, 1_000, 1_000_000] {
        let list: Vec<u32> = (1..=n).collect();
        println!("{n:>9} টা product: linear {:>7} ধাপ, binary {:>2} ধাপ", linear(&list, n), binary(&list, n));
    }
}
'''),
    jargon(("Big-O notation", "ডেটা বাড়লে ধাপ কত বাড়ে তার হিসাব"),
           ("O(1)", "ডেটা যত-ই হোক ধাপ এক (index ধরে পড়া)"),
           ("O(n)", "ডেটার সাথে সমান হারে বাড়ে (linear search)"),
           ("O(log n)", "ডেটা কয়েক গুণ হলেও ধাপ সামান্য বাড়ে (binary search — উপরে ১০ লক্ষে মাত্র ২০ ধাপ)"),
           ("O(n²)", "ডেটা ১০ গুণ → ধাপ ১০০ গুণ; বড় ডেটায় বিপজ্জনক (loop-এর ভিতরে loop)")),
    php_note("Laravel-এর N+1 query সমস্যা আসলে এই কথাই: ১০০ order দেখাতে ১০১টা query। ডেটা বাড়লে ধাপ খুব দ্রুত বাড়ে — Big-O-র দৃষ্টিতে সেটাই দুর্বলতা।"))

c.lesson("Recursion: নিজেকেই ডাকা",
    say("একটা function নিজেকেই ছোট সংস্করণে ডাকলে তাকে <b>recursion</b> বলে। প্রতিটা ডাক stack-এ একটা করে থালা বসায় — তাই অসীম ডাক হলে stack ভরে যায়, একেই বলে <b>stack overflow</b> (বিখ্যাত website-টার নামও এই থেকে)।"),
    code(r'''
fn factorial(n: u64) -> u64 {
    if n <= 1 { 1 } else { n * factorial(n - 1) }
}

fn main() {
    println!("5! = {}", factorial(5));
    println!("10! = {}", factorial(10));
}
'''),
    jargon(("Base case", "যেখানে ডাকা থামে (<code>n &lt;= 1</code>) — না থাকলে চিরকাল চলে"),
           ("Stack overflow", "ডাকের স্তূপ stack-এর সীমা ছাড়িয়ে যাওয়া — program crash")))

c.lesson("Pointer আর reference",
    say("<b>Pointer</b>/<b>reference</b> = মান নয়, <b>মানটা যেখানে আছে তার ঠিকানা</b>। বড় জিনিস কপি না করে ঠিকানা দিলে দ্রুত — কিন্তু ঠিকানা ভুল হলে (জিনিস মুছে গেছে) বিপদ। Rust-এ <code>&amp;</code> চিহ্ন reference, আর borrow checker নিশ্চিত করে ঠিকানাটা সবসময় বৈধ।"),
    code(r'''
fn total(prices: &Vec<i32>) -> i32 {      // &: শুধু ঠিকানা, কপি না
    prices.iter().sum()
}

fn main() {
    let cart = vec![18500, 41500, 112000];
    let t1 = total(&cart);                 // ধার দিলাম
    let t2 = total(&cart);                 // আবার ধার দিলাম — cart এখনো আমার
    println!("{t1} {t2} {}", cart.len());
}
'''),
    jargon(("Pointer", "ঠিকানা (C-তে ভুল পথে যেতে পারে)"),
           ("Reference (<code>&amp;</code>)", "Rust-এর নিরাপদ pointer — borrow checker যাচাই করে"),
           ("Smart pointer", "ঠিকানার সাথে বাড়তি দায়িত্ব (মুছে ফেলা, গোনা) — C++ <code>unique_ptr</code>, Rust <code>Box</code>/<code>Rc</code>"),
           ("Segmentation fault (seg fault)", "program এমন memory ছুঁয়েছে যা তার নয় — OS জোর করে বন্ধ করে")))

# ================================================================== ৫. ভাষার ভিতর
c.section("ভাষার ভিতরের কথা")
c.lesson("Type: PHP-র গোলমাল, Rust-এর কড়াকড়ি",
    say("PHP চুপচাপ type বদলে নেয় (<b>type juggling</b>) — সুবিধা, কিন্তু অদ্ভুত ফল। Rust এটা করে না; ভুল হলে compile-এই থামায়।"),
    code('''<?php
var_dump("5" + 3);        // text + সংখ্যা: চুপচাপ ৮
var_dump("10" == "1e1");  // দুটো text — কিন্তু PHP সংখ্যা ভেবে তুলনা করে
var_dump(0 == "abc");     // PHP 8-এ false (PHP 7-এ true ছিল!)
''', "php"),
    code(r'''
fn main() {
    let total = "5" + 3;
    println!("{total}");
}
''', err="E0369"),
    jargon(("Type juggling / coercion", "ভাষা নিজে নিজে type বদলে দেওয়া"),
           ("Strong vs weak typing", "strong: ভুল type মেশানো আটকায় (Rust); weak: চুপচাপ মেলায় (পুরনো PHP/JS)"),
           ("Static vs dynamic typing", "type compile-এ ঠিক (Rust) / চলার সময় ঠিক (PHP)")))

c.lesson("ভাষার ব্যাকরণ: syntax-এর শব্দ",
    say("ভাষা শেখার সময় এই শব্দগুলো বারবার আসে। একটা ছোট লাইনে সবগুলো দেখুন:"),
    code(r'''
fn main() {
    let price = 18500;                 // let: keyword | price: identifier | 18500: literal
    let vat = price * 15 / 100;        // * / : operator | price * 15 / 100: expression
    println!("VAT: {vat}");            // println!: macro | "VAT..." : string literal
}
'''),
    jargon(("Keyword", "ভাষার সংরক্ষিত শব্দ (<code>let</code>, <code>fn</code>, <code>if</code>) — নাম হিসেবে ব্যবহার নিষেধ"),
           ("Identifier", "আপনার দেওয়া নাম (variable, function)"),
           ("Literal", "সরাসরি লেখা মান (<code>18500</code>, <code>\"text\"</code>)"),
           ("Operator", "<code>+ - * / ==</code> ইত্যাদি চিহ্ন"),
           ("Syntax", "ব্যাকরণ — কীভাবে লিখতে হবে"),
           ("Semantics", "অর্থ — লেখাটা কী করে (ব্যাকরণ ঠিক কিন্তু ভুল হিসাব = semantic bug)")))

c.lesson("Error handling: exception বনাম Result",
    say("কিছু ভুল হতেই পারে (ফাইল নেই, ভুল input)। PHP <b>exception ছোঁড়ে</b> আর <code>try/catch</code>-এ ধরতে হয় — না ধরলে crash। Rust ভুলকে <b>সাধারণ মান</b> হিসেবে ফেরত দেয় (<code>Result</code>) — তাই না সামলে এগোনোই যায় না।"),
    code('''<?php
try {
    echo intdiv(10, 0);
} catch (DivisionByZeroError $e) {
    echo "ধরা পড়ল: ", $e->getMessage(), "\\n";
}
''', "php"),
    code(r'''
fn main() {
    let good = "42".parse::<i32>();
    let bad = "forty-two".parse::<i32>();
    println!("{good:?}");
    println!("{bad:?}");

    match bad {
        Ok(n) => println!("সংখ্যা: {n}"),
        Err(e) => println!("ভুল input: {e}"),
    }
}
'''),
    jargon(("Exception", "ভুলের সংকেত যা call stack বেয়ে উপরে ছোটে (PHP, Java)"),
           ("Result", "Rust-এর মান: <code>Ok(সফল)</code> অথবা <code>Err(ব্যর্থ)</code>"),
           ("Unwrap", "\"নিশ্চিত Ok\" ধরে নিয়ে মান বের করা — ভুল হলে panic; production-এ এড়িয়ে চলুন")))

c.lesson("Generic: একবার লিখে সব type-এ",
    say("ভিডিওতে \"largest item in a list\" function-টা এখানে। <b>Generic</b> (<code>&lt;T&gt;</code>) মানে \"যেকোনো type, তবে শর্ত মানতে হবে\"। শর্তটাকে বলে <b>trait bound</b> (এখানে <code>PartialOrd</code> = তুলনা করা যায়)।"),
    code(r'''
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut big = &list[0];
    for item in list {
        if item > big { big = item; }
    }
    big
}

fn main() {
    println!("{}", largest(&[18500, 41500, 112000]));
    println!("{}", largest(&[1.5, 9.25, 3.0]));
    println!("{}", largest(&["Mirpur", "Uttara", "Gulshan"]));
}
'''),
    jargon(("Generic (<code>&lt;T&gt;</code>)", "type-কে চলক করা — একই code বহু type-এ"),
           ("Trait / trait bound", "type-এর চুক্তি / \"এই চুক্তি মানলে তবেই\" শর্ত"),
           ("Zero-cost abstraction", "সুবিধাজনক ভাষা-গঠন যার জন্য চলার সময় বাড়তি খরচ নেই — compile-এ সব খুলে যায়")))

c.lesson("Runtime, VM, bytecode, JIT",
    say("\"Runtime\" শব্দটার তিন রূপ — প্রসঙ্গ দেখে বুঝতে হয়:"),
    table(["অর্থ", "উদাহরণ"], [
        ["<b>১. সময়</b>: program চলার সময় (compile time-এর উল্টো)", "\"এই ভুল runtime-এ ধরা পড়ে\""],
        ["<b>২. ব্যবস্থা</b>: চালানোর সময় ভাষার সাথে থাকা যন্ত্র", "PHP-র Zend Engine, Java-র JVM, Go-র runtime (GC সহ)"],
        ["<b>৩. async runtime</b>: Rust-এ async কাজ চালানোর library", "<code>tokio</code>"]]),
    jargon(("Virtual machine (VM)", "software দিয়ে বানানো কাল্পনিক computer যা bytecode চালায়"),
           ("Bytecode", "source আর machine code-এর মাঝের ছোট নির্দেশমালা (PHP opcode, Java bytecode)"),
           ("JIT (Just-In-Time)", "চলতে চলতে ঘন ঘন চলা অংশ machine code-এ বদলে নেওয়া — PHP 8-এ আছে"),
           ("Rust-এর runtime", "প্রায় নেই — GC নেই, VM নেই; binary সরাসরি চলে")))


# ================================================================== ৬. Rust কেন
c.section("Rust কেন?")
c.lesson("Rust-এর পাঁচ শক্তি",
    table(["শক্তি", "মানে", "কারণ"], [
        ["<b>গতি</b>", "C/C++-এর কাছাকাছি", "compile হয়ে machine code; GC নেই; runtime প্রায় নেই"],
        ["<b>Memory safety</b>", "memory-র মারাত্মক ভুল হয়ই না", "ownership + borrow checker"],
        ["<b>নিরাপদ concurrency</b>", "একসাথে অনেক কাজ, data race compile-এই বন্ধ", "একই borrow নিয়ম thread-এও"],
        ["<b>নির্ভরযোগ্যতা</b>", "null নেই, ভুল ঢেকে রাখা যায় না", "<code>Option</code>, <code>Result</code>, exhaustive <code>match</code>"],
        ["<b>ভালো tooling</b>", "এক tool-এ build, test, package, doc", "<code>cargo</code>, <code>rustfmt</code>, <code>clippy</code>, <code>rust-analyzer</code>"]]),
    tip("এই পাঁচটার জন্য দাম দিতে হয় — শেখার ঢাল আর compile-এর সময়। পরের কয়েকটা lesson-এ দুই দিকই দেখব।"))

c.lesson("Concurrency-র bug compile-এ",
    say("দুই thread একসাথে একই সংখ্যা বদলালে (<b>data race</b>) ফল এলোমেলো। অন্য ভাষায় এটা চলার সময় কখনো-কখনো ধরা পড়ে, কখনো ধরাই পড়ে না। Rust compile-এই থামায়:"),
    code(r'''
use std::thread;

fn main() {
    let mut sold = 0;
    let handle = thread::spawn(|| {
        sold += 1;                    // অন্য thread-এ আমার variable বদলাচ্ছি!
    });
    handle.join().unwrap();
    println!("{sold}");
}
''', err="E0373"),
    say("ঠিক পথ: <code>Arc</code> (অনেক thread মালিক) + <code>Mutex</code> (একবারে একজন):"),
    code(r'''
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let sold = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    for _ in 0..4 {
        let sold = Arc::clone(&sold);
        handles.push(thread::spawn(move || {
            for _ in 0..1000 {
                *sold.lock().unwrap() += 1;
            }
        }));
    }
    for h in handles { h.join().unwrap(); }
    println!("মোট বিক্রি: {}", *sold.lock().unwrap());
}
'''),
    jargon(("Thread", "program-এর ভিতরে একটা আলাদা কাজের সুতো"),
           ("Data race", "একাধিক thread একসাথে একই data পড়া/বদলানো, অন্তত একজন বদলাচ্ছে — ফল অনির্দিষ্ট"),
           ("Mutex", "তালা: একবারে একজনই ভিতরে"),
           ("Arc", "Atomically Reference Counted — thread-নিরাপদ ভাগাভাগির মালিকানা")))

c.lesson("কারা Rust ব্যবহার করছে",
    say("নিচের তালিকা এই কোর্স লেখার সময় প্রকাশ্যে জানা ব্যবহারগুলো (বিস্তারিত আলাদা করে যাচাই করে নেবেন — কোম্পানির সিদ্ধান্ত বদলায়):"),
    table(["কে", "কোথায় Rust"], [
        ["Linux kernel", "২০২২-এর Linux 6.1 থেকে Rust-এ driver লেখার সমর্থন"],
        ["Android (Google)", "নতুন native code-এ memory-safe ভাষা হিসেবে Rust"],
        ["Firefox (Mozilla)", "Rust-এর জন্মদাতা; browser-এর অংশ (যেমন CSS engine)"],
        ["Cloudflare", "ইন্টারনেট ট্রাফিক সামলানো প্রক্সির অংশ (Pingora)"],
        ["AWS", "Firecracker — serverless-এর হালকা virtual machine"],
        ["Discord, Dropbox", "নিজেদের service/sync engine-এর অংশ Rust-এ নিয়ে গেছে (ভিডিওতে বলা — পরের section দেখুন)"],
        ["CLI tool-এর দুনিয়া", "ripgrep (<code>rg</code>), fd, bat — পুরনো Unix tool-এর দ্রুত বিকল্প"]]),
    tip("\"অনেকে ব্যবহার করে\" মানে \"আপনার জন্য সঠিক\" না। এর পরের lesson-এ উল্টো দিকটাও দেখুন।"))

c.lesson("Rust-এর দুর্বলতা — সৎভাবে",
    table(["সমস্যা", "ব্যাখ্যা"], [
        ["<b>শেখার ঢাল</b>", "ownership, borrow, lifetime একসাথে আসে; স্বস্তি পেতে কয়েক সপ্তাহ-মাস"],
        ["<b>Compile ধীর</b>", "ছোট project-ও সেকেন্ডে সেকেন্ডে; বড় project মিনিটে। PHP-র \"save করে refresh\" নেই"],
        ["<b>Ecosystem ছোট (কিছু ক্ষেত্রে)</b>", "web, CLI, systems — পরিণত। GUI, machine learning — Python/JS/C++ এগিয়ে"],
        ["<b>Hiring</b>", "Rust জানা developer কম; onboarding লাগে"],
        ["<b>Prototype ধীর</b>", "ধারণা দ্রুত যাচাইয়ে PHP/Laravel অনেক দ্রুত"],
        ["<b>Legacy integration</b>", "বিদ্যমান PHP/Java system-এর সাথে জোড়া লাগানো কষ্টকর"]]),
    warn("\"Rust-এ লিখলেই app দ্রুত হয়\" — ভুল। বেশিরভাগ web app-এর ধীরগতির কারণ database query আর network, ভাষা না। Laravel-এ index ঠিক করলে যা হয়, Rust-এ গেলে তা-ই হবে না।"))

c.lesson("Laravel vs Rust: কোথায় কোনটা?",
    table(["দরকার", "Laravel (PHP)", "Rust"], [
        ["Admin panel, CRUD, দ্রুত MVP", "<b>দারুণ</b> — মিনিটে হয়", "পারে, কিন্তু ধীর"],
        ["বিদ্যমান ecosystem (auth, payment, mail package)", "<b>অনেক</b>", "কম, নিজে জুড়তে হয়"],
        ["খুব বেশি concurrent user, কম server খরচ", "বাড়তি server লাগে", "<b>দারুণ</b>"],
        ["CPU-ভারী কাজ (ছবি, PDF, রিপোর্ট)", "ধীর", "<b>দারুণ</b>"],
        ["Long-running service, কম memory", "ঠিক আছে", "<b>দারুণ</b>"],
        ["CLI tool, ছোট binary", "অচল প্রায়", "<b>দারুণ</b>"],
        ["Team ছোট, deadline কম", "<b>ভালো</b>", "ঝুঁকি আছে"]]),
    tip("প্রায়ই সেরা উত্তর <b>মিশিয়ে</b>: সাধারণ page Laravel-এ, ভারী/গতিশীল অংশ Rust service-এ। শেষ section-এ এই পথ দেখব।"))

c.lesson("Rust-এর পরিবেশ: Laravel-এর সাথে মিলিয়ে",
    table(["কাজ", "Laravel/PHP", "Rust"], [
        ["Package manager", "Composer", "<b>Cargo</b>"],
        ["Package registry", "Packagist", "<b>crates.io</b>"],
        ["Documentation", "Laravel docs", "<b>docs.rs</b> (প্রতিটা crate-এর docs নিজে বানায়)"],
        ["Command-line helper", "<code>php artisan</code>", "<code>cargo</code> (<code>run</code>, <code>build</code>, <code>test</code>)"],
        ["Test", "PHPUnit / Pest", "<code>cargo test</code> (ভিতরে বানানো)"],
        ["Code format", "Laravel Pint", "<code>rustfmt</code> (<code>cargo fmt</code>)"],
        ["Static analysis", "PHPStan / Larastan", "<b>Clippy</b> (<code>cargo clippy</code>)"],
        ["Version manager", "phpbrew/Herd", "<b>rustup</b>"],
        ["Editor intelligence", "Intelephense", "<b>rust-analyzer</b>"]]),
    jargon(("Toolchain", "একটা ভাষার সব সরঞ্জাম: compiler + package manager + formatter + linter"),
           ("Linter", "ভুল বা খারাপ অভ্যাসের কোড খুঁজে সতর্ক করা tool"),
           ("Formatter", "কোডের সাজসজ্জা এক ধাঁচে করা")))


# ================================================================== ৭. ভিডিও ১
c.section("ভিডিও ১: Rust hype")
c.lesson("ভিডিও ১: শব্দ-ভুল (auto-caption)",
    say("আপনার পেস্ট করা transcript YouTube-এর স্বয়ংক্রিয় লেখা — তাই অনেক প্রযুক্তি-শব্দ ভুল বানানে। আগে এগুলো ঠিক করে নিই, নইলে বিভ্রান্তি:"),
    table(["transcript-এ", "আসলে", "মানে"], [
        ["Malik, Malak", "<code>malloc</code>", "C-তে memory চাওয়ার function"],
        ["Zigg", "<b>Zig</b>", "C-র আধুনিক বিকল্প একটা systems ভাষা"],
        ["Gradel", "<b>Gradle</b>", "Java-র build tool (Rust-এর Cargo-র মতো কাজ)"],
        ["seale performance", "C-level performance", "C-র সমান গতি"],
        ["RIP, Grep, FD, BAT", "<b>ripgrep</b> (<code>rg</code>), <b>fd</b>, <b>bat</b>", "Rust-এ লেখা দ্রুত command-line tool"],
        ["guey development", "<b>GUI</b> development", "Graphical User Interface — window/button-ওয়ালা app"],
        ["seg fault", "segmentation fault", "ভুল memory ছোঁয়ায় OS-এর জোর করে বন্ধ করা"]]),
    tip("পরের lesson-গুলোতে ভিডিওর প্রতিটা শব্দ ক্রমানুসারে। যে শব্দ আটকাবে, সেই lesson-এর <b>📘 জার্গন</b> কার্ডে খুঁজুন।"))

c.lesson("ভিডিও ১: Rewrite, port, legacy",
    say("ভিডিওর শুরুতে \"সবাই সবকিছু Rust-এ rewrite করছে\"। এই বাক্যের শব্দগুলো:"),
    jargon(("Rewrite", "চালু software-এর কোড নতুন ভাষায়/নতুন করে গোড়া থেকে লেখা — ব্যয়বহুল, ঝুঁকিপূর্ণ"),
           ("Port", "কোড এক ভাষা/platform থেকে আরেকটায় নিয়ে যাওয়া; ভিডিওতে TypeScript compiler-কে Go-তে port করার কথা"),
           ("Codebase", "একটা project-এর সব source code"),
           ("Legacy", "পুরনো কিন্তু এখনো ব্যবসা-চালানো system; বদলানো কঠিন"),
           ("Sync engine", "Dropbox-এর যে অংশ আপনার ফাইল আর server-এর ফাইল মিলিয়ে রাখে"),
           ("Backend", "server-এর দিকের অংশ (database, business logic) — যা user সরাসরি দেখে না"),
           ("Adoption", "কোনো প্রযুক্তি মানুষ/কোম্পানি কতটা নিচ্ছে"),
           ("Force multiplier", "যা একই লোকবলে কাজের পরিমাণ বহুগুণ করে — Dropbox বলেছিল Rust তাদের জন্য তা-ই")),
    warn("\"Rewrite\" সফটওয়্যারের সবচেয়ে ঝুঁকিপূর্ণ সিদ্ধান্তগুলোর একটা। ভিডিওর Dropbox-এর সাড়ে চার বছর (\"four years\") এর প্রমাণ। শেষ section-এ দেখব নিরাপদ বিকল্প।"))

c.lesson("ভিডিও ১: Systems programming language",
    say("ভিডিও বলছে \"Rust is a systems programming language\"। মানে কী?"),
    jargon(("Systems programming", "যে software অন্য software-এর নিচে বসে: operating system, database, browser engine, network server, driver — যেখানে গতি আর memory-র উপর নিয়ন্ত্রণ জরুরি"),
           ("Application programming", "user-এর কাজের software: invoice page, shop website — Laravel-এর জগৎ"),
           ("Low-level control", "memory/CPU-র সাথে সরাসরি, বেশি কাছ থেকে কাজ করার ক্ষমতা")),
    say("ভিডিও আরও বলছে Rust \"as fast as C, as safe as Java, and as expressive as Python\"। শব্দ-বিশ্লেষণ:"),
    table(["অংশ", "মানে"], [
        ["as fast as C", "গতি C-র সমান (compile + GC নেই)"],
        ["as safe as Java", "memory-র ভুল Java-র মতোই নিরাপদ (কিন্তু GC ছাড়া)"],
        ["as expressive as Python", "<b>expressive</b> = অল্প কোডে অনেক কিছু প্রকাশ করা যায়; <code>iter().map().sum()</code>, <code>match</code>, <code>enum</code> ইত্যাদি"]]),
    php_note("\"Memory safety without garbage collection\" = PHP/Java-র মতো নিরাপদ, কিন্তু GC-র পেছনে-চলা কাজ ছাড়া।"))

c.lesson("ভিডিও ১: ভিডিওর দুই code",
    say("ভিডিওতে বলা হয়েছিল: C-তে <code>malloc</code> করে <code>free</code> করে আবার ব্যবহার করলে compile হয়ে যায় — এটা <b>use-after-free</b>। (নিচের C code শুধু দেখানোর জন্য — চালালে ফল অনির্দিষ্ট, তাই চালাইনি।)"),
    code(r'''
#include <stdlib.h>

int main(void) {
    char *p = malloc(10);   // memory চাইলাম
    free(p);                // ফেরত দিলাম
    p[0] = 'x';             // ফেরত-দেওয়া জায়গায় লিখছি — compile হয়, কিন্তু security ফাঁক
    return 0;
}
''', "c", run=False, label="C — compile হয়, বিপজ্জনক"),
    say("Rust-এ ভিডিওর সমান উদাহরণ — \"create a box, drop it, try to use it\":"),
    code(r'''
fn main() {
    let stock = Box::new(42);     // Box: heap-এ একটা মান
    drop(stock);                  // মুছে ফেললাম
    println!("{stock}");          // আবার ব্যবহার — compile-ই হবে না
}
''', err="E0382"),
    jargon(("Box", "heap-এ একটা মান রাখার smart pointer"),
           ("drop", "মান মুছে memory ফেরত দেওয়া (Rust-এ সাধারণত নিজে নিজেই হয়)"),
           ("Security vulnerability", "hacker কাজে লাগাতে পারে এমন ফাঁক — ভিডিওর \"70%\" দাবিটা Microsoft-এর বলা: তাদের security bug-এর প্রায় ৭০% memory-সংক্রান্ত")))

c.lesson("ভিডিও ১: Performance-এর শব্দ",
    say("Discord-এর গল্প: তাদের এক service Go-তে ছিল, আর Go-র GC প্রায় প্রতি ২ মিনিটে একবার বড় পরিষ্কারে নামত — ফলে সব user-এর app ক্ষণিক আটকে যেত। Rust-এ নিয়ে ফেলায় (ভিডিওর ভাষায়) \"১০ গুণ\" দ্রুত হলো আর সেই বিরতি গেল।"),
    jargon(("GC pause / spike", "GC চলার সময় program-এর ক্ষণিক থেমে যাওয়া বা হঠাৎ বেড়ে-যাওয়া সময় (latency spike)"),
           ("Overhead", "আসল কাজের বাইরে বাড়তি খরচ (GC-র সময়, memory)"),
           ("Latency", "এক কাজের সময় — \"স্পাইক\" মানে হঠাৎ এটা অনেক বেড়ে যাওয়া"),
           ("Throughput", "নির্দিষ্ট সময়ে কত কাজ হয় (সেকেন্ডে কত request)"),
           ("10x (দশ গুণ)", "ভিডিওর দাবি — নির্দিষ্ট service-এর নির্দিষ্ট মাপে; সব app-এ ১০ গুণ আশা করা ভুল"),
           ("Benchmark", "একই কাজে দুই জিনিসের গতি মাপার পরীক্ষা — ফল নির্ভর করে কী মাপা হলো তার উপর")),
    warn("\"Discord ১০ গুণ দ্রুত পেয়েছে\" শোনার পর \"আমার Laravel app-ও Rust-এ ১০ গুণ দ্রুত হবে\" ভাবা ঠিক না। তাদের সমস্যা ছিল একটা নির্দিষ্ট GC pause; আপনার app-এর সমস্যা হয়তো ধীর query।"))

c.lesson("ভিডিও ১: C, C++, Go, Zig তুলনা",
    say("ভিডিও একই ছোট CLI app পাঁচ ভাষায় বানিয়ে তুলনা করেছে:"),
    table(["ভাষা", "ভিডিওর কথা", "শব্দ"], [
        ["C", "কাঁচা গতি; malloc/free নিজে", "<b>segfault</b>, memory leak"],
        ["C++", "vector, smart pointer আছে কিন্তু জটিল; \"প্রতিটা কাজের ছয় উপায়\"", "<b>smart pointer</b> (<code>unique_ptr</code>), <b>feature bloat</b> (ভাষায় অতিরিক্ত অনেক উপায়)"],
        ["Go", "সহজ, দ্রুত compile; কম নিয়ন্ত্রণ, কিছু গতি কম", "<b>fast compilation</b>, GC আছে"],
        ["Zig", "C-র মতো কিন্তু ভালো tooling, compile-time নিরাপত্তা; ecosystem ছোট; ৮-৯ বছর beta", "<b>ecosystem</b>, <b>beta</b>, <b>comptime</b>"],
        ["Rust", "দুইয়ের মাঝের মিষ্টি জায়গা", "borrow checker"]]),
    jargon(("Ecosystem", "ভাষাকে ঘিরে library, tool, কমিউনিটি, চাকরির বাজার — সব মিলিয়ে"),
           ("Beta", "প্রায় তৈরি কিন্তু পুরোপুরি স্থির না; বদলাতে পারে"),
           ("\"shaking hands with the CPU\"", "ইংরেজি বাগধারা: CPU-র একদম কাছাকাছি, সরাসরি কাজ করা — এখানে Zig অত্যন্ত low-level"),
           ("Sponsor segment", "YouTube ভিডিওর মাঝে টাকা-দেওয়া বিজ্ঞাপন (Micro Center অংশ) — প্রযুক্তি-আলোচনা না, বাদ দিন")))

c.lesson("ভিডিও ১: Rust লেখার অভিজ্ঞতা",
    say("বক্তা বলেছেন তিনি Java developer হিসেবে সব জায়গায় <code>for</code> loop লিখতেন, iterator method জানতেন না। দুটো একই ফল দেয়; Rust-এ দ্বিতীয়টাই স্বাভাবিক:"),
    code(r'''
fn main() {
    let prices = [18500, 41500, 112000, 1200];

    // for loop (Java-মনের লেখা)
    let mut total = 0;
    for p in prices {
        if p > 10000 { total += p; }
    }

    // iterator method (Rust-স্টাইল): filter + sum
    let total2: i32 = prices.iter().filter(|&&p| p > 10000).sum();

    println!("{total} {total2}");
}
'''),
    jargon(("Iterator method", "<code>map</code>, <code>filter</code>, <code>sum</code> — list-কে ধাপে ধাপে বদলানোর method (Laravel Collection-এর মতো)"),
           ("Fighting the borrow checker", "borrow checker বারবার কোড নাকচ করছে, আর আপনি বুঝছেন না কেন — Rust শেখার প্রথম দিকের সাধারণ অভিজ্ঞতা"),
           ("Learning curve", "শেখার কষ্টের ঢাল: কতটা সময়ে স্বচ্ছন্দ হওয়া যায় (ভিডিও: ৩–৬ মাস)"),
           ("Mental model", "একটা বিষয় আপনার মাথায় কীভাবে কাজ করে ভাবা — GC-ভাষা থেকে এলে ownership-র নতুন \"মনের ছবি\" বানাতে হয়"),
           ("Onboarding", "নতুন লোক কাজে স্বচ্ছন্দ হওয়ার প্রক্রিয়া")),
    tip("ভিডিওর সেই \"vector-এর reference নিয়ে push\" ঝামেলা আমরা আগেই দেখেছি (Borrow checker lesson, E0502)। আর \"vec macro নাকি Vec\" — দুটোই এক জিনিস বানায়।"))

c.lesson("ভিডিও ১: Tooling — Cargo, Gradle, compile সময়",
    jargon(("Cargo", "Rust-এর build + package manager + test runner একসাথে (<code>cargo run</code>, <code>cargo test</code>)"),
           ("Gradle", "Java/Android-এর build tool — খুব নমনীয়, যেকোনো কিছু বানানো যায়, কিন্তু জটিল"),
           ("Opinionated", "tool নিজে একটা \"সঠিক পথ\" ঠিক করে দেয়, বিকল্প কম — Cargo তেমন; Laravel-ও opinionated; সুবিধা: সহজ, অসুবিধা: নমনীয়তা কম"),
           ("Hot reload", "কোড সেভ করলেই চলমান app-এ বদল ঢুকে যাওয়া (PHP-তে refresh করলেই হয়)"),
           ("Compile time", "compile করতে যত সময় লাগে — ভিডিওতে ছোট project-এও ১৫–২০ সেকেন্ড"),
           ("Error messages", "Rust-এর compiler সমস্যা কোথায় আর কীভাবে সারবেন তা-ও বলে — যা আপনি আগের lesson-গুলোর আসল error-এ দেখেছেন"),
           ("\"Stockholm syndrome\"", "মজা করে বলা: যে বন্দী করে তাকেই ভালোবেসে ফেলা — এখানে Rust-এর ধীর compile-কে community-র মেনে নেওয়া")),
    php_note("PHP-তে save করে refresh করলেই নতুন কোড চলে — compile-এর অপেক্ষা নেই। Rust-এ <code>cargo watch</code> বা <code>topcoat dev</code>-এর মতো tool সেই অভিজ্ঞতার কাছাকাছি আনে।"))

c.lesson("ভিডিও ১: Lifetime — concept fatigue-র একটা",
    say("ভিডিও বলছে Rust-এ ownership, borrowing, <b>lifetime</b>, trait, generic, macro, async/await — একসাথে অনেক ধারণা (\"concept fatigue\")। এর অনেকগুলো আমরা দেখেছি; <b>lifetime</b> নতুন। নিচে compiler জিজ্ঞেস করছে \"ফেরত-দেওয়া reference কার জীবন ধরে বাঁচবে?\":"),
    code(r'''
fn longest(a: &str, b: &str) -> &str {
    if a.len() > b.len() { a } else { b }
}

fn main() {
    println!("{}", longest("Mirpur", "Gulshan"));
}
''', err="E0106"),
    say("সমাধান: একটা <b>lifetime নাম</b> (<code>'a</code>) দিয়ে বলে দেওয়া — \"ফল আর দুই input একই সময় পর্যন্ত বাঁচে\":"),
    code(r'''
fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() { a } else { b }
}

fn main() {
    println!("{}", longest("Mirpur", "Gulshan"));
}
'''),
    jargon(("Lifetime", "একটা reference কতক্ষণ বৈধ — compiler নিশ্চিত করে reference তার আসল মানের চেয়ে বেশিদিন বাঁচে না"),
           ("Concept fatigue", "একসাথে অনেক নতুন ধারণা শিখতে গিয়ে ক্লান্তি (JS-এর \"framework fatigue\"-এর মতো)"),
           ("Trait / Generic / Async", "চুক্তি / যেকোনো type / অপেক্ষার সময় অন্য কাজ — আগের lesson-গুলোতে")))

c.lesson("ভিডিও ১: Rust কেন সবাই বেছে নেয় না",
    say("ভিডিওর সবচেয়ে শিক্ষণীয় অংশ: TypeScript-এর দল Rust ভালোবাসে, তবু তাদের compiler Go-তে port করেছে। কেন?"),
    jargon(("Port to Go vs Rust", "তাদের পুরনো code-এ ছিল অনেক পরস্পর-জড়ানো object (graph), যা Rust-এর ownership নিয়মে বসানো কঠিন; Go-তে (GC আছে) প্রায় সরাসরি নেওয়া গেল — ~১ বছর, Rust-এ অনেক বছর লাগত"),
           ("Unsafe code", "compiler-এর পাহারা বন্ধ-করা অংশ — ভিডিও: Rust-এ করতে গেলে প্রচুর <code>unsafe</code> বা নিজের GC বানাতে হতো, যা Rust-এর উদ্দেশ্যই নষ্ট করে"),
           ("Design goal", "ভাষা বানানোর সময় যে লক্ষ্য ঠিক করা — Rust-এর লক্ষ্য \"পুরনো Java code সহজে port করা\" নয়"),
           ("Time to market", "ধারণা থেকে বাজারে পৌঁছাতে কত সময় — Go/PHP এখানে এগিয়ে"),
           ("Rapid prototyping", "দ্রুত একটা কাঁচা সংস্করণ বানিয়ে ধারণা পরীক্ষা — Laravel এখানে দারুণ"),
           ("Integration", "নতুন system পুরনোর সাথে জোড়া লাগানো — Java/.NET/C++ বিনিয়োগ থাকলে খরচ বেশি"),
           ("Trade-off", "একটা পেতে আরেকটা ছাড়া — গতি বনাম শেখার সহজতা")),
    tip("পাঠ: \"সেরা ভাষা\" বলে কিছু নেই — আছে \"এই সমস্যার জন্য উপযুক্ত ভাষা\"।"))

c.lesson("ভিডিও ১: উপসংহারের শব্দ",
    jargon(("Most admired language", "Stack Overflow-র বার্ষিক developer জরিপে \"যারা ব্যবহার করেছে, তাদের মধ্যে আবার ব্যবহার করতে চায়\" র‍্যাঙ্কিং-এ Rust বহু বছর ধরে এক নম্বর — জনপ্রিয়তা (কতজন ব্যবহার করে) থেকে আলাদা"),
           ("Hype", "যতটা প্রাপ্য তার চেয়ে বেশি আলোচনা/উত্তেজনা — ভিডিওর প্রশ্ন: Rust কি hype মাত্র?"),
           ("Sustainable adoption", "দীর্ঘমেয়াদে টেকসই গ্রহণ — হুজুগ না, বাস্তব ব্যবসায়িক মূল্যের জন্য"),
           ("Zero-sum", "একজনের লাভ মানেই আরেকজনের ক্ষতি — ভিডিও: প্রযুক্তি তা নয়, Rust নিলে বাকিরা মরে না"),
           ("Use case", "নির্দিষ্ট কাজ/পরিস্থিতি যার জন্য প্রযুক্তি বেছে নেওয়া হচ্ছে"),
           ("Strategic position", "যে ক্ষেত্রে Rust-এর শক্তি সবচেয়ে কাজে লাগে: performance-critical system, security-sensitive app, long-running service, CLI tool")),
    table(["ভিডিওর রায়: Rust ভালো", "Rust ভালো না"], [
        ["Performance-critical system", "Rapid prototyping"],
        ["Security-sensitive application", "Tight deadline-এর দল"],
        ["Long-running service", "বিস্তৃত legacy integration"],
        ["CLI tool, systems", "GUI, machine learning (ecosystem ছোট)"]]))


# ================================================================== ৮. ভিডিও ২
c.section("ভিডিও ২: Topcoat")
c.lesson("ভিডিও ২: একটা আধুনিক web framework-এর ফিচার",
    say("বক্তা শুরুতে বললেন Topcoat \"on the surface looks like a typical modern web framework\" — তার ফিচার-তালিকার শব্দগুলো:"),
    jargon(("Web framework", "web app বানানোর কাঠামো (Laravel, Rails, Next.js) — routing, template, database সহ"),
           ("Server-side rendering (SSR)", "HTML server-এ বানিয়ে পাঠানো — Blade যেমন"),
           ("API endpoint", "JSON/data দেওয়ার URL (<code>/api/products</code>)"),
           ("Component library", "তৈরি করা UI অংশের সংগ্রহ (button, dialog, table)"),
           ("shadcn/ui-inspired", "<b>shadcn/ui</b> একটা জনপ্রিয় React component library; তার নকশা-দর্শন: component-এর কোড আপনার project-এ <b>কপি</b> হয়ে আসে, library হিসেবে লুকানো থাকে না। Topcoat-এর <code>topcoat ui</code> command-ও সেভাবে চলে"),
           ("Tailwind CSS", "\"utility-first\" CSS: <code>class=\"p-4 text-red-500\"</code> এভাবে ছোট ছোট class জুড়ে styling — আলাদা CSS ফাইল কম লাগে"),
           ("Client-side interactivity", "page লোডের পর browser-এ click/type-এ কিছু বদলানো"),
           ("Component function", "UI-র অংশ বানানো function (<code>#[component]</code>)"),
           ("<code>view!</code> macro", "Rust-এর ভিতরে HTML লেখার macro"),
           ("Signal", "বদলানো-যায় এমন মান, যা বদলালে নির্ভরশীল অংশ নিজে আপডেট হয় — Vue-এর <code>ref</code>"),
           ("Client state", "browser-এ থাকা বদলানো-যায় এমন তথ্য")))

c.lesson("ভিডিও ২: Boilerplate আর WebAssembly-র ঝামেলা",
    say("ভিডিওর মূল বক্তব্য: Topcoat-এর ফিচারগুলো \"requires little or no boilerplate\"। আর অন্য Rust framework-এর interactivity <b>WebAssembly</b>-তে — যা শক্তিশালী কিন্তু \"caveat\" আছে:"),
    jargon(("Boilerplate", "বারবার লিখতে হয় এমন একঘেয়ে কাঠামো-কোড — যত কম, তত ভালো"),
           ("WebAssembly (WASM)", "browser-এ চলার জন্য compile করা binary; Rust compile করে এখানে নেওয়া যায় (Leptos এভাবে)"),
           ("Caveat", "সতর্কতা/সীমাবদ্ধতা; \"it comes with caveats\" = এর সাথে কিছু অসুবিধাও আছে"),
           ("Browser API", "browser-এর দেওয়া সুবিধা: <code>localStorage</code>, <code>fetch</code>, camera, clipboard — JavaScript সরাসরি পায়; WASM-কে মাঝখানে \"সেতু\" লাগে (ঝামেলা)"),
           ("JavaScript library", "অন্য মানুষের লেখা JS code (chart, date-picker) — WASM থেকে ডাকা কষ্টকর"),
           ("Escape hatch", "নিয়মের বাইরে যাওয়ার দরজা: যা framework সরাসরি পারে না, তা নিজে করার সুযোগ — Topcoat-এ <code>raw!</code> macro দিয়ে সরাসরি JavaScript লেখা যায়"),
           ("Friction", "কাজ ধীর বা কষ্টকর করা ছোট ছোট বাধা")),
    tip("Leptos (আমাদের আগের course) WASM ব্যবহার করে; Topcoat করে না — দুটোর পার্থক্যের মূল এটাই।"))

c.lesson("ভিডিও ২: Server আর client — দুই পথ",
    say("বক্তা বলছেন Topcoat দুই আলাদা পথ নেয়: <b>server</b> আর <b>client</b>। সহজ ভাষায়:"),
    table(["", "Server-এ", "Client (browser)-এ"], [
        ["কী চলে", "markup বানানো, <b>runtime expression</b> প্রথমবার হিসাব", "<b>একই expression</b> JavaScript হয়ে আবার চলে"],
        ["কখন", "<b>initial render</b> — page প্রথম আসার সময়", "পরে, click বা input-এ"],
        ["ভাষা", "Rust", "<b>Rust → JavaScript-এ compile</b>"]]),
    jargon(("Runtime expression (<code>$(...)</code>)", "Topcoat-এর বিশেষ চিহ্ন: ভিতরের Rust expression server আর browser — দুই জায়গাতেই চলে"),
           ("Initial render", "page প্রথমবার যে অবস্থায় আঁকা হয়"),
           ("Compile Rust into JavaScript", "ভিডিওর অদ্ভুত অংশ: Rust code ছোট JS code-এ বদলে browser-কে দেওয়া; WASM লাগে না"),
           ("Limited subset", "Rust-এর সব ক্ষমতা নয়, শুধু একটা সীমিত অংশ চলে — কারণ JS-এ সমান আচরণ নিশ্চিত করতে হয়"),
           ("Design decision", "ইচ্ছাকৃত সিদ্ধান্ত — সীমিত রাখা দুর্বলতা না; জটিল কাজ server-এ করানোই Topcoat-এর পথ")),
    php_note("Alpine.js-এ <code>x-data</code> আর <code>@click</code> যেমন সরল interactivity দেয় — Topcoat-এর <code>$()</code> সেই ধরনের, কিন্তু type-checked Rust-এ। জটিল কাজ Livewire-এর মতো server-এ।"))

c.lesson("ভিডিও ২: Server-first দর্শন (GOTH, HTMX)",
    say("বক্তা বলছেন তিনি \"server-side solution\" পছন্দ করেন — তাঁর আগের course website <b>GOTH stack</b>-এ।"),
    jargon(("Paradigm", "কাজ করার মূল ধরন/দর্শন"),
           ("Server-first philosophy", "যথাসম্ভব কাজ server-এ, browser-এ ন্যূনতম — Laravel + Livewire-এর ধারার"),
           ("GOTH stack", "<b>G</b>o + <b>T</b>empl + <b>H</b>TMX + (Tailwind) — Go ভাষার server-rendered web stack"),
           ("HTMX", "ছোট JavaScript library: HTML attribute দিয়ে \"click করলে server থেকে HTML টুকরো এনে এই জায়গায় বসাও\" বলা যায়, বড় JS framework ছাড়া"),
           ("Heavy front-end framework", "React/Vue/Angular — browser-এ অনেক কাজ, বড় JavaScript bundle")),
    table(["ধরন", "HTML কোথায় বানায়", "উদাহরণ"], [
        ["Blade (পুরনো SSR)", "server, প্রতিবার পুরো page", "Laravel Blade"],
        ["Livewire / HTMX / Topcoat shard", "server, শুধু বদলানো অংশ", "Livewire, HTMX, Topcoat"],
        ["SPA (React/Vue)", "browser (client)", "React + Laravel API"],
        ["WASM framework", "browser, Rust-এ", "Leptos"]]))

c.lesson("ভিডিও ২: Procedure — server function-কে client থেকে ডাকা",
    say("ভিডিওর \"procedure\": একটা সাধারণ <code>async fn</code> লিখে <code>#[procedure]</code> attribute দিলে সেটা <b>server-এ চলে</b>, কিন্তু browser-এর expression থেকে সাধারণ async function-এর মতো <code>.await</code> করে ডাকা যায়। Topcoat <b>HTTP endpoint আর client-এর request code দুটোই নিজে বানায়</b>।"),
    code(r'''
#[procedure]
async fn save_note(cx: &Cx, text: String) -> Result<()> {
    // server-এ চলে: database-এ লেখা (সত্যিকারের demo আমাদের Topcoat course-এ)
    Ok(())
}
''', "rust", run=False, file="src/notes.rs"),
    jargon(("Async function", "যে function অপেক্ষার সময় অন্য কাজ করতে দেয় (<code>.await</code>)"),
           ("Attribute (<code>#[procedure]</code>)", "function-এর উপরের নির্দেশ — compiler/macro-কে বলে \"এর সাথে বাড়তি কিছু বানাও\""),
           ("RPC", "Remote Procedure Call: দূরের function-কে নিজের function-এর মতো ডাকা"),
           ("Seamless", "মসৃণ — জোড়ার দাগ বোঝা যায় না"),
           ("HTTP endpoint", "network-এ একটা URL যেখানে request নেওয়া হয়")),
    tip("আসল চালানো উদাহরণ: <b>Rust Topcoat</b> কোর্সে \"Procedure: browser থেকে server function\" lesson।"))

c.lesson("ভিডিও ২: Database আর Neon",
    say("ভিডিওর স্পনসর অংশে Postgres database-এর কিছু ধারণা আছে, যেগুলো যেকোনো production app-এ লাগে:"),
    jargon(("PostgreSQL (Postgres)", "জনপ্রিয় open-source relational database — MySQL-এর মতো কিন্তু আরও শক্তিশালী"),
           ("Provider / managed database", "database নিজে চালানোর বদলে যে কোম্পানি আপনার জন্য চালায় (Neon তেমন একটা)"),
           ("Database instance", "চলমান একটা database-এর কপি"),
           ("Connection URL", "database-এ ঢোকার ঠিকানা + পাসওয়ার্ড একসাথে: <code>postgres://user:pass@host/db</code>"),
           ("<code>.env</code> file", "গোপন সেটিং (পাসওয়ার্ড, URL) রাখার ফাইল — Laravel-এও আছে; কখনো Git-এ তোলা হয় না"),
           ("CLI", "Command-Line Interface — terminal থেকে চালানো tool (<code>neon</code>, <code>topcoat</code>, <code>cargo</code>)"),
           ("Database branching", "Git branch-এর মতো database-এর কপি বানানো: আসল ডেটায় হাত না দিয়ে পরীক্ষা"),
           ("Review app / dev environment", "pull request বা পরীক্ষার জন্য আলাদা অস্থায়ী app/পরিবেশ — প্রতিটার নিজস্ব database branch"),
           ("Production (prod)", "আসল user যে সংস্করণ ব্যবহার করছে — এখানে ভুল মানে আসল ক্ষতি"),
           ("Automatic backup", "নিজে নিজে নিয়মিত কপি রাখা"),
           ("Point-in-time recovery (PITR)", "\"গতকাল বিকেল ৩:১৫ যেমন ছিল\" ঠিক সেই অবস্থায় database ফিরিয়ে আনা"),
           ("Data anonymization", "আসল ডেটার নাম/ফোন ইত্যাদি বদলে পরীক্ষার কাজে নিরাপদে ব্যবহার"),
           ("Free plan / sponsor", "ভিডিওর প্রযোজক Neon-কে প্রচার করছেন — প্রযুক্তিগত সুপারিশ নয়, বিজ্ঞাপন; যেকোনো Postgres দিয়েই কাজ হয়")),
    php_note("Laravel-এ <code>.env</code>-এ <code>DB_URL</code>, <code>php artisan migrate</code> আর staging database — একই ধারণা; branching তার ওপর বাড়তি সুবিধা।"))

c.lesson("ভিডিও ২: App context আর request context",
    say("বক্তা বলছেন \"axum-এর <code>with_state</code>-এর মতো\" আর \"axum আর Topcoat একই GitHub org-এর\" — দুটোই সত্য: <code>tokio-rs</code> অর্গানাইজেশনে দুটোই।"),
    jargon(("App context", "সব request-এ ভাগ হওয়া মান যা এক request-এর চেয়ে বেশিদিন বাঁচে — যেমন database pool"),
           ("Database pool", "আগে থেকে খুলে রাখা কয়েকটা connection; request এলে একটা ধার নেয়, শেষে ফেরত দেয়"),
           ("Request context (<code>Cx</code>)", "এক request-এর সব তথ্য ও হাতল: HTTP header/path/method, signal বানানো, app context পড়া"),
           ("HTTP method", "<code>GET</code>, <code>POST</code>… request-এর ধরন"),
           ("Server handler", "server-এ চলে এমন অংশ: page, layout, route, component, procedure, shard"),
           ("Keyed by type", "মানটা খোঁজা হয় তার <b>Rust type</b> দিয়ে — তাই <code>let db: &amp;Database = app_context(cx)</code> লিখলেই হলো"),
           ("<code>with_state</code> (axum)", "axum-এর সমান ধারণা: router-এ shared মান জুড়ে দেওয়া"),
           ("GitHub org", "একই সংগঠনের অধীনে প্রকল্পগুলো — তাই দুটোর নকশা-ভাবনা মেলে")))

c.lesson("ভিডিও ২: Shard, DOM merge আর latency",
    say("\"Shard\": যে component-এর argument বদলালে <b>server আবার সেই অংশের HTML বানিয়ে</b> পাঠায়, আর browser সেটা পুরনো অংশের জায়গায় মিলিয়ে (merge) দেয়। ভিডিওর শব্দগুলো:"),
    jargon(("Shard", "আলাদা HTTP endpoint-ওয়ালা server-component; শুধু নিজের অংশ আবার আঁকে — তাই একটা optimization"),
           ("Re-render", "আবার আঁকা"),
           ("DOM / merge into the DOM", "browser-এর page-tree; নতুন HTML পুরো বদলে না ফেলে মিলিয়ে দেওয়া যাতে focus/scroll নষ্ট না হয়"),
           ("Server-read signal", "signal server-ও পড়ে (runtime expression-এর বাইরে) — বদলালে পুরো page server-এ আবার আঁকা হয়; shard হলে শুধু সেই অংশ"),
           ("Server round trip", "browser → server → browser পুরো যাওয়া-আসা; এতে সময় লাগে = latency"),
           ("In-flight request", "পাঠানো হয়েছে কিন্তু উত্তর আসেনি এমন request"),
           ("Coalescing", "একই \"tick\"-এ (এক ঝলকে) একাধিক পরিবর্তন জুড়ে <b>একটাই</b> request পাঠানো"),
           ("Abort previous request", "নতুন পরিবর্তন এলে আগের পাঠানো request বাতিল"),
           ("Latest wins", "সবসময় শেষ মানের উত্তরটাই ব্যবহার — পুরনো ধীর উত্তর নতুনের উপর বসে যায় না")),
    code(r'''
fn main() {
    // ধারণার ছোট মডেল (Topcoat-এর আসল code নয়): একই ঝলকে ৫টা পরিবর্তন → ১টা request
    let typed = ["r", "re", "red", "redm", "redmi"];
    let mut latest = "";
    for t in typed {
        latest = t;                 // প্রতিটা পরিবর্তন শুধু "সর্বশেষ মান" বদলায়
    }
    println!("{} টা পরিবর্তন, request গেল ১টা, মান: {latest}", typed.len());
}
'''),
    tip("আপনি search box-এ \"redmi\" লিখতে প্রতিটা অক্ষরে আলাদা request গেলে server ভেসে যেত, আর ধীর উত্তর পরে এসে নতুন ফল ঢেকে দিত। এই দুটো সমস্যারই সমাধান coalescing + abort।"))

c.lesson("ভিডিও ২: Memoization আর single-flight",
    say("ভিডিওর শেষ বড় ফিচার <code>#[memoize]</code>। একটা request-এর মধ্যে একই function একই argument-এ দুবার ডাকলে দ্বিতীয়বার database না গিয়ে <b>আগের ফল</b> দেয়। নিচে ধারণার ছোট মডেল (দুটো আসল আউটপুটের তুলনা):"),
    code(r'''
use std::collections::HashMap;

fn get_user(id: u32, db_calls: &mut u32) -> String {
    *db_calls += 1;
    println!("  database query: user {id}");
    format!("user-{id}")
}

fn main() {
    println!("memoize ছাড়া:");
    let mut calls = 0;
    let a = get_user(7, &mut calls);
    let b = get_user(7, &mut calls);
    println!("  {a}, {b} — database ডাক: {calls}");

    println!("memoize সহ (ফল মনে রাখি):");
    let mut cache: HashMap<u32, String> = HashMap::new();
    let mut calls = 0;
    for _ in 0..2 {
        let user = cache.entry(7).or_insert_with(|| get_user(7, &mut calls));
        println!("  পেলাম {user}");
    }
    println!("  database ডাক: {calls}");
}
'''),
    jargon(("Memoization", "ফাংশনের ফল তার argument অনুযায়ী মনে রাখা (cache); একই argument-এ আবার হিসাব না করা"),
           ("Per-request cache", "শুধু এক request-এর জন্য বেঁচে থাকে — request শেষে মুছে যায়, তাই পুরনো-ডেটার ভয় নেই"),
           ("Keyed by arguments", "cache-এর চাবি হলো function-এর argument"),
           ("Single-flight", "একই মুহূর্তে একই কাজের অনেকগুলো অনুরোধ এলে আসলে একটাই চলে, বাকিরা তার ফলের জন্য অপেক্ষা করে — ১০ জন গ্রাহক একসাথে দাম জিজ্ঞেস করলে ক্যাশিয়ার একবারই দেখে সবাইকে বলে"),
           ("Sync vs async function", "sync: শেষ না হওয়া পর্যন্ত আটকে থাকে; async: অপেক্ষার সময় ছেড়ে দেয়")),
    php_note("Laravel-এ <code>$user = once(fn () =&gt; User::find(7))</code> বা <code>Cache::remember()</code> — একই ধারণা। N+1 সমস্যা সারানোর একটা পথ।"))

c.lesson("ভিডিও ২: বাকি শব্দ — routing, assets, live, experimental",
    jargon(("Module-based routing", "ফাইল/module-এর গঠনই URL (<code>src/app/about.rs</code> → <code>/about</code>) — আলাদা route ফাইল নেই"),
           ("Asset bundling", "ছবি, CSS, JS ফাইল জড়ো করে নাম-এ content-hash বসিয়ে (<code>logo-1a2b.png</code>) ছড়ানো — browser cache নিরাপদ হয়"),
           ("Live feature", "server <b>নিজে থেকে</b> UI আপডেট client-এ ঠেলে পাঠায় (push) — chat বা রিপোর্ট-সংখ্যা সরাসরি বদলায়; পেছনে SSE/WebSocket ধরনের সংযোগ"),
           ("Push vs poll", "push: server খবর হলেই জানায়; poll: client বারবার জিজ্ঞেস করে"),
           ("Experimental", "পরীক্ষামূলক — API যেকোনো সময় বদলাতে পারে"),
           ("Breaking change", "নতুন সংস্করণে এমন বদল যাতে পুরনো কোড আর চলে না"),
           ("Production application", "আসল user-দের সামনে চলা app — Topcoat-এ এখনই না, ভিডিওর বক্তাও সতর্ক করেছেন"),
           ("\"degenerate Rust enjoyer\"", "মজা করে বলা: Rust-প্রেমী যিনি নিজের ঝুঁকিতে সবকিছু সারাতে রাজি")),
    tip("ভিডিওর শেষ উপদেশ আমাদের Topcoat course-এও আছে: শেখার জন্য চমৎকার, গুরুত্বপূর্ণ production app-এ এখনই নয়।"))

c.lesson("দুই ভিডিওর শব্দ এক জায়গায়",
    table(["শব্দ", "এক লাইনে", "কোন ভিডিওতে"], [
        ["Rewrite / Port", "নতুন করে লেখা / ভাষা বদলে নেওয়া", "১"],
        ["Systems programming", "OS, database, server-এর নিচের স্তর", "১"],
        ["GC pause / overhead", "GC-র বিরতি / বাড়তি খরচ", "১"],
        ["Borrow checker / lifetime", "ধার-নিয়ম যাচাইকারী / reference-এর আয়ু", "১"],
        ["Cargo / opinionated", "Rust-এর build tool / নিজস্ব পথ-দেওয়া", "১"],
        ["Trade-off / use case", "একটা পেতে আরেকটা ছাড়া / কোন কাজের জন্য", "১, ২"],
        ["SSR / API endpoint", "server-এ HTML / data-র URL", "২"],
        ["WASM / escape hatch", "browser-এ চলা binary / নিয়মের বাইরের দরজা", "২"],
        ["Runtime expression", "server ও browser দুই জায়গায় চলা expression", "২"],
        ["Procedure / Shard", "client থেকে ডাকা server function / server-এ আবার আঁকা অংশ", "২"],
        ["App context / Cx", "সবার ভাগের মান / এক request-এর হাতল", "২"],
        ["Memoization / single-flight", "ফল মনে রাখা / একই কাজ একবারই", "২"],
        ["Branching / PITR", "database-এর কপি / সময়ে ফেরত", "২"]]))


# ================================================================== ৯. Software practice
c.section("Team আর practice-এর জার্গন")
c.lesson("Git আর version control",
    say("Git হলো কোডের \"সময়-যন্ত্র\": প্রতিটা বদলের ছবি তুলে রাখে, যেকোনো পুরনো অবস্থায় ফেরা যায়, আর অনেকে একসাথে কাজ করতে পারে।"),
    jargon(("Repository (repo)", "একটা project-এর সব কোড + পুরো ইতিহাস"),
           ("Commit", "একটা বদলের ছবি + বার্তা (\"invoice VAT ঠিক করা\")"),
           ("Branch", "মূল কোড না ছুঁয়ে আলাদা সমান্তরাল লাইনে কাজ"),
           ("Merge", "দুই branch-এর কাজ এক করা; <b>conflict</b> হয় একই লাইনে দুজন বদলালে"),
           ("Pull request (PR)", "\"আমার branch মূলের সাথে মেলাও\" অনুরোধ — এখানেই <b>code review</b> হয়"),
           ("Clone / Push / Pull", "কপি নামানো / নিজের কাজ পাঠানো / অন্যদেরটা আনা"),
           ("Fork", "অন্যের repo-র নিজস্ব কপি বানানো (open source-এ)"),
           ("GitHub / GitLab", "Git repo রাখার ও সহযোগিতার website; Git নিজে আলাদা tool")),
    shell('''git init                          # নতুন repo
git add . && git commit -m "Add invoice page"   # ছবি তোলা
git switch -c fix-vat             # নতুন branch
git push origin fix-vat           # GitHub-এ পাঠানো → তারপর Pull Request'''))

c.lesson("Frontend, backend, full-stack",
    table(["", "কী", "Laravel জগতে", "ভাষা"], [
        ["<b>Frontend (client)</b>", "user যা দেখে ও ছোঁয়: page, button", "Blade, Vue, Livewire-এর view, CSS", "HTML, CSS, JavaScript (বা WASM)"],
        ["<b>Backend (server)</b>", "পেছনের যুক্তি: database, নিয়ম, নিরাপত্তা", "route, controller, model, queue", "PHP, Rust, Go…"],
        ["<b>Full-stack</b>", "দুটোই সামলানো", "আপনি এখন যা করেন", "—"]]),
    jargon(("Client / Server", "যে অনুরোধ করে (browser) / যে উত্তর দেয় (আপনার app)"),
           ("Static site vs dynamic app", "স্থির HTML ফাইল / প্রতি অনুরোধে বানানো page"),
           ("UI / UX", "User Interface (চেহারা) / User Experience (ব্যবহারের অনুভূতি)")))

c.lesson("API, REST, JSON, webhook",
    code('''<?php
$order = ['invoice' => 'INV-1001', 'total' => 23500, 'paid' => false];
echo json_encode($order, JSON_UNESCAPED_UNICODE), "\\n";
var_dump(json_decode('{"branch":"Mirpur","stock":4}', true));
''', "php"),
    jargon(("API", "একটা software অন্যটাকে কী কী করতে দেয় তার সুনির্দিষ্ট ইন্টারফেস"),
           ("REST", "URL = জিনিস (<code>/orders/5</code>), HTTP method = কাজ (GET, POST, PUT, DELETE) — web API-র সবচেয়ে প্রচলিত ধরন"),
           ("JSON", "data পাঠানোর text ফরম্যাট; উপরের <code>json_encode</code>-এর ফল"),
           ("Webhook", "অন্য service আপনার URL-এ নিজে থেকে POST করে জানায় (bKash পেমেন্ট সফল হলে)"),
           ("Rate limit", "একজন কত দ্রুত API ডাকতে পারে তার সীমা"),
           ("SDK", "কোনো service-এর API সহজে ব্যবহারের তৈরি library")))

c.lesson("Database-এর গভীরের শব্দ",
    jargon(("Relational database", "table আর table-এর সম্পর্ক (MySQL, PostgreSQL) — Laravel যা ব্যবহার করে"),
           ("NoSQL", "table ছাড়া অন্য ধাঁচ (document: MongoDB, key-value: Redis)"),
           ("Index", "বইয়ের সূচিপত্র: খোঁজা দ্রুত, কিন্তু লিখতে একটু বেশি সময় আর জায়গা"),
           ("Transaction / ACID", "কয়েকটা কাজ হয় সবই নয়তো কিছুই না; ACID = Atomic, Consistent, Isolated, Durable (ব্যাংকের টাকা-সরানোর নিরাপত্তা)"),
           ("Normalization", "একই তথ্য বহু জায়গায় না রেখে ভেঙে সাজানো"),
           ("Foreign key", "অন্য table-এর সারির দিকে নির্দেশ (<code>orders.customer_id</code>)"),
           ("Cache (Redis)", "ঘন ঘন দরকারি ফল দ্রুত মেমরিতে রাখা — database বারবার না ডেকে"),
           ("Replica", "আসল database-এর পড়ার-কপি — চাপ ভাগ করতে")),
    tip("MySQL আর PostgreSQL কোর্স এই সাইটেই আছে — প্রতিটা query আসল database-এ চালানো।"))

c.lesson("Architecture-এর জার্গন",
    table(["শব্দ", "মানে", "উপমা"], [
        ["<b>Monolith</b>", "পুরো app একটাই project/deploy — Laravel app সাধারণত এটাই", "একটাই বড় দোকান"],
        ["<b>Microservice</b>", "ছোট ছোট আলাদা service, API-তে কথা বলে", "আলাদা আলাদা কাউন্টার-দোকান"],
        ["<b>Queue / worker</b>", "ভারী কাজ লাইনে রেখে পেছনে করা (<code>dispatch(new SendInvoice)</code>)", "অর্ডার-স্লিপের লাইন"],
        ["<b>Load balancer</b>", "একাধিক server-এ অনুরোধ ভাগ করা", "প্রবেশদ্বারে লাইন-ম্যানেজার"],
        ["<b>CDN</b>", "ছবি/CSS পৃথিবীর নানা জায়গার server থেকে, user-এর কাছেরটা থেকে", "প্রতি এলাকায় গুদাম"],
        ["<b>Horizontal / vertical scaling</b>", "আরও server যোগ / একটা server বড় করা", "আরও দোকান / দোকান বড় করা"]]),
    jargon(("Scalability", "ব্যবহারকারী বাড়লে সিস্টেম সামাল দিতে পারা"),
           ("Single point of failure", "যেটা ভাঙলে সব বন্ধ"),
           ("Event-driven", "ঘটনা ঘটলে (order এলো) প্রতিক্রিয়া চলে")))

c.lesson("Testing আর quality-র শব্দ",
    say("Test কীভাবে লেখে তার একটা সত্যিকারের চালানো উদাহরণ (<code>#[test]</code> attribute, <code>assert_eq!</code> macro):"),
    code(r'''
fn with_vat(price: u32) -> u32 {
    price * 115 / 100
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn vat_is_fifteen_percent() {
        assert_eq!(with_vat(18500), 21275);
    }

    #[test]
    fn zero_stays_zero() {
        assert_eq!(with_vat(0), 0);
    }
}
''', test=True),
    jargon(("Unit / Integration / E2E test", "একটা function / কয়েক অংশ একসাথে / user-এর মতো পুরো app browser-এ"),
           ("CI (Continuous Integration)", "প্রতি commit-এ স্বয়ংক্রিয়ভাবে build + test চালানো (GitHub Actions)"),
           ("CD (Continuous Delivery/Deployment)", "test পাস করলে স্বয়ংক্রিয়ভাবে deploy"),
           ("Code review", "সহকর্মী PR পড়ে মন্তব্য/অনুমোদন করা"),
           ("Refactoring", "আচরণ না বদলে কোডের গঠন পরিষ্কার করা"),
           ("Technical debt", "তাড়াহুড়োয় রাখা নোংরা কোড — পরে সুদসহ শোধ করতে হয়"),
           ("Bug / Debugging", "ভুল / ভুল খুঁজে সারানো")))

c.lesson("Performance-এর জার্গন",
    jargon(("Latency / Throughput", "এক কাজের সময় / সময়ে কত কাজ"),
           ("p50 / p95 / p99", "১০০টা অনুরোধ সাজালে মাঝেরটা / ৯৫তম / ৯৯তমের সময় — p99 ধীরতম ১%-এর কষ্ট দেখায়; গড়ের চেয়ে বেশি সত্য বলে"),
           ("Bottleneck", "পুরো system-এর ধীরতম অংশ — এটা না সারালে বাকি সব সারানো বৃথা"),
           ("Profiling", "program-এর কোন অংশ কত সময়/memory খাচ্ছে মেপে দেখা"),
           ("Caching", "ঘন ঘন লাগে এমন ফল কাছে রাখা"),
           ("Premature optimization", "মাপার আগেই কোড জটিল করে \"দ্রুত\" বানানো — \"মাপো, তারপর বদলাও\""),
           ("CPU-bound / I/O-bound", "হিসাবে আটকা / অপেক্ষায় আটকা")),
    warn("বেশিরভাগ Laravel app-এর bottleneck: database query (N+1, index নেই) আর network। আগে profile করুন — ভাষা বদলানোর আগে।"))

c.lesson("Security-র জার্গন",
    say("নিচে hash-এর আসল আচরণ। একই ইনপুটে সবসময় একই ফল; এক অক্ষর বদলালেই পুরো আলাদা; আর ফল থেকে মূল পাসওয়ার্ডে ফেরা যায় না:"),
    code('''<?php
echo hash('sha256', 'rahim123'), "\\n";
echo hash('sha256', 'rahim124'), "\\n";   // এক অক্ষর আলাদা
''', "php"),
    jargon(("Authentication / Authorization", "কে তুমি / তুমি কী পারো"),
           ("Hashing", "একমুখী গোলানো — পাসওয়ার্ড রাখার সঠিক উপায়, তবে সরাসরি SHA-256 না, <code>password_hash</code> (salt সহ, ধীর) ব্যবহার করুন"),
           ("Encryption", "<b>দ্বিমুখী</b> — চাবি দিয়ে তালা, চাবি দিয়ে খোলা; hash নয়!"),
           ("Salt", "hash-এর আগে মেশানো এলোমেলো লেখা — একই পাসওয়ার্ডের ফল আলাদা করে"),
           ("SQL injection / XSS / CSRF", "SQL-এ অনুপ্রবেশ / page-এ script ঢোকানো / অন্য site থেকে জাল POST"),
           ("OWASP Top 10", "web-এর সবচেয়ে সাধারণ ১০টা নিরাপত্তা-ভুলের তালিকা"),
           ("Least privilege", "যার যতটুকু দরকার ততটুকুই অনুমতি"),
           ("Secret", "পাসওয়ার্ড/API key — কখনো Git-এ নয়, <code>.env</code> বা secret manager-এ"),
           ("Dependency vulnerability", "ব্যবহৃত package-এর নিজের ফাঁক — তাই update জরুরি (<code>cargo audit</code>, <code>composer audit</code>)")))

c.lesson("DevOps আর deploy-এর জার্গন",
    jargon(("Linux / shell / SSH", "server-এর OS / terminal ভাষা / দূরের server-এ নিরাপদ প্রবেশ"),
           ("Container / Docker", "app + তার সব দরকারি জিনিস একটা প্যাকেটে — \"আমার machine-এ চলে\" সমস্যা শেষ"),
           ("Kubernetes (K8s)", "অনেক container চালানো ও দেখাশোনার ব্যবস্থা"),
           ("IaC (Infrastructure as Code)", "server/নেটওয়ার্ক কোডে লিখে বানানো (Terraform, OpenTofu)"),
           ("Cloud: IaaS / PaaS / Serverless", "ভাড়া-machine (EC2) / app তুলে দিলেই চলে (Heroku, Forge) / কোড-টুকরো ফাংশন (Lambda)"),
           ("Observability: logs, metrics, traces", "কী ঘটল লেখা / সংখ্যায় স্বাস্থ্য (Prometheus) / এক অনুরোধের সম্পূর্ণ পথ"),
           ("Uptime / SLA", "কতক্ষণ চালু (৯৯.৯%) / চালু রাখার চুক্তি"),
           ("Staging", "production-এর হুবহু মহড়া পরিবেশ")),
    tip("DevOps সিরিজ এই সাইটেই: Linux, Docker, Kubernetes, CI/CD, Monitoring, IaC — সব আসল tool-এ চালানো।"))

c.lesson("Open source আর license",
    jargon(("Open source", "কোড সবার দেখার ও (শর্তে) ব্যবহারের জন্য খোলা — Rust, Laravel, Linux সবই"),
           ("License", "ব্যবহারের শর্ত: <b>MIT</b>/<b>Apache-2.0</b> (প্রায় মুক্ত), <b>GPL</b> (আপনার কোডও খুলতে হতে পারে) — Rust ও Topcoat MIT/Apache"),
           ("Maintainer", "প্রকল্পটা যিনি দেখাশোনা করেন"),
           ("Issue / PR", "সমস্যার রিপোর্ট / সংশোধনের প্রস্তাব"),
           ("Changelog", "প্রতি সংস্করণে কী বদলাল তার তালিকা — upgrade-এর আগে পড়ুন"),
           ("Semantic versioning", "<code>MAJOR.MINOR.PATCH</code>: major বদলালে breaking change"),
           ("Fork", "নিজের স্বাধীন কপি")),
    php_note("Packagist-এ package নেওয়ার সময় আপনি license মেনে চলার চুক্তিতে সই করছেন — বাণিজ্যিক project-এ license দেখে নিন।"))

c.lesson("Software-এর জীবনচক্র আর team-এর শব্দ",
    steps("<b>Requirement</b> — কী বানাতে হবে (stakeholder-দের চাহিদা)",
          "<b>Design</b> — কীভাবে বানাব (architecture, database নকশা)",
          "<b>Build</b> — কোড লেখা",
          "<b>Test</b> — ঠিকঠাক চলে কিনা",
          "<b>Deploy</b> — user-দের হাতে",
          "<b>Maintain</b> — bug সারানো, নতুন ফিচার (সবচেয়ে দীর্ঘ ধাপ!)"),
    jargon(("Agile / Scrum / Sprint", "ছোট ছোট ধাপে (১–২ সপ্তাহের sprint) কাজ করে বারবার ফিডব্যাক নেওয়ার পদ্ধতি"),
           ("MVP (Minimum Viable Product)", "সবচেয়ে ছোট সংস্করণ যা দিয়ে ধারণা যাচাই করা যায়"),
           ("Backlog", "করার কাজের অগ্রাধিকার-সাজানো তালিকা"),
           ("Stakeholder", "প্রকল্পে যার স্বার্থ আছে (মালিক, গ্রাহক, marketing)"),
           ("Scope creep", "কাজের পরিধি চুপিসারে বাড়তে থাকা")),
    tip("আপনি marketing background থেকে এসেছেন — stakeholder, MVP, backlog শব্দগুলো আপনার সুবিধা: developer ও ব্যবসার মাঝে আপনি সেতু হতে পারেন।"))


# ================================================================== ১০. Laravel → Rust
c.section("Laravel থেকে Rust-এ")
c.lesson("Laravel-এর প্রতিটা জিনিস Rust-এ কী?",
    say("আপনার app-এ যা যা আছে, Rust-এর দুনিয়ায় তার জন্য আলাদা crate। একটাই framework সব দেয় না — ছোট ছোট crate জুড়ে বানাতে হয় (এটা Rust-এর সংস্কৃতি)। নিচে সুপরিচিত বিকল্প, আরও আছে:"),
    table(["Laravel", "Rust-এ কাছাকাছি", "মন্তব্য"], [
        ["Routing, controller, middleware", "<b>axum</b> (বা Topcoat)", "Rust Web Development কোর্স"],
        ["Blade", "<b>Askama</b>, <b>Maud</b>, <b>Leptos</b>, <b>Topcoat</b>", "compile-time-checked template"],
        ["Livewire / Alpine", "<b>Leptos</b>, <b>Topcoat</b>, HTMX", "আমাদের Leptos ও Topcoat কোর্স"],
        ["Eloquent / Query Builder", "<b>sqlx</b>, <b>SeaORM</b>, <b>Diesel</b>", "sqlx = সরাসরি SQL, compile-এ যাচাই"],
        ["Migration", "<code>sqlx migrate</code>, SeaORM migration", ""],
        ["Validation (<code>$request-&gt;validate</code>)", "<b>validator</b> crate + serde struct", ""],
        ["Auth, session", "<b>tower-sessions</b>, <b>axum-login</b>; পাসওয়ার্ডে <b>argon2</b>", "Fortify/Breeze-এর মতো তৈরি kit কম"],
        ["Queue / Job", "<b>apalis</b>, বা <code>tokio</code> task + Redis", ""],
        ["Mail", "<b>lettre</b>", ""],
        ["Scheduler (<code>schedule:run</code>)", "<b>tokio-cron-scheduler</b>", ""],
        ["Cache", "<b>moka</b> (memory), <b>redis</b> crate", ""],
        ["HTTP client (<code>Http::get</code>)", "<b>reqwest</b>", ""],
        ["<code>.env</code>, config", "<b>dotenvy</b>, <b>config</b> crate", ""],
        ["Artisan command", "<b>clap</b>", "CLI argument parsing"],
        ["Log", "<b>tracing</b>", ""],
        ["PHPUnit / Pest", "<code>cargo test</code>", "ভিতরে বানানো"]]),
    warn("এই তালিকার প্রতিটা crate-এর version, API আর রক্ষণাবেক্ষণের অবস্থা আলাদা করে যাচাই করে নিন (docs.rs, GitHub) — আমি এই কোর্সে এদের কোড চালাইনি, শুধু পরিচিত নাম দিয়েছি।"))

c.lesson("শেখার ক্রম: এই সাইটে",
    steps("<b>Software Development 101</b> — এই কোর্স: ভিত ও জার্গন",
          "<b>Rust 101</b> — ভাষার মূল: variable, type, function, loop, match",
          "<b>Rust 102</b> — ownership, borrow, struct, enum, Option, Result",
          "<b>Rust 103</b> — trait, generic, closure, iterator, test, thread, async",
          "<b>Rust Web Development</b> — axum + SQLite: আপনার Laravel API-র Rust রূপ",
          "<b>Rust Leptos</b> অথবা <b>Rust Topcoat</b> — page ও interactivity (দুটোই দেখে পছন্দ করুন)",
          "<b>MySQL / PostgreSQL</b> আর <b>DevOps</b> — database ও deploy, যেকোনো ভাষায় লাগে"),
    tip("Rust 102-এর ownership অংশে আটকে গেলে হতাশ হবেন না — প্রায় সবাই ওখানেই আটকায়। এই কোর্সের Memory আর Borrow checker lesson-গুলো আবার দেখুন।"))

c.lesson("পুরো app এক ধাক্কায় rewrite — কেন বিপজ্জনক",
    say("\"সব Rust-এ বানাব\" ইচ্ছাটা বুঝি, কিন্তু চালু business-এর app একবারে নতুন করে লেখা সফটওয়্যার-দুনিয়ার সবচেয়ে ব্যয়বহুল ভুলগুলোর একটা। কারণ:"),
    points("পুরনো app-এর শত শত ছোট নিয়ম (কোড-এ লুকানো) আপনি ভুলে যাবেন",
           "নতুন ও পুরনো একসাথে চালাতে হয় — নতুনটা তৈরি হতে হতে ব্যবসা থেমে থাকে না",
           "ভিডিওর Dropbox-এর সাড়ে ৪ বছর, TypeScript-এর \"অনেক বছর\" — আপনার ছোট দলের জন্য আরও কঠিন",
           "ভুল হলে ফিরে যাওয়ার পথ থাকে না"),
    jargon(("Feature parity", "নতুন system-এ পুরনোর সব ফিচার থাকা — \"parity\" পৌঁছানোই সবচেয়ে কঠিন"),
           ("Rollback", "নতুন সংস্করণ সমস্যা করলে পুরনোতে ফিরে যাওয়া"),
           ("Big-bang rewrite", "একদিনে পুরোটা বদলে ফেলা — ঝুঁকি সবচেয়ে বেশি"),
           ("Strangler fig pattern", "বটগাছ যেভাবে পুরনো গাছকে ধীরে ধীরে ঘিরে ফেলে: <b>একটা একটা অংশ</b> নতুনে নিয়ে যাওয়া, বাকিটা পুরনোই চলে — শেষে পুরনো আপনা-আপনি অপ্রয়োজনীয়")))

c.lesson("হাইব্রিড: Laravel আর Rust পাশাপাশি",
    say("বাস্তব পথ: Nginx-এর সামনের দরজা একটাই, কিন্তু কিছু URL যায় Rust service-এ, বাকি সব আগের মতো Laravel-এ। একই database, বা Rust service API দিয়ে কথা বলে।"),
    code('''server {
    listen 80;
    server_name shop.example.com;

    # ভারী রিপোর্ট এখন Rust service-এ
    location /api/reports {
        proxy_pass http://127.0.0.1:8080;      # Rust (axum)
    }

    # বাকি সব আগের মতো Laravel (PHP-FPM)-এ
    location / {
        try_files $uri /index.php?$query_string;
    }
}
''', "nginx", run=False, file="nginx.conf"),
    jargon(("Reverse proxy", "সামনে বসে অনুরোধ ঠিক পেছনের app-কে পাঠায়"),
           ("Contract (API contract)", "দুই system-এর মধ্যে কী পাঠানো-নেওয়া হবে তার সুনির্দিষ্ট চুক্তি — এটা ঠিক থাকলে ভিতরে যা-ই লেখা হোক"),
           ("Shared database", "দুই system একই database ব্যবহার করে — সহজ কিন্তু পরস্পর-নির্ভরতা তৈরি করে")))

c.lesson("প্রথম Rust প্রজেক্ট: কম ঝুঁকি থেকে বেশি",
    table(["ধাপ", "কী বানাবেন", "কেন ভালো শুরু"], [
        ["১", "<b>CLI tool</b>: CSV থেকে invoice import, বা stock রিপোর্ট", "web/database লাগে না; ownership শেখার সেরা মাঠ"],
        ["২", "<b>ছোট read-only API</b> (axum): product list, search", "ভুল হলেও কিছু নষ্ট হয় না"],
        ["৩", "<b>ভারী কাজের service</b>: রিপোর্ট, CSV/PDF বানানো, ছবি ছোট করা", "Rust-এর গতির আসল লাভ এখানে; Laravel থেকে HTTP/queue দিয়ে ডাকা"],
        ["৪", "<b>Background worker</b>: queue-র ভারী job", "Laravel queue থেকে আলাদা করা সহজ"],
        ["৫", "<b>একটা পুরো module</b> (যেমন inventory) নিজস্ব database সহ", "strangler পদ্ধতির প্রথম বড় ধাপ"],
        ["৬", "<b>পুরো page ও interactivity</b> (Leptos/Topcoat)", "সবশেষে — সবচেয়ে বেশি নতুন ধারণা"]]),
    tip("প্রথম ৩ ধাপেই আপনি Rust-এর বেশিরভাগ লাভ পাবেন, ঝুঁকি কম রেখে।"))

c.lesson("Rust-এ নেওয়ার আগে ৬ প্রশ্ন",
    steps("<b>ধীরতার আসল কারণ কী?</b> মেপেছেন? (query, network, নাকি PHP?)",
          "<b>বিকল্প সস্তা সমাধান আছে?</b> index, cache, queue, Octane দিয়ে হয়ে যায় কি?",
          "<b>দলে সময় আছে?</b> ৩–৬ মাস শেখার ধাক্কা ধরে নিয়েছেন?",
          "<b>দরকারি package আছে?</b> payment gateway, SMS, auth-এর Rust crate যাচাই করেছেন?",
          "<b>test আছে?</b> পুরনো app-এর আচরণ ধরে রাখার automated test না থাকলে ভাঙা ধরা পড়বে না",
          "<b>ফিরে আসার পথ?</b> rollback আর পাশাপাশি চালানোর পরিকল্পনা"),
    warn("ছয়টার বেশিরভাগ উত্তর \"না/জানি না\" হলে আগে সেগুলো ঠিক করুন — Rust-এ লিখলেও সমস্যা থেকেই যাবে।"))

c.section("সারাংশ")
c.lesson("Quiz",
    quiz("Stack আর heap-এর পার্থক্য কী? (Memory অর্থে)",
         "Stack ছোট, নির্দিষ্ট-আকারের মানের জন্য দ্রুত জায়গা; function শেষে নিজে নিজে সাফ। Heap বড়, বাড়তে-পারা মানের জন্য (লেখা, vector), ধীর, আর কাউকে পরিষ্কার করতে হয় (C: আপনি, PHP: GC, Rust: ownership)।"),
    quiz("Garbage collector ছাড়া Rust memory কীভাবে সাফ করে?",
         "Ownership: প্রতিটা মানের একজন মালিক; মালিকের scope শেষ হলে compiler ঠিক সেখানেই সাফ করার কোড বসায়। কখন সাফ হবে তা আগে থেকেই নির্দিষ্ট — কোনো পেছনের প্রক্রিয়া বা বিরতি নেই।"),
    quiz("Borrow checker কী আটকায়?",
         "যে reference ঝুলে থাকতে পারে, বা একসাথে কেউ বদলাচ্ছে আর কেউ পড়ছে এমন পরিস্থিতি। নিয়ম: একসাথে একজন লেখক (<code>&amp;mut</code>) অথবা অনেক পাঠক (<code>&amp;</code>)। এতে use-after-free, data race compile-এই বন্ধ।"),
    quiz("Memory safe মানে কি bug-মুক্ত?",
         "না। শুধু memory-র নির্দিষ্ট ধরনের ভুল (overflow, use-after-free ইত্যাদি) হয় না। Logic-এর ভুল, SQL injection, দুর্বল পাসওয়ার্ড — যেকোনো ভাষায় সম্ভব।"),
    quiz("Compiler আর interpreter-এর মূল পার্থক্য?",
         "Compiler চালানোর আগে পুরো কোড machine code-এ বদলে (ভুল compile-এই ধরা পড়ে, program দ্রুত); interpreter চলার সময় পড়ে চালায় (নমনীয়, কিন্তু ধীর এবং ভুল runtime-এ)।"),
    quiz("Vector আর array-র পার্থক্য?",
         "Array-র সংখ্যা নির্দিষ্ট; vector বাড়তে-কমতে পারে (ভিতরে array, ভরে গেলে বড় জায়গায় সরে — length আর capacity আলাদা)। PHP-র array দুটোই (এবং hash map)।"),
    quiz("Rewrite-এর বদলে strangler পদ্ধতি কেন ভালো?",
         "এক সাথে একটা অংশ নতুনে নিয়ে বাকিটা পুরনোতে রেখে চলা যায়, ভুল হলে শুধু সেই অংশ rollback হয়, ব্যবসা থামে না।"))

c.lesson("সব এক স্লাইডে: Software Development 101",
    say("এই কোর্সের সবকিছুর এক পাতার সারাংশ। যে শব্দে আটকাবেন, সেই সারির বিষয়ের lesson-এ ফিরুন।"),
    table(["বিষয়", "মূল শব্দ ও এক লাইনে মানে"], [
        ["<b>Computer</b>", "<b>bit/byte</b> 0-1 তথ্য · <b>CPU</b> হিসাব · <b>RAM</b> চলমান memory · <b>OS</b> ব্যবস্থাপক · <b>machine code</b> CPU-র ভাষা"],
        ["<b>কোড চলা</b>", "<b>compile</b> আগে অনুবাদ (Rust, C) · <b>interpret</b> চলার সময় (PHP) · <b>binary</b> ফল · <b>runtime/VM/JIT</b> চলার ব্যবস্থা"],
        ["<b>ভাষা</b>", "<b>C</b> ১৯৭০, manual memory · <b>C++</b> C+object · <b>Rust</b> ২০১৫, গতি+নিরাপত্তা · <b>PHP/Go</b> GC · <b>paradigm</b> OOP/functional/procedural"],
        ["<b>Memory</b>", "<b>stack</b> ছোট দ্রুত · <b>heap</b> বড় ধীর · <b>manual</b> / <b>GC</b> / <b>ownership</b> · <b>leak, dangling, overflow, use-after-free</b> বিপদ · <b>memory safe</b>"],
        ["<b>Rust-এর নিয়ম</b>", "<b>ownership</b> একজন মালিক · <b>borrow</b> ধার · <b>borrow checker</b> পাহারা · <b>lifetime</b> reference-এর আয়ু · <b>unsafe</b> শেষ উপায়"],
        ["<b>Data</b>", "<b>array/vector</b> list · <b>HashMap</b> key→value · <b>struct/enum/tuple</b> · <b>stack/queue</b> LIFO/FIFO · <b>pointer/reference</b> ঠিকানা"],
        ["<b>Algorithm</b>", "<b>Big-O</b> ধাপ কত বাড়ে (O(1), O(n), O(log n), O(n²)) · <b>recursion</b> নিজেকে ডাকা · <b>N+1</b> ধীর query"],
        ["<b>ভাষার গঠন</b>", "<b>type</b> static/dynamic, strong/weak · <b>macro</b> code-বানানো code · <b>attribute</b> <code>#[..]</code> · <b>generic/trait</b> · <b>Result</b> ভুল মান হিসেবে"],
        ["<b>Concurrency</b>", "<b>thread</b> · <b>data race</b> · <b>mutex/Arc</b> · <b>async/await</b> অপেক্ষায় অন্য কাজ · <b>blocking vs non-blocking</b> · <b>I/O vs CPU-bound</b>"],
        ["<b>Web</b>", "<b>HTTP request/response</b> · <b>endpoint</b> · <b>REST/JSON</b> · <b>SSR/CSR/hydration</b> · <b>WASM</b> · <b>signal/reactivity</b> · <b>middleware</b> · <b>CSRF/XSS</b>"],
        ["<b>Framework</b>", "<b>Laravel</b> PHP · <b>axum</b> HTTP · <b>Leptos</b> WASM · <b>Topcoat</b> server-first, Rust→JS · <b>procedure/shard/memoize</b>"],
        ["<b>Database</b>", "<b>SQL</b> · <b>index</b> · <b>transaction/ACID</b> · <b>migration</b> · <b>ORM</b> · <b>pool</b> · <b>branching/PITR/backup</b>"],
        ["<b>Team</b>", "<b>Git</b> repo/commit/branch/PR · <b>CI/CD</b> · <b>test</b> unit/integration/E2E · <b>code review</b> · <b>tech debt</b> · <b>Agile/MVP</b>"],
        ["<b>Deploy</b>", "<b>Linux</b> · <b>Docker/Kubernetes</b> · <b>reverse proxy/HTTPS</b> · <b>cloud</b> IaaS/PaaS/serverless · <b>logs/metrics/traces</b> · <b>staging/prod</b>"],
        ["<b>Rust কেন</b>", "গতি + memory safety + নিরাপদ concurrency + tooling · দাম: শেখার ঢাল, ধীর compile, ছোট ecosystem (GUI/ML) · <b>use case</b> দেখে বাছুন"],
        ["<b>Laravel → Rust</b>", "<b>strangler</b> পদ্ধতি, <b>big-bang rewrite</b> নয় · CLI → API → ভারী service → module · আগে <b>মাপুন</b>"]]),
    tip("পরের ধাপ: <b>Rust 101</b>-এ গিয়ে প্রথম <code>Hello, World!</code> — এখন ভিতরের প্রতিটা শব্দের মানে আপনার জানা।"))

# @@END
c.finish("Software Development 101 শেষ", "এখন \"vector\", \"heap\", \"macro\", \"CI/CD\" শুনলে ঘাবড়াবেন না — প্রতিটার জায়গা আপনি জানেন। এবার Rust 101।",
         recap=["Computer machine code বোঝে; compiler/interpreter অনুবাদক", "C → C++ → Rust: গতি + নিরাপত্তার ইতিহাস",
                "Memory: stack, heap; manual vs GC vs ownership", "Vector, hash map, Big-O, recursion", "Type, macro, runtime, concurrency",
                "Git, API, database, test, CI/CD, security, DevOps", "Laravel → Rust: ধাপে ধাপে, একসাথে সব নয়"])
c.build()
