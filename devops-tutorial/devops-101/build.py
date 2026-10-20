"""DevOps 101 — Linux shell, files, text tools, permissions, users, env, processes, nginx reverse proxy,
SSH keys, Git, bash scripts. Every `$` command runs in a real Ubuntu 24.04 container. Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
import devops_env  # noqa: E402
from kit import Course, code, php_note, points, quiz, say, shell, table, task, term, tip, warn  # noqa: E402

c = Course(slug="devops-101", title="DevOps 101 — Linux, Server ও Git", folder=HERE,
           subtitle="DevOps-এর ভিত্তি: Linux command, file, permission, process, Nginx reverse proxy, SSH key, Git আর bash script — আসল Ubuntu-তে চালানো",
           series="DevOps 101", shell=True, shell_env=devops_env.docker_env(),
           next_course=("../docker/index.html", "Docker — Container দিয়ে App চালানো"))
c.shell_container = "devops-lab"
c.shell_setup = lambda: devops_env.lab_container(packages=["git", "curl", "nginx", "openssh-client", "procps", "iproute2", "tree", "less", "ca-certificates"])
c.shell_teardown = lambda: devops_env.remove_container()

c.cover("DevOps 101<br>Linux, Server ও Git",
        "আপনার Laravel app শেষ পর্যন্ত একটা Linux server-এ চলে। DevOps মানে সেই server, deploy, monitoring — সব নির্ভরযোগ্যভাবে চালানো। এই কোর্সের প্রতিটি command আসল Ubuntu-তে চালিয়ে আউটপুট বসানো।",
        learn=["DevOps কী, কোন টুল কোথায়", "Linux-এর মূল command", "grep, awk, pipe দিয়ে log বিশ্লেষণ", "Permission, user আর sudo",
               "Environment variable আর process", "Nginx reverse proxy", "SSH key আর Git workflow", "Bash script দিয়ে deploy"],
        need="Terminal খুলতে পারা। Laravel/PHP জানলে উদাহরণগুলো চেনা লাগবে।")

c.section("শুরু")
c.lesson("DevOps কী?",
    say("আগে developer কোড লিখে \"ops\" টিমকে দিত, তারা server-এ চালাত — মাঝখানে দেয়াল। DevOps মানে দুই কাজ এক ধারায়: কোড → test → build → deploy → monitor, যতটা সম্ভব স্বয়ংক্রিয়।"),
    table(["ধাপ", "কাজ", "টুল (এই সিরিজে)"], [
        ["Code", "কোড আর তার ইতিহাস", "Git, GitHub"], ["Build", "চালানোর মতো package", "Docker image"],
        ["Test + Deploy", "প্রতিটি push-এ স্বয়ংক্রিয়", "GitHub Actions (CI/CD)"], ["Run", "অনেক server-এ চালানো", "Kubernetes"],
        ["Monitor", "কী হচ্ছে, কোথায় ধীর", "Prometheus, Grafana"], ["Infrastructure", "server/cloud কোডে লেখা", "Terraform/OpenTofu"]]),
    php_note("Laravel Forge বা Envoyer যা করে দেয় (server set up, zero-downtime deploy) — সেগুলো ভিতরে কী হয়, এই সিরিজে নিজে হাতে শিখব।"))

c.lesson("Linux কোথায় পাবেন",
    points("<b>VPS:</b> DigitalOcean, Vultr, Hetzner, AWS Lightsail — মাসে কয়েক ডলার", "<b>Windows-এ:</b> WSL2 (Ubuntu)",
           "<b>Mac-এ:</b> Multipass, OrbStack বা Docker দিয়ে Ubuntu container", "এই কোর্সের সব command চালানো হয়েছে <b>Ubuntu 24.04</b>-এ"),
    term("$ cat /etc/os-release | head -3\n$ uname -m\n$ hostname"),
    tip("নিজের computer নষ্ট হওয়ার ভয় ছাড়া অনুশীলনের সবচেয়ে সহজ উপায়: <code>docker run -it ubuntu:24.04 bash</code> (Docker কোর্সে বিস্তারিত)।"))

c.section("Shell-এর মূল কথা")
c.lesson("কোথায় আছি, কী আছে",
    term("$ whoami\n$ pwd\n$ mkdir -p shop/storage/logs shop/public\n$ cd shop\n$ ls -la"),
    points("<code>pwd</code> — বর্তমান folder", "<code>mkdir -p</code> — ভিতরের folder সহ বানায়", "<code>ls -la</code> — লুকানো file সহ বিস্তারিত তালিকা"))

c.lesson("File বানানো, পড়া, কপি",
    term('''$ echo "APP_NAME=Shop" > .env
$ echo "APP_ENV=production" >> .env
$ cat .env
$ cp .env .env.backup
$ mv .env.backup .env.old
$ touch public/index.php storage/logs/laravel.log
$ tree -a'''),
    points("<code>&gt;</code> — file-এ লেখে (আগেরটা মুছে)", "<code>&gt;&gt;</code> — শেষে যোগ করে", "<code>cp</code>, <code>mv</code>, <code>rm</code> — কপি, সরানো/নাম বদল, মোছা"),
    warn("<code>rm -rf</code>-এ কোনো \"undo\" নেই। Production server-এ চালানোর আগে path দুইবার পড়ুন।"))

c.lesson("Log বিশ্লেষণ: grep, awk, pipe",
    say("<code>|</code> (pipe) এক command-এর আউটপুট পরেরটার input বানায়। Nginx access log থেকে কোন status কতবার — এক লাইনে।"),
    term('''$ cat > access.log <<'EOF'
103.4.145.2 - - [21/Oct/2026:10:01:12 +0600] "GET /products HTTP/1.1" 200 5120
103.4.145.2 - - [21/Oct/2026:10:01:15 +0600] "POST /cart HTTP/1.1" 201 312
27.147.20.9 - - [21/Oct/2026:10:02:01 +0600] "GET /admin HTTP/1.1" 403 162
103.4.145.2 - - [21/Oct/2026:10:02:44 +0600] "GET /products/7 HTTP/1.1" 200 2048
45.9.20.11 - - [21/Oct/2026:10:03:10 +0600] "GET /wp-login.php HTTP/1.1" 404 153
27.147.20.9 - - [21/Oct/2026:10:04:22 +0600] "POST /checkout HTTP/1.1" 500 98
EOF
$ grep " 500 " access.log
$ awk '{print $9}' access.log | sort | uniq -c | sort -rn
$ awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -2
$ wc -l access.log'''),
    php_note("Laravel-এর <code>storage/logs/laravel.log</code>-এ <code>grep ERROR</code> — production-এ ভুল খোঁজার প্রথম অস্ত্র।"))

c.lesson("Permission: কে কী করতে পারে",
    say("<code>rwx</code> = read, write, execute; তিন দল: মালিক, group, বাকি সবাই। সংখ্যায়: r=4, w=2, x=1 → <code>640</code> = মালিক পড়া-লেখা, group পড়া, বাকিরা কিছু না।"),
    term('''$ ls -l .env
$ chmod 600 .env
$ ls -l .env
$ printf '#!/bin/bash\\necho "deploy শুরু"\\n' > deploy.sh
$ ./deploy.sh''', err="Permission denied"),
    term("$ chmod +x deploy.sh\n$ ls -l deploy.sh\n$ ./deploy.sh"),
    php_note("Laravel deploy-এ <code>storage</code> আর <code>bootstrap/cache</code> web server user (<code>www-data</code>)-কে লেখার অনুমতি দিতে হয় — permission ভুল হলে 500 error।"))

c.lesson("User আর sudo",
    say("Server-এ সব কাজ <code>root</code> দিয়ে করবেন না। Deploy-এর জন্য আলাদা user, file-এর মালিক ঠিক করে দেওয়া।"),
    term('''$ useradd -m -s /bin/bash deploy
$ id deploy
$ chown -R deploy:www-data /root/shop/storage
$ ls -ld /root/shop/storage
$ su - deploy -c 'whoami && pwd' '''),
    tip("সত্যিকারের server-এ: <code>adduser deploy</code>, <code>usermod -aG sudo deploy</code>, তারপর root দিয়ে SSH login বন্ধ।"))

c.lesson("Environment variable",
    say("App-এর setting (database password, API key) কোডে না রেখে environment-এ রাখা — DevOps-এর মূল নিয়মগুলোর একটা।"),
    term('''$ export APP_ENV=production
$ echo "এখন চলছে: $APP_ENV"
$ env | grep APP_
$ set -a; source .env; set +a
$ echo "$APP_NAME"
$ APP_DEBUG=true bash -c 'echo "শুধু এই command-এ: $APP_DEBUG"'
$ echo "বাইরে: ${APP_DEBUG:-ফাঁকা}"'''),
    php_note("Laravel-এর <code>env('APP_ENV')</code> এই environment variable-ই পড়ে। Docker আর Kubernetes-এ <code>.env</code> file না দিয়ে সরাসরি variable দেওয়া হয়।"))

c.lesson("Process: কী চলছে",
    term('''$ sleep 300 &
$ ps aux | grep -v grep | grep sleep
$ pgrep -a sleep
$ kill %1
$ sleep 0.2; pgrep sleep || echo "আর চলছে না"'''),
    table(["Command", "কাজ"], [["<code>ps aux</code>", "সব process"], ["<code>top</code> / <code>htop</code>", "live CPU/memory"],
        ["<code>kill PID</code>", "থামতে বলা (SIGTERM)"], ["<code>kill -9 PID</code>", "জোর করে থামানো — শেষ উপায়"],
        ["<code>free -h</code>, <code>df -h</code>", "memory আর disk"]]))

c.lesson("Package install: apt",
    term("$ apt-get install -y -qq jq > /dev/null && echo installed\n$ echo '{\"name\":\"Redmi 13\",\"price\":17500}' | jq .price\n$ dpkg -l | grep -c ^ii"),
    points("<code>apt update</code> — তালিকা হালনাগাদ", "<code>apt install nginx</code> — install", "<code>apt upgrade</code> — security update (নিয়মিত!)"),
    php_note("PHP extension-ও এভাবেই: <code>apt install php8.3-mysql php8.3-mbstring</code>।"))

c.section("Server ও Network")
c.lesson("Port আর curl",
    say("Server-এ প্রতিটি program একটা <b>port</b>-এ শোনে: web 80/443, MySQL 3306, SSH 22, Laravel <code>artisan serve</code> 8000। <code>ss</code> দেখায় কে কোন port-এ।"),
    term('''$ nginx
$ ss -tlnp | grep -E 'State|nginx'
$ curl -sI http://localhost | head -3'''),
    php_note("\"Address already in use\" error মানে ঐ port-এ আগে থেকে কেউ শুনছে — <code>ss -tlnp | grep :8000</code> দিয়ে খুঁজুন।"))

c.lesson("Nginx reverse proxy",
    say("App চলে ভিতরের একটা port-এ (এখানে 8080-এ নকল API), Nginx বাইরে 80-তে দাঁড়িয়ে request পাঠায় — HTTPS, gzip, static file সব Nginx সামলায়। Go/Rust/Node app এভাবেই চালানো হয়।"),
    code('''
server {
    listen 8080;
    location /api/ {
        default_type application/json;
        return 200 '{"app":"shop-api","from":"port 8080"}';
    }
}

server {
    listen 80 default_server;
    server_name shop.example.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        root /var/www/shop/public;
        try_files $uri $uri/ =404;
    }
}
''', "nginx", file="/etc/nginx/sites-enabled/default", save=True),
    term('''$ nginx -t
$ nginx -s reload
$ curl -s http://localhost/api/products'''),
    php_note("Laravel-এ শেষ block-টা হয় <code>location ~ \\.php$ { fastcgi_pass unix:/run/php/php8.3-fpm.sock; }</code> — PHP-FPM-এ পাঠানো।"))

c.lesson("HTTPS: Let's Encrypt",
    say("বিনা খরচে SSL certificate। <code>certbot</code> নিজেই Nginx config বদলে HTTPS চালু করে আর ৯০ দিন পরপর নবায়ন করে।"),
    shell("$ sudo apt install certbot python3-certbot-nginx\n$ sudo certbot --nginx -d shop.example.com\n$ sudo certbot renew --dry-run",
          out="Successfully received certificate.\nCertificate is saved at: /etc/letsencrypt/live/shop.example.com/fullchain.pem\nCongratulations! You have successfully enabled HTTPS on https://shop.example.com"),
    warn("Domain-এর DNS (A record) আগে server-এর IP-তে দিতে হবে, আর firewall-এ 80/443 খোলা থাকতে হবে — নইলে certbot যাচাই করতে পারে না।"))

c.lesson("systemd: app সবসময় চালু",
    say("Server restart হলে বা app crash করলে নিজে থেকে আবার চালু করতে systemd service। Container ছাড়া চালালে এটাই নিয়ম (container-এ systemd থাকে না, তাই এখানে শুধু দেখানো)।"),
    code('''
[Unit]
Description=Shop API
After=network.target

[Service]
User=deploy
WorkingDirectory=/opt/shop
EnvironmentFile=/opt/shop/.env
ExecStart=/opt/shop/shop-api
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
''', "ini", file="/etc/systemd/system/shop-api.service"),
    shell("$ sudo systemctl daemon-reload\n$ sudo systemctl enable --now shop-api\n$ systemctl status shop-api\n$ journalctl -u shop-api -f"),
    php_note("Laravel queue worker-এর জন্য একই রকম service বা Supervisor: <code>ExecStart=/usr/bin/php artisan queue:work --sleep=3 --tries=3</code>।"))

c.section("SSH ও Git")
c.lesson("SSH key",
    say("Password না, key দিয়ে server-এ ঢুকুন: private key আপনার কাছে, public key server-এর <code>~/.ssh/authorized_keys</code>-এ। GitHub-এও একই key।"),
    term('''$ ssh-keygen -t ed25519 -N "" -C "rahim@laptop" -f ~/.ssh/id_ed25519 -q
$ ls -l ~/.ssh
$ cut -c1-40 ~/.ssh/id_ed25519.pub'''),
    code('''
Host shop
    HostName 203.0.113.10
    User deploy
    IdentityFile ~/.ssh/id_ed25519
''', "text", run=False, file="~/.ssh/config"),
    shell("$ ssh-copy-id deploy@203.0.113.10\n$ ssh shop          # config-এর নাম দিয়েই ঢোকা"),
    warn("Private key (<code>id_ed25519</code>, পাশে <code>.pub</code> নেই যেটার) কখনো কাউকে দেবেন না, git-এ দেবেন না।"))

c.lesson("Git: commit আর branch",
    term('''$ cd /root/shop && git init -q -b main
$ git config user.name "Rahim" && git config user.email "rahim@example.com"
$ printf ".env\\nstorage/logs/*.log\\nvendor/\\n" > .gitignore
$ git add . && git commit -qm "Initial shop skeleton"
$ git switch -qc feature/stock-alert
$ echo "LOW_STOCK=3" >> .env.example && git add .env.example && git commit -qm "Add low stock setting"
$ git switch -q main && git merge -q --no-ff feature/stock-alert -m "Merge stock alert"
$ git log --oneline --graph
$ git status --short --ignored'''),
    tip("<code>.env</code> কখনো commit করবেন না — <code>.env.example</code> commit করুন (key আছে, মান নেই)। Laravel project-এ এটাই নিয়ম।"))

c.lesson("Release tag",
    term('''$ git tag -a v1.0.0 -m "First release"
$ git tag
$ git describe --tags'''),
    php_note("Composer package-এর version এই tag থেকেই আসে। CI/CD কোর্সে tag push করলেই Docker image বানানো আর deploy হবে।"))

c.section("Bash script")
c.lesson("নিরাপদ bash script",
    say("<code>set -euo pipefail</code> — কোনো command ব্যর্থ হলে script থামবে, অজানা variable ধরা পড়বে। Deploy script-এ এটা বাধ্যতামূলক।"),
    code('''
#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/root/shop
RELEASE=$(date +%Y%m%d)-$(git -C "$APP_DIR" rev-parse --short HEAD)

log() { echo "[deploy] $*"; }

log "release $RELEASE"
log "অবস্থা পরীক্ষা: $(git -C "$APP_DIR" describe --tags)"
mkdir -p "$APP_DIR/releases/$RELEASE"
git -C "$APP_DIR" archive HEAD | tar -x -C "$APP_DIR/releases/$RELEASE"
ln -sfn "$APP_DIR/releases/$RELEASE" "$APP_DIR/current"
log "current → $(readlink "$APP_DIR/current" | xargs basename)"
log "শেষ ✓"
''', "bash", file="/root/shop/deploy.sh", save=True),
    term("$ chmod +x deploy.sh && ./deploy.sh\n$ ls current/"),
    php_note("Envoyer/Deployer-এর zero-downtime deploy ঠিক এভাবে কাজ করে: নতুন <code>releases/</code> folder, তারপর <code>current</code> symlink এক নিমেষে বদলানো।"))

c.lesson("Cron: সময় ধরে কাজ",
    table(["লেখা", "মানে"], [["<code>* * * * *</code>", "প্রতি মিনিট"], ["<code>0 2 * * *</code>", "প্রতিদিন রাত ২টা"],
        ["<code>*/15 * * * *</code>", "প্রতি ১৫ মিনিট"], ["<code>0 9 * * 6</code>", "প্রতি শনিবার সকাল ৯টা"]]),
    shell("$ crontab -e\n* * * * * cd /var/www/shop && php artisan schedule:run >> /dev/null 2>&1\n0 2 * * * /opt/backup/db-backup.sh"),
    php_note("Laravel-এর scheduler (<code>routes/console.php</code>) চালাতে server-এ শুধু প্রথম লাইনটাই লাগে।"))

c.lesson("Server নিরাপত্তার চেকলিস্ট",
    table(["করুন", "কেন"], [
        ["<code>ufw allow 22,80,443/tcp</code> তারপর <code>ufw enable</code>", "বাকি সব port বন্ধ (MySQL বাইরে খোলা না)"],
        ["SSH: <code>PasswordAuthentication no</code>, <code>PermitRootLogin no</code>", "Password-guessing আক্রমণ বন্ধ"],
        ["<code>fail2ban</code>", "বারবার ভুল login-এ IP block"], ["<code>unattended-upgrades</code>", "Security update নিজে থেকে"],
        ["আলাদা <code>deploy</code> user, <code>.env</code> 600", "কম অনুমতি = কম ক্ষতি"],
        ["প্রতিদিন backup, অন্য জায়গায় রাখা, restore পরীক্ষা", "Disk নষ্ট বা ভুল DELETE থেকে রক্ষা"]]),
    task("একটা ছোট VPS নিন (বা Ubuntu container), deploy user বানান, SSH key দিয়ে ঢুকুন, Nginx বসিয়ে একটা static page দেখান।"))

c.finish("DevOps 101 শেষ! 🎉",
         "Linux, Nginx, SSH আর Git — যেকোনো server-এ app চালানোর ভিত্তি তৈরি। এবার সেই app-কে container-এ মোড়াই: Docker।",
         recap=["File, permission (<code>chmod 600 .env</code>), user, process", "grep/awk/pipe দিয়ে log বিশ্লেষণ",
                "Environment variable-এ setting", "Nginx reverse proxy + <code>nginx -t</code>",
                "SSH key, Git branch/tag", "<code>set -euo pipefail</code> deploy script, symlink release"])

if __name__ == "__main__":
    c.build()
