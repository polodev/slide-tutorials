"""Shared setup for the DevOps courses: a Docker engine (Colima on macOS) and an Ubuntu 'lab' container
where Linux commands run, so terminal output on the slides is real Linux output."""
import os
import shutil
import subprocess
import time


KIT_CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tutorial-kit", ".cache")


def docker_env():
    """Kit-local toolchain first on PATH (tutorial-kit/fetch_devops_bins.py), docker CLI plugins from the kit,
    and the docker CLI pointed at Colima's socket."""
    sock = os.path.expanduser("~/.colima/default/docker.sock")
    return {
        "PATH": os.path.join(KIT_CACHE, "bin") + os.pathsep + os.environ.get("PATH", ""),
        "DOCKER_CONFIG": os.path.join(KIT_CACHE, "docker-config"),
        "DOCKER_HOST": f"unix://{sock}",
        "KUBECONFIG": os.path.join(KIT_CACHE, "kubeconfig"),
    }


def ensure_docker():
    env = {**os.environ, **docker_env()}
    if subprocess.run(["docker", "info"], capture_output=True, env=env).returncode == 0:
        return
    if not shutil.which("colima", path=env["PATH"]):
        raise SystemExit("Docker engine not running; run tutorial-kit/fetch_devops_bins.py first")
    print("  … starting colima (Linux VM for Docker)", flush=True)
    subprocess.run(["colima", "start", "--vm-type", "vz", "--cpu", "4", "--memory", "6", "--disk", "40"], check=True, env=env)
    for _ in range(60):
        if subprocess.run(["docker", "info"], capture_output=True, env=env).returncode == 0:
            return
        time.sleep(2)
    raise SystemExit("docker did not come up")


def lab_container(name="devops-lab", image="ubuntu:24.04", packages=()):
    """Fresh Ubuntu container with the given apt packages; returns its name."""
    env = {**os.environ, **docker_env()}
    ensure_docker()
    subprocess.run(["docker", "rm", "-f", name], capture_output=True, env=env)
    subprocess.run(["docker", "run", "-d", "--name", name, "--hostname", "shop-server", image, "sleep", "infinity"],
                   check=True, capture_output=True, env=env)
    if packages:
        print(f"  … apt install {' '.join(packages)}", flush=True)
        subprocess.run(["docker", "exec", name, "bash", "-c",
                        "export DEBIAN_FRONTEND=noninteractive && apt-get update -qq && "
                        f"apt-get install -y -qq --no-install-recommends {' '.join(packages)} >/dev/null"],
                       check=True, env=env)
    return name


def remove_container(name="devops-lab"):
    env = {**os.environ, **docker_env()}
    subprocess.run(["docker", "rm", "-f", name], capture_output=True, env=env)
