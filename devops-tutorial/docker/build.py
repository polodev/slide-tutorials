"""Docker — container, image, Dockerfile, multi-stage, cache, volume, network, Compose, Laravel stack, security.
Every `$` command really runs against a Docker engine (Colima); the Go Shop API from the Go course is the app.
Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
import devops_env  # noqa: E402
from kit import Course, code, php_note, points, quiz, say, shell, table, task, term, tip, warn  # noqa: E402

API_SRC = (ROOT / "go-tutorial/go-web-development/go-shop-api/main.go").read_text()
GO_MOD = "module shop-api\n\ngo 1.25\n\nrequire modernc.org/sqlite v1.40.1\n"
JSON = "-H 'Content-Type: application/json'"
KEY = "-H 'X-Api-Key: secret-123'"

c = Course(slug="docker", title="Docker — Container দিয়ে App চালানো", folder=HERE,
           subtitle="Image, container, Dockerfile, multi-stage build, volume, network, Compose আর Laravel stack — প্রতিটি command আসল Docker-এ চালানো",
           series="Docker", shell=True, shell_env=devops_env.docker_env(),
           next_course=("../kubernetes/index.html", "Kubernetes — অনেক container একসাথে চালানো"))


def _setup():
    devops_env.ensure_docker()
    for name in ("web", "api", "api2", "site"):
        devops_env.remove_container(name)


c.shell_setup = _setup
c.shell_teardown = lambda: [devops_env.remove_container(n) for n in ("web", "api", "api2", "site")]

c.cover("Docker<br>Container দিয়ে App চালানো",
        "\"আমার computer-এ তো চলছিল!\" — Docker এই সমস্যার শেষ। App, তার PHP/Go version, library সব এক image-এ; যেকোনো জায়গায় একই ভাবে চলে। এই কোর্সের প্রতিটি command আসলেই চালানো।",
        learn=["Image বনাম container", "docker run, ps, logs, exec", "Dockerfile লেখা", "Multi-stage: ৮০০ MB থেকে ১৫ MB",
               "Layer cache আর .dockerignore", "Volume আর network", "Docker Compose: অনেক service একসাথে", "Laravel stack, registry, নিরাপত্তা"],
        need="DevOps 101 (Linux command, environment variable)।")

c.section("শুরু")
c.lesson("Container কী?",
    table(["", "Virtual Machine", "Container"], [
        ["ভিতরে", "পুরো OS (kernel সহ)", "শুধু app + তার library; host-এর kernel ভাগ করে"],
        ["আকার", "কয়েক GB", "কয়েক MB থেকে কয়েকশো MB"], ["চালু হতে", "মিনিট", "সেকেন্ড বা তার কম"],
        ["একই server-এ", "কয়েকটা", "শত শত"]]),
    php_note("সহজ তুলনা: <b>image</b> হলো PHP-র <code>class</code>, <b>container</b> হলো <code>new</code> দিয়ে বানানো object। এক image থেকে অনেক container।"))

c.lesson("Install আর প্রথম container",
    points("<b>Windows/Mac:</b> Docker Desktop (বা Mac-এ OrbStack/Colima)", "<b>Linux:</b> <code>curl -fsSL https://get.docker.com | sh</code>",
           "এই কোর্স চালানো হয়েছে Colima-র Linux VM-এ"),
    term("$ docker version --format 'Client {{.Client.Version}} / Server {{.Server.Version}} ({{.Server.Os}}/{{.Server.Arch}})'\n$ docker run --rm hello-world | head -4", timeout=600),
    say("<code>hello-world</code> image আগে ছিল না, তাই Docker Hub থেকে নামিয়ে (pull) চালাল। <code>--rm</code> — শেষ হলে container মুছে দাও।"))

c.section("Container")
c.lesson("docker run: Nginx এক command-এ",
    term('''$ docker run -d --name web -p 8088:80 nginx:1.27-alpine
$ docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'
$ curl -s localhost:8088 | grep -o '<title>.*</title>' ''', timeout=600),
    points("<code>-d</code> — background-এ চালাও", "<code>-p 8088:80</code> — আমার 8088 port → container-এর 80", "<code>--name web</code> — নাম দিয়ে পরে ধরা যায়"),
    php_note("Server-এ Nginx install-config ছাড়াই — এক লাইনে চালু, এক লাইনে মুছে ফেলা যায়।"))

c.lesson("logs, exec, stop, rm",
    term('''$ docker logs web 2>&1 | tail -2
$ docker exec web nginx -v
$ docker exec web sh -c 'ls /usr/share/nginx/html'
$ docker stop web && docker rm web
$ docker ps -a --filter name=web --format '{{.Names}}' | wc -l'''),
    table(["Command", "কাজ"], [["<code>docker logs -f web</code>", "Live log (tail -f)"], ["<code>docker exec -it web sh</code>", "Container-এর ভিতরে shell"],
        ["<code>docker stop</code> / <code>start</code>", "থামানো / আবার চালানো"], ["<code>docker rm -f</code>", "জোর করে মোছা"]]))

c.lesson("Image আর layer",
    term('''$ docker pull -q alpine:3.20
$ docker images --format 'table {{.Repository}}:{{.Tag}}\\t{{.Size}}' | grep -E 'REPO|alpine|nginx|hello'
$ docker history --format '{{.CreatedBy}}' nginx:1.27-alpine | head -5 | cut -c1-70''', timeout=600),
    say("Image হলো অনেকগুলো <b>layer</b>-এর স্তূপ — প্রতিটি Dockerfile লাইন একটা layer। একই layer অনেক image ভাগ করে, তাই disk আর download বাঁচে।"))

c.section("Dockerfile")
c.lesson("প্রথম Dockerfile",
    code('''
<!doctype html>
<html><body><h1>Rahim Mobile</h1><p>Docker থেকে পরিবেশিত</p></body></html>
''', "html", file="site/index.html", save=True, hidden=False),
    code('''
FROM nginx:1.27-alpine
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
''', "dockerfile", file="site/Dockerfile", save=True, validate="dockerfile"),
    term('''$ cd site && docker build -q -t shop-site:1.0 .
$ docker run -d --name site -p 8089:80 shop-site:1.0
$ curl -s localhost:8089 | grep -o '<h1>.*</h1>'
$ docker rm -f site >/dev/null && cd ..'''),
    points("<code>FROM</code> — কোন image-এর উপর বানাব", "<code>COPY</code> — আমার file image-এর ভিতরে", "<code>-t shop-site:1.0</code> — নাম আর version (tag)"))

c.lesson("Go API-কে container-এ",
    say("এবার Go Web Development কোর্সের Shop API। প্রথমে সবচেয়ে সরল উপায়: পুরো Go toolchain সহ image।"),
    code(API_SRC, "go", file="shop-api/main.go", save=True, hidden=True),
    code(GO_MOD, "text", file="shop-api/go.mod", save=True, hidden=True),
    code('''
FROM golang:1.25
WORKDIR /src
COPY . .
RUN go mod tidy && go build -o /shop-api .
ENV APP_ADDR=0.0.0.0:3000
EXPOSE 3000
CMD ["/shop-api"]
''', "dockerfile", file="shop-api/Dockerfile.simple", save=True),
    term("$ cd shop-api && docker build -q -f Dockerfile.simple -t shop-api:simple . && cd ..\n$ docker images shop-api:simple --format '{{.Repository}}:{{.Tag}}  {{.Size}}'", timeout=1200),
    warn("চলে, কিন্তু image-এর আকার দেখুন — Go compiler, source, সব ভিতরে। Production-এ এগুলোর কোনো দরকার নেই।"))

c.lesson("Multi-stage: শুধু binary রাখা",
    say("প্রথম stage-এ build, দ্বিতীয় stage-এ শুধু তৈরি binary একটা খালি image-এ কপি। <code>CGO_ENABLED=0</code> — কোনো system library লাগে না।"),
    code('''
FROM golang:1.25 AS build
WORKDIR /src
COPY go.mod ./
COPY . .
RUN go mod tidy && CGO_ENABLED=0 go build -ldflags="-s -w" -o /shop-api .

FROM gcr.io/distroless/static-debian12
COPY --from=build /shop-api /shop-api
ENV APP_ADDR=0.0.0.0:3000 DATABASE_PATH=/data/shop.db
USER nonroot
EXPOSE 3000
ENTRYPOINT ["/shop-api"]
''', "dockerfile", file="shop-api/Dockerfile", save=True, validate="dockerfile"),
    term("$ cd shop-api && docker build -q -t shop-api:1.0 . && cd ..\n$ docker images shop-api --format 'table {{.Repository}}:{{.Tag}}\\t{{.Size}}'", timeout=1200),
    tip("একই app, কিন্তু image কয়েকশো MB থেকে নেমে প্রায় ১৫ MB — দ্রুত download, দ্রুত deploy, কম আক্রমণের জায়গা।"))

c.lesson("চালিয়ে দেখি",
    term(f'''$ docker run -d --name api -p 8090:3000 -e API_KEY=secret-123 shop-api:1.0
$ sleep 1 && curl -s -X POST localhost:8090/api/v1/products {KEY} {JSON} -d '{{"name":"Redmi 13","brand":"Xiaomi","price":17500,"stock":5}}'
$ curl -s localhost:8090/api/v1/products
$ docker logs api'''),
    php_note("PHP-র মতো server-এ runtime install করতে হলো না — image-এর ভিতরেই সব।"))

c.lesson("Volume: container মুছলেও data থাকে",
    say("Container-এর ভিতরের file container মুছলে হারায়। Database file রাখতে <b>volume</b> — Docker-এর রাখা আলাদা জায়গা।"),
    term(f'''$ docker rm -f api >/dev/null
$ docker volume create shop-data
$ docker run -d --name api -p 8090:3000 -e API_KEY=secret-123 -v shop-data:/data shop-api:1.0
$ sleep 1 && curl -s -o /dev/null -w '%{{http_code}}\\n' -X POST localhost:8090/api/v1/products {KEY} {JSON} -d '{{"name":"Vivo Y28","brand":"Vivo","price":18000,"stock":4}}'
$ docker rm -f api >/dev/null && echo "container মুছে দিলাম"
$ docker run -d --name api2 -p 8090:3000 -v shop-data:/data shop-api:1.0
$ sleep 1 && curl -s localhost:8090/api/v1/products
$ docker rm -f api2 >/dev/null'''),
    php_note("Laravel-এ <code>storage/</code> আর MySQL-এর data folder ঠিক এভাবেই volume-এ রাখতে হয়।"))

c.lesson("Layer cache আর .dockerignore",
    say("Docker প্রতিটি ধাপ cache করে। কোড বদলালে শুধু তার পরের ধাপগুলো আবার চলে — তাই যা কম বদলায় (dependency) আগে, যা বেশি বদলায় (কোড) পরে।"),
    code("*.db\n.git\nDockerfile*\n", "text", file="shop-api/.dockerignore", save=True),
    term('''$ cd shop-api && echo "// small change" >> main.go
$ docker build --progress=plain -t shop-api:1.1 . 2>&1 | grep -E '^#[0-9]+ \\[|CACHED' | head -8
$ cd ..''', timeout=1200),
    php_note("Laravel image-এ আগে <code>COPY composer.json composer.lock</code> + <code>composer install</code>, তারপর বাকি কোড — তাহলে প্রতিবার vendor আবার install হয় না।"))

c.lesson("Dockerfile-এর ভুল ধরা: hadolint",
    code('''
FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y curl
ADD app.tar.gz /app
''', "dockerfile", file="Dockerfile.bad", save=True),
    term("$ hadolint --no-color Dockerfile.bad", err="DL3007"),
    points("<code>latest</code> tag — কোন version আসবে নিশ্চিত না", "<code>apt-get update</code> আলাদা লাইনে — পুরনো cache-এর ঝুঁকি",
           "Version না দেওয়া package — প্রতিবার আলাদা build"),
    tip("CI-তে hadolint চালান — ভুল Dockerfile merge হওয়ার আগেই ধরা পড়ে।"))

c.section("Network ও Compose")
c.lesson("Network: নাম দিয়ে খুঁজে পাওয়া",
    say("একই Docker network-এ container-রা একে অপরকে <b>নাম দিয়ে</b> খুঁজে পায় — IP লাগে না। এভাবেই app database-কে <code>mysql</code> নামে ডাকে।"),
    term('''$ docker network create shopnet
$ docker run -d --name api --network shopnet shop-api:1.0
$ sleep 1 && docker run --rm --network shopnet curlimages/curl:8.10.1 -s http://api:3000/api/v1/products
$ docker rm -f api >/dev/null && docker network rm shopnet''', timeout=600),
    php_note("Laravel <code>.env</code>-এ <code>DB_HOST=mysql</code> লেখা হয় এই কারণেই — <code>mysql</code> হলো container-এর নাম।"))

c.lesson("Docker Compose: সব service এক file-এ",
    say("অনেক <code>docker run</code> মনে রাখার বদলে একটা <code>compose.yaml</code>: কোন service, কোন image, port, volume, environment। এখানে Nginx সামনে, পিছনে Go API।"),
    code('''
server {
    listen 80;
    location / {
        proxy_pass http://api:3000;
        proxy_set_header Host $host;
    }
}
''', "nginx", file="stack/nginx.conf", save=True),
    code('''
services:
  api:
    build: ../shop-api
    environment:
      API_KEY: secret-123
    volumes:
      - shop-data:/data
    healthcheck:
      test: ["CMD", "/shop-api", "-healthcheck"]
      disable: true
    restart: unless-stopped

  web:
    image: nginx:1.27-alpine
    ports:
      - "8088:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - api

volumes:
  shop-data:
''', "yaml", file="stack/compose.yaml", save=True),
    term(f'''$ cd stack && docker compose up -d --build --quiet-pull 2>&1 | tail -3
$ docker compose ps --format 'table {{{{.Service}}}}\\t{{{{.State}}}}\\t{{{{.Ports}}}}'
$ sleep 1 && curl -s localhost:8088/api/v1/products
$ docker compose logs --no-log-prefix api | head -2
$ docker compose down && cd ..''', timeout=1200))

c.lesson("Laravel stack: app + Nginx + MySQL + Redis",
    say("Laravel-এর জন্য সাধারণ Compose: PHP-FPM container-এ app, Nginx সামনে, MySQL আর Redis পাশে। <code>docker compose config</code> file যাচাই করে পূর্ণ রূপ দেখায়।"),
    code('''
services:
  app:
    build: .
    volumes:
      - ./:/var/www/html
    environment:
      DB_HOST: mysql
      REDIS_HOST: redis
    depends_on:
      mysql:
        condition: service_healthy

  nginx:
    image: nginx:1.27-alpine
    ports:
      - "8000:80"
    volumes:
      - ./:/var/www/html:ro
      - ./docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - app

  mysql:
    image: mysql:8.4
    environment:
      MYSQL_DATABASE: shop
      MYSQL_ROOT_PASSWORD: secret
    volumes:
      - mysql-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-psecret"]
      interval: 5s
      retries: 10

  redis:
    image: redis:7-alpine

volumes:
  mysql-data:
''', "yaml", file="laravel/compose.yaml", save=True),
    term("$ cd laravel && docker compose config --services && docker compose config --quiet && echo 'compose.yaml ঠিক আছে ✓' && cd .."),
    php_note("Laravel Sail ঠিক এই ধরনের compose file বানিয়ে দেয় (<code>php artisan sail:install</code>)। এখন আপনি জানেন ভিতরে কী আছে।"))

c.lesson("Laravel-এর Dockerfile",
    code('''
FROM composer:2 AS vendor
WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --prefer-dist --no-interaction

FROM php:8.3-fpm-alpine
WORKDIR /var/www/html
RUN docker-php-ext-install pdo_mysql opcache
COPY --from=vendor /app/vendor ./vendor
COPY . .
RUN php artisan config:cache && php artisan route:cache \\
    && chown -R www-data:www-data storage bootstrap/cache
USER www-data
''', "dockerfile", file="laravel/Dockerfile", save=True, validate="dockerfile"),
    points("Composer আলাদা stage-এ — final image-এ composer নেই", "<code>composer.json</code> আগে কপি → vendor layer cache হয়",
           "<code>storage</code>, <code>bootstrap/cache</code> www-data-কে", "Root না, <code>www-data</code> user"))

c.section("Ship ও নিরাপত্তা")
c.lesson("Registry: image অন্য জায়গায় পাঠানো",
    say("Image বানিয়ে registry-তে push করি; server বা Kubernetes সেখান থেকে pull করে। GitHub Container Registry (ghcr.io) বিনামূল্যে।"),
    shell("$ echo $GITHUB_TOKEN | docker login ghcr.io -u rahim --password-stdin\n$ docker tag shop-api:1.0 ghcr.io/rahim/shop-api:1.0\n$ docker push ghcr.io/rahim/shop-api:1.0\n\n# server-এ:\n$ docker pull ghcr.io/rahim/shop-api:1.0"),
    tip("Tag-এ <code>latest</code>-এর উপর ভরসা করবেন না — version বা git commit (<code>:1.0</code>, <code>:sha-3f2a9c1</code>) দিন, যাতে কোনটা চলছে সবসময় জানা থাকে। CI/CD কোর্সে এটা স্বয়ংক্রিয়।"))

c.lesson("Secret কখনো image-এ না",
    say("<code>ENV</code> বা <code>COPY .env</code> দিয়ে password image-এ দিলে image যার কাছে আছে সে-ই দেখতে পায় — <code>docker history</code> সব বলে দেয়।"),
    code('''
FROM alpine:3.20
ENV DB_PASSWORD=super-secret-123
CMD ["echo", "running"]
''', "dockerfile", file="leaky/Dockerfile", save=True),
    term("$ cd leaky && docker build -q -t leaky . >/dev/null && cd ..\n$ docker history --no-trunc --format '{{.CreatedBy}}' leaky | grep PASSWORD"),
    warn("Secret দিন চালানোর সময়: <code>docker run -e</code>, Compose-এর <code>env_file</code>, বা Kubernetes Secret। <code>.env</code>-কে <code>.dockerignore</code>-এ রাখুন।"))

c.lesson("Debug আর পরিষ্কার",
    term('''$ docker system df
$ docker image prune -f >/dev/null && echo "অব্যবহৃত image মোছা হলো"
$ docker volume rm shop-data stack_shop-data >/dev/null 2>&1; echo done'''),
    table(["সমস্যা", "দেখুন"], [["Container চালু হয়েই থেমে যায়", "<code>docker logs NAME</code>, <code>docker ps -a</code>-এ exit code"],
        ["Port-এ পৌঁছায় না", "<code>-p</code> ঠিক কিনা, app <code>0.0.0.0</code>-এ শুনছে কিনা"],
        ["\"no such host\"", "দুই container একই network-এ কিনা"], ["Disk ভরে গেছে", "<code>docker system df</code>, <code>docker system prune</code>"]]))

c.finish("Docker শেষ! 🎉",
         "আপনার app এখন একটা ছোট, নিরাপদ image — যেকোনো জায়গায় একই ভাবে চলে। কিন্তু অনেক server-এ, অনেক copy, স্বয়ংক্রিয় restart আর zero-downtime update? সেটা Kubernetes-এর কাজ।",
         recap=["Image = class, container = object", "<code>run</code>, <code>ps</code>, <code>logs</code>, <code>exec</code>, <code>rm</code>",
                "Multi-stage + distroless = ছোট image", "Volume-এ data, network-এ নাম দিয়ে খোঁজা",
                "Compose: পুরো stack এক file-এ", "Secret image-এ না; non-root user"])

if __name__ == "__main__":
    c.build()
