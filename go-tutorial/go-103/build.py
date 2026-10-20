"""Go 103 — goroutine, WaitGroup, channel, select, worker pool, context, Mutex, errgroup, tests, build & cross-compile.
Run: python3 build.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tutorial-kit"))
from kit import Course, code, php_note, points, quiz, say, shell, table, task, tip, warn  # noqa: E402


def go(src, **kw):
    return code(src, "go", **kw)


BILLING = '''
package main

func Vat(amount int) int { return amount * 15 / 100 }

func Discount(amount int) int {
	if amount >= 10000 {
		return amount / 10
	}
	return 0
}

func DeliveryCharge(district string) int {
	if district == "Dhaka" {
		return 60
	}
	return 120
}

func main() {}
'''

c = Course(slug="go-103", title="Go 103 — Goroutine, Channel ও Test", folder=Path(__file__).parent,
           subtitle="Go-র আসল শক্তি: goroutine, channel, select, worker pool, context, Mutex — সাথে table test আর এক binary-তে deploy",
           series="Go 103", next_course=("../go-web-development/index.html", "Go Web Development"))

c.cover("Go 103<br>Goroutine, Channel ও Test",
        "হাজারটা কাজ একসাথে, খুব কম memory-তে — এই কারণেই Docker, Kubernetes আর অসংখ্য API Go-তে লেখা। সাথে Go-র built-in test আর deploy।",
        learn=["goroutine আর WaitGroup", "Channel: goroutine-এর মধ্যে বার্তা", "Buffered channel আর select", "Worker pool",
               "context: timeout আর cancel", "Mutex আর race detector", "Table-driven test", "Cross-compile: Linux binary"],
        need="Go 102।")

c.section("Goroutine")
c.lesson("goroutine আর WaitGroup",
    say("কোনো function-এর আগে <code>go</code> লিখলেই সেটা আলাদা goroutine-এ একসাথে চলে। সব শেষ হওয়া পর্যন্ত অপেক্ষা করতে <code>sync.WaitGroup</code>।"),
    go('''
package main

import (
	"fmt"
	"sync"
	"time"
)

func fetchBranch(name string, ms int) {
	time.Sleep(time.Duration(ms) * time.Millisecond)   // ধরি API call
	fmt.Println("এসেছে:", name)
}

func main() {
	start := time.Now()
	var wg sync.WaitGroup
	for _, b := range []struct {
		name string
		ms   int
	}{{"Gulshan", 300}, {"Mirpur", 100}, {"Uttara", 200}} {
		wg.Go(func() { fetchBranch(b.name, b.ms) })
	}
	wg.Wait()
	fmt.Printf("সময় ~%dms (৬০০ না!)\\n", time.Since(start).Round(100*time.Millisecond).Milliseconds())
}
'''),
    php_note("PHP-তে তিনটা API ডাকলে একটার পর একটা — মোট সময় যোগ হয়। Go-তে একসাথে চলে, সময় লাগে সবচেয়ে ধীরটার সমান।"),
    tip("<code>wg.Go(func)</code> (Go 1.25+) — Add/Done নিজেই করে। পুরনো কোডে দেখবেন <code>wg.Add(1)</code> আর <code>defer wg.Done()</code>।"))

c.section("Channel")
c.lesson("Channel: goroutine-এর মধ্যে বার্তা",
    say("<code>ch &lt;- v</code> পাঠায়, <code>v := &lt;-ch</code> নেয়। পাঠানো আর নেওয়া একে অপরের জন্য অপেক্ষা করে — তাই lock ছাড়াই নিরাপদ।"),
    go('''
package main

import "fmt"

func branchTotal(name string, sales []int, out chan<- string) {
	sum := 0
	for _, s := range sales {
		sum += s
	}
	out <- fmt.Sprintf("%s: %d", name, sum)
}

func main() {
	out := make(chan string)
	go branchTotal("Mirpur", []int{18150, 21300, 18000}, out)
	go branchTotal("Uttara", []int{24150, 3450}, out)

	fmt.Println(<-out)
	fmt.Println(<-out)
}
'''),
    tip("Go-র মূলমন্ত্র: \"memory share করে যোগাযোগ কোরো না; যোগাযোগ করে memory share কোরো।\" — channel দিয়ে data পাঠান।"))

c.lesson("range আর close",
    go('''
package main

import "fmt"

func invoices(n int) <-chan string {
	ch := make(chan string)
	go func() {
		defer close(ch)        // শেষ হলে বন্ধ: range থামবে
		for i := 1; i <= n; i++ {
			ch <- fmt.Sprintf("INV-%04d", 1000+i)
		}
	}()
	return ch
}

func main() {
	for inv := range invoices(3) {
		fmt.Println("নতুন:", inv)
	}
	fmt.Println("সব শেষ")
}
'''))

c.lesson("select: যেটা আগে আসে",
    say("<code>select</code> কয়েকটা channel-এর জন্য একসাথে অপেক্ষা করে — যেটা আগে তৈরি সেটা নেয়। <code>time.After</code> দিয়ে timeout।"),
    go('''
package main

import (
	"fmt"
	"time"
)

func api(name string, ms int) <-chan string {
	ch := make(chan string, 1)
	go func() {
		time.Sleep(time.Duration(ms) * time.Millisecond)
		ch <- name
	}()
	return ch
}

func main() {
	select {
	case r := <-api("bKash", 300):
		fmt.Println("আগে এলো:", r)
	case r := <-api("Nagad", 100):
		fmt.Println("আগে এলো:", r)
	}

	select {
	case r := <-api("slow-sms", 500):
		fmt.Println(r)
	case <-time.After(200 * time.Millisecond):
		fmt.Println("timeout — SMS পরে পাঠাব")
	}
}
'''))

c.lesson("Worker pool",
    say("১০০০টা invoice-এর SMS — একসাথে ১০০০ goroutine না, নির্দিষ্ট কয়েকজন worker। Job channel-এ কাজ, result channel-এ ফল।"),
    go('''
package main

import (
	"fmt"
	"sync"
)

func main() {
	jobs := make(chan int)
	results := make(chan string)
	var wg sync.WaitGroup

	for w := 1; w <= 3; w++ {
		wg.Go(func() {
			for inv := range jobs {
				results <- fmt.Sprintf("worker %d → INV-%d SMS পাঠাল", w, inv)
			}
		})
	}
	go func() {
		for inv := 1001; inv <= 1006; inv++ {
			jobs <- inv
		}
		close(jobs)
	}()
	go func() { wg.Wait(); close(results) }()

	count := 0
	for range results {
		count++
	}
	fmt.Println("মোট SMS:", count, "— ৩ জন worker দিয়ে")
}
'''),
    php_note("Laravel-এ <code>php artisan queue:work</code> কয়েকটা চালালে যা হয় — Go-তে এক program-এর ভিতরেই।"))

c.section("Context ও Mutex")
c.lesson("context: timeout আর cancel",
    say("<code>context</code> কাজের সাথে সময়সীমা আর \"বাতিল\" সংকেত বহন করে। User request ছেড়ে দিলে database query-ও থামানো যায় — Go-র প্রতিটি web আর DB library context নেয়।"),
    go('''
package main

import (
	"context"
	"errors"
	"fmt"
	"time"
)

func slowReport(ctx context.Context) (string, error) {
	select {
	case <-time.After(500 * time.Millisecond):
		return "রিপোর্ট তৈরি", nil
	case <-ctx.Done():
		return "", ctx.Err()
	}
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 200*time.Millisecond)
	defer cancel()

	_, err := slowReport(ctx)
	fmt.Println("ফল:", err, "| deadline?", errors.Is(err, context.DeadlineExceeded))

	r, err := slowReport(context.Background())
	fmt.Println("ফল:", r, err)
}
'''))

c.lesson("Mutex: ভাগ করা data",
    say("অনেক goroutine একটা map বা সংখ্যা বদলালে <code>sync.Mutex</code> দিয়ে তালা দিতে হয়। <code>go run -race</code> ভুলে যাওয়া তালা ধরে ফেলে।"),
    go('''
package main

import (
	"fmt"
	"sync"
)

type Stock struct {
	mu  sync.Mutex
	qty map[string]int
}

func (s *Stock) Sell(name string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.qty[name]--
}

func main() {
	s := &Stock{qty: map[string]int{"Charger": 100}}
	var wg sync.WaitGroup
	for range 40 {
		wg.Go(func() { s.Sell("Charger") })
	}
	wg.Wait()
	fmt.Println("বাকি Charger:", s.qty["Charger"])
}
'''),
    warn("Mutex ছাড়া একসাথে map-এ লিখলে Go program নিজেই থামিয়ে দেয়: <code>fatal error: concurrent map writes</code>।"))

c.section("Test ও Deploy")
c.lesson("Table-driven test",
    say("Go-তে test framework আলাদা install করতে হয় না: <code>_test.go</code> file, <code>func TestXxx(t *testing.T)</code>, আর <code>go test</code>। প্রচলিত ধরন হলো table-driven — অনেক case একটা table-এ।"),
    code(BILLING, "go", run=False, file="main.go"),
    go('''
package main

import "testing"

func TestDiscount(t *testing.T) {
	cases := []struct {
		name   string
		amount int
		want   int
	}{
		{"১০ হাজারের কম", 9999, 0},
		{"ঠিক ১০ হাজার", 10000, 1000},
		{"২০ হাজার", 20000, 2000},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			if got := Discount(tc.amount); got != tc.want {
				t.Errorf("Discount(%d) = %d, চাই %d", tc.amount, got, tc.want)
			}
		})
	}
}

func TestVat(t *testing.T) {
	if Vat(1000) != 150 {
		t.Fatal("VAT ১৫% হওয়ার কথা")
	}
}
''', test=True, app=BILLING, file="main_test.go"),
    php_note("Pest-এর dataset (<code>-&gt;with([...])</code>)-এর মতো। <code>go test ./...</code> পুরো project-এর সব test চালায়।"))

c.lesson("Test ব্যর্থ হলে",
    go('''
package main

import "testing"

func TestDelivery(t *testing.T) {
	if got := DeliveryCharge("Dhaka"); got != 60 {
		t.Errorf("Dhaka: %d, চাই 60", got)
	}
	if got := DeliveryCharge("Gazipur"); got != 60 {
		t.Errorf("Gazipur: %d, চাই 60 (নতুন নিয়ম, কোড পুরনো)", got)
	}
}
''', test=True, app=BILLING, panic=True, file="main_test.go"))

c.lesson("go vet, fmt আর race",
    table(["Command", "কাজ", "PHP-তে"], [
        ["<code>gofmt -w .</code> / <code>go fmt ./...</code>", "কোড একরকম সাজায় — তর্কের সুযোগ নেই", "Pint"],
        ["<code>go vet ./...</code>", "সন্দেহজনক কোড ধরে", "PHPStan"], ["<code>go test -race ./...</code>", "Data race ধরে", "—"],
        ["<code>go test -cover ./...</code>", "কত শতাংশ কোড test-এ", "<code>--coverage</code>"],
        ["<code>golangci-lint run</code>", "অনেক linter একসাথে", "Larastan + Rector"]]),
    tip("Editor-এ save করলেই gofmt চলুক (VS Code Go extension নিজেই করে)। এই কোর্সের সব Go কোডও gofmt দিয়ে সাজানো।"))

c.lesson("Build আর cross-compile",
    say("Go এক command-এ যেকোনো OS-এর binary বানায় — Mac থেকে Linux server-এর জন্য। Binary-তে সব আছে, server-এ Go install করতে হয় না।"),
    shell("$ go build -o shop ./cmd/api\n$ GOOS=linux GOARCH=amd64 go build -o shop-linux ./cmd/api\n$ GOOS=windows GOARCH=amd64 go build -o shop.exe ./cmd/api\n$ ls -lh shop-linux\n$ scp shop-linux server:/opt/shop/",
          out="-rwxr-xr-x  1 rahim  staff   9.8M Oct 21 12:00 shop-linux"),
    php_note("PHP deploy-এ server-এ PHP, extension, Composer লাগে। Go-তে একটা file কপি করলেই শেষ — Docker image-ও কয়েক MB (DevOps কোর্সে দেখব)।"))

c.lesson("Project: সব শাখার রিপোর্ট একসাথে",
    go('''
package main

import (
	"context"
	"fmt"
	"slices"
	"sync"
	"time"
)

type Report struct {
	Branch string
	Total  int
	Err    error
}

func fetch(ctx context.Context, branch string, ms int, sales []int) Report {
	select {
	case <-time.After(time.Duration(ms) * time.Millisecond):
		sum := 0
		for _, s := range sales {
			sum += s
		}
		return Report{Branch: branch, Total: sum}
	case <-ctx.Done():
		return Report{Branch: branch, Err: ctx.Err()}
	}
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 250*time.Millisecond)
	defer cancel()

	branches := map[string]struct {
		ms    int
		sales []int
	}{
		"Mirpur":  {100, []int{18150, 2100, 21300}},
		"Uttara":  {150, []int{24150, 3450}},
		"Gulshan": {400, []int{48000, 21650}}, // খুব ধীর
	}

	var mu sync.Mutex
	var reports []Report
	var wg sync.WaitGroup
	for name, b := range branches {
		wg.Go(func() {
			r := fetch(ctx, name, b.ms, b.sales)
			mu.Lock()
			reports = append(reports, r)
			mu.Unlock()
		})
	}
	wg.Wait()

	slices.SortFunc(reports, func(a, b Report) int { return b.Total - a.Total })
	for _, r := range reports {
		if r.Err != nil {
			fmt.Printf("%-8s সময় শেষ (%v)\\n", r.Branch, r.Err)
			continue
		}
		fmt.Printf("%-8s ৳%d\\n", r.Branch, r.Total)
	}
}
'''),
    task("<code>Report</code> গুলো channel দিয়ে সংগ্রহ করুন (Mutex ছাড়া), আর একটা test লিখুন যেখানে timeout ১ সেকেন্ড হলে তিন শাখাই আসে।"))

c.finish("Go 103 শেষ! 🎉",
         "Goroutine, channel, context আর test — Go-র শক্তির জায়গাগুলো এখন হাতে। এবার এগুলো দিয়ে web API।",
         recap=["<code>go f()</code> + <code>WaitGroup</code>", "Channel: পাঠানো/নেওয়া, <code>close</code>, <code>range</code>",
                "<code>select</code> + <code>time.After</code> = timeout", "Worker pool দিয়ে নিয়ন্ত্রিত concurrency",
                "<code>context</code> সব জায়গায়; ভাগ করা data-য় <code>Mutex</code>", "Table-driven test, cross-compile"])

if __name__ == "__main__":
    c.build()
