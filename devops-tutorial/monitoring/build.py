"""Monitoring — metrics/logs/traces, instrumenting the Go API with Prometheus client, a real Prometheus scraping it,
PromQL (promtool query), alert rules with unit tests, and a provisioned Grafana dashboard screenshotted headlessly.
Everything runs natively (no VM). Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
import devops_env  # noqa: E402
from kit import Course, Html, code, php_note, points, quiz, say, shell, table, task, term, tip, warn  # noqa: E402

GRAFANA = ROOT / "tutorial-kit/.cache/grafana"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SHOT = HERE / "shots/grafana-dashboard.png"

c = Course(slug="monitoring", title="Monitoring — Prometheus ও Grafana", folder=HERE,
           subtitle="Deploy-এর পর app কেমন চলছে: metric, PromQL, alert আর Grafana dashboard — আসল Prometheus আর Grafana চালিয়ে",
           series="Monitoring", shell=True, shell_env={**devops_env.docker_env(), "GRAFANA_HOME": str(GRAFANA)},
           next_course=("../infrastructure-as-code/index.html", "Infrastructure as Code — OpenTofu"))


def _cleanup():
    import subprocess
    for pat in ("shop-metrics", "prometheus --config.file", "grafana server"):
        subprocess.run(["pkill", "-f", pat], capture_output=True)


c.shell_setup = _cleanup
c.shell_teardown = _cleanup

c.cover("Monitoring<br>Prometheus ও Grafana",
        "Deploy শেষ মানে কাজ শেষ না। কয়টা request আসছে, কতটা ধীর, কত error, কখন disk ভরবে — এগুলো দেখতে আর সময়মতো সতর্ক হতে monitoring। এই কোর্সে আসল Prometheus আর Grafana চালানো হয়েছে।",
        learn=["Metric, log আর trace", "Counter, gauge, histogram", "Go app-এ metric যোগ", "Prometheus দিয়ে scrape",
               "PromQL: rate, sum, p95", "Alert rule আর তার test", "Grafana dashboard", "Laravel, server আর Kubernetes monitoring"],
        need="Go Web Development (Go app), DevOps 101।")

c.section("ধারণা")
c.lesson("Observability-র তিন স্তম্ভ",
    table(["", "কী", "প্রশ্ন", "টুল"], [
        ["Metric", "সময়ের সাথে সংখ্যা", "এখন সেকেন্ডে কত request? কত শতাংশ error?", "Prometheus"],
        ["Log", "ঘটনার লেখা", "INV-1007-এ ঠিক কী ভুল হলো?", "Loki, ELK"],
        ["Trace", "একটা request-এর পুরো পথ", "কোন অংশে ৩ সেকেন্ড গেল — DB না API?", "Tempo, Jaeger"]]),
    php_note("Laravel-এর Telescope একটা request-এর ভিতর দেখায়; Prometheus দেখায় হাজার request-এর সামগ্রিক ছবি। দুটোই লাগে।"))

c.lesson("Prometheus কীভাবে কাজ করে",
    points("App একটা <code>/metrics</code> URL-এ নিজের সংখ্যাগুলো লেখা আকারে দেখায়", "Prometheus কয়েক সেকেন্ড পরপর সেটা পড়ে (<b>scrape</b>, pull model)",
           "প্রতিটি সংখ্যা একটা <b>time series</b>: নাম + label (<code>status=\"500\"</code>)", "PromQL দিয়ে প্রশ্ন, Grafana দিয়ে ছবি, Alertmanager দিয়ে সতর্কবার্তা"),
    table(["Type", "কী", "উদাহরণ"], [
        ["Counter", "শুধু বাড়ে", "<code>http_requests_total</code>"], ["Gauge", "বাড়ে-কমে", "স্টকে product, memory"],
        ["Histogram", "মানের বণ্টন (bucket)", "response time → p95"]]))

c.section("Instrument ও Scrape")
c.lesson("Go app-এ metric যোগ",
    say("<code>prometheus/client_golang</code> দিয়ে তিন ধরনের metric। Middleware প্রতিটি request গুনে আর সময় মাপে।"),
    code('''
package main

import (
	"fmt"
	"log"
	"math/rand/v2"
	"net/http"
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	requests = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "shop_http_requests_total", Help: "HTTP requests by route and status.",
	}, []string{"route", "status"})
	latency = promauto.NewHistogramVec(prometheus.HistogramOpts{
		Name: "shop_http_request_duration_seconds", Help: "Request latency.",
		Buckets: []float64{0.01, 0.05, 0.1, 0.25, 0.5, 1},
	}, []string{"route"})
	stock = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "shop_products_in_stock", Help: "Products currently in stock.",
	})
)

type rec struct {
	http.ResponseWriter
	code int
}

func (r *rec) WriteHeader(c int) { r.code = c; r.ResponseWriter.WriteHeader(c) }

func observe(route string, h http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		start, rw := time.Now(), &rec{w, 200}
		h(rw, r)
		latency.WithLabelValues(route).Observe(time.Since(start).Seconds())
		requests.WithLabelValues(route, strconv.Itoa(rw.code)).Inc()
	}
}

func main() {
	stock.Set(42)
	mux := http.NewServeMux()
	mux.HandleFunc("GET /products", observe("/products", func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(time.Duration(rand.IntN(60)) * time.Millisecond)
		fmt.Fprintln(w, `[{"name":"Redmi 13"}]`)
	}))
	mux.HandleFunc("POST /checkout", observe("/checkout", func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(time.Duration(100+rand.IntN(300)) * time.Millisecond)
		if rand.IntN(10) == 0 {
			http.Error(w, "payment gateway timeout", http.StatusBadGateway)
			return
		}
		stock.Dec()
		fmt.Fprintln(w, `{"ok":true}`)
	}))
	mux.Handle("GET /metrics", promhttp.Handler())
	log.Fatal(http.ListenAndServe("127.0.0.1:8097", mux))
}
''', "go", file="shop-metrics/main.go", save=True),
    term('''$ cd shop-metrics && go mod init shop-metrics >/dev/null 2>&1 && go mod tidy >/dev/null 2>&1 && go build -o shop-metrics . && echo "build ✓"
$ ./shop-metrics >/dev/null 2>&1 &
$ sleep 1 && curl -s -o /dev/null localhost:8097/products && curl -s localhost:8097/metrics | grep '^shop_' | head -6
$ cd ..''', timeout=900),
    php_note("Laravel-এ <code>spatie/laravel-prometheus</code> package একই রকম <code>/prometheus</code> endpoint দেয়।"))

c.lesson("Prometheus চালু করা",
    code('''
global:
  scrape_interval: 2s

rule_files:
  - alerts.yml

scrape_configs:
  - job_name: shop-api
    static_configs:
      - targets: ["127.0.0.1:8097"]
        labels:
          env: demo
''', "yaml", file="prometheus.yml", save=True, validate="prometheus"),
    term('''$ prometheus --config.file=prometheus.yml --web.listen-address=127.0.0.1:9097 --storage.tsdb.path=data >prom.log 2>&1 &
$ sleep 4 && curl -s 127.0.0.1:9097/-/ready
$ promtool query instant http://127.0.0.1:9097 'up' '''),
    say("<code>up == 1</code> — Prometheus app-কে খুঁজে পেয়েছে আর পড়তে পারছে। App বন্ধ হলে এটা 0 হবে — সবচেয়ে প্রাথমিক alert।"))

c.section("PromQL")
c.lesson("Traffic পাঠিয়ে প্রশ্ন করি",
    term('''$ for i in $(seq 1 150); do curl -s -o /dev/null localhost:8097/products; done
$ for i in $(seq 1 40); do curl -s -o /dev/null -X POST localhost:8097/checkout & done; wait
$ sleep 5 && promtool query instant http://127.0.0.1:9097 'sum by (route, status) (shop_http_requests_total)' ''', timeout=300),
    points("Counter মোট সংখ্যা রাখে — app restart না হলে শুধু বাড়ে", "<code>sum by (route, status)</code> — label ধরে যোগফল (SQL-এর GROUP BY)"))

c.lesson("rate: প্রতি সেকেন্ডে কত",
    say("মোট সংখ্যার চেয়ে কাজের প্রশ্ন: <b>এখন</b> প্রতি সেকেন্ডে কত request, কত শতাংশ error। <code>rate(x[1m])</code> = শেষ ১ মিনিটে counter যত বেড়েছে ÷ সময়।"),
    term('''$ for i in $(seq 1 60); do curl -s -o /dev/null localhost:8097/products; curl -s -o /dev/null -X POST localhost:8097/checkout; done
$ sleep 3 && promtool query instant http://127.0.0.1:9097 'round(sum by (route) (rate(shop_http_requests_total[1m])), 0.01)'
$ promtool query instant http://127.0.0.1:9097 'round(100 * sum(rate(shop_http_requests_total{status=~"5.."}[1m])) / sum(rate(shop_http_requests_total[1m])), 0.1)' ''', timeout=300),
    php_note("SQL-এর মতো ভাবুন: <code>sum by (route)</code> = <code>GROUP BY route</code>, <code>{status=~\"5..\"}</code> = <code>WHERE status LIKE '5%'</code>।"))

c.lesson("Histogram: p95 response time",
    say("গড় সময় ভুল বোঝায় — ১০০ জনের ৯৫ জন দ্রুত পেলেও ৫ জন খুব ধীর পেতে পারে। <b>p95</b> = ৯৫% request এর চেয়ে দ্রুত।"),
    term('''$ promtool query instant http://127.0.0.1:9097 'round(histogram_quantile(0.95, sum by (le, route) (rate(shop_http_request_duration_seconds_bucket[2m]))), 0.001)'
$ promtool query instant http://127.0.0.1:9097 'shop_products_in_stock' '''),
    say("<code>/products</code> দ্রুত, <code>/checkout</code> ধীর (payment gateway-এর অনুকরণ) — ঠিক যেমন কোডে লেখা। Gauge-এ স্টক কমেছে সফল checkout-এর সমান।"))

c.section("Alert")
c.lesson("Alert rule",
    say("PromQL শর্ত কিছুক্ষণ সত্য থাকলে alert। <code>for: 5m</code> — এক মুহূর্তের ঝাঁকুনিতে রাত ৩টায় ফোন বাজবে না।"),
    code('''
groups:
  - name: shop
    rules:
      - alert: ShopApiDown
        expr: up{job="shop-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Shop API বন্ধ ({{ $labels.instance }})"

      - alert: HighErrorRate
        expr: |
          sum(rate(shop_http_requests_total{status=~"5.."}[5m]))
            / sum(rate(shop_http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "৫%-এর বেশি request ব্যর্থ"

      - alert: LowStock
        expr: shop_products_in_stock < 10
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "স্টক কম: {{ $value }}টা"
''', "yaml", file="alerts.yml", save=True, validate="promrules"))

c.lesson("Alert-এরও test",
    say("<code>promtool test rules</code> নকল data দিয়ে যাচাই করে alert ঠিক সময়ে বাজে কিনা — alert-এর unit test।"),
    code('''
rule_files:
  - alerts.yml
evaluation_interval: 1m
tests:
  - interval: 1m
    input_series:
      - series: 'up{job="shop-api", instance="api-1"}'
        values: "1 1 0 0 0"
    alert_rule_test:
      - eval_time: 2m
        alertname: ShopApiDown
        exp_alerts: []
      - eval_time: 4m
        alertname: ShopApiDown
        exp_alerts:
          - exp_labels:
              severity: critical
              job: shop-api
              instance: api-1
            exp_annotations:
              summary: "Shop API বন্ধ (api-1)"
''', "yaml", file="alerts_test.yml", save=True),
    term("$ promtool test rules alerts_test.yml"),
    tip("Alert পাঠানোর কাজ Alertmanager-এর: Slack, email, Telegram, PagerDuty — একই alert একবারই, দলভিত্তিক, রাতে শুধু critical।"))

c.section("Grafana")
c.lesson("Grafana: dashboard",
    say("Grafana Prometheus থেকে PromQL চালিয়ে graph আঁকে। Datasource আর dashboard <b>provisioning</b> file দিয়ে কোডে রাখা যায় — হাতে click করে বানালে হারিয়ে যায়।"),
    code('''
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    uid: prom
    url: http://127.0.0.1:9097
    isDefault: true
''', "yaml", file="grafana/provisioning/datasources/prom.yml", save=True),
    code('''
apiVersion: 1
providers:
  - name: shop
    type: file
    options:
      path: dashboards
''', "yaml", file="grafana/provisioning/dashboards/shop.yml", save=True, hidden=True),
    code('''
{
  "uid": "shop", "title": "Shop API", "time": {"from": "now-5m", "to": "now"}, "refresh": "",
  "panels": [
    {"type": "stat", "title": "Requests / sec", "gridPos": {"x": 0, "y": 0, "w": 8, "h": 5},
     "datasource": {"uid": "prom"}, "targets": [{"expr": "sum(rate(shop_http_requests_total[1m]))"}],
     "fieldConfig": {"defaults": {"decimals": 1, "unit": "reqps"}}},
    {"type": "stat", "title": "Error %", "gridPos": {"x": 8, "y": 0, "w": 8, "h": 5},
     "datasource": {"uid": "prom"},
     "targets": [{"expr": "100 * sum(rate(shop_http_requests_total{status=~\\"5..\\"}[1m])) / sum(rate(shop_http_requests_total[1m]))"}],
     "fieldConfig": {"defaults": {"decimals": 1, "unit": "percent",
       "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": null}, {"color": "red", "value": 5}]}}}},
    {"type": "stat", "title": "In stock", "gridPos": {"x": 16, "y": 0, "w": 8, "h": 5},
     "datasource": {"uid": "prom"}, "targets": [{"expr": "shop_products_in_stock"}]},
    {"type": "timeseries", "title": "p95 latency by route", "gridPos": {"x": 0, "y": 5, "w": 24, "h": 9},
     "datasource": {"uid": "prom"},
     "targets": [{"expr": "histogram_quantile(0.95, sum by (le, route) (rate(shop_http_request_duration_seconds_bucket[1m])))", "legendFormat": "{{route}}"}],
     "fieldConfig": {"defaults": {"unit": "s"}}}
  ]
}
''', "json", file="grafana/dashboards/shop.json", save=True),
    term(f'''$ for r in $(seq 1 25); do for i in $(seq 1 6); do curl -s -o /dev/null localhost:8097/products; curl -s -o /dev/null -X POST localhost:8097/checkout; done; sleep 1; done
$ GF_PATHS_PROVISIONING=$PWD/grafana/provisioning GF_PATHS_DATA=$PWD/grafana/data GF_SERVER_HTTP_PORT=3097 GF_AUTH_ANONYMOUS_ENABLED=true GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer GF_ANALYTICS_REPORTING_ENABLED=false GF_NEWS_NEWS_FEED_ENABLED=false "$GRAFANA_HOME/bin/grafana" server --homepath "$GRAFANA_HOME" >grafana.log 2>&1 &
$ for i in $(seq 1 60); do curl -s localhost:3097/api/health | grep -q ok && break; sleep 1; done; curl -s localhost:3097/api/health | grep -o '"database": *"ok"'
$ curl -s localhost:3097/api/dashboards/uid/shop | grep -o '"title":"Shop API"' ''', timeout=600),
    term(f'''$ "{CHROME}" --headless=new --disable-gpu --hide-scrollbars --window-size=1280,760 --force-device-scale-factor=1 --virtual-time-budget=15000 --screenshot="{SHOT}" "http://localhost:3097/d/shop/shop?orgId=1&kiosk&theme=light" >/dev/null 2>&1; test -s "{SHOT}" && echo screenshot ✓''',
         hidden=True, timeout=300),
    Html(f'<figure class="dash-shot"><img src="shots/{SHOT.name}" alt="Grafana dashboard"><figcaption>আসল screenshot — উপরের data দিয়ে চালানো Grafana</figcaption></figure>'))

c.lesson("Laravel, server আর database",
    table(["কী monitor করবেন", "Exporter / টুল"], [
        ["Server CPU, memory, disk", "<code>node_exporter</code>"], ["MySQL", "<code>mysqld_exporter</code>"], ["PostgreSQL", "<code>postgres_exporter</code>"],
        ["Nginx", "<code>nginx-prometheus-exporter</code>"], ["Laravel request, queue, job", "<code>spatie/laravel-prometheus</code>"],
        ["Website বাইরে থেকে চালু কিনা", "<code>blackbox_exporter</code>, Uptime Kuma"]]),
    tip("Grafana-র dashboard library-তে (grafana.com/dashboards) এগুলোর তৈরি dashboard আছে — ID দিয়ে import করলেই হয়, যেমন Node Exporter Full (1860)।"))

c.lesson("Log: Loki",
    say("Metric বলে <b>কিছু</b> ভুল হচ্ছে; log বলে <b>কী</b> ভুল। Loki Prometheus-এর মতো label ধরে log রাখে, Grafana-তেই খোঁজা যায়। JSON আকারে log লিখলে খোঁজা সহজ।"),
    code('''
logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
logger.Error("checkout failed",
	"invoice", "INV-1007",
	"gateway", "bkash",
	"duration_ms", 2840,
)
// {"time":"...","level":"ERROR","msg":"checkout failed","invoice":"INV-1007","gateway":"bkash","duration_ms":2840}
''', "go", run=False, label="Go — structured log"),
    code('{app="shop-api"} | json | level="ERROR" | gateway="bkash"', "text", run=False, label="LogQL (Grafana Explore)"),
    php_note("Laravel-এ <code>config/logging.php</code>-এ JSON formatter দিন, আর <code>Log::error('checkout failed', ['invoice' =&gt; $no])</code> — context array-টাই JSON field হয়।"))

c.lesson("Kubernetes-এ পুরো stack এক লাইনে",
    shell("$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts\n$ helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace\n$ kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80"),
    points("Prometheus, Alertmanager, Grafana, node-exporter, kube-state-metrics — সব একসাথে", "Cluster, node, Pod-এর তৈরি dashboard আর alert",
           "নিজের app scrape করাতে <code>ServiceMonitor</code> resource"))

c.lesson("SLO: কতটা ভালো \"যথেষ্ট ভালো\"",
    table(["শব্দ", "মানে", "উদাহরণ"], [
        ["SLI", "যা মাপছি", "সফল request-এর শতাংশ"], ["SLO", "লক্ষ্য", "মাসে ৯৯.৫% request সফল"],
        ["Error budget", "বাকি ০.৫% — কতটা ভুলের সুযোগ", "মাসে ~৩.৬ ঘণ্টা সমস্যা চলবে"]]),
    tip("Error budget শেষ হয়ে আসলে নতুন feature কম, স্থিতিশীলতায় বেশি মন — আর budget বাকি থাকলে সাহস করে deploy। এটাই SRE-এর মূল ভাবনা।"),
    task("নিজের Laravel app-এ <code>spatie/laravel-prometheus</code> বসিয়ে এই কোর্সের Prometheus-কে দিয়ে scrape করান, p95 আর error % panel বানান।"))

c.finish("Monitoring শেষ! 🎉",
         "এখন আপনি দেখতে পান app কেমন চলছে, ধীর হলে কোথায়, আর সমস্যা হলে আগে জানতে পারেন। শেষ ধাপ: server আর cloud-ও কোড দিয়ে বানানো — Infrastructure as Code।",
         recap=["Metric, log, trace", "Counter/gauge/histogram + <code>/metrics</code>", "PromQL: <code>rate</code>, <code>sum by</code>, <code>histogram_quantile</code>",
                "Alert rule + <code>promtool test rules</code>", "Grafana provisioning — dashboard কোডে", "SLO আর error budget"])


if __name__ == "__main__":
    SHOT.parent.mkdir(exist_ok=True)
    c.build()
