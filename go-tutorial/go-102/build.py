"""Go 102 — struct, method, pointer, embedding, interface, type switch, generics, error wrapping, JSON, package layout.
Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402


def go(src, **kw):
    return code(src, "go", **kw)


c = Course(slug="go-102", title="Go 102 — Struct, Interface ও Package", folder=Path(__file__).parent,
           subtitle="Class ছাড়াই object-oriented: struct, method, pointer, embedding, interface, generic, error wrapping, JSON আর package",
           series="Go 102", next_course=("../go-103/index.html", "Go 103 — Goroutine, Channel ও Test"))

c.cover("Go 102<br>Struct, Interface ও Package",
        "Go-তে class নেই — আছে struct আর method। Inheritance নেই — আছে embedding আর interface। শুনতে অদ্ভুত, কিন্তু কোড অনেক সরল হয়।",
        learn=["struct আর method", "Value বনাম pointer receiver", "Embedding: inheritance-এর বদলে", "Interface: নিজে থেকেই মেলে",
               "Type switch আর Stringer", "Generic function ও type", "errors.Is, errors.As, %w", "JSON tag আর package সাজানো"],
        need="Go 101।")

c.section("Struct")
c.lesson("struct আর method",
    go('''
package main

import "fmt"

type Product struct {
	Name  string
	Price int
	Stock int
}

func (p Product) StockValue() int {
	return p.Price * p.Stock
}

func main() {
	p := Product{Name: "Redmi 13", Price: 17500, Stock: 5}
	fmt.Println(p.Name, p.StockValue())
	fmt.Printf("%+v\\n", p)
}
'''),
    php_note("<code>class Product { public string $name; ... public function stockValue() }</code> — Go-তে data (<code>struct</code>) আর method আলাদা লেখা; <code>(p Product)</code> হলো PHP-র <code>$this</code>।"),
    tip("বড় হাতের অক্ষরে শুরু নাম (<code>Name</code>, <code>StockValue</code>) package-এর বাইরে দেখা যায় = public। ছোট হাতের = private।"))

c.lesson("Pointer receiver: নিজেকে বদলানো",
    say("Value receiver <code>(p Product)</code> কপি পায় — বদলালে আসলটা বদলায় না। বদলাতে চাইলে pointer receiver <code>(p *Product)</code>।"),
    go('''
package main

import "fmt"

type Product struct {
	Name  string
	Stock int
}

func (p Product) SellCopy(qty int) { p.Stock -= qty }    // কপি বদলাল
func (p *Product) Sell(qty int)    { p.Stock -= qty }    // আসলটা বদলাল

func main() {
	p := Product{Name: "Vivo Y28", Stock: 4}
	p.SellCopy(1)
	fmt.Println("SellCopy-এর পর:", p.Stock)
	p.Sell(1)
	fmt.Println("Sell-এর পর:", p.Stock)
}
'''),
    php_note("PHP object সবসময় handle হিসেবে যায় (তাই বদলায়)। Go-তে struct ডিফল্টভাবে কপি হয় — বদলাতে <code>*</code> (pointer) লাগে।"))

c.lesson("Constructor function",
    say("Go-তে constructor নেই — প্রথা হলো <code>NewXxx</code> function, যা validation করে pointer ফেরত দেয়।"),
    go('''
package main

import (
	"errors"
	"fmt"
)

type Customer struct {
	Name  string
	Phone string
	Due   int
}

func NewCustomer(name, phone string) (*Customer, error) {
	if len(phone) != 11 {
		return nil, errors.New("ফোন নম্বর ১১ সংখ্যার হতে হবে")
	}
	return &Customer{Name: name, Phone: phone}, nil
}

func main() {
	c, err := NewCustomer("Karim", "01711000001")
	fmt.Println(c, err)
	_, err = NewCustomer("Nusrat", "0181")
	fmt.Println(err)
}
'''))

c.lesson("Embedding: inheritance-এর বদলে",
    say("একটা struct-এর ভিতরে আরেকটা struct নাম ছাড়া বসালে তার field আর method সরাসরি পাওয়া যায় — \"is-a\" না, \"has-a\"।"),
    go('''
package main

import (
	"fmt"
	"time"
)

type Timestamps struct {
	CreatedAt time.Time
}

func (t *Timestamps) Touch() { t.CreatedAt = time.Date(2026, 10, 21, 10, 30, 0, 0, time.UTC) }

type Customer struct {
	Timestamps          // embedded
	Name       string
}

func main() {
	c := Customer{Name: "Karim"}
	c.Touch()                       // Timestamps-এর method সরাসরি
	fmt.Println(c.Name, c.CreatedAt.Format("2006-01-02 15:04"))
}
'''),
    php_note("Laravel model-এর trait (<code>use HasTimestamps;</code>)-এর মতো কাজ করে।"),
    tip("Go-তে তারিখের format লেখা হয় একটা নির্দিষ্ট তারিখ দিয়ে: <code>2006-01-02 15:04:05</code> (১-২-৩-৪-৫-৬)।"))

c.section("Interface")
c.lesson("Interface: নিজে থেকেই মেলে",
    say("Go-তে <code>implements</code> লেখা লাগে না। কোনো type-এর interface-এর সব method থাকলেই সে ঐ interface — একে বলে implicit interface।"),
    go('''
package main

import "fmt"

type Payable interface {
	Amount() int
	Label() string
}

type Invoice struct{ No, Total int }
type ServiceBill struct{ Parts, Labour int }

func (i Invoice) Amount() int        { return i.Total }
func (i Invoice) Label() string      { return fmt.Sprintf("Invoice #%d", i.No) }
func (s ServiceBill) Amount() int    { return s.Parts + s.Labour }
func (s ServiceBill) Label() string  { return "Service" }

func main() {
	items := []Payable{Invoice{101, 23500}, ServiceBill{1800, 500}}
	total := 0
	for _, it := range items {
		fmt.Printf("%-13s %6d\\n", it.Label(), it.Amount())
		total += it.Amount()
	}
	fmt.Println("মোট:", total)
}
'''),
    php_note("PHP-তে <code>class Invoice implements Payable</code> লিখতে হয়। Go-তে লেখার দরকারই নেই — test-এ fake বানানো খুব সহজ।"))

c.lesson("Stringer আর type switch",
    say("<code>String() string</code> method থাকলে <code>fmt</code> সেটা দিয়েই প্রিন্ট করে (PHP-র <code>__toString</code>)। <code>switch v := x.(type)</code> দিয়ে আসল type দেখা।"),
    go('''
package main

import "fmt"

type Taka int

func (t Taka) String() string { return fmt.Sprintf("৳%d", int(t)) }

func describe(x any) string {
	switch v := x.(type) {
	case Taka:
		return "টাকা: " + v.String()
	case int:
		return fmt.Sprintf("সংখ্যা %d", v)
	case string:
		return "লেখা: " + v
	case nil:
		return "কিছু নেই"
	default:
		return fmt.Sprintf("অজানা %T", v)
	}
}

func main() {
	fmt.Println(Taka(17500))
	for _, x := range []any{Taka(650), 42, "Redmi", nil, 3.5} {
		fmt.Println(describe(x))
	}
}
'''))

c.section("Generic ও Error")
c.lesson("Generic",
    go('''
package main

import "fmt"

type Number interface{ ~int | ~float64 }

func Sum[T Number](items []T) T {
	var total T
	for _, x := range items {
		total += x
	}
	return total
}

func Filter[T any](items []T, keep func(T) bool) []T {
	var out []T
	for _, x := range items {
		if keep(x) {
			out = append(out, x)
		}
	}
	return out
}

func main() {
	prices := []int{17500, 650, 21000, 250}
	fmt.Println(Sum(prices), Sum([]float64{4.5, 3.9}))
	fmt.Println(Filter(prices, func(p int) bool { return p > 1000 }))
	fmt.Println(Filter([]string{"Dhaka", "Khulna", "Dinajpur"}, func(s string) bool { return s[0] == 'D' }))
}
'''),
    php_note("Laravel Collection-এর <code>filter()</code>/<code>sum()</code> যেকোনো data-তে চলে — Go generic দিয়ে সেটাই, কিন্তু type-নিরাপদ।"))

c.lesson("Error wrapping: %w, errors.Is, errors.As",
    say("<code>fmt.Errorf(\"...: %w\", err)</code> দিয়ে error-এর উপর প্রসঙ্গ যোগ হয়, ভিতরের error হারায় না। পরে <code>errors.Is</code> (নির্দিষ্ট error?) আর <code>errors.As</code> (নির্দিষ্ট type?) দিয়ে খোঁজা যায়।"),
    go('''
package main

import (
	"errors"
	"fmt"
)

var ErrNotFound = errors.New("পাওয়া যায়নি")

type StockError struct {
	Product string
	Have    int
}

func (e *StockError) Error() string { return fmt.Sprintf("%s: আছে মাত্র %d", e.Product, e.Have) }

func findProduct(id int) error {
	if id > 100 {
		return ErrNotFound
	}
	return &StockError{Product: "iPhone 12", Have: 0}
}

func sell(id int) error {
	if err := findProduct(id); err != nil {
		return fmt.Errorf("sell %d: %w", id, err)
	}
	return nil
}

func main() {
	err := sell(999)
	fmt.Println(err, "| not found?", errors.Is(err, ErrNotFound))

	err = sell(4)
	var se *StockError
	if errors.As(err, &se) {
		fmt.Println(err, "| product:", se.Product)
	}
}
'''),
    php_note("PHP-র exception chaining (<code>new Exception('...', 0, $previous)</code>) আর <code>instanceof</code>-এর মতো।"))

c.section("JSON ও Package")
c.lesson("JSON আর struct tag",
    say("Struct-এর field-এর পাশে <code>`json:\"name\"`</code> tag দিয়ে JSON-এর key ঠিক করি। <code>omitempty</code> — ফাঁকা হলে বাদ, <code>-</code> — কখনো না।"),
    go('''
package main

import (
	"encoding/json"
	"fmt"
)

type Product struct {
	ID       int      `json:"id"`
	Name     string   `json:"name"`
	Price    int      `json:"price"`
	Colors   []string `json:"colors,omitempty"`
	CostPrice int     `json:"-"`
}

func main() {
	p := Product{ID: 7, Name: "Redmi 13", Price: 17500, CostPrice: 15800}
	out, _ := json.Marshal(p)
	fmt.Println(string(out))

	var in Product
	err := json.Unmarshal([]byte(`{"id":2,"name":"Galaxy A15","price":21000,"colors":["Blue"]}`), &in)
	fmt.Printf("%+v %v\\n", in, err)

	err = json.Unmarshal([]byte(`{"id":"two"}`), &in)
	fmt.Println(err)
}
'''),
    php_note("<code>json_encode()</code> আর Laravel model-এর <code>$hidden = ['cost_price']</code> — Go-তে <code>`json:\"-\"`</code>।"))

c.lesson("Package আর module সাজানো",
    say("একটা folder = একটা package। <code>go.mod</code> module-এর নাম আর dependency রাখে (<code>composer.json</code>)। বাইরে ব্যবহার করতে নাম বড় হাতের অক্ষরে।"),
    code('''
shop/
├── go.mod                  module github.com/rahim/shop
├── cmd/
│   └── api/
│       └── main.go         package main — চালানোর জায়গা
├── internal/               শুধু এই module ব্যবহার করতে পারে
│   ├── product/
│   │   ├── product.go      package product
│   │   └── product_test.go
│   └── store/
│       └── sqlite.go       package store
└── README.md
''', "text", run=False, label="Folder structure"),
    code('''
package main

import (
	"fmt"

	"github.com/rahim/shop/internal/product"
)

func main() {
	p := product.New("Redmi 13", 17500)
	fmt.Println(p.Name)
}
''', "go", run=False, file="cmd/api/main.go"),
    shell("$ go get github.com/google/uuid@latest     # composer require\n$ go mod tidy                                # অপ্রয়োজনীয় সরায়\n$ go build ./...\n$ go run ./cmd/api"),
    tip("<code>internal/</code> folder-এর package বাইরের project import করতে পারে না — Go নিজেই এই নিয়ম মানায়।"))

c.lesson("Project: Inventory",
    go('''
package main

import (
	"errors"
	"fmt"
	"slices"
	"strings"
)

type Product struct {
	Name  string
	Price int
	Stock int
}

type Inventory struct{ items map[string]*Product }

var ErrNoStock = errors.New("স্টক নেই")

func NewInventory() *Inventory { return &Inventory{items: map[string]*Product{}} }

func (inv *Inventory) Add(name string, price, qty int) {
	if p, ok := inv.items[name]; ok {
		p.Stock += qty
		return
	}
	inv.items[name] = &Product{name, price, qty}
}

func (inv *Inventory) Sell(name string, qty int) (int, error) {
	p, ok := inv.items[name]
	if !ok {
		return 0, fmt.Errorf("%q: পাওয়া যায়নি", name)
	}
	if p.Stock < qty {
		return 0, fmt.Errorf("%s (আছে %d): %w", name, p.Stock, ErrNoStock)
	}
	p.Stock -= qty
	return p.Price * qty, nil
}

func (inv *Inventory) Report() string {
	names := make([]string, 0, len(inv.items))
	for n := range inv.items {
		names = append(names, n)
	}
	slices.Sort(names)
	var b strings.Builder
	for _, n := range names {
		p := inv.items[n]
		fmt.Fprintf(&b, "%-12s %3dটা  ৳%d\\n", n, p.Stock, p.Price*p.Stock)
	}
	return b.String()
}

func main() {
	inv := NewInventory()
	inv.Add("Redmi 13", 17500, 5)
	inv.Add("Galaxy A15", 21000, 2)
	inv.Add("Redmi 13", 17500, 1)

	for _, s := range []struct {
		name string
		qty  int
	}{{"Redmi 13", 2}, {"Galaxy A15", 3}, {"Nokia", 1}} {
		if amount, err := inv.Sell(s.name, s.qty); err != nil {
			fmt.Println("✗", err, "| no stock?", errors.Is(err, ErrNoStock))
		} else {
			fmt.Println("✓", s.name, "বিক্রি:", amount)
		}
	}
	fmt.Print(inv.Report())
}
'''),
    task("<code>Inventory</code>-কে JSON-এ save আর load করুন (<code>encoding/json</code> + <code>os.WriteFile</code>)।"))

c.finish("Go 102 শেষ! 🎉",
         "Struct, interface, generic আর error wrapping — Go-র গঠন জানা হলো। এবার Go-র আসল শক্তি: goroutine আর channel।",
         recap=["struct + method; বদলাতে pointer receiver", "<code>NewXxx</code> constructor প্রথা", "Embedding = has-a, inheritance না",
                "Interface নিজে থেকেই মেলে", "<code>%w</code>, <code>errors.Is</code>, <code>errors.As</code>", "JSON tag; বড় হাতের নাম = public"])

if __name__ == "__main__":
    c.build()
