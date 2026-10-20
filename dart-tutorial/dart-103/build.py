"""Dart 103 — Future, async/await, Stream, Isolate, JSON, files, HTTP (server + client), packages, tests.
Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402


def dart(src, **kw):
    return code(src, "dart", **kw)


c = Course(slug="dart-103", title="Dart 103 — Async, JSON ও Test", folder=Path(__file__).parent,
           subtitle="Future আর async/await, Stream, Isolate, JSON ↔ class, file, HTTP server ও client, pub package আর test",
           series="Dart 103", next_course=("../flutter/index.html", "Flutter — প্রথম App থেকে API পর্যন্ত"))

c.cover("Dart 103<br>Async, JSON ও Test",
        "App-এর আসল কাজ: API থেকে data আনা, JSON পড়া, অপেক্ষার সময় UI আটকে না রাখা। এই কোর্সের প্রতিটি অংশ Flutter-এ সরাসরি লাগবে।",
        learn=["Future আর async/await", "Error সামলানো আর timeout", "Future.wait: একসাথে কয়েকটা কাজ", "Stream আর async*",
               "Isolate: ভারী কাজ আলাদা thread-এ", "JSON ↔ Dart class", "HTTP server ও client", "pub package আর dart test"],
        need="Dart 102 (class, generic, exception)।")

c.section("Future")
c.lesson("Future: পরে আসবে এমন মান",
    say("Network বা file-এর মতো ধীর কাজ সাথে সাথে ফল দেয় না — দেয় একটা <code>Future</code>, মানে \"পরে দেব\"। <code>await</code> দিয়ে অপেক্ষা করি, আর function-এ <code>async</code> লিখি।"),
    dart('''
Future<int> fetchPrice(String model) async {
  await Future.delayed(const Duration(milliseconds: 300));   // ধরি API call
  return model == 'Redmi 13' ? 17500 : 21000;
}

Future<void> main() async {
  print('দাম খুঁজছি...');
  final price = await fetchPrice('Redmi 13');
  print('দাম: $price');
}
'''),
    php_note("PHP সাধারণত অপেক্ষার সময় পুরো request আটকে রাখে। Dart অপেক্ষার সময় অন্য কাজ (যেমন UI আঁকা) চালিয়ে যায় — এজন্যই Flutter app মসৃণ থাকে।"))

c.lesson("await না দিলে কী হয়?",
    dart('''
Future<String> load() async {
  await Future.delayed(const Duration(milliseconds: 100));
  return 'data এসেছে';
}

Future<void> main() async {
  print('১. শুরু');
  load().then((v) => print('৩. then পেল: $v'));   // অপেক্ষা করল না
  print('২. এই লাইন load শেষ হওয়ার আগেই চলল');
  final v = await load();                           // এখানে অপেক্ষা
  print('৪. await পেল: $v');
}
'''),
    say("<code>await</code> না দিলে Dart অপেক্ষা করে না — ২ নম্বর লাইন ৩-এর আগে ছাপা হলো। <code>.then()</code> পুরনো লেখার ধরন; নতুন কোডে <code>await</code>।"))

c.lesson("Error আর timeout",
    dart('''
Future<int> fetchStock() async {
  await Future.delayed(const Duration(milliseconds: 50));
  throw Exception('server বন্ধ');
}

Future<int> slowApi() => Future.delayed(const Duration(seconds: 5), () => 1);

Future<void> main() async {
  try {
    await fetchStock();
  } catch (e) {
    print('ধরা পড়ল: $e');
  }

  final v = await slowApi()
      .timeout(const Duration(milliseconds: 200), onTimeout: () => -1);
  print('timeout হলে ডিফল্ট: $v');
}
'''))

c.lesson("Future.wait: একসাথে কয়েকটা কাজ",
    say("তিনটা API একটার পর একটা ডাকলে সময় যোগ হয়। <code>Future.wait</code> দিয়ে একসাথে চালালে সময় লাগে সবচেয়ে ধীরটার সমান।"),
    dart('''
Future<int> branchSales(String branch, int ms) async {
  await Future.delayed(Duration(milliseconds: ms));
  return branch.length * 10000;
}

Future<void> main() async {
  final sw = Stopwatch()..start();
  final results = await Future.wait([
    branchSales('Mirpur', 300),
    branchSales('Uttara', 200),
    branchSales('Gulshan', 300),
  ]);
  final ms = (sw.elapsedMilliseconds / 100).round() * 100;
  print('$results → মোট ${results.reduce((a, b) => a + b)}');
  print('সময় ~$ms ms (৮০০ না!)');
}
'''),
    php_note("Laravel-এর <code>Http::pool()</code> বা <code>Concurrency::run()</code>-এর মতো।"))

c.section("Stream")
c.lesson("Stream: একের পর এক আসা মান",
    say("Future একটা মান দেয়; <b>Stream</b> সময়ের সাথে অনেকগুলো — যেমন live বিক্রির খবর, chat message, GPS। <code>async*</code> আর <code>yield</code> দিয়ে বানাই, <code>await for</code> দিয়ে পড়ি।"),
    dart('''
Stream<String> liveSales() async* {
  for (final inv in ['INV-1001', 'INV-1002', 'INV-1003']) {
    await Future.delayed(const Duration(milliseconds: 100));
    yield inv;
  }
}

Future<void> main() async {
  await for (final inv in liveSales()) {
    print('নতুন বিক্রি: $inv');
  }
  print('stream শেষ');
}
'''))

c.lesson("StreamController আর listen",
    dart('''
import 'dart:async';

Future<void> main() async {
  final cart = StreamController<int>();
  var total = 0;

  final sub = cart.stream
      .where((price) => price > 0)
      .listen((price) {
        total += price;
        print('যোগ হলো $price → মোট $total');
      });

  cart.add(650);
  cart.add(-10);       // filter-এ বাদ
  cart.add(17500);
  await cart.close();
  await sub.asFuture<void>();
}
'''),
    tip("Flutter-এ <code>StreamBuilder</code> widget এই stream শুনে UI নিজে থেকেই আপডেট করে।"))

c.section("Isolate")
c.lesson("Isolate.run: ভারী কাজ আলাদা জায়গায়",
    say("Dart এক thread-এ চলে। বড় হিসাব (লাখ row-এর রিপোর্ট) মূল thread-এ করলে Flutter app আটকে যায়। <code>Isolate.run</code> কাজটা আলাদা isolate-এ পাঠায়।"),
    dart('''
import 'dart:isolate';

int heavyReport(int n) {
  var sum = 0;
  for (var i = 1; i <= n; i++) {
    sum += i % 7;
  }
  return sum;
}

Future<void> main() async {
  final result = await Isolate.run(() => heavyReport(20000000));
  print('রিপোর্ট তৈরি: $result');
}
'''),
    php_note("Laravel-এ ভারী কাজ queue job-এ পাঠান; Dart/Flutter-এ isolate। Flutter-এ <code>compute()</code> একই কাজের সহজ রূপ।"))

c.section("JSON ও File")
c.lesson("JSON পড়া আর লেখা",
    dart('''
import 'dart:convert';

void main() {
  const body = '{"id": 7, "name": "Redmi 13", "price": 17500, "colors": ["Black", "Green"]}';

  final map = jsonDecode(body) as Map<String, dynamic>;
  print(map['name']);
  print((map['colors'] as List).length);

  final out = jsonEncode({'invoice': 'INV-1001', 'paid': true, 'total': 18150});
  print(out);
  print(const JsonEncoder.withIndent('  ').convert({'ok': true}));
}
'''),
    php_note("<code>json_decode($body, true)</code> → <code>jsonDecode(body)</code>, <code>json_encode()</code> → <code>jsonEncode()</code>।"))

c.lesson("JSON ↔ class: fromJson আর toJson",
    say("Map দিয়ে কাজ করলে typo ধরা পড়ে না। Model class বানিয়ে <code>fromJson</code>/<code>toJson</code> — Flutter app-এ প্রতিটি API response এভাবে।"),
    dart('''
import 'dart:convert';

class Product {
  Product({required this.id, required this.name, required this.price, this.stock = 0});
  final int id;
  final String name;
  final int price;
  final int stock;

  factory Product.fromJson(Map<String, dynamic> j) => Product(
        id: j['id'] as int,
        name: j['name'] as String,
        price: j['price'] as int,
        stock: (j['stock'] as int?) ?? 0,
      );

  Map<String, dynamic> toJson() => {'id': id, 'name': name, 'price': price, 'stock': stock};
}

void main() {
  const body = '[{"id":1,"name":"Redmi 13","price":17500,"stock":5},{"id":2,"name":"Galaxy A15","price":21000}]';
  final products = (jsonDecode(body) as List).map((j) => Product.fromJson(j)).toList();

  for (final p in products) {
    print('${p.name}: ${p.price} (স্টক ${p.stock})');
  }
  print(jsonEncode(products.first.toJson()));
}
'''),
    tip("বড় project-এ <code>json_serializable</code> বা <code>freezed</code> package এই কোড নিজে লিখে দেয় (<code>dart run build_runner build</code>)।"))

c.lesson("File পড়া আর লেখা",
    dart('''
import 'dart:io';

Future<void> main() async {
  final file = File('sales.csv');
  await file.writeAsString('invoice,total\\nINV-1001,18150\\nINV-1002,2100\\n');

  final lines = await file.readAsLines();
  final total = lines.skip(1).map((l) => int.parse(l.split(',')[1])).reduce((a, b) => a + b);
  print('${lines.length - 1}টা invoice, মোট $total');

  await file.delete();
}
'''),
    php_note("<code>file_put_contents()</code> / <code>file()</code> → <code>writeAsString()</code> / <code>readAsLines()</code> — Dart-এ async।"))

c.section("HTTP ও Package")
c.lesson("ছোট HTTP server আর client",
    say("<code>dart:io</code> দিয়েই server বানানো যায়। একই program-এ server চালু করে client দিয়ে call করি — কোনো package ছাড়া।"),
    dart('''
import 'dart:convert';
import 'dart:io';

Future<void> main() async {
  final server = await HttpServer.bind('127.0.0.1', 0);   // 0 = যেকোনো খালি port
  server.listen((req) {
    final body = req.uri.path == '/products'
        ? jsonEncode([{'name': 'Redmi 13', 'price': 17500}])
        : jsonEncode({'message': 'নেই'});
    req.response
      ..statusCode = req.uri.path == '/products' ? 200 : 404
      ..headers.contentType = ContentType.json
      ..write(body)
      ..close();
  });

  final client = HttpClient();
  for (final path in ['/products', '/orders']) {
    final res = await (await client.get('127.0.0.1', server.port, path)).close();
    print('GET $path → ${res.statusCode} ${await res.transform(utf8.decoder).join()}');
  }
  client.close();
  await server.close();
}
'''),
    tip("Dart-এ backend লিখতে <code>shelf</code> বা <code>dart_frog</code> framework আছে। তবে Flutter app-এর backend সাধারণত Laravel বা Rust (এই সাইটের অন্য কোর্স)।"))

c.lesson("pub package: http",
    say("<code>pubspec.yaml</code> হলো Dart-এর <code>composer.json</code>। <code>dart pub add http</code> দিলে package যোগ হয়। Flutter app-এ API call-এর জন্য এটাই সবচেয়ে প্রচলিত।"),
    shell("$ dart pub add http\n$ dart pub get"),
    code('''
name: shop_cli
environment:
  sdk: ^3.9.0
dependencies:
  http: ^1.2.0
dev_dependencies:
  test: ^1.25.0
''', "yaml", file="pubspec.yaml"),
    dart('''
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

Future<void> main() async {
  final server = await HttpServer.bind('127.0.0.1', 0);
  server.listen((r) => r.response
    ..headers.contentType = ContentType.json
    ..write(jsonEncode({'total': 18150, 'paid': true}))
    ..close());

  final res = await http.get(Uri.parse('http://127.0.0.1:${server.port}/invoices/1001'));
  final data = jsonDecode(res.body) as Map<String, dynamic>;
  print('${res.statusCode}: total ${data['total']}, paid ${data['paid']}');
  await server.close();
}
''', deps={"http": "^1.2.0"}),
    php_note("<code>Http::get($url)-&gt;json()</code> (Laravel) ≈ <code>jsonDecode((await http.get(uri)).body)</code>।"))

c.lesson("Test লেখা: dart test",
    say("<code>package:test</code> দিয়ে <code>test()</code> আর <code>expect()</code>। Group করে সাজানো যায়।"),
    dart('''
import 'package:test/test.dart';

int vat(int amount) => amount * 15 ~/ 100;
int discount(int amount) => amount >= 10000 ? amount ~/ 10 : 0;

void main() {
  group('billing', () {
    test('VAT ১৫%', () => expect(vat(1000), 150));
    test('১০ হাজারের কমে ছাড় নেই', () => expect(discount(9999), 0));
    test('১০ হাজার থেকে ১০% ছাড়', () => expect(discount(20000), 2000));
  });
}
''', test=True),
    php_note("Pest-এর <code>it('...', fn () =&gt; expect(vat(1000))-&gt;toBe(150));</code> — প্রায় হুবহু।"))

c.lesson("Async কোডের test",
    dart('''
import 'package:test/test.dart';

Future<int> fetchStock(String model) async {
  await Future.delayed(const Duration(milliseconds: 10));
  if (model.isEmpty) throw ArgumentError('model দিন');
  return 5;
}

void main() {
  test('stock আসে', () async {
    expect(await fetchStock('Redmi 13'), 5);
  });

  test('খালি model-এ error', () {
    expect(fetchStock(''), throwsArgumentError);
  });

  test('ইচ্ছাকৃত ভুল expectation', () async {
    expect(await fetchStock('Vivo'), 10);
  });
}
''', test=True, panic=True))

c.lesson("Project: API থেকে রিপোর্ট",
    say("সব একসাথে: local server API হিসেবে, <code>http</code> দিয়ে data আনা, JSON → class, <code>Future.wait</code> দিয়ে তিন শাখা একসাথে।"),
    dart('''
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class Sale {
  Sale.fromJson(Map<String, dynamic> j) : invoice = j['invoice'] as String, total = j['total'] as int;
  final String invoice;
  final int total;
}

const fakeDb = {
  'mirpur': [{'invoice': 'INV-1001', 'total': 18150}, {'invoice': 'INV-1005', 'total': 21300}],
  'uttara': [{'invoice': 'INV-1003', 'total': 24150}],
  'gulshan': [{'invoice': 'INV-1004', 'total': 48000}, {'invoice': 'INV-1008', 'total': 21650}],
};

Future<void> main() async {
  final server = await HttpServer.bind('127.0.0.1', 0);
  server.listen((r) {
    final branch = r.uri.pathSegments.last;
    r.response
      ..headers.contentType = ContentType.json
      ..write(jsonEncode(fakeDb[branch] ?? []))
      ..close();
  });
  final base = 'http://127.0.0.1:${server.port}/branches';

  Future<List<Sale>> load(String b) async {
    final res = await http.get(Uri.parse('$base/$b'));
    return (jsonDecode(res.body) as List).map((j) => Sale.fromJson(j)).toList();
  }

  final branches = fakeDb.keys.toList();
  final all = await Future.wait(branches.map(load));
  for (var i = 0; i < branches.length; i++) {
    final total = all[i].fold(0, (s, x) => s + x.total);
    print('${branches[i].padRight(8)} ${all[i].length}টা invoice  $total');
  }
  await server.close();
}
''', deps={"http": "^1.2.0"}),
    task("যে শাখার ফল আসতে ২০০ms-এর বেশি লাগে, সেটায় timeout দিয়ে \"পরে চেষ্টা করুন\" দেখান।"))

c.finish("Dart 103 শেষ! 🎉",
         "Future, Stream, JSON আর HTTP — Flutter app-এর পুরো data অংশ এখন জানা। চলুন UI বানাই: Flutter।",
         recap=["<code>async</code>/<code>await</code>, <code>try/catch</code>, <code>.timeout()</code>",
                "<code>Future.wait</code> — একসাথে কয়েকটা কাজ", "Stream: <code>async*</code>, <code>yield</code>, <code>await for</code>, <code>listen</code>",
                "<code>Isolate.run</code> — ভারী কাজ আলাদা", "<code>fromJson</code>/<code>toJson</code> model", "<code>package:http</code> আর <code>dart test</code>"])

if __name__ == "__main__":
    c.build()
