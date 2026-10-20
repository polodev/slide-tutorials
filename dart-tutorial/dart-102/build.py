"""Dart 102 — class, constructor, getter, inheritance, interface, mixin, enum, extension, generics,
record, pattern, sealed class, exception. Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, table, task, tip, warn  # noqa: E402


def dart(src, **kw):
    return code(src, "dart", **kw)


c = Course(slug="dart-102", title="Dart 102 — Class, Mixin ও Pattern", folder=Path(__file__).parent,
           subtitle="Class আর constructor, inheritance, interface, mixin (PHP trait), enum, extension, generic, record, pattern আর sealed class",
           series="Dart 102", next_course=("../dart-103/index.html", "Dart 103 — Async, JSON ও Test"))

c.cover("Dart 102<br>Class, Mixin ও Pattern",
        "Flutter-এ সবকিছুই class — প্রতিটি widget, প্রতিটি model। এই কোর্সে Dart-এর object-oriented দিক আর Dart 3-এর আধুনিক record ও pattern।",
        learn=["Class আর ছোট constructor", "Named আর factory constructor", "Getter, setter, private (_)",
               "extends, implements, abstract", "Mixin = PHP trait", "Enhanced enum আর extension",
               "Generic, record, pattern matching", "Sealed class আর exception"],
        need="Dart 101।")

c.section("Class")
c.lesson("Class আর ছোট constructor",
    say("<code>this.name</code> লিখলে constructor নিজেই field-এ মান বসায় — PHP 8-এর constructor promotion-এর মতো।"),
    dart('''
class Product {
  final String name;
  final int price;
  int stock;

  Product(this.name, this.price, {this.stock = 0});

  int get stockValue => price * stock;

  void sell(int qty) {
    stock -= qty;
  }
}

void main() {
  final p = Product('Redmi 13', 17500, stock: 5);
  p.sell(2);
  print('${p.name}: স্টক ${p.stock}, মূল্য ${p.stockValue}');
}
'''),
    code('''
<?php
class Product {
    public function __construct(
        public readonly string $name,
        public readonly int $price,
        public int $stock = 0,
    ) {}
}
''', "php", run=False, label="PHP 8-এ তুলনা"),
    tip("Dart-এ <code>new</code> লেখা লাগে না: <code>Product(...)</code>।"))

c.lesson("Named আর factory constructor",
    say("একাধিক উপায়ে object বানাতে named constructor: <code>Product.used(...)</code>। <code>factory</code> চাইলে নতুন object না বানিয়ে অন্য কিছু ফেরত দিতে পারে — যেমন Map থেকে বানানো।"),
    dart('''
class Product {
  final String name;
  final int price;
  final bool used;

  Product(this.name, this.price) : used = false;
  Product.used(this.name, this.price) : used = true;

  factory Product.fromMap(Map<String, dynamic> m) =>
      Product(m['name'] as String, m['price'] as int);

  @override
  String toString() => '$name ($price টাকা${used ? ', used' : ''})';
}

void main() {
  print(Product('Galaxy A15', 21000));
  print(Product.used('iPhone 12', 48000));
  print(Product.fromMap({'name': 'Vivo Y28', 'price': 18000}));
}
'''),
    php_note("Laravel-এর <code>Product::make([...])</code> বা static constructor-এর মতো। <code>toString()</code> = PHP-র <code>__toString()</code>।"))

c.lesson("Private: নামের আগে _",
    say("Dart-এ <code>private</code> keyword নেই — নাম <code>_</code> দিয়ে শুরু হলে সেটা ঐ file-এর বাইরে দেখা যায় না। Getter/setter দিয়ে নিয়ন্ত্রিত প্রবেশ।"),
    dart('''
class Wallet {
  int _balance = 0;

  int get balance => _balance;

  set deposit(int amount) {
    if (amount <= 0) throw ArgumentError('টাকা ০-এর বেশি দিন');
    _balance += amount;
  }
}

void main() {
  final w = Wallet();
  w.deposit = 500;
  w.deposit = 200;
  print('ব্যালেন্স: ${w.balance}');
  try {
    w.deposit = -50;
  } on ArgumentError catch (e) {
    print('আটকাল: ${e.message}');
  }
}
'''))

c.section("Inheritance ও Interface")
c.lesson("extends আর abstract",
    dart('''
abstract class Payable {
  int get amount;
  String get label;
  String describe() => '$label: $amount টাকা';
}

class Invoice extends Payable {
  Invoice(this.no, this.amount);
  final int no;
  @override
  final int amount;
  @override
  String get label => 'Invoice #$no';
}

class ServiceBill extends Payable {
  ServiceBill(this.parts, this.labour);
  final int parts, labour;
  @override
  int get amount => parts + labour;
  @override
  String get label => 'Service';
}

void main() {
  final List<Payable> items = [Invoice(101, 23500), ServiceBill(1800, 500)];
  for (final i in items) {
    print(i.describe());
  }
}
'''),
    php_note("PHP-র <code>abstract class</code> আর <code>extends</code> একই। <code>@override</code> শুধু চিহ্ন, ভুল নাম লিখলে Dart সতর্ক করে।"))

c.lesson("implements: যেকোনো class-ই interface",
    say("Dart-এ আলাদা <code>interface</code> keyword লাগে না — যেকোনো class <code>implements</code> করা যায়, তখন তার সব method নিজে লিখতে হয়।"),
    dart('''
abstract interface class SmsSender {
  String send(String phone, String text);
}

class FakeSms implements SmsSender {
  @override
  String send(String phone, String text) => 'SMS → $phone: $text';
}

void notifyCustomer(SmsSender sms) {
  print(sms.send('01711000001', 'আপনার invoice তৈরি হয়েছে'));
}

void main() {
  notifyCustomer(FakeSms());
}
'''),
    tip("Laravel-এ যেমন interface bind করে test-এ fake দেন, Dart/Flutter-এও একই কৌশল।"))

c.lesson("Mixin = PHP trait",
    say("<code>mixin</code> হলো এমন কোড যা অনেক class-এ <code>with</code> দিয়ে মিশিয়ে দেওয়া যায় — inheritance ছাড়াই। PHP-র <code>trait</code>।"),
    dart('''
mixin Timestamps {
  DateTime? createdAt;
  void touch() => createdAt = DateTime(2026, 10, 21, 10, 30);
}

mixin SoftDeletes {
  bool deleted = false;
  void softDelete() => deleted = true;
}

class Customer with Timestamps, SoftDeletes {
  Customer(this.name);
  final String name;
}

void main() {
  final c = Customer('Karim')..touch()..softDelete();
  print('${c.name}: তৈরি ${c.createdAt}, মোছা? ${c.deleted}');
}
'''),
    php_note("<code>class Customer { use Timestamps, SoftDeletes; }</code> — Laravel model-এর trait-গুলোর মতোই। <code>..</code> হলো cascade: একই object-এ পরপর method ডাকা।"))

c.section("Enum, Extension, Generic")
c.lesson("Enhanced enum",
    say("Dart enum-এ field আর method থাকতে পারে — PHP 8.1-এর backed enum-এর চেয়েও শক্তিশালী।"),
    dart('''
enum PaymentMethod {
  cash('নগদ', 0),
  bkash('bKash', 1.5),
  nagad('Nagad', 1.5),
  card('Card', 2.0);

  const PaymentMethod(this.label, this.feePercent);
  final String label;
  final double feePercent;

  double feeOn(int amount) => amount * feePercent / 100;
}

void main() {
  for (final m in PaymentMethod.values) {
    print('${m.label.padRight(6)} ১০,০০০ টাকায় চার্জ ${m.feeOn(10000)}');
  }
  print(PaymentMethod.values.byName('bkash').label);
}
'''))

c.lesson("Extension: পুরনো type-এ নতুন method",
    say("নিজের লেখা না এমন class-এও method যোগ করা যায় — যেমন <code>int</code>-এ টাকা লেখার format।"),
    dart('''
extension Taka on int {
  String get taka {
    final s = toString();
    if (s.length <= 3) return '৳$s';
    final last3 = s.substring(s.length - 3);
    var rest = s.substring(0, s.length - 3);
    final parts = <String>[];
    while (rest.length > 2) {
      parts.insert(0, rest.substring(rest.length - 2));
      rest = rest.substring(0, rest.length - 2);
    }
    if (rest.isNotEmpty) parts.insert(0, rest);
    return '৳${parts.join(',')},$last3';
  }
}

void main() {
  print(170400.taka);
  print(12500000.taka);
  print(650.taka);
}
'''),
    php_note("PHP-তে এটা সম্ভব না (built-in type-এ method যোগ)। Laravel-এর <code>Str::macro()</code> কাছাকাছি ধারণা।"))

c.lesson("Generic",
    dart('''
class Paginated<T> {
  Paginated(this.items, {required this.page, required this.total});
  final List<T> items;
  final int page, total;
  bool hasNext(int perPage) => page * perPage < total;
}

T firstOr<T>(List<T> list, T fallback) => list.isEmpty ? fallback : list.first;

void main() {
  final phones = Paginated(['Redmi', 'Vivo'], page: 1, total: 5);
  print('${phones.items} → পরের পাতা? ${phones.hasNext(2)}');
  print(firstOr(<int>[], 0));
  print(firstOr(['Dhaka'], 'নেই'));
}
'''))

c.section("Record ও Pattern (Dart 3)")
c.lesson("Record: কয়েকটা মান একসাথে ফেরত",
    say("<code>(int, String)</code> বা নামসহ <code>({int total, int count})</code> — ছোট class না বানিয়েই কয়েকটা মান ফেরত।"),
    dart('''
({int total, int count}) summarize(List<int> sales) =>
    (total: sales.fold(0, (a, b) => a + b), count: sales.length);

(String, int) cheapest(Map<String, int> prices) {
  final e = prices.entries.reduce((a, b) => a.value <= b.value ? a : b);
  return (e.key, e.value);
}

void main() {
  final s = summarize([18150, 2100, 24150]);
  print('মোট ${s.total}, invoice ${s.count}টা');

  final (name, price) = cheapest({'Redmi 13': 17500, 'Nokia 105': 2100, 'Vivo Y28': 18000});
  print('সবচেয়ে সস্তা: $name ($price)');
}
'''),
    php_note("PHP-তে array ফেরত দিয়ে <code>[$name, $price] = cheapest()</code> করতাম — Dart-এ এটা type-নিরাপদ।"))

c.lesson("Pattern matching",
    say("switch-এ শুধু মান না, আকৃতিও মেলানো যায়: list, map, record, type — আর সাথে <code>when</code> শর্ত।"),
    dart('''
String describe(Object? command) => switch (command) {
  ['sell', String item, int qty] when qty > 0 => '$item × $qty বিক্রি',
  ['sell', _, _] => 'পরিমাণ ভুল',
  {'type': 'refund', 'amount': int a} => '$a টাকা ফেরত',
  int n => 'শুধু একটা সংখ্যা: $n',
  null => 'কিছু নেই',
  _ => 'বুঝিনি',
};

void main() {
  print(describe(['sell', 'Charger', 2]));
  print(describe(['sell', 'Charger', 0]));
  print(describe({'type': 'refund', 'amount': 650}));
  print(describe(42));
  print(describe(null));
  print(describe('hello'));
}
'''))

c.lesson("Sealed class: সব ক্ষেত্র ধরা বাধ্যতামূলক",
    say("<code>sealed</code> class-এর সব subclass একই file-এ থাকে, তাই switch-এ কোনোটা বাদ পড়লে compiler ধরে। Flutter-এ loading/success/error state-এর জন্য দারুণ।"),
    dart('''
sealed class Payment {}

class Cash extends Payment {}

class Bkash extends Payment {
  Bkash(this.trxId);
  final String trxId;
}

class Card extends Payment {
  Card(this.last4);
  final String last4;
}

String receipt(Payment p) => switch (p) {
  Cash() => 'নগদ',
  Bkash(:final trxId) => 'bKash TrxID $trxId',
  Card(:final last4) => 'Card ****$last4',
};

void main() {
  for (final p in [Cash(), Bkash('BK7X9'), Card('4421')]) {
    print(receipt(p));
  }
}
'''),
    dart('''
sealed class Payment {}
class Cash extends Payment {}
class Card extends Payment {}

String receipt(Payment p) => switch (p) {
  Cash() => 'নগদ',
};

void main() => print(receipt(Card()));
''', err="exhaustively"))

c.section("Collection ও Exception")
c.lesson("Spread, collection-if আর for",
    say("List বানানোর সময়ই শর্ত আর loop — Flutter-এ widget-এর তালিকা বানাতে প্রতিদিন লাগে।"),
    dart('''
void main() {
  const isVip = true;
  final base = ['Invoice', 'Products'];
  final branches = ['Mirpur', 'Uttara'];

  final menu = [
    'Dashboard',
    ...base,
    if (isVip) 'Reports',
    for (final b in branches) 'POS — $b',
  ];
  print(menu);
}
'''),
    php_note("PHP-র spread <code>[...$base]</code> একই। শর্ত দিয়ে item যোগ — PHP-তে <code>array_filter</code> বা আলাদা <code>if</code> লাগে।"))

c.lesson("Exception: throw, try, catch",
    dart('''
class OutOfStock implements Exception {
  OutOfStock(this.product, this.have);
  final String product;
  final int have;
  @override
  String toString() => '$product: আছে মাত্র $have টা';
}

void sell(Map<String, int> stock, String item, int qty) {
  final have = stock[item] ?? 0;
  if (have < qty) throw OutOfStock(item, have);
  stock[item] = have - qty;
}

void main() {
  final stock = {'iPhone 12': 1};
  try {
    sell(stock, 'iPhone 12', 1);
    sell(stock, 'iPhone 12', 1);
  } on OutOfStock catch (e) {
    print('বিক্রি হলো না — $e');
  } finally {
    print('এখন স্টক: $stock');
  }
}
'''),
    php_note("<code>try { } catch (OutOfStock $e) { } finally { }</code> — Dart-এ <code>on Type catch (e)</code>।"))

c.lesson("Project: দোকানের cart",
    dart('''
enum Pay { cash, bkash }

class Item {
  const Item(this.name, this.price, [this.qty = 1]);
  final String name;
  final int price, qty;
  int get total => price * qty;
}

class Cart {
  final _items = <Item>[];
  void add(Item i) => _items.add(i);
  int get subtotal => _items.fold(0, (s, i) => s + i.total);
  int discount() => subtotal >= 20000 ? subtotal * 5 ~/ 100 : 0;

  String checkout(Pay pay) {
    final lines = [
      for (final i in _items) '${i.name.padRight(10)} ${i.qty} × ${i.price} = ${i.total}',
      'Subtotal: $subtotal',
      if (discount() > 0) 'ছাড় (৫%): -${discount()}',
      'দেবেন: ${subtotal - discount()} (${pay.name})',
    ];
    return lines.join('\\n');
  }
}

void main() {
  final cart = Cart()
    ..add(const Item('Redmi 13', 17500))
    ..add(const Item('Charger', 650, 2))
    ..add(const Item('Cover', 250, 5));
  print(cart.checkout(Pay.bkash));
}
'''),
    task("<code>sealed class Discount</code> বানান: <code>Percent(5)</code> আর <code>Flat(500)</code> — <code>checkout</code> যেকোনোটা নেবে।"))

c.finish("Dart 102 শেষ! 🎉",
         "Class থেকে sealed class — Dart-এর গঠন এখন জানা। শেষ ধাপ: async, Future, Stream, JSON আর test।",
         recap=["<code>this.name</code> constructor, named/factory constructor", "<code>_name</code> = private",
                "<code>extends</code>, <code>implements</code>, <code>mixin</code> (= trait)", "Enum-এ field/method, extension দিয়ে নতুন method",
                "Record আর pattern matching", "Sealed class + exhaustive switch"])

if __name__ == "__main__":
    c.build()
