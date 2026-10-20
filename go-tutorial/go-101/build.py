"""Go 101 — variables, types, strings, if/for/switch, functions, errors, slices, maps, defer.
Every Go block is run with `go run` (go 1.27). Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402


def go(src, **kw):
    return code(src, "go", **kw)


def php(src, label="PHP-তে তুলনা"):
    return code(src, "php", label=label)


c = Course(slug="go-101", title="Go 101 — শূন্য থেকে শুরু", folder=Path(__file__).parent,
           subtitle="Variable, type, string, if/for/switch, function, error, slice, map আর defer — PHP-র পাশাপাশি",
           series="Go 101", next_course=("../go-102/index.html", "Go 102 — Struct, Interface ও Package"))

c.cover("Go 101<br>শূন্য থেকে শুরু",
        "Go (Golang) — Google-এর বানানো সহজ, দ্রুত ভাষা। Docker, Kubernetes, Grafana, Terraform — DevOps-এর প্রায় সব টুল Go-তে লেখা। PHP জানলে Go শেখা খুবই সহজ, কারণ ভাষাটা ছোট।",
        learn=["Go কেন, install আর go run", "var, := আর zero value", "Type আর type conversion", "String, byte আর rune (বাংলা)",
               "if, for, switch", "Function আর একাধিক return", "error: Go-র নিজস্ব ধরন", "Slice, map, defer"],
        need="সাধারণ programming (PHP যথেষ্ট)।")

c.section("শুরু")
c.lesson("Go কেন?",
    table(["", "PHP", "Go"], [
        ["চলে কীভাবে", "Interpreter", "Compile হয়ে একটা binary — server-এ শুধু ঐ file"],
        ["Type", "Dynamic", "Static, কিন্তু <code>:=</code> দিয়ে অনুমান"],
        ["Error", "Exception, try/catch", "Error একটা সাধারণ return মান"],
        ["একসাথে কাজ", "Queue, আলাদা process", "goroutine — হাজার হাজার, খুব হালকা"],
        ["কোথায়", "Web app", "API, CLI, DevOps tool (Docker, Kubernetes)"]]),
    tip("Go ইচ্ছা করে ছোট রাখা — class নেই, exception নেই, inheritance নেই। কম জিনিস শিখতে হয়, সবার কোড একই রকম দেখায়।"))

c.lesson("Install আর Hello, World!",
    shell("$ go version\n$ mkdir hello && cd hello\n$ go mod init hello\n$ go run .", out="go version go1.27.3 darwin/arm64\ngo: creating new go.mod: module hello\nHello, World!"),
    go('''
package main

import "fmt"

func main() {
	fmt.Println("Hello, World!")
	fmt.Println("Go শেখা শুরু হলো")
}
'''),
    points("প্রতিটি file শুরু হয় <code>package</code> দিয়ে; চালানোর program হলো <code>package main</code>",
           "<code>import \"fmt\"</code> — print-এর package", "Statement-এর শেষে <code>;</code> লাগে না"),
    php_note("<code>echo \"Hello, World!\\n\";</code> → <code>fmt.Println(\"Hello, World!\")</code>। <code>go mod init</code> হলো <code>composer init</code>।"))

c.lesson("fmt.Printf: সাজিয়ে প্রিন্ট",
    go('''
package main

import "fmt"

func main() {
	name := "Rahim"
	price := 1250.5
	qty := 3

	fmt.Printf("Customer: %s\\n", name)
	fmt.Printf("Total: %.2f টাকা\\n", price*float64(qty))
	fmt.Printf("[%8s] [%-8s]\\n", "ডানে", "বামে")
	fmt.Printf("%v | %T | %q\\n", qty, price, name)
	line := fmt.Sprintf("%s × %d", name, qty)
	fmt.Println(line)
}
'''),
    php_note("PHP-র <code>printf()</code>/<code>sprintf()</code> একই — <code>%v</code> হলো Go-র \"যেকোনো মান\", <code>%T</code> type দেখায়।"))

c.section("Variable ও Type")
c.lesson("var, := আর zero value",
    say("<code>:=</code> দিয়ে variable বানানো আর মান দেওয়া একসাথে (শুধু function-এর ভিতরে)। মান না দিলে Go নিজেই \"zero value\" বসায় — null নেই।"),
    go('''
package main

import "fmt"

func main() {
	var shop string = "Rahim Mobile"
	balance := 500          // type অনুমান: int
	balance += 200

	var stock int           // মান দিইনি → 0
	var note string         // → ""
	var paid bool           // → false

	fmt.Println(shop, balance)
	fmt.Printf("stock=%d note=%q paid=%t\\n", stock, note, paid)
}
'''),
    php_note("PHP-তে মান না দেওয়া variable <code>null</code>/undefined। Go-তে int হলে 0, string হলে \"\" — কখনো \"নেই\" হয় না।"))

c.lesson("ব্যবহার না করা variable = error",
    say("Go কঠোর: variable বানিয়ে ব্যবহার না করলে, বা package import করে ব্যবহার না করলে — compile হবে না। কোড পরিষ্কার থাকে।"),
    go('''
package main

import (
	"fmt"
	"os"
)

func main() {
	total := 1500
	fmt.Println("হিসাব")
}
''', err="declared and not used"),
    tip("সাময়িকভাবে কিছু উপেক্ষা করতে <code>_</code> ব্যবহার করুন: <code>_ = total</code>।"))

c.lesson("Type আর conversion",
    say("আলাদা type মেশানো যায় না — নিজে বদলাতে হয়: <code>float64(qty)</code>। Integer ভাগে দশমিক বাদ।"),
    go('''
package main

import (
	"fmt"
	"strconv"
)

func main() {
	a, b := 7, 2
	fmt.Println(a/b, a%b, float64(a)/float64(b))

	price := 17500
	vat := float64(price) * 0.15
	fmt.Printf("VAT: %.0f\\n", vat)

	n, _ := strconv.Atoi("250")
	s := strconv.Itoa(price)
	fmt.Println(n+1, s+" টাকা")
}
'''),
    warn("<code>string(65)</code> দিলে \"65\" না, \"A\" হয় (অক্ষর কোড)! সংখ্যাকে লেখা বানাতে সবসময় <code>strconv.Itoa</code> বা <code>fmt.Sprint</code>।"))

c.lesson("const আর iota",
    go('''
package main

import "fmt"

const VatPercent = 15
const ShopName = "Rahim Mobile"

type Status int

const (
	Pending Status = iota   // 0
	Paid                    // 1
	Returned                // 2
)

func main() {
	fmt.Println(ShopName, VatPercent)
	fmt.Println(Pending, Paid, Returned)
}
'''),
    php_note("<code>iota</code> নিজে থেকে ০, ১, ২ ... বসায় — PHP enum-এর মতো ক্রমিক মানের জন্য।"))

c.lesson("String, byte আর rune",
    say("Go string হলো UTF-8 byte। <code>len()</code> byte গোনে। অক্ষর (rune) ধরে চলতে <code>for range</code> বা <code>utf8.RuneCountInString</code>।"),
    go('''
package main

import (
	"fmt"
	"strings"
	"unicode/utf8"
)

func main() {
	city := "ঢাকা"
	fmt.Println(len(city), utf8.RuneCountInString(city))
	for i, r := range city {
		fmt.Printf("%d:%c ", i, r)
	}
	fmt.Println()

	model := "  Redmi Note 13  "
	fmt.Println(strings.TrimSpace(model), strings.ToUpper("redmi"), strings.Contains(model, "Note"))
	fmt.Println(strings.Split("Mirpur,Uttara,Gulshan", ","))
}
'''),
    php_note("<code>strlen</code>/<code>mb_strlen</code> → <code>len</code>/<code>utf8.RuneCountInString</code>; <code>explode</code> → <code>strings.Split</code>।"))

c.section("Control flow")
c.lesson("if — ছোট statement সহ",
    say("শর্তের চারপাশে bracket নেই, কিন্তু <code>{}</code> বাধ্যতামূলক। <code>if</code>-এর আগে ছোট statement লেখা যায়। Ternary (<code>?:</code>) নেই।"),
    go('''
package main

import "fmt"

func main() {
	amount := 1800
	if amount >= 1500 {
		fmt.Println("ফ্রি ডেলিভারি")
	} else if amount >= 1000 {
		fmt.Println("ডেলিভারি ৩০")
	} else {
		fmt.Println("ডেলিভারি ৬০")
	}

	if discount := amount / 10; discount > 100 {
		fmt.Println("ছাড়:", discount)
	}
}
'''))

c.lesson("for — Go-র একমাত্র loop",
    say("<code>while</code> নেই, <code>foreach</code> নেই — সব <code>for</code>। <code>range</code> দিয়ে slice/map/string ঘোরা।"),
    go('''
package main

import "fmt"

func main() {
	for i := 1; i <= 3; i++ {
		fmt.Printf("7 × %d = %d\\n", i, 7*i)
	}

	seconds := 3
	for seconds > 0 {          // while-এর মতো
		fmt.Print(seconds, "... ")
		seconds--
	}
	fmt.Println()

	for i, city := range []string{"Dhaka", "Khulna", "Sylhet"} {
		fmt.Println(i, city)
	}
}
'''),
    php_note("<code>foreach ($cities as $i =&gt; $city)</code> → <code>for i, city := range cities</code>।"))

c.lesson("switch",
    say("<code>break</code> লিখতে হয় না — মিল হলে শুধু সেই case চলে। শর্ত ছাড়া <code>switch</code> লিখলে if-else-এর মতো।"),
    go('''
package main

import "fmt"

func grade(marks int) string {
	switch {
	case marks >= 80:
		return "A+"
	case marks >= 70:
		return "A"
	case marks >= 33:
		return "পাস"
	default:
		return "F"
	}
}

func main() {
	for _, m := range []int{95, 72, 48, 20} {
		fmt.Println(m, grade(m))
	}
	switch day := "Friday"; day {
	case "Friday":
		fmt.Println("ছুটি")
	case "Saturday", "Sunday":
		fmt.Println("কাজের দিন")
	}
}
'''))

c.section("Function ও Error")
c.lesson("Function আর একাধিক return",
    go('''
package main

import "fmt"

func total(price, qty int) int {
	return price * qty
}

func minMax(nums []int) (int, int) {
	lo, hi := nums[0], nums[0]
	for _, n := range nums {
		lo, hi = min(lo, n), max(hi, n)
	}
	return lo, hi
}

func main() {
	fmt.Println(total(450, 4))
	lo, hi := minMax([]int{18150, 2100, 48000, 1300})
	fmt.Println("ছোট", lo, "বড়", hi)
}
'''),
    php_note("PHP-তে কয়েকটা মান ফেরত দিতে array লাগে; Go সরাসরি <code>(int, int)</code> ফেরত দেয়।"))

c.lesson("error: Go-র নিয়ম",
    say("ব্যর্থ হতে পারে এমন function শেষে একটা <code>error</code> ফেরত দেয়। ডাকার পরেই <code>if err != nil</code> — Go কোডে এটা সবচেয়ে বেশি দেখবেন।"),
    go('''
package main

import (
	"errors"
	"fmt"
	"strconv"
)

func withdraw(balance, amount int) (int, error) {
	if amount > balance {
		return balance, fmt.Errorf("ব্যালেন্স কম: আছে %d, চাইছেন %d", balance, amount)
	}
	return balance - amount, nil
}

var ErrZero = errors.New("০ টাকা তোলা যায় না")

func main() {
	if _, err := strconv.Atoi("দুইশো"); err != nil {
		fmt.Println("ভুল:", err)
	}
	left, err := withdraw(1000, 5000)
	if err != nil {
		fmt.Println("ব্যর্থ:", err)
	}
	fmt.Println("বাকি:", left, ErrZero)
}
'''),
    php_note("PHP-র <code>throw</code>/<code>catch</code> নেই। Rust-এর <code>Result</code>-এর মতো — error উপেক্ষা করা কঠিন, কারণ চোখের সামনে থাকে।"))

c.lesson("panic: সত্যিকারের অপ্রত্যাশিত ভুল",
    say("Slice-এর বাইরে index বা nil map-এ লেখা — Go program থামায় (panic)। সাধারণ ভুলে panic না, error ব্যবহার করুন।"),
    go('''
package main

import "fmt"

func main() {
	sales := []int{1200, 3400, 2100}
	i := len(sales) + 2
	fmt.Println("চেষ্টা করছি index", i)
	fmt.Println(sales[i])
}
''', panic=True))

c.section("Slice, Map, defer")
c.lesson("Slice: বাড়ানো যায় এমন list",
    go('''
package main

import (
	"fmt"
	"slices"
	"strings"
)

func main() {
	brands := []string{"Samsung", "Xiaomi"}
	brands = append(brands, "Walton", "Vivo")

	fmt.Println(brands, len(brands))
	fmt.Println(brands[1:3])                 // index ১ থেকে ২
	fmt.Println(slices.Contains(brands, "Walton"))
	slices.Sort(brands)
	fmt.Println(strings.Join(brands, " | "))
}
'''),
    php_note("<code>$brands[] = 'Walton'</code> → <code>brands = append(brands, \"Walton\")</code> — append নতুন slice ফেরত দেয়, তাই আবার বসাতে হয়।"))

c.lesson("Map আর \"comma ok\"",
    go('''
package main

import "fmt"

func main() {
	stock := map[string]int{
		"Redmi 13":   5,
		"Galaxy A15": 2,
	}
	stock["Vivo Y28"] = 4
	stock["Redmi 13"]--

	qty, ok := stock["Nokia"]
	fmt.Println(qty, ok)                // নেই: 0 false

	delete(stock, "Galaxy A15")
	for name, n := range stock {
		if n > 3 {
			fmt.Println(name, n)
		}
	}
	fmt.Println(len(stock))
}
'''),
    warn("Map-এর <code>range</code>-এর ক্রম প্রতিবার আলাদা হতে পারে। ক্রম লাগলে key নিয়ে <code>slices.Sort</code> করুন।"),
    php_note("<code>$stock['Nokia'] ?? 0</code> আর <code>isset()</code> — Go-তে একসাথে: <code>qty, ok := stock[\"Nokia\"]</code>।"))

c.lesson("defer: শেষে চালাও",
    say("<code>defer</code> দেওয়া কাজ function শেষ হওয়ার ঠিক আগে চলে — file বন্ধ, lock খোলা, connection ফেরত। একাধিক defer উল্টো ক্রমে চলে।"),
    go('''
package main

import "fmt"

func sell() {
	fmt.Println("lock নিলাম")
	defer fmt.Println("lock ছাড়লাম")   // যাই হোক, শেষে চলবে
	defer fmt.Println("log লিখলাম")
	fmt.Println("স্টক কমালাম")
}

func main() {
	sell()
}
'''),
    php_note("PHP-র <code>try { } finally { }</code>-এর কাজ, কিন্তু যেখানে resource খোলেন ঠিক তার পাশেই লেখা যায়।"))

c.lesson("Project: টাকার নোট ভাঙানো",
    go('''
package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func main() {
	notes := []int{1000, 500, 200, 100, 50, 20, 10, 5, 2, 1}
	fmt.Print("কত টাকা ফেরত? ")
	line, _ := bufio.NewReader(os.Stdin).ReadString('\\n')
	amount, err := strconv.Atoi(strings.TrimSpace(line))
	if err != nil {
		fmt.Println("সংখ্যা লিখুন")
		return
	}
	fmt.Println()
	total := 0
	for _, note := range notes {
		if count := amount / note; count > 0 {
			fmt.Printf("%5d টাকা × %d\\n", note, count)
			amount %= note
			total += count
		}
	}
	fmt.Println("মোট নোট:", total)
}
''', stdin="2785\n"),
    task("একটা <code>map[int]int</code>-এ রাখুন কোন নোট কয়টা, আর ভুল input-এ আবার জিজ্ঞেস করুন (<code>for</code> loop)।"))

c.finish("Go 101 শেষ! 🎉",
         "Go-র ভিত্তি তৈরি। এবার struct, method, interface আর package — Go-তে \"class\" ছাড়াই কীভাবে বড় কোড সাজানো হয়।",
         recap=["<code>:=</code> আর zero value — null নেই", "ব্যবহার না করা variable/import = compile error",
                "<code>for</code>-ই একমাত্র loop, <code>range</code> দিয়ে ঘোরা", "একাধিক return; শেষেরটা <code>error</code>",
                "<code>if err != nil</code> — Go-র প্রতিদিনের লাইন", "Slice + <code>append</code>, map + comma-ok, <code>defer</code>"])

if __name__ == "__main__":
    c.build()
