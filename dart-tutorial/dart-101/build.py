"""Dart 101 — variables, types, null safety, strings, control flow, functions, collections.
Every Dart block is run with `dart run`; PHP comparisons are run with php. Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402


def dart(src, **kw):
    return code(src, "dart", **kw)


def php(src, label="PHP-তে তুলনা"):
    return code(src, "php", label=label)


c = Course(slug="dart-101", title="Dart 101 — শূন্য থেকে শুরু", folder=Path(__file__).parent,
           subtitle="Flutter-এর ভাষা Dart: variable, type, null safety, string, if/switch/loop, function আর List/Map — PHP-র পাশাপাশি",
           series="Dart 101", next_course=("../dart-102/index.html", "Dart 102 — Class, Mixin ও Pattern"))

c.cover("Dart 101<br>শূন্য থেকে শুরু",
        "Dart হলো Flutter-এর ভাষা — একই কোডে Android, iPhone, web আর desktop app। PHP জানলে Dart-এর অনেক কিছুই চেনা লাগবে: <code>$name</code> দিয়ে string, <code>??</code>, named argument।",
        learn=["Dart কেন, কোথায় চলে", "var, final, const", "int, double, String, bool", "Null safety: String? আর ??",
               "String interpolation আর multiline", "if, switch expression, loop", "Function: named আর optional parameter",
               "List, Map, Set আর keyboard input"],
        need="সাধারণ programming (PHP যথেষ্ট)।")

c.section("শুরু")
c.lesson("Dart কেন?",
    table(["", "PHP", "Dart"], [
        ["Type", "Dynamic (ঐচ্ছিক type)", "Static, কিন্তু অনুমান করে নেয় (<code>var</code>)"],
        ["null", "যেকোনো variable null হতে পারে", "<b>Null safety</b>: <code>String?</code> লিখলেই শুধু null চলে"],
        ["চলে কোথায়", "Server", "Mobile (Flutter), web, desktop, server, CLI"],
        ["Package", "Composer, Packagist", "<code>dart pub</code>, pub.dev"],
        ["String-এ মান", "<code>\"Hi $name\"</code>", "<code>'Hi $name'</code> — প্রায় একই!"]]),
    tip("Dart শেখার মূল কারণ সাধারণত Flutter। এই তিনটা Dart কোর্স শেষে Flutter কোর্স সহজ লাগবে।"))

c.lesson("Install আর প্রথম program",
    say("Flutter install করলে Dart সাথেই আসে। শুধু Dart চাইলে dart.dev থেকে। <code>main()</code> থেকে program শুরু, <code>print()</code> দিয়ে লেখা।"),
    shell("$ dart --version\n$ dart create hello\n$ cd hello && dart run", out="Dart SDK version: 3.13.4 (stable)\nHello world: 42!"),
    dart('''
void main() {
  print('Hello, World!');
  print('Dart শেখা শুরু হলো 🎯');
}
'''),
    php_note("PHP-তে <code>&lt;?php</code> ছাড়াই চলে না, Dart-এ <code>main()</code> ছাড়া চলে না। প্রতিটি statement-এর শেষে <code>;</code> দুটোতেই।"))

c.section("Variable ও Type")
c.lesson("var, final, const",
    say("<code>var</code> — বদলানো যায়। <code>final</code> — একবারই মান দেওয়া যায়। <code>const</code> — compile-এর সময়েই জানা স্থির মান।"),
    dart('''
void main() {
  var balance = 500;        // type অনুমান: int
  balance = balance + 200;

  final shop = 'Rahim Mobile';      // একবারই
  const vatPercent = 15;           // compile-time স্থির

  print('$shop: balance $balance, VAT $vatPercent%');
}
'''),
    dart('''
void main() {
  final shop = 'Rahim Mobile';
  shop = 'Karim Mobile';
}
''', err="final variable"),
    php_note("PHP-র <code>const VAT = 15;</code> ≈ Dart <code>const</code>। <code>final</code>-এর মতো কিছু PHP-তে variable-এ নেই (PHP 8.1-এর <code>readonly</code> property কাছাকাছি)।"))

c.lesson("Type: int, double, String, bool",
    say("Type লেখা ঐচ্ছিক, কিন্তু দিলে Dart মেনে চলে। ভুল type দিলে program চলার আগেই error।"),
    dart('''
void main() {
  int stock = 5;
  double price = 17500.50;
  String model = 'Redmi 13';
  bool inStock = stock > 0;

  print('$model — $price টাকা — স্টক $stock — আছে? $inStock');
  print(price.runtimeType);
}
'''),
    dart('''
void main() {
  int stock = '5';
}
''', err="can't be assigned"))

c.lesson("ভাগ: / আর ~/",
    say("Dart-এ <code>/</code> সবসময় <code>double</code> দেয় (PHP-র মতো)। পূর্ণসংখ্যার ভাগ চাইলে <code>~/</code>।"),
    dart('''
void main() {
  print(7 / 2);      // 3.5
  print(7 ~/ 2);     // 3
  print(7 % 2);      // 1
  print(17499.567.toStringAsFixed(2));
  print(int.parse('250') + 1);
  print(double.parse('99.5') * 2);
}
'''),
    php('''
<?php
echo 7 / 2, "\\n", intdiv(7, 2), "\\n", 7 % 2, "\\n";
''', "PHP-তে তুলনা"))

c.lesson("Null safety: ? আর ??",
    say("সাধারণ variable কখনো null হতে পারে না। null রাখতে চাইলে type-এর পরে <code>?</code>। ব্যবহারের আগে Dart বাধ্য করে null সামলাতে।"),
    dart('''
void main() {
  String? district;                 // null হতে পারে
  print(district ?? 'জানা নেই');     // PHP-র ?? একদম একই

  district = 'Sylhet';
  print(district.length);           // এখন নিশ্চিত, তাই চলে

  String? phone;
  print(phone?.length);             // null হলে null, error না
}
'''),
    dart('''
void main() {
  String? phone;
  print(phone.length);
}
''', err="potentially null"),
    php_note("PHP-তে <code>$phone-&gt;length</code> null হলে চলার সময় error। Dart compile-এর সময়েই আটকায়। <code>?.</code> হলো PHP 8-এর nullsafe <code>?-&gt;</code>।"))

c.lesson("String: $ আর ${}",
    say("<code>$name</code> দিয়ে variable বসে, হিসাবের জন্য <code>${...}</code>। তিনটা quote দিয়ে কয়েক লাইনের লেখা।"),
    dart('''
void main() {
  final name = 'Nusrat';
  final price = 650;
  final qty = 3;

  print('Customer: $name');
  print('মোট: ${price * qty} টাকা');
  print('নামের দৈর্ঘ্য: ${name.length}');

  final receipt = """
