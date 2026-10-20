"""Download the DevOps toolchain (official release binaries) into tutorial-kit/.cache/bin, nothing system-wide.

    python3 tutorial-kit/fetch_devops_bins.py

Docker CLI plugins (compose, buildx) go to .cache/docker-config/cli-plugins; builds set DOCKER_CONFIG to it.
Latest versions are resolved with the GitHub API through `gh` (authenticated, no rate-limit trouble)."""
import io
import json
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
BIN = KIT / ".cache/bin"
PLUGINS = KIT / ".cache/docker-config/cli-plugins"
ARCH = {"arm64": "arm64", "x86_64": "amd64"}[platform.machine()]


def gh_release(repo):
    out = subprocess.run(["gh", "api", f"repos/{repo}/releases/latest"], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def asset(repo, pattern):
    rel = gh_release(repo)
    for a in rel["assets"]:
        if re.fullmatch(pattern, a["name"]):
            return a["browser_download_url"], rel["tag_name"]
    raise SystemExit(f"{repo}: no asset matching {pattern}: {[a['name'] for a in rel['assets']][:30]}")


def fetch(url):
    print("  ↓", url, flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": "slide-tutorials"})
    import ssl
    ctx = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
    with urllib.request.urlopen(req, context=ctx, timeout=600) as r:
        return r.read()


def install(data, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def from_tar(data, member_suffix, dest):
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        m = next(m for m in t.getmembers() if m.name.endswith(member_suffix) and m.isfile())
        install(t.extractfile(m).read(), dest)


def main():
    BIN.mkdir(parents=True, exist_ok=True)
    a = "aarch64" if ARCH == "arm64" else "x86_64"

    if not (BIN / "docker").exists():
        index = fetch(f"https://download.docker.com/mac/static/stable/{a}/").decode()
        latest = sorted(set(re.findall(r"docker-(\d+\.\d+\.\d+)\.tgz", index)), key=lambda v: tuple(map(int, v.split("."))))[-1]
        from_tar(fetch(f"https://download.docker.com/mac/static/stable/{a}/docker-{latest}.tgz"), "docker/docker", BIN / "docker")

    if not (PLUGINS / "docker-compose").exists():
        url, _ = asset("docker/compose", rf"docker-compose-darwin-{a}")
        install(fetch(url), PLUGINS / "docker-compose")
    if not (PLUGINS / "docker-buildx").exists():
        url, _ = asset("docker/buildx", rf"buildx-v[\d.]+\.darwin-{ARCH}")
        install(fetch(url), PLUGINS / "docker-buildx")

    lima = KIT / ".cache/lima"
    if not (lima / "bin/limactl").exists():
        url, _ = asset("lima-vm/lima", r"lima-[\d.]+-Darwin-" + ("arm64" if ARCH == "arm64" else "x86_64") + r"\.tar\.gz")
        lima.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(fetch(url))) as t:
            t.extractall(lima, filter="tar")
    for tool in ("limactl", "lima"):
        if (lima / "bin" / tool).exists() and not (BIN / tool).exists():
            (BIN / tool).symlink_to(lima / "bin" / tool)

    simple = {
        "colima": ("abiosoft/colima", rf"colima-Darwin-{'arm64' if ARCH == 'arm64' else 'x86_64'}"),
        "kind": ("kubernetes-sigs/kind", rf"kind-darwin-{ARCH}"),
    }
    for name, (repo, pat) in simple.items():
        if not (BIN / name).exists():
            url, _ = asset(repo, pat)
            install(fetch(url), BIN / name)

    if not (BIN / "kubectl").exists():
        v = fetch("https://dl.k8s.io/release/stable.txt").decode().strip()
        install(fetch(f"https://dl.k8s.io/release/{v}/bin/darwin/{ARCH}/kubectl"), BIN / "kubectl")

    if not (BIN / "helm").exists():
        tag = gh_release("helm/helm")["tag_name"]
        from_tar(fetch(f"https://get.helm.sh/helm-{tag}-darwin-{ARCH}.tar.gz"), "/helm", BIN / "helm")

    tars = {
        "kubeconform": ("yannh/kubeconform", rf"kubeconform-darwin-{ARCH}\.tar\.gz", "kubeconform"),
        "actionlint": ("rhysd/actionlint", rf"actionlint_[\d.]+_darwin_{ARCH}\.tar\.gz", "actionlint"),
        "prometheus": ("prometheus/prometheus", rf"prometheus-[\d.]+\.darwin-{ARCH}\.tar\.gz", "/prometheus"),
        "promtool": ("prometheus/prometheus", rf"prometheus-[\d.]+\.darwin-{ARCH}\.tar\.gz", "/promtool"),
    }
    for name, (repo, pat, member) in tars.items():
        if not (BIN / name).exists():
            url, _ = asset(repo, pat)
            from_tar(fetch(url), member, BIN / name)

    if not (BIN / "hadolint").exists():
        url, _ = asset("hadolint/hadolint", rf"hadolint-(Darwin|macos)-({'arm64' if ARCH == 'arm64' else 'x86_64'})")
        install(fetch(url), BIN / "hadolint")

    if not (BIN / "tofu").exists():
        url, _ = asset("opentofu/opentofu", rf"tofu_[\d.]+_darwin_{ARCH}\.zip")
        with zipfile.ZipFile(io.BytesIO(fetch(url))) as z:
            install(z.read("tofu"), BIN / "tofu")

    graf = KIT / ".cache/grafana"
    if not (graf / "bin/grafana").exists():
        tag = gh_release("grafana/grafana")["tag_name"].lstrip("v")
        data = fetch(f"https://dl.grafana.com/oss/release/grafana-{tag}.darwin-{ARCH}.tar.gz")
        with tarfile.open(fileobj=io.BytesIO(data)) as t:
            t.extractall(graf.parent / "grafana-extract", filter="tar")
        top = next((graf.parent / "grafana-extract").iterdir())
        if graf.exists():
            shutil.rmtree(graf)
        top.rename(graf)
        shutil.rmtree(graf.parent / "grafana-extract", ignore_errors=True)

    for f in sorted(BIN.iterdir()):
        print(f"  ✓ {f.name}")
    print(f"  ✓ docker plugins: {', '.join(p.name for p in PLUGINS.iterdir())}")
    print(f"  ✓ grafana: {graf}")


if __name__ == "__main__":
    sys.exit(main())
