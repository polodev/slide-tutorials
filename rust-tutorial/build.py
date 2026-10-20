"""Builds the four Rust courses and the Rust series page.  Run: python3 build.py"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tutorial-kit"))
from kit import build_home  # noqa: E402

COURSES = [("rust-101", "🦀"), ("rust-102", "🔐"), ("rust-103", "⚙️"), ("rust-web-development", "🌐")]

if __name__ == "__main__":
    for folder, _ in COURSES:
        if (HERE / folder / "build.py").exists():
            runpy.run_path(str(HERE / folder / "build.py"), run_name="__main__")
    build_home(HERE, "Rust টিউটোরিয়াল — বাংলায়",
               "PHP/Laravel developer-দের জন্য ছোট ছোট পাঠে Rust: শূন্য থেকে শুরু করে Laravel-এর মতো web API পর্যন্ত। "
               "প্রতিটি কোড compile করে চালানো, আউটপুটও আসল।",
               COURSES,
               extra='<p class="note">শুরু করুন <b>Rust 101</b> থেকে, তারপর ক্রমানুসারে। অগ্রগতি এই browser-এ সেভ থাকে — '
                     'যেকোনো সময় এসে <b>চালিয়ে যান</b> চাপুন।</p>')