Rahim Mobile
------------
$name × $qty
""";
  print(receipt.trim());
  print('Redmi 13'.toUpperCase().contains('REDMI'));
}
'''),
    php_note("PHP-র <code>\"Hi {$name}\"</code> ≈ Dart <code>'Hi ${name}'</code>। পার্থক্য: Dart-এ single quote-এও interpolation চলে, আর জোড়া দিতে <code>.</code> না, <code>+</code> (বা interpolation)।"))

c.section("Control flow")
c.lesson("if/else",
    dart('''
void main() {
  final amount = 1800;
  if (amount >= 1500) {
    print('ফ্রি ডেলিভারি');
  } else if (amount >= 1000) {
    print('ডেলিভারি ৩০ টাকা');
  } else {
    print('ডেলিভারি ৬০ টাকা');
  }

  final label = amount > 1000 ? 'বড় অর্ডার' : 'ছোট অর্ডার';   // ternary আছে
  print(label);
}
'''),
    warn("শর্ত অবশ্যই <code>bool</code>: <code>if (count)</code> লিখলে error — PHP-র মতো 0 বা '' দিয়ে false চলে না।"))

c.lesson("switch expression (Dart 3)",
    say("নতুন <code>switch</code> একটা মান ফেরত দেয়, <code>=&gt;</code> দিয়ে লেখা, <code>_</code> মানে বাকি সব। PHP 8-এর <code>match</code>-এর মতোই।"),
    dart('''
String grade(int marks) => switch (marks) {
  >= 80 => 'A+',
  >= 70 => 'A',
  >= 60 => 'A-',
  >= 33 => 'পাস',
  _ => 'F',
};

void main() {
  for (final m in [95, 72, 48, 20]) {
    print('$m → ${grade(m)}');
  }
}
'''),
    php('''
<?php
$m = 72;
echo match (true) { $m >= 80 => 'A+', $m >= 70 => 'A', default => 'F' }, "\\n";
'''))

c.lesson("Loop: for, for-in, while",
    dart('''
void main() {
  for (var i = 1; i <= 5; i++) {
    print('7 × $i = ${7 * i}');
  }

  for (final city in ['Dhaka', 'Khulna', 'Barishal']) {
    print(city);
  }

  var seconds = 3;
  while (seconds > 0) {
    print('$seconds...');
    seconds--;
  }
}
'''),
    php_note("<code>foreach ($cities as $city)</code> → <code>for (final city in cities)</code>।"))

c.section("Function")
c.lesson("Function আর arrow",
    say("Return type নামের আগে। এক লাইনের function <code>=&gt;</code> দিয়ে।"),
    dart('''
int totalPrice(int price, int qty) {
  return price * qty;
}

int withVat(int amount) => amount + amount * 15 ~/ 100;

void main() {
  final t = totalPrice(450, 4);
  print('মোট $t, VAT সহ ${withVat(t)}');
}
'''),
    php_note("<code>fn($a) =&gt; $a * 2</code> (PHP arrow function) ≈ Dart <code>(a) =&gt; a * 2</code>।"))

c.lesson("Named আর optional parameter",
    say("<code>{}</code> দিয়ে named parameter — ডাকার সময় নাম লিখতে হয়, ক্রম লাগে না। <code>required</code> না দিলে ডিফল্ট মান বা <code>?</code> লাগে। Flutter-এ সব জায়গায় এটা।"),
    dart('''
String invoiceLine(String item, {required int price, int qty = 1, String? note}) {
  final line = '$item × $qty = ${price * qty}';
  return note == null ? line : '$line ($note)';
}

void main() {
  print(invoiceLine('Charger', price: 650));
  print(invoiceLine('Cover', qty: 2, price: 250, note: 'ছাড় ১০%'));
}
'''),
    php_note("PHP 8-এর named argument <code>invoiceLine('Cover', qty: 2, price: 250)</code> — Dart-এ একই লেখা!"))

c.lesson("Function-ও একটা মান",
    say("Function variable-এ রাখা যায়, অন্য function-এ পাঠানো যায়। নামহীন function: <code>(x) =&gt; ...</code>।"),
    dart('''
int applyTwice(int Function(int) f, int value) => f(f(value));

void main() {
  final addVat = (int x) => x + x * 15 ~/ 100;
  print(applyTwice(addVat, 1000));

  final prices = [17500, 650, 21000];
  prices.forEach((p) => print('দাম: $p'));
}
'''))

c.section("Collection")
c.lesson("List",
    dart('''
void main() {
  final brands = ['Samsung', 'Xiaomi'];
  brands.add('Walton');
  brands.addAll(['Vivo', 'Oppo']);

  print(brands);
  print('প্রথম: ${brands.first}, মোট: ${brands.length}');
  print('আছে Walton? ${brands.contains('Walton')}');
  brands.remove('Oppo');
  brands.sort();
  print(brands.join(' | '));
}
'''),
    php_note("<code>$brands[] = 'Walton'</code> → <code>brands.add('Walton')</code>, <code>count()</code> → <code>.length</code>, <code>implode()</code> → <code>.join()</code>।"))

c.lesson("Map: key → value",
    dart('''
void main() {
  final stock = <String, int>{
    'Redmi 13': 5,
    'Galaxy A15': 2,
  };
  stock['Vivo Y28'] = 4;
  stock['Redmi 13'] = stock['Redmi 13']! - 1;

  print(stock);
  print(stock['Nokia'] ?? 0);           // নেই → null → 0
  for (final entry in stock.entries) {
    print('${entry.key}: ${entry.value}টা');
  }
}
'''),
    tip("<code>stock['Redmi 13']!</code> — শেষের <code>!</code> মানে \"আমি নিশ্চিত এটা null না\"। ভুল হলে চলার সময় error, তাই কম ব্যবহার করুন।"))

c.lesson("Set: duplicate নেই",
    dart('''
void main() {
  final sold = ['Redmi', 'Vivo', 'Redmi', 'Samsung', 'Vivo'];
  final unique = sold.toSet();
  print(unique);
  print('আলাদা brand: ${unique.length}');

  final mirpur = {'Redmi', 'Vivo'};
  final uttara = {'Vivo', 'Samsung'};
  print('দুই শাখায়ই: ${mirpur.intersection(uttara)}');
}
'''),
    php_note("PHP-র <code>array_unique()</code> আর <code>array_intersect()</code>-এর কাজ।"))

c.lesson("List-এ map, where, fold",
    say("Laravel Collection-এর মতো: <code>where</code> = filter, <code>map</code> = বদলানো, <code>fold</code>/<code>reduce</code> = যোগফল।"),
    dart('''
void main() {
  final prices = [17500, 650, 21000, 250, 9900];

  final expensive = prices.where((p) => p >= 5000).map((p) => p * 95 ~/ 100).toList();
  final total = prices.fold(0, (sum, p) => sum + p);

  print('দামি (৫% ছাড়): $expensive');
  print('মোট: $total');
  print('সবচেয়ে দামি: ${prices.reduce((a, b) => a > b ? a : b)}');
}
'''))

c.section("Input ও Project")
c.lesson("Keyboard থেকে input",
    dart('''
import 'dart:io';

void main() {
  stdout.write('কত কেজি চাল? ');
  final input = stdin.readLineSync() ?? '';
  final kg = int.tryParse(input.trim());

  if (kg == null) {
    print('সংখ্যা লিখুন');
    return;
  }
  print('$kg কেজি × ৭৫ = ${kg * 75} টাকা');
}
''', stdin="12\n"),
    tip("<code>int.tryParse</code> ভুল লেখায় exception না দিয়ে <code>null</code> দেয় — null safety-র সাথে মিলিয়ে সুন্দর।"))

c.lesson("Project: টাকার নোট ভাঙানো",
    dart('''
import 'dart:io';

void main() {
  const notes = [1000, 500, 200, 100, 50, 20, 10, 5, 2, 1];
  stdout.write('কত টাকা ফেরত? ');
  var amount = int.tryParse(stdin.readLineSync()?.trim() ?? '') ?? 0;
  print('');

  var totalNotes = 0;
  for (final note in notes) {
    final count = amount ~/ note;
    if (count > 0) {
      print('${note.toString().padLeft(5)} টাকা × $count');
      amount %= note;
      totalNotes += count;
    }
  }
  print('মোট নোট: $totalNotes');
}
''', stdin="2785\n"),
    task("একটা <code>Map&lt;int, int&gt;</code>-এ রাখুন কোন নোট কয়টা, শেষে map প্রিন্ট করুন।"))

c.finish("Dart 101 শেষ! 🎉",
         "Dart-এর ভিত্তি তৈরি। এবার class, mixin, enum আর Dart 3-এর record ও pattern — Flutter-এর widget বুঝতে এগুলো লাগবে।",
         recap=["<code>var</code> / <code>final</code> / <code>const</code>", "Null safety: <code>String?</code>, <code>??</code>, <code>?.</code>",
                "<code>/</code> double দেয়, <code>~/</code> পূর্ণসংখ্যা", "<code>'$name ${a * b}'</code> interpolation",
                "switch expression = PHP match", "Named parameter <code>{required ...}</code>"])

if __name__ == "__main__":
    c.build()
