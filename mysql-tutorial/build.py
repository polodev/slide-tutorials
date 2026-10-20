"""Builds the four MySQL courses and the MySQL series page.  Run: python3 build.py
Needs a local MySQL 8 (mysql -uroot) and, for MySQL for Laravel, `composer install` in tutorial-kit/eloquent."""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tutorial-kit"))
from kit import build_home  # noqa: E402

COURSES = [("mysql-101", "🐬"), ("mysql-102", "🔗"), ("mysql-103", "⚡"), ("mysql-for-laravel", "🧱")]

if __name__ == "__main__":
    for folder, _ in COURSES:
        if (HERE / folder / "build.py").exists():
            runpy.run_path(str(HERE / folder / "build.py"), run_name="__main__")
    build_home(HERE, "MySQL টিউটোরিয়াল — বাংলায়",
               "একটা মোবাইল দোকানের database দিয়ে SQL: প্রথম table থেকে JOIN, index, transaction, window function — "
               "আর শেষে Eloquent আসলে কোন SQL পাঠায়। প্রতিটি query আসল MySQL 8-এ চালানো।",
               COURSES,
               extra='<p class="note">Laravel developer? <b>MySQL 101</b> থেকে শুরু করুন — প্রতিটি পাঠে Eloquent/Migration-এর তুলনা আছে। '
                     'শেষ কোর্সে Laravel কোডও আসলেই চালিয়ে query log দেখানো হয়েছে।</p>')
