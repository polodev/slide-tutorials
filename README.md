# Slide Tutorials — বাংলায়

Byte-size Bangla slide tutorials. Each slide is one small idea; every code example is compiled or run
at build time, and the real output (or real compiler error) is shown on the slide.

| Folder | Tutorial |
|---|---|
| `rust-tutorial/` | Software Development 101 (jargon and foundations), Rust 101, 102, 103, Rust Web Development (axum), Rust Leptos (reactive full-stack web) and Rust Topcoat (Tokio's server-first framework), with PHP/Laravel comparisons |
| `go-tutorial/` | Go 101, 102, 103 and Go Web Development (net/http + SQLite) |
| `dart-tutorial/` | Dart 101, 102, 103 and Flutter (screenshots rendered by `flutter test`) |
| `mysql-tutorial/` | MySQL from the first table to joins, indexes and transactions |
| `postgresql-tutorial/` | PostgreSQL, including JSONB, window functions and full-text search |
| `devops-tutorial/` | DevOps 101, Docker, Kubernetes, CI/CD, Monitoring, Infrastructure as Code |
| `accounts-101/` | Accounting basics with a mobile-shop example (Dokani) |

Open `index.html` (or the GitHub Pages site). Keys: `→`/`←` change slide, `M` lesson list, `D` dark mode,
`F` fullscreen; swipe on mobile. Progress is saved in the browser, so learners can close the tab and continue later.

## Build

```bash
pip3 install pygments          # highlighting
python3 build.py               # build every tutorial + the hub page
python3 rust-tutorial/build.py # one series
python3 build.py --hub         # hub page only
```

Requirements for verifying code: `rustc`/`cargo` (Rust; Leptos also needs the wasm32 target, wasm-bindgen-cli and Playwright, see AGENTS.md), `go` (Go), `dart`/`flutter`, `php` (PHP comparisons), a local MySQL server
(`mysql -uroot`) and PostgreSQL (`psql`). Laravel snippets run through `illuminate/database`:
run `composer install` in `tutorial-kit/eloquent` once. Results are cached in `tutorial-kit/.cache` (git-ignored).

The shared engine is `tutorial-kit/kit.py`. A course is a `build.py` that creates a `Course`, adds
`lesson(...)` slides with `say`, `points`, `php_note`, `code(...)`, `task`, `quiz`, and calls `build()`.

## GitHub Pages

Settings → Pages → Deploy from a branch → `main` / `/ (root)`. The built `index.html` files are committed,
so no build step runs on GitHub.
