"""Builds the Dart courses, the Flutter course and the series page.  Run: python3 build.py
Needs the Dart and Flutter SDKs; Flutter lessons are analyzed, widget-tested and screenshotted."""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tutorial-kit"))
from kit import build_home  # noqa: E402

COURSES = [("dart-101", "🎯"), ("dart-102", "🧩"), ("dart-103", "⏳"), ("flutter", "📱")]

if __name__ == "__main__":
    for folder, _ in COURSES:
        if (HERE / folder / "build.py").exists():
            runpy.run_path(str(HERE / folder / "build.py"), run_name="__main__")
    build_home(HERE, "Dart ও Flutter টিউটোরিয়াল — বাংলায়",
               "PHP developer-দের জন্য Dart — তারপর Flutter দিয়ে একটা দোকানের mobile app। প্রতিটি Dart কোড চালানো, "
               "আর প্রতিটি Flutter app-এর পাশে তার আসল screenshot।",
               COURSES,
               extra='<p class="note">Flutter শিখতে চাইলেও আগে <b>Dart 101–103</b> করুন — Flutter-এর প্রায় সব সমস্যা আসলে Dart না জানার সমস্যা।</p>')
