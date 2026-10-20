"""Builds the DevOps courses and the series page.  Run: python3 build.py
Needs `python3 tutorial-kit/fetch_devops_bins.py` once (Colima/Docker/kind/kubectl/helm/Prometheus/Grafana/OpenTofu
into tutorial-kit/.cache — nothing system-wide). Terminal sessions are cached; unchanged courses do not re-run."""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tutorial-kit"))
from kit import build_home  # noqa: E402

COURSES = [("devops-101", "🐧"), ("docker", "🐳"), ("kubernetes", "☸️"), ("ci-cd", "🔁"),
           ("monitoring", "📈"), ("infrastructure-as-code", "🏗️")]

if __name__ == "__main__":
    only = sys.argv[1:]
    for folder, _ in COURSES:
        if (HERE / folder / "build.py").exists() and (not only or folder in only):
            runpy.run_path(str(HERE / folder / "build.py"), run_name="__main__")
    build_home(HERE, "DevOps টিউটোরিয়াল — বাংলায়",
               "Laravel developer থেকে পুরো system চালানো: Linux, Docker, Kubernetes, GitHub Actions, Prometheus/Grafana আর "
               "OpenTofu। প্রতিটি command আসল Ubuntu, Docker, Kubernetes cluster, Prometheus আর Grafana-য় চালিয়ে আউটপুট বসানো।",
               COURSES,
               extra='<p class="note">ক্রম: DevOps 101 → Docker → Kubernetes → CI/CD → Monitoring → Infrastructure as Code। '
                     'উদাহরণের app হলো Go টিউটোরিয়ালের Shop API — আগে Go Web Development দেখে নিলে আরও সহজ।</p>')
