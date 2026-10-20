"""Builds the four Go courses and the series page.  Run: python3 build.py  (needs Go 1.25+)"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tutorial-kit"))
from kit import build_home  # noqa: E402

COURSES = [("go-101", "🐹"), ("go-102", "🧱"), ("go-103", "⚡"), ("go-web-development", "🌐")]

if __name__ == "__main__":
    for folder, _ in COURSES:
        if (HERE / folder / "build.py").exists():
            runpy.run_path(str(HERE / folder / "build.py"), run_name="__main__")
    build_home(HERE, "Go টিউটোরিয়াল — বাংলায়",
               "PHP/Laravel developer-দের জন্য Go: ছোট ভাষা, দ্রুত binary, goroutine — শেষে framework ছাড়াই একটা পুরো API। "
               "Docker, Kubernetes, Grafana — DevOps-এর বেশিরভাগ টুল Go-তে লেখা। প্রতিটি কোড go run/go test দিয়ে চালানো।",
               COURSES,
               extra='<p class="note">শুরু করুন <b>Go 101</b> থেকে। Go Web Development শেষে DevOps টিউটোরিয়ালে এই API-টাই Docker আর Kubernetes-এ চালানো হবে।</p>')
