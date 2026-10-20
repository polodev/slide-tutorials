"""Flutter — first app to API-driven list. Every app is analyzed against the real Flutter SDK and
screenshotted through a golden test (Bangla font + Material icons loaded), optionally after taps/typing;
widget-test lessons run `flutter test`. Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402


def app(src, actions=None, **kw):
    """A complete Flutter app (defines `App`); shown with a real screenshot."""
    return code(src, "dart", flutter=True, actions=actions, label=kw.pop("label", "lib/main.dart"), **kw)


def widget_test(src, app_src, **kw):
    return code(src, "dart", flutter=True, test=True, app=app_src, label="test/widget_test.dart", **kw)


HEAD = "import 'package:flutter/material.dart';\n\nvoid main() => runApp(const App());\n"

c = Course(slug="flutter", title="Flutter — প্রথম App থেকে API পর্যন্ত", folder=Path(__file__).parent,
           subtitle="Widget, layout, state, form, navigation, provider, FutureBuilder আর API — প্রতিটি app-এর আসল screenshot সহ",
           series="Flutter")

c.cover("Flutter<br>প্রথম App থেকে API পর্যন্ত",
        "এক কোডে Android, iPhone, web আর desktop। এই কোর্সে একটা মোবাইল দোকানের app ধাপে ধাপে বানাব — প্রতিটি কোডের পাশে সেই কোড চালিয়ে তোলা আসল screenshot।",
        learn=["Flutter কী, widget tree", "Text, Icon, Container, Row, Column", "Card, ListTile, ListView.builder",
               "StatefulWidget আর setState", "TextField, Form আর validation", "Navigator আর NavigationBar",
               "provider দিয়ে shared state", "FutureBuilder, API আর widget test"],
        need="Dart 101–103 (বিশেষ করে class, named parameter, async/await)।")

# ================================================================== start
c.section("শুরু")
c.lesson("Flutter কী, Laravel developer-এর চোখে",
    say("Flutter-এ পুরো UI হলো <b>widget</b>-এর গাছ: একটা widget-এর ভিতরে আরেকটা। Data বদলালে Flutter গাছটা আবার আঁকে।"),
    table(["Laravel / web", "Flutter"], [
        ["Blade view", "Widget-এর <code>build()</code> method"], ["CSS (margin, flex)", "<code>Padding</code>, <code>Row</code>, <code>Column</code>, <code>Expanded</code>"],
        ["Livewire property বদলালে UI বদলায়", "<code>setState()</code> দিলে widget আবার আঁকে"], ["routes/web.php", "<code>Navigator</code> / <code>go_router</code>"],
        ["<code>Http::get()</code>", "<code>http.get()</code> + <code>FutureBuilder</code>"], ["Form request validation", "<code>Form</code> + <code>validator</code>"],
        ["Pest/PHPUnit feature test", "<code>flutter test</code> widget test"]]),
    tip("Backend থাকে আলাদা — আপনার Laravel API বা এই সাইটের Rust API। Flutter শুধু app-এর চেহারা আর আচরণ।"))

c.lesson("Install আর প্রথম project",
    shell("$ flutter doctor\n$ flutter create shop_app\n$ cd shop_app\n$ flutter run          # চালু emulator/phone/Chrome-এ",
          out="Doctor summary (to see all details, run flutter doctor -v):\n[✓] Flutter (Channel stable, 3.47.5)\n[✓] Android toolchain\n[✓] Chrome - develop for the web\n[✓] VS Code"),
    points("<code>flutter doctor</code> যা যা কম আছে বলে দেয় (Android Studio, Xcode ইত্যাদি)",
           "চালু অবস্থায় কোড save করলে <b>hot reload</b> — সাথে সাথে বদল দেখায়, state হারায় না",
           "মূল কোড <code>lib/main.dart</code>-এ"),
    tip("কোনো phone না থাকলে <code>flutter run -d chrome</code> — web-এ চালিয়ে শিখতে পারেন।"))

c.lesson("প্রথম App",
    say("<code>MaterialApp</code> পুরো app মুড়ে রাখে (theme, navigation)। <code>Scaffold</code> একটা পাতার কাঠামো: উপরে <code>AppBar</code>, মাঝে <code>body</code>, নিচে বাটন।"),
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.green),
      home: Scaffold(
        appBar: AppBar(title: const Text('Rahim Mobile')),
        body: const Center(
          child: Text('আসসালামু আলাইকুম!', style: TextStyle(fontSize: 26)),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () {},
          child: const Icon(Icons.add),
        ),
      ),
    );
  }
}
'''),
    php_note("<code>StatelessWidget</code> = যে widget নিজে কখনো বদলায় না, শুধু যা পায় তা দেখায় — Blade component-এর মতো।"))

# ================================================================== layout
c.section("Layout")
c.lesson("Column, Row আর Icon",
    say("<code>Column</code> উপর থেকে নিচে, <code>Row</code> বাম থেকে ডানে সাজায়। <code>SizedBox</code> দিয়ে ফাঁকা জায়গা।"),
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.green),
      home: Scaffold(
        appBar: AppBar(title: const Text('আজকের হিসাব')),
        body: const Padding(
          padding: EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [Icon(Icons.point_of_sale, color: Colors.green), SizedBox(width: 8), Text('বিক্রি: ৳১,৭০,৪০০')]),
              SizedBox(height: 12),
              Row(children: [Icon(Icons.receipt_long, color: Colors.blue), SizedBox(width: 8), Text('Invoice: ১২টা')]),
              SizedBox(height: 12),
              Row(children: [Icon(Icons.warning_amber, color: Colors.orange), SizedBox(width: 8), Text('স্টক কম: ৩টা product')]),
            ],
          ),
        ),
      ),
    );
  }
}
'''),
    php_note("CSS-এর <code>display: flex; flex-direction: column</code> = <code>Column</code>; <code>row</code> = <code>Row</code>।"))

c.lesson("Container আর decoration",
    say("<code>Container</code>-এ রং, গোল কোণা, border, ছায়া — CSS box-এর মতো। <code>Expanded</code> বাকি জায়গা নিয়ে নেয়।"),
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.green),
      home: Scaffold(
        appBar: AppBar(title: const Text('Dashboard')),
        body: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(child: _stat('আজ', '৳১,৭০,৪০০', Colors.green)),
              const SizedBox(width: 12),
              Expanded(child: _stat('বাকি', '৳১২,৫০০', Colors.orange)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _stat(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color, width: 1.5),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(color: color, fontWeight: FontWeight.w600)),
          const SizedBox(height: 6),
          Text(value, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
'''),
    tip("বারবার লাগে এমন অংশ ছোট function বা নিজের widget বানিয়ে আলাদা করুন — Blade-এর component-এর মতো।"))

c.lesson("Card আর ListTile",
    say("<code>ListTile</code> তালিকার একটা row-এর তৈরি নকশা: বামে icon/ছবি, মাঝে লেখা, ডানে কিছু।"),
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.green),
      home: Scaffold(
        appBar: AppBar(title: const Text('Customer')),
        body: ListView(
          padding: const EdgeInsets.all(12),
          children: const [
            Card(child: ListTile(leading: CircleAvatar(child: Text('K')), title: Text('Karim Uddin'), subtitle: Text('01711-000001 · Dhaka'), trailing: Text('৳০'))),
            Card(child: ListTile(leading: CircleAvatar(child: Text('N')), title: Text('Nusrat Jahan'), subtitle: Text('01811-000002 · Sylhet'), trailing: Text('৳৫০০'))),
            Card(child: ListTile(leading: CircleAvatar(child: Text('R')), title: Text('Rahim Mia'), subtitle: Text('01911-000003 · Khulna'), trailing: Text('৳১,৫০০', style: TextStyle(color: Colors.red)))),
          ],
        ),
      ),
    );
  }
}
'''))

c.lesson("ListView.builder: model থেকে তালিকা",
    say("Data থাকে model class-এর list-এ। <code>ListView.builder</code> শুধু পর্দায় দেখা row-গুলো বানায় — হাজার product-এও দ্রুত।"),
    app(HEAD + '''
class Product {
  const Product(this.name, this.brand, this.price, this.stock);
  final String name, brand;
  final int price, stock;
}

const products = [
  Product('Redmi 13', 'Xiaomi', 17500, 5),
  Product('Galaxy A15', 'Samsung', 21000, 0),
  Product('iPhone 12', 'Apple', 48000, 1),
  Product('Vivo Y28', 'Vivo', 18000, 4),
  Product('Walton NEXG N9', 'Walton', 9990, 7),
];

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.green),
      home: Scaffold(
        appBar: AppBar(title: const Text('Products')),
        body: ListView.builder(
          itemCount: products.length,
          itemBuilder: (context, i) {
            final p = products[i];
            return ListTile(
              leading: const Icon(Icons.smartphone),
              title: Text(p.name),
              subtitle: Text(p.brand),
              trailing: p.stock == 0
                  ? const Chip(label: Text('শেষ'))
                  : Text('৳${p.price}', style: const TextStyle(fontWeight: FontWeight.bold)),
            );
          },
        ),
      ),
    );
  }
}
'''),
    php_note("Blade-এর <code>@foreach ($products as $p)</code> ≈ <code>itemBuilder</code>।"))

# ================================================================== state
c.section("State")
c.lesson("StatefulWidget আর setState",
    say("যে widget-এর ভিতরের মান বদলায়, সেটা <code>StatefulWidget</code>। মান বদলে <code>setState()</code> ডাকলে Flutter আবার <code>build()</code> চালায়। Screenshot নেওয়া হয়েছে + বাটন ৩ বার চাপার পর।"),
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: Colors.green),
        home: const CounterPage(),
      );
}

class CounterPage extends StatefulWidget {
  const CounterPage({super.key});

  @override
  State<CounterPage> createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> {
  int _qty = 1;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('পরিমাণ')),
      body: Center(
        child: Text('Charger × $_qty = ৳${650 * _qty}', style: const TextStyle(fontSize: 24)),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => setState(() => _qty++),
        child: const Icon(Icons.add),
      ),
    );
  }
}
''', actions=["for (var i = 0; i < 3; i++) { await tester.tap(find.byIcon(Icons.add)); await tester.pump(); }"]),
    php_note("Livewire-এ <code>$this-&gt;qty++</code> করলে component আবার render হয় — একদম একই ভাবনা।"),
    warn("<code>setState</code> ছাড়া শুধু <code>_qty++</code> করলে মান বদলাবে কিন্তু পর্দা বদলাবে না।"))

COUNTER = HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) => const MaterialApp(home: CounterPage());
}

class CounterPage extends StatefulWidget {
  const CounterPage({super.key});

  @override
  State<CounterPage> createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> {
  int _qty = 1;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(child: Text('Charger × $_qty = ৳${650 * _qty}')),
      floatingActionButton: FloatingActionButton(
        onPressed: () => setState(() => _qty++),
        child: const Icon(Icons.add),
      ),
    );
  }
}
'''

c.lesson("Widget test",
    say("App চালু না করেই UI test করা যায়: widget বসাও, বাটন চাপো, লেখা খোঁজো। আগের পাঠের counter-এর test:"),
    widget_test('''
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app/main.dart';

void main() {
  testWidgets('add চাপলে পরিমাণ ও দাম বাড়ে', (tester) async {
    await tester.pumpWidget(const App());
    expect(find.text('Charger × 1 = ৳650'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.add));
    await tester.pump();

    expect(find.text('Charger × 2 = ৳1300'), findsOneWidget);
    expect(find.text('Charger × 1 = ৳650'), findsNothing);
  });
}
''', COUNTER),
    php_note("Laravel-এর <code>$this-&gt;get('/')-&gt;assertSee('...')</code> বা Livewire test-এর <code>-&gt;call('increment')-&gt;assertSee()</code>-এর মতো।"))

c.lesson("Cart: তালিকা থেকে যোগ",
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: Colors.green),
        home: const PosPage(),
      );
}

const items = {'Redmi 13': 17500, 'Charger 20W': 650, 'Glass Protector': 150};

class PosPage extends StatefulWidget {
  const PosPage({super.key});

  @override
  State<PosPage> createState() => _PosPageState();
}

class _PosPageState extends State<PosPage> {
  final cart = <String, int>{};

  int get total => cart.entries.fold(0, (s, e) => s + items[e.key]! * e.value);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('POS')),
      body: ListView(
        children: [
          for (final e in items.entries)
            ListTile(
              title: Text(e.key),
              subtitle: Text('৳${e.value}'),
              trailing: FilledButton.tonal(
                onPressed: () => setState(() => cart[e.key] = (cart[e.key] ?? 0) + 1),
                child: Text(cart[e.key] == null ? 'যোগ' : '× ${cart[e.key]}'),
              ),
            ),
        ],
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(20),
        color: Colors.green.shade50,
        child: Text('মোট: ৳$total', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
      ),
    );
  }
}
''', actions=["await tester.tap(find.text('যোগ').first); await tester.pump();",
              "await tester.tap(find.text('যোগ').first); await tester.pump();",
              "await tester.tap(find.text('যোগ').first); await tester.pump();",
              "await tester.tap(find.text('× 1').last); await tester.pump();"]),
    say("Screenshot নেওয়ার আগে test তিনটা product যোগ করেছে, তারপর Glass Protector আরেকবার।"))

# ================================================================== forms
c.section("Form ও Navigation")
c.lesson("TextField আর controller",
    say("<code>TextEditingController</code> দিয়ে লেখা পড়ি। Screenshot-এর আগে test নাম লিখে বাটন চেপেছে।"),
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: Colors.green),
        home: const GreetPage(),
      );
}

class GreetPage extends StatefulWidget {
  const GreetPage({super.key});

  @override
  State<GreetPage> createState() => _GreetPageState();
}

class _GreetPageState extends State<GreetPage> {
  final _name = TextEditingController();
  String _message = '';

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('নতুন Customer')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(controller: _name, decoration: const InputDecoration(labelText: 'নাম', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: () => setState(() => _message = 'স্বাগতম, ${_name.text}!'),
              child: const Text('Save'),
            ),
            const SizedBox(height: 20),
            Text(_message, style: const TextStyle(fontSize: 20)),
          ],
        ),
      ),
    );
  }
}
''', actions=["await tester.enterText(find.byType(TextField), 'Nusrat Jahan');",
              "await tester.tap(find.text('Save')); await tester.pump();"]),
    tip("Controller শেষে <code>dispose()</code> করুন — নইলে memory leak।"))

c.lesson("Form validation",
    say("<code>Form</code> + <code>TextFormField</code>-এর <code>validator</code>: ভুল হলে লেখা ফেরত দিন, ঠিক হলে <code>null</code>। Screenshot: খালি form-এ Save চাপার পর।"),
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: Colors.green),
        home: const ProductForm(),
      );
}

class ProductForm extends StatefulWidget {
  const ProductForm({super.key});

  @override
  State<ProductForm> createState() => _ProductFormState();
}

class _ProductFormState extends State<ProductForm> {
  final _form = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Product যোগ')),
      body: Form(
        key: _form,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            TextFormField(
              decoration: const InputDecoration(labelText: 'নাম'),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'নাম দিতে হবে' : null,
            ),
            TextFormField(
              decoration: const InputDecoration(labelText: 'দাম'),
              keyboardType: TextInputType.number,
              validator: (v) => (int.tryParse(v ?? '') ?? 0) <= 0 ? 'দাম ০-এর বেশি হতে হবে' : null,
            ),
            const SizedBox(height: 20),
            FilledButton(onPressed: () => _form.currentState!.validate(), child: const Text('Save')),
          ],
        ),
      ),
    );
  }
}
''', actions=["await tester.tap(find.text('Save')); await tester.pump();"]),
    php_note("<code>'name' =&gt; 'required'</code>, <code>'price' =&gt; 'integer|min:1'</code> — একই নিয়ম, শুধু app-এর ভিতরে। Server-এ Laravel validation তবুও রাখুন।"))

c.lesson("Navigator: আরেক পাতায় যাওয়া",
    say("<code>Navigator.push</code> নতুন পাতা উপরে বসায়, back চাপলে <code>pop</code>। Screenshot: তালিকা থেকে iPhone 12-এ tap করার পর।"),
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: Colors.green),
        home: const ListPage(),
      );
}

const phones = {'Redmi 13': 17500, 'iPhone 12': 48000, 'Vivo Y28': 18000};

class ListPage extends StatelessWidget {
  const ListPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Products')),
      body: ListView(
        children: [
          for (final e in phones.entries)
            ListTile(
              title: Text(e.key),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => DetailPage(name: e.key, price: e.value)),
              ),
            ),
        ],
      ),
    );
  }
}

class DetailPage extends StatelessWidget {
  const DetailPage({super.key, required this.name, required this.price});
  final String name;
  final int price;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(name)),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(Icons.phone_iphone, size: 96),
            Text(name, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
            Text('৳$price', style: const TextStyle(fontSize: 22, color: Colors.green)),
            const SizedBox(height: 20),
            FilledButton.icon(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.arrow_back), label: const Text('ফিরে যান')),
          ],
        ),
      ),
    );
  }
}
''', actions=["await tester.tap(find.text('iPhone 12')); await tester.pumpAndSettle();"]),
    tip("বড় app-এ URL-ভিত্তিক routing-এর জন্য <code>go_router</code> package — Laravel route-এর মতো <code>/products/:id</code>।"))

c.lesson("NavigationBar: নিচের tab",
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: Colors.green),
        home: const HomeShell(),
      );
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _tab = 0;
  static const _titles = ['Dashboard', 'POS', 'Report'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(_titles[_tab])),
      body: Center(child: Text('${_titles[_tab]} পাতা', style: const TextStyle(fontSize: 24))),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (i) => setState(() => _tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard_outlined), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.point_of_sale), label: 'POS'),
          NavigationDestination(icon: Icon(Icons.bar_chart), label: 'Report'),
        ],
      ),
    );
  }
}
''', actions=["await tester.tap(find.byIcon(Icons.point_of_sale)); await tester.pumpAndSettle();"]))

# ================================================================== provider
c.section("State management ও API")
c.lesson("provider: অনেক পাতায় একই cart",
    say("Cart যখন POS পাতা আর AppBar-এর badge দুই জায়গায় লাগে, তখন state widget থেকে বের করে <code>ChangeNotifier</code>-এ রাখি; <code>provider</code> সেটা পুরো app-এ পৌঁছে দেয়। <code>context.watch</code> বদল শোনে, <code>context.read</code> শুধু ডাকে।"),
    shell("$ flutter pub add provider"),
    app('''
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class Cart extends ChangeNotifier {
  final _items = <String, int>{};
  int get count => _items.values.fold(0, (a, b) => a + b);
  int get total => _items.entries.fold(0, (s, e) => s + prices[e.key]! * e.value);
  void add(String name) {
    _items[name] = (_items[name] ?? 0) + 1;
    notifyListeners();
  }
}

const prices = {'Redmi 13': 17500, 'Charger 20W': 650, 'Cover': 250};

void main() => runApp(const App());

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) => ChangeNotifierProvider(
        create: (_) => Cart(),
        child: MaterialApp(
          debugShowCheckedModeBanner: false,
          theme: ThemeData(colorSchemeSeed: Colors.green),
          home: const Pos(),
        ),
      );
}

class Pos extends StatelessWidget {
  const Pos({super.key});

  @override
  Widget build(BuildContext context) {
    final cart = context.watch<Cart>();
    return Scaffold(
      appBar: AppBar(
        title: const Text('POS'),
        actions: [Badge(label: Text('${cart.count}'), child: const Icon(Icons.shopping_cart)), const SizedBox(width: 20)],
      ),
      body: ListView(
        children: [
          for (final name in prices.keys)
            ListTile(
              title: Text(name),
              subtitle: Text('৳${prices[name]}'),
              trailing: IconButton.filledTonal(
                icon: const Icon(Icons.add),
                onPressed: () => context.read<Cart>().add(name),
              ),
            ),
          ListTile(title: Text('মোট: ৳${cart.total}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold))),
        ],
      ),
    );
  }
}
''', actions=["await tester.tap(find.byIcon(Icons.add).at(0)); await tester.pump();",
              "await tester.tap(find.byIcon(Icons.add).at(1)); await tester.pump();",
              "await tester.tap(find.byIcon(Icons.add).at(1)); await tester.pump();"]),
    tip("আরও বড় app-এ <code>riverpod</code> বা <code>bloc</code> জনপ্রিয়। শুরু করুন provider দিয়ে — ধারণা একই।"))

API_APP = '''
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

class Product {
  Product.fromJson(Map<String, dynamic> j) : name = j['name'] as String, price = j['price'] as int;
  final String name;
  final int price;
}

class ProductApi {
  ProductApi(this.client, {this.baseUrl = 'https://api.example.com'});
  final http.Client client;
  final String baseUrl;

  Future<List<Product>> list() async {
    final res = await client.get(Uri.parse('$baseUrl/api/v1/products'));
    if (res.statusCode != 200) throw Exception('Server error ${res.statusCode}');
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    return (body['data'] as List).map((j) => Product.fromJson(j as Map<String, dynamic>)).toList();
  }
}

// ডেমো: আসল app-এ লিখুন ProductApi(http.Client(), baseUrl: 'https://আপনার-api')
final demoApi = ProductApi(MockClient((req) async => http.Response(
    jsonEncode({'data': [{'name': 'Redmi 13', 'price': 17500}, {'name': 'Galaxy A15', 'price': 21000}, {'name': 'Vivo Y28', 'price': 18000}]}),
    200, headers: {'content-type': 'application/json; charset=utf-8'})));

void main() => runApp(const App());

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: Colors.green),
        home: ProductsPage(api: demoApi),
      );
}

class ProductsPage extends StatefulWidget {
  const ProductsPage({super.key, required this.api});
  final ProductApi api;

  @override
  State<ProductsPage> createState() => _ProductsPageState();
}

class _ProductsPageState extends State<ProductsPage> {
  late final Future<List<Product>> _future = widget.api.list();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('API থেকে Products')),
      body: FutureBuilder<List<Product>>(
        future: _future,
        builder: (context, snap) {
          if (snap.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snap.hasError) return Center(child: Text('ভুল: ${snap.error}'));
          return ListView(
            children: [
              for (final p in snap.data!) ListTile(leading: const Icon(Icons.cloud_done), title: Text(p.name), trailing: Text('৳${p.price}')),
            ],
          );
        },
      ),
    );
  }
}
'''

c.lesson("API থেকে data: FutureBuilder",
    say("<code>FutureBuilder</code> একটা Future দেখে তিন অবস্থা আঁকে: লোড হচ্ছে, ভুল, data। API-টা Laravel বা এই সাইটের Rust Shop API-র মতো <code>{\"data\": [...]}</code> দেয়।"),
    app(API_APP),
    points("<code>late final _future = ...</code> — Future একবারই বানাই; <code>build()</code>-এর ভিতরে বানালে প্রতি redraw-এ নতুন request যেত",
           "Screenshot-এর জন্য <code>MockClient</code> — নকল server; আসল app-এ <code>http.Client()</code>",
           "Android-এ internet permission আর emulator থেকে PC-র server-এ যেতে <code>10.0.2.2</code>"),
    warn("Emulator থেকে <code>localhost</code> মানে emulator নিজেই, আপনার PC না। Laravel <code>php artisan serve --host=0.0.0.0</code> চালিয়ে <code>http://10.0.2.2:8000</code> দিন।"))

c.lesson("API-র widget test",
    say("নকল client দিয়ে test: server ছাড়াই নিশ্চিত হই যে JSON থেকে তালিকা ঠিক আঁকা হয়, আর error-এ বার্তা দেখায়।"),
    widget_test('''
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:flutter_app/main.dart';

Widget wrap(ProductApi api) => MaterialApp(home: ProductsPage(api: api));

void main() {
  testWidgets('API data তালিকায় দেখায়', (tester) async {
    final api = ProductApi(MockClient((_) async => http.Response('{"data":[{"name":"Nokia 105","price":2100}]}', 200)));
    await tester.pumpWidget(wrap(api));
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    await tester.pumpAndSettle();
    expect(find.text('Nokia 105'), findsOneWidget);
  });

  testWidgets('server error হলে বার্তা দেখায়', (tester) async {
    final api = ProductApi(MockClient((_) async => http.Response('oops', 500)));
    await tester.pumpWidget(wrap(api));
    await tester.pumpAndSettle();
    expect(find.textContaining('Server error 500'), findsOneWidget);
  });
}
''', API_APP))

c.lesson("Theme আর dark mode",
    say("<code>ColorScheme.fromSeed</code> একটা রং থেকে পুরো রং-পরিবার বানায় (Material 3)। <code>darkTheme</code> + <code>themeMode</code> দিয়ে dark mode।"),
    app(HEAD + '''
class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: const Color(0xFF0D8A4A)),
      darkTheme: ThemeData(colorSchemeSeed: const Color(0xFF0D8A4A), brightness: Brightness.dark),
      themeMode: ThemeMode.dark,
      home: Scaffold(
        appBar: AppBar(title: const Text('Dokani')),
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Card(child: ListTile(leading: Icon(Icons.trending_up), title: Text('আজকের বিক্রি'), trailing: Text('৳১,৭০,৪০০'))),
            const SizedBox(height: 8),
            FilledButton.icon(onPressed: () {}, icon: const Icon(Icons.point_of_sale), label: const Text('POS খুলুন')),
            const SizedBox(height: 8),
            OutlinedButton.icon(onPressed: () {}, icon: const Icon(Icons.inventory_2), label: const Text('Stock দেখুন')),
            const SwitchListTile(value: true, onChanged: null, title: Text('Invoice SMS')),
          ],
        ),
      ),
    );
  }
}
'''),
    tip("<code>themeMode: ThemeMode.system</code> দিলে phone-এর setting অনুযায়ী নিজেই বদলায়।"))

c.lesson("Release: APK, iOS আর web",
    shell("$ flutter build apk --release        # Android\n$ flutter build appbundle            # Play Store\n$ flutter build ios --release        # macOS + Xcode লাগে\n$ flutter build web                  # build/web → যেকোনো hosting"),
    points("App-এর নাম ও icon: <code>flutter_launcher_icons</code> package", "Play Store-এ দিতে signing key (<code>keytool</code>) আর <code>android/key.properties</code>",
           "Web build GitHub Pages বা Netlify-তে দেওয়া যায় — এই tutorial site-এর মতোই static file"),
    php_note("Laravel deploy-এ server লাগে; Flutter app store-এ যায়, আর API থাকে আপনার server-এ।"))

c.lesson("Project: ছোট POS",
    app(HEAD + '''
class Item {
  const Item(this.name, this.price, this.icon);
  final String name;
  final int price;
  final IconData icon;
}

const catalog = [
  Item('Redmi 13', 17500, Icons.smartphone),
  Item('Galaxy A15', 21000, Icons.smartphone),
  Item('Charger', 650, Icons.power),
  Item('Earbuds', 3300, Icons.headphones),
  Item('Cover', 250, Icons.phone_android),
  Item('Glass', 150, Icons.shield),
];

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: const Color(0xFF0D8A4A)),
        home: const Pos(),
      );
}

class Pos extends StatefulWidget {
  const Pos({super.key});

  @override
  State<Pos> createState() => _PosState();
}

class _PosState extends State<Pos> {
  final cart = <Item, int>{};
  int get total => cart.entries.fold(0, (s, e) => s + e.key.price * e.value);

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Rahim Mobile · POS')),
      body: GridView.count(
        crossAxisCount: 2,
        padding: const EdgeInsets.all(12),
        mainAxisSpacing: 10,
        crossAxisSpacing: 10,
        childAspectRatio: 1.35,
        children: [
          for (final item in catalog)
            Card(
              clipBehavior: Clip.antiAlias,
              color: cart.containsKey(item) ? scheme.primaryContainer : null,
              child: InkWell(
                onTap: () => setState(() => cart[item] = (cart[item] ?? 0) + 1),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(item.icon, color: scheme.primary),
                      const Spacer(),
                      Text(item.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                      Text('৳${item.price}${cart[item] != null ? '  × ${cart[item]}' : ''}'),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: FilledButton(
            onPressed: total == 0 ? null : () {},
            style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(56)),
            child: Text('Charge ৳$total', style: const TextStyle(fontSize: 18)),
          ),
        ),
      ),
    );
  }
}
''', actions=["await tester.tap(find.text('Redmi 13')); await tester.pump();",
              "await tester.tap(find.text('Charger')); await tester.pump();",
              "await tester.tap(find.text('Glass')); await tester.pump();",
              "await tester.tap(find.text('Glass')); await tester.pump();"]),
    task("Charge চাপলে একটা <code>AlertDialog</code>-এ invoice দেখান, আর provider দিয়ে cart আলাদা class-এ নিন।"))

c.finish("Flutter শেষ! 🎉",
         "Widget, layout, state, form, navigation, provider আর API — একটা আসল দোকানের app বানানোর সব ধাপ এখন জানা।",
         recap=["সব widget: <code>Scaffold</code>, <code>Column</code>/<code>Row</code>, <code>Container</code>, <code>ListView.builder</code>",
                "<code>StatefulWidget</code> + <code>setState</code>", "<code>Form</code> + <code>validator</code>, <code>TextEditingController</code>",
                "<code>Navigator.push</code>, <code>NavigationBar</code>", "provider: <code>watch</code> আর <code>read</code>",
                "<code>FutureBuilder</code> + <code>http</code>; <code>MockClient</code> দিয়ে widget test"])

if __name__ == "__main__":
    c.build()
