"""CI/CD — GitHub Actions for the Go Shop API and a Laravel app: test, matrix, cache, services, Docker image to
GHCR, deploy over SSH and to Kubernetes, environments with approval. Every workflow is checked by actionlint.
Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
import devops_env  # noqa: E402
from kit import Course, code, php_note, points, quiz, say, shell, table, task, term, tip, warn  # noqa: E402

c = Course(slug="ci-cd", title="CI/CD — GitHub Actions", folder=HERE,
           subtitle="প্রতিটি push-এ test, build আর deploy: Go API আর Laravel-এর pipeline, Docker image GHCR-এ, SSH আর Kubernetes deploy — actionlint দিয়ে যাচাই করা",
           series="CI/CD", shell=True, shell_env=devops_env.docker_env(),
           next_course=("../monitoring/index.html", "Monitoring — Prometheus ও Grafana"))


def wf(src, file, **kw):
    return code(src, "yaml", file=f".github/workflows/{file}", save=True, validate="actions", **kw)


c.cover("CI/CD<br>GitHub Actions",
        "\"Deploy করার আগে test চালিয়েছিলে?\" — এই প্রশ্ন আর লাগবে না। প্রতিটি push-এ GitHub নিজেই test চালাবে, Docker image বানাবে, আর অনুমতি পেলে server-এ পাঠাবে।",
        learn=["CI আর CD কী", "Workflow, job, step, runner", "Go API-র test pipeline", "Laravel: MySQL service সহ test",
               "Matrix আর cache", "Docker image → GitHub Container Registry", "SSH আর Kubernetes-এ deploy", "Approval সহ production"],
        need="Git, Docker; Kubernetes কোর্স করা থাকলে শেষ অংশ সহজ।")

c.section("শুরু")
c.lesson("CI আর CD",
    table(["", "মানে", "উদাহরণ"], [
        ["CI — Continuous Integration", "প্রতিটি push/PR-এ নিজে থেকে build + test", "PR-এ লাল ✗ হলে merge হবে না"],
        ["CD — Continuous Delivery", "main-এ গেলেই deploy-এর জন্য তৈরি (image, artifact)", "প্রতিটি merge-এ Docker image"],
        ["CD — Continuous Deployment", "এমনকি deploy-ও স্বয়ংক্রিয়", "tag দিলেই production-এ"]]),
    php_note("Laravel-এ <code>php artisan test</code> হাতে চালানোর অভ্যাস থাকলে — CI মানে সেটাই প্রতিবার, কেউ ভুলে না গিয়ে।"))

c.lesson("GitHub Actions-এর গঠন",
    table(["শব্দ", "মানে"], [
        ["Workflow", "<code>.github/workflows/*.yml</code> file — পুরো pipeline"], ["<code>on</code>", "কখন চলবে: push, pull_request, tag, schedule"],
        ["Job", "এক machine-এ চলা ধাপের দল; job-গুলো আলাদা machine-এ, ডিফল্টে একসাথে"],
        ["Step", "একটা command (<code>run:</code>) বা তৈরি action (<code>uses:</code>)"], ["Runner", "যে machine-এ চলে: <code>ubuntu-latest</code>"],
        ["<code>needs</code>", "এই job আগেরটা শেষ হলে চলবে"]]),
    tip("Public repo-তে GitHub Actions বিনামূল্যে; private repo-তে মাসে ২০০০ মিনিট ফ্রি।"))

c.section("CI: Test")
c.lesson("প্রথম workflow: Go API-র test",
    wf('''
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: "1.25"
          cache: true

      - name: Format check
        run: test -z "$(gofmt -l .)"

      - name: Vet
        run: go vet ./...

      - name: Test
        run: go test -race -cover ./...
''', "ci.yml"),
    points("<code>actions/checkout</code> — repo-র কোড নামায়", "<code>setup-go</code> — Go install + module cache",
           "যেকোনো step ব্যর্থ হলে (exit code ≠ 0) পুরো job লাল"),
    tip("ডানে সবুজ ✓ মানে <b>actionlint</b> file-টা যাচাই করেছে: ভুল key, ভুল expression, অজানা action version ধরা পড়ে। Push করার আগে নিজের computer-এ চালান।"))

c.lesson("Laravel CI: MySQL service সহ",
    say("<code>services</code> দিয়ে job-এর পাশে আসল MySQL container। Laravel test এর সাথে কথা বলে <code>127.0.0.1:3306</code>-এ।"),
    wf('''
name: Laravel CI

on: [push, pull_request]

jobs:
  tests:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.4
        env:
          MYSQL_DATABASE: testing
          MYSQL_ROOT_PASSWORD: secret
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping -psecret"
          --health-interval=5s --health-timeout=5s --health-retries=10

    steps:
      - uses: actions/checkout@v4

      - uses: shivammathur/setup-php@v2
        with:
          php-version: "8.3"
          extensions: mbstring, pdo_mysql
          coverage: none

      - name: Cache composer
        uses: actions/cache@v4
        with:
          path: vendor
          key: composer-${{ hashFiles('composer.lock') }}

      - run: composer install --no-interaction --prefer-dist --no-progress
      - run: cp .env.example .env && php artisan key:generate

      - name: Run tests
        env:
          DB_CONNECTION: mysql
          DB_HOST: 127.0.0.1
          DB_DATABASE: testing
          DB_USERNAME: root
          DB_PASSWORD: secret
        run: php artisan test --parallel
''', "laravel.yml"),
    php_note("Local-এ <code>phpunit.xml</code>-এ SQLite in-memory দিলে CI আরও দ্রুত; কিন্তু production MySQL হলে MySQL দিয়েই test করা নিরাপদ।"))

c.lesson("Matrix: অনেক version একসাথে",
    wf('''
name: Matrix

on: pull_request

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        php: ["8.2", "8.3", "8.4"]
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ matrix.php }}
      - run: composer install --no-interaction --no-progress
      - run: vendor/bin/pest
''', "matrix.yml"),
    say("২ OS × ৩ PHP = ৬টা job একসাথে। Package বানালে বিশেষ কাজের — সব version-এ চলে কিনা নিশ্চিত।"))

c.lesson("actionlint যা ধরে",
    code('''
name: Broken

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "${{ github.event.pull_request.title }}"
      - run: echo "${{ matrix.php }}"
      - uses: actions/setup-go@v5
        with:
          go_version: "1.25"
''', "yaml", file=".github/workflows/broken.yml", save=True),
    term("$ actionlint -no-color .github/workflows/broken.yml", err="matrix"),
    points("<code>go_version</code> — আসল নাম <code>go-version</code>", "<code>matrix</code> নেই অথচ ব্যবহার করা হয়েছে",
           "PR title সরাসরি shell-এ — script injection-এর ঝুঁকি (env দিয়ে পাঠান)"),
    warn("<code>${{ github.event.pull_request.title }}</code> সরাসরি <code>run:</code>-এ বসালে কেউ PR-এর নামে command ঢুকিয়ে চালাতে পারে। আগে <code>env:</code>-এ নিন, তারপর <code>\"$TITLE\"</code>।"))

c.section("CD: Build ও Deploy")
c.lesson("Docker image → GHCR",
    say("Tag push করলে (<code>v1.2.0</code>) image বানিয়ে GitHub Container Registry-তে। <code>GITHUB_TOKEN</code> নিজেই থাকে — আলাদা password লাগে না, শুধু <code>packages: write</code> অনুমতি।"),
    wf('''
name: Release image

on:
  push:
    tags: ["v*"]

permissions:
  contents: read
  packages: write

jobs:
  image:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=semver,pattern={{version}}
            type=sha

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
''', "release.yml"),
    tip("<code>metadata-action</code> tag থেকে <code>1.2.0</code> আর commit থেকে <code>sha-3f2a9c1</code> — দুটো tag বানায়; কোন image কোন commit থেকে, সবসময় জানা।"))

c.lesson("Secret আর environment",
    table(["কোথায়", "কী রাখবেন"], [
        ["Repo → Settings → Secrets → Actions", "<code>SSH_PRIVATE_KEY</code>, <code>KUBE_CONFIG</code>, API key"],
        ["Environment (staging/production)", "Environment-ভিত্তিক secret + approval নিয়ম"], ["Variables", "গোপন না এমন setting (<code>APP_URL</code>)"]]),
    points("Workflow-এ ব্যবহার: <code>${{ secrets.SSH_PRIVATE_KEY }}</code>", "Log-এ secret নিজে থেকে <code>***</code> হয়ে যায়",
           "Fork থেকে আসা PR-এ secret পাওয়া যায় না — নিরাপত্তার জন্য"),
    warn("<code>.env</code> repo-তে commit করে CI-তে পড়বেন না। Secret শুধু GitHub Secrets-এ।"))

c.lesson("SSH দিয়ে VPS-এ deploy",
    say("Image registry-তে গেলে server-এ ঢুকে নতুন image নামিয়ে Compose আবার চালু — ছোট project-এর জন্য সবচেয়ে সহজ CD।"),
    wf('''
name: Deploy VPS

on:
  workflow_run:
    workflows: ["Release image"]
    types: [completed]

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Add SSH key
        run: |
          mkdir -p ~/.ssh
          echo "$SSH_KEY" > ~/.ssh/id_ed25519
          chmod 600 ~/.ssh/id_ed25519
          ssh-keyscan -H "$HOST" >> ~/.ssh/known_hosts
        env:
          SSH_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          HOST: ${{ vars.SERVER_HOST }}

      - name: Pull and restart
        run: ssh "deploy@$HOST" 'cd /opt/shop && docker compose pull && docker compose up -d && docker image prune -f'
        env:
          HOST: ${{ vars.SERVER_HOST }}
''', "deploy-vps.yml"),
    php_note("Laravel হলে শেষ command-এ যোগ হবে: <code>docker compose exec app php artisan migrate --force</code>।"))

c.lesson("Kubernetes-এ deploy",
    wf('''
name: Deploy k8s

on:
  push:
    tags: ["v*"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: azure/setup-kubectl@v4

      - name: Kubeconfig
        run: |
          mkdir -p ~/.kube
          echo "$KUBE_CONFIG" | base64 -d > ~/.kube/config
        env:
          KUBE_CONFIG: ${{ secrets.KUBE_CONFIG }}

      - name: Roll out new image
        run: |
          kubectl set image deployment/shop-api api="ghcr.io/${GITHUB_REPOSITORY}:${GITHUB_REF_NAME#v}"
          kubectl rollout status deployment/shop-api --timeout=180s
''', "deploy-k8s.yml"),
    tip("বড় টিমে \"GitOps\" (Argo CD): CI শুধু Git-এ image tag বদলায়, Argo CD cluster-কে Git-এর সাথে মিলিয়ে রাখে — cluster-এর চাবি CI-কে দিতে হয় না।"))

c.lesson("পুরো pipeline: staging → approval → production",
    wf('''
name: Pipeline

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.25"
      - run: go test ./...

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.tag.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
      - id: tag
        run: echo "tag=sha-${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"
      - run: echo "docker build + push ghcr.io/${GITHUB_REPOSITORY}:${{ steps.tag.outputs.tag }}"

  staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - run: echo "deploy ${{ needs.build.outputs.tag }} to staging"

  production:
    needs: [build, staging]
    runs-on: ubuntu-latest
    environment: production
    steps:
      - run: echo "deploy ${{ needs.build.outputs.tag }} to production"
''', "pipeline.yml"),
    points("<code>needs</code> দিয়ে ক্রম: test → build → staging → production", "<code>outputs</code> দিয়ে job থেকে job-এ মান পাঠানো",
           "GitHub-এ <b>production</b> environment-এ \"Required reviewers\" দিলে deploy-এর আগে কেউ অনুমোদন দিতে হবে"))

c.lesson("ভালো অভ্যাস",
    table(["করুন", "কেন"], [
        ["main-এ branch protection: PR + সবুজ CI বাধ্যতামূলক", "ভাঙা কোড main-এ যায় না"],
        ["Action version pin (<code>@v4</code>, বা commit SHA)", "কেউ action বদলালে হঠাৎ ভাঙে না"],
        ["<code>permissions:</code> ন্যূনতম", "Token চুরি হলেও ক্ষতি কম"], ["Cache (Go module, composer, Docker layer)", "Pipeline দ্রুত"],
        ["Image tag = version/commit, <code>latest</code> না", "কোনটা চলছে জানা আর rollback সহজ"],
        ["Deploy-এর পর smoke test (<code>curl /health</code>)", "ভুল হলে সাথে সাথে জানা"]]),
    task("নিজের একটা Laravel repo-তে <code>laravel.yml</code> বসান, একটা PR খুলে CI চলতে দেখুন, তারপর branch protection চালু করুন।"))

c.finish("CI/CD শেষ! 🎉",
         "এখন প্রতিটি push-এ test, প্রতিটি tag-এ image, আর অনুমতি সাপেক্ষে deploy — সব স্বয়ংক্রিয়। কিন্তু deploy-এর পর app কেমন চলছে? সেটা Monitoring।",
         recap=["Workflow → job → step; <code>on</code>, <code>needs</code>, <code>services</code>", "Matrix আর cache",
                "<code>GITHUB_TOKEN</code> + <code>packages: write</code> → GHCR", "Secret শুধু GitHub Secrets-এ; script injection থেকে সাবধান",
                "SSH/Compose বা Kubernetes deploy", "Environment + required reviewers"])

if __name__ == "__main__":
    c.build()
