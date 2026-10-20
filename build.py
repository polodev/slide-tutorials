"""Builds every tutorial and the hub page (index.html).

    python3 build.py            # everything
    python3 build.py --hub      # only the hub page

Each series folder has its own build.py; code blocks are compiled/run there (results are cached in
tutorial-kit/.cache, so rebuilding is fast)."""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "tutorial-kit"))
from kit import build_hub, series_meta  # noqa: E402

SERIES = ["rust-tutorial", "dart-tutorial", "mysql-tutorial", "postgresql-tutorial", "accounts-101"]


def tutorials():
    return [
        ("rust-tutorial", "🦀", "Rust", "শূন্য থেকে Rust, তারপর axum দিয়ে Laravel-এর মতো web API। PHP developer-দের জন্য তুলনাসহ।",
         series_meta(HERE / "rust-tutorial")),
        ("dart-tutorial", "🎯", "Dart ও Flutter", "PHP থেকে Dart, তারপর Flutter দিয়ে mobile app — প্রতিটি app-এর আসল screenshot সহ।",
         series_meta(HERE / "dart-tutorial")),
        ("mysql-tutorial", "🐬", "MySQL", "Table বানানো থেকে join, index, transaction — প্রতিটি query আসল MySQL-এ চালানো।",
         series_meta(HERE / "mysql-tutorial")),
        ("postgresql-tutorial", "🐘", "PostgreSQL", "PostgreSQL-এর শক্তি: JSONB, window function, CTE, full-text search।",
         series_meta(HERE / "postgresql-tutorial")),
        ("accounts-101", "📒", "Accounts 101", "হিসাবের মূল ধারণা একটা মোবাইল দোকানের উদাহরণে: লাভ, ক্যাশ, Balance sheet।",
         "একটি কোর্স · Dokani-র সাথে"),
    ]


if __name__ == "__main__":
    if "--hub" not in sys.argv:
        for s in SERIES:
            if (HERE / s / "build.py").exists():
                runpy.run_path(str(HERE / s / "build.py"), run_name="__main__")
    build_hub(HERE, "স্লাইড টিউটোরিয়াল — বাংলায়",
              "ছোট ছোট পাঠে programming আর ব্যবসার হিসাব। প্রতিটি স্লাইড এক মিনিটের, কোড আসলে চালানো, "
              "আর আপনার অগ্রগতি browser-এ সেভ থাকে।",
              tutorials(),
              extra='<p class="note">কীবোর্ড: <code>→</code> / <code>←</code> স্লাইড বদলান, <code>M</code> সব পাঠ, '
                    '<code>D</code> dark mode, <code>F</code> fullscreen। মোবাইলে swipe করুন।</p>')
