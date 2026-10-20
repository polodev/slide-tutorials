"""Builds the four PostgreSQL courses and the series page.  Run: python3 build.py
Needs PostgreSQL 16/17 binaries (Homebrew postgresql@16, or set PG_BIN); the kit starts a private
throwaway cluster on port 5544, so your own PostgreSQL is never touched."""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tutorial-kit"))
from kit import build_home  # noqa: E402

COURSES = [("postgresql-101", "🐘"), ("postgresql-102", "🔗"), ("postgresql-103", "⚡"), ("postgresql-for-laravel", "🧱")]

if __name__ == "__main__":
    for folder, _ in COURSES:
        if (HERE / folder / "build.py").exists():
            runpy.run_path(str(HERE / folder / "build.py"), run_name="__main__")
    build_home(HERE, "PostgreSQL টিউটোরিয়াল — বাংলায়",
               "একই মোবাইল দোকানের database, এবার PostgreSQL-এ: RETURNING, FILTER, DISTINCT ON, JSONB, full-text, SKIP LOCKED — "
               "আর Laravel app PostgreSQL-এ চালালে কী বদলায়। প্রতিটি query আসল PostgreSQL 16-এ চালানো।",
               COURSES,
               extra='<p class="note">MySQL টিউটোরিয়াল করা থাকলে একই data-তে পার্থক্যগুলো সহজে চোখে পড়বে। '
                     'নতুন হলে <b>PostgreSQL 101</b> থেকে শুরু করুন।</p>')
