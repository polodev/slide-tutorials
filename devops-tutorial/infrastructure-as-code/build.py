"""Infrastructure as Code — OpenTofu (open-source Terraform): init/plan/apply/destroy, state, variables, outputs,
the Docker provider building a real network + container on Colima, modules, environments, a validated
DigitalOcean config, remote state. Every `$` command really runs. Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
import devops_env  # noqa: E402
from kit import Course, code, php_note, points, quiz, say, shell, table, task, term, tip, warn  # noqa: E402

c = Course(slug="infrastructure-as-code", title="Infrastructure as Code — OpenTofu", folder=HERE,
           subtitle="Server, network, container — হাতে click না করে কোডে লেখা: plan, apply, state, variable, module আর cloud — আসলেই চালানো",
           series="Infrastructure as Code", shell=True,
           shell_env={**devops_env.docker_env(), "TF_IN_AUTOMATION": "1", "TF_CLI_ARGS": "-no-color"})
c.shell_setup = devops_env.ensure_docker
c.shell_teardown = lambda: devops_env.remove_container("shop-web")


def tf(src, file):
    return code(src, "hcl", file=file, save=True)


c.cover("Infrastructure as Code<br>OpenTofu",
        "Cloud dashboard-এ click করে server বানালে কেউ জানে না কী কেন বানানো হয়েছিল, আর আবার বানানো কঠিন। IaC মানে infrastructure-ও কোড: Git-এ থাকে, review হয়, এক command-এ আবার বানানো যায়।",
        learn=["IaC কেন, Terraform আর OpenTofu", "init → plan → apply → destroy", "State: tofu কী মনে রাখে", "Variable, output, tfvars",
               "Docker provider: আসল container", "Module দিয়ে পুনর্ব্যবহার", "Cloud server (DigitalOcean) config", "Remote state আর টিমে কাজ"],
        need="DevOps 101 আর Docker।")

c.section("শুরু")
c.lesson("IaC কেন?",
    table(["হাতে click করে", "কোডে (IaC)"], [
        ["কী বানানো আছে কেউ নিশ্চিত না", "কোডই সত্য — Git-এ দেখা যায়"], ["নতুন environment বানাতে দিন লাগে", "এক command-এ staging = production-এর কপি"],
        ["ভুল বদল ফেরানো কঠিন", "Git revert + apply"], ["Review নেই", "PR-এ <code>plan</code> দেখে review"]]),
    points("<b>Terraform</b> (HashiCorp) — সবচেয়ে জনপ্রিয়; <b>OpenTofu</b> — একই ভাষা, open-source fork (এই কোর্সে <code>tofu</code>)",
           "<b>Ansible</b> — server-এর ভিতরে কী install হবে; Terraform — server/network/database নিজেই বানানো"),
    php_note("Laravel migration database-এর গঠন কোডে রাখে; Terraform পুরো server আর cloud-এর গঠন কোডে রাখে। <code>plan</code> ≈ <code>migrate --pretend</code>।"))

c.lesson("প্রথম config",
    tf('''
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

resource "local_file" "motd" {
  filename = "${path.module}/out/motd.txt"
  content  = "Welcome to Rahim Mobile server\\n"
}
''', "basics/main.tf"),
    term("$ cd basics && tofu version | head -1\n$ tofu init 2>&1 | grep -E 'Installing|Installed|successfully'", timeout=600),
    points("<code>resource \"type\" \"name\"</code> — কী বানাতে চাই", "<code>provider</code> — কার সাথে কথা বলবে (local, docker, aws, digitalocean...)",
           "<code>tofu init</code> — provider plugin নামায় (composer install-এর মতো)"))

c.lesson("plan আর apply",
    say("<code>plan</code> দেখায় কী বদলাবে, কিছু বদলায় না। <code>apply</code> সত্যিই করে। <code>+</code> মানে নতুন বানাবে।"),
    term('''$ tofu plan -out=tfplan | grep -E '^\\s+[+~-]|Plan:'
$ tofu apply -auto-approve tfplan | tail -2
$ cat out/motd.txt'''),
    tip("CI-তে PR-এর জন্য <code>plan</code> চালিয়ে comment-এ দেখানো হয়; merge হলে <code>apply</code>। কেউ না দেখে infrastructure বদলায় না।"))

c.lesson("State আর পরিবর্তন",
    say("Tofu একটা <b>state</b> file-এ মনে রাখে কী বানিয়েছে। কোড বদলালে state-এর সাথে মিলিয়ে শুধু পার্থক্যটুকু করে।"),
    term('''$ tofu state list
$ sed -i.bak 's/Welcome to Rahim Mobile server/Welcome to Rahim Mobile — Mirpur branch/' main.tf
$ tofu plan | grep -E '^\\s+[+~-]|Plan:|must be replaced'
$ tofu apply -auto-approve | tail -1 && cat out/motd.txt'''),
    warn("<code>terraform.tfstate</code>-এ password-সহ সব থাকতে পারে — Git-এ দেবেন না। টিমে remote state (শেষের পাঠ)।"))

c.lesson("destroy",
    term("$ tofu destroy -auto-approve | tail -1\n$ ls out/ 2>/dev/null | wc -l\n$ cd .."),
    say("যা বানিয়েছিল সব মুছে দিল। Test environment কাজ শেষে destroy করলে cloud-এর বিল বাঁচে।"))

c.section("Variable ও আসল resource")
c.lesson("Docker provider: আসল network আর container",
    say("এবার সত্যিকারের infrastructure: Docker provider দিয়ে network আর Nginx container। Cloud provider-এর সাথেও ঠিক এভাবেই কাজ হয়।"),
    tf('''
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

variable "env" {
  type        = string
  description = "staging বা production"
  default     = "staging"
}

variable "web_port" {
  type    = number
  default = 8096
}

resource "docker_network" "shop" {
  name = "shop-${var.env}"
}

resource "docker_image" "nginx" {
  name         = "nginx:1.27-alpine"
  keep_locally = true
}

resource "docker_container" "web" {
  name  = "shop-web"
  image = docker_image.nginx.image_id
  networks_advanced {
    name = docker_network.shop.name
  }
  ports {
    internal = 80
    external = var.web_port
  }
  labels {
    label = "env"
    value = var.env
  }
}

output "url" {
  value = "http://localhost:${var.web_port}"
}

output "network" {
  value = docker_network.shop.name
}
''', "docker/main.tf"),
    term('''$ cd docker && tofu init >/dev/null 2>&1 && echo "init ✓"
$ tofu apply -auto-approve -var env=production 2>&1 | grep -E 'Creation complete|Apply complete|url|network'
$ curl -s "$(tofu output -raw url)" | grep -o '<title>.*</title>'
$ docker ps --filter name=shop-web --format '{{.Names}} {{.Ports}}' ''', timeout=900),
    points("<code>variable</code> — input (ডিফল্ট সহ)", "<code>-var env=production</code> — চালানোর সময় মান", "<code>output</code> — ফলাফল থেকে দরকারি মান"))

c.lesson("Environment অনুযায়ী tfvars",
    code('env = "staging"\nweb_port = 8098\n', "hcl", file="docker/staging.tfvars", save=True),
    term('''$ tofu plan -var-file=staging.tfvars | grep -E 'must be replaced|~ name|Plan:'
$ tofu destroy -auto-approve 2>&1 | tail -1
$ cd ..''', timeout=600),
    say("Staging-এর মান দিলে tofu দেখাল network-এর নাম বদলাবে (<code>shop-production</code> → <code>shop-staging</code>) — তাই resource নতুন করে বানাতে হবে। Apply-এর আগেই প্রভাব জানা গেল।"),
    php_note("Laravel-এর <code>.env.staging</code> আর <code>.env.production</code>-এর মতো — একই কোড, আলাদা মান।"))

c.section("Module ও Cloud")
c.lesson("Module: পুনর্ব্যবহার",
    say("বারবার লাগে এমন অংশ module বানিয়ে input দিয়ে ডাকা — function-এর মতো। এক module দিয়ে তিন শাখার config।"),
    tf('''
variable "branch" { type = string }
variable "manager" { type = string }

resource "local_file" "config" {
  filename = "${path.root}/out/${var.branch}.env"
  content  = "BRANCH=${var.branch}\\nMANAGER=${var.manager}\\n"
}

output "file" {
  value = local_file.config.filename
}
''', "modules-demo/modules/branch/main.tf"),
    tf('''
locals {
  branches = {
    mirpur  = "Sabbir"
    uttara  = "Fahim"
    gulshan = "Riya"
  }
}

module "branch" {
  source   = "./modules/branch"
  for_each = local.branches
  branch   = each.key
  manager  = each.value
}

output "files" {
  value = [for m in module.branch : basename(m.file)]
}
''', "modules-demo/main.tf"),
    term('''$ cd modules-demo && tofu init >/dev/null 2>&1 && tofu apply -auto-approve 2>&1 | grep -E 'Apply complete'
$ tofu output files
$ cat out/uttara.env
$ cd ..''', timeout=600))

c.lesson("Cloud: DigitalOcean server",
    say("আসল cloud-এ একই নিয়ম। নিচের config একটা Ubuntu server, firewall আর SSH key বানায়। Account ছাড়া apply করা যায় না, কিন্তু <code>validate</code> দিয়ে সঠিকতা যাচাই হয়েছে।"),
    tf('''
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.40"
    }
  }
}

variable "do_token" {
  type      = string
  sensitive = true
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_ssh_key" "rahim" {
  name       = "rahim-laptop"
  public_key = file("~/.ssh/id_ed25519.pub")
}

resource "digitalocean_droplet" "shop" {
  name     = "shop-prod-1"
  region   = "sgp1"
  size     = "s-1vcpu-2gb"
  image    = "ubuntu-24-04-x64"
  ssh_keys = [digitalocean_ssh_key.rahim.id]
}

resource "digitalocean_firewall" "shop" {
  name        = "shop-web"
  droplet_ids = [digitalocean_droplet.shop.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0"]
  }
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80-443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

output "ip" {
  value = digitalocean_droplet.shop.ipv4_address
}
''', "cloud/main.tf"),
    term("$ cd cloud && tofu init -backend=false >/dev/null 2>&1 && tofu validate && tofu fmt -check && echo 'fmt ✓'\n$ cd ..", timeout=900),
    tip("Singapore (<code>sgp1</code>) region বাংলাদেশ থেকে সবচেয়ে কাছের — latency কম। Token কখনো কোডে না: <code>TF_VAR_do_token</code> environment variable-এ।"))

c.lesson("টিমে কাজ: remote state আর lock",
    code('''
terraform {
  backend "s3" {
    bucket                      = "rahim-tofu-state"
    key                         = "shop/production.tfstate"
    region                      = "auto"
    endpoints                   = { s3 = "https://<account-id>.r2.cloudflarestorage.com" }
    skip_credentials_validation = true
    skip_region_validation      = true
    use_lockfile                = true
  }
}
''', "hcl", run=False, file="backend.tf"),
    points("State সবার জন্য এক জায়গায় (S3, Cloudflare R2, DigitalOcean Spaces)", "<b>Lock</b> — দুজন একসাথে apply করলে state নষ্ট হয় না",
           "State-এ secret থাকে: bucket private, encryption চালু"),
    table(["কাজ", "কোথায়"], [["<code>tofu fmt</code>, <code>validate</code>, <code>plan</code>", "প্রতিটি PR-এ CI"],
        ["<code>apply</code>", "merge-এর পর CI, বা অনুমোদিত মানুষ"], ["Production বদল", "PR review + plan দেখা বাধ্যতামূলক"]]))

c.lesson("পুরো ছবি: DevOps সিরিজ এক নজরে",
    table(["ধাপ", "টুল", "এই সিরিজের কোর্স"], [
        ["Server আর cloud বানানো", "OpenTofu/Terraform", "Infrastructure as Code"], ["Server-এ ঢোকা, Nginx, Git", "Linux, SSH", "DevOps 101"],
        ["App প্যাকেজ", "Docker", "Docker"], ["অনেক server-এ চালানো", "Kubernetes", "Kubernetes"],
        ["প্রতিটি push-এ test আর deploy", "GitHub Actions", "CI/CD"], ["চলার পর নজর রাখা", "Prometheus, Grafana", "Monitoring"]]),
    task("একটা ছোট project শুরু থেকে শেষ: tofu দিয়ে server → SSH + Docker install → GitHub Actions দিয়ে image + deploy → Grafana-য় p95 দেখা।"))

c.finish("Infrastructure as Code শেষ! 🎉 DevOps সিরিজ সম্পূর্ণ",
         "Linux থেকে Kubernetes, CI/CD, monitoring আর IaC — একজন Laravel developer থেকে পুরো system চালাতে পারা engineer হওয়ার পথ এখন আপনার জানা।",
         recap=["init → plan → apply → destroy", "State মনে রাখে কী বানানো; Git-এ না, remote-এ",
                "Variable, tfvars, output", "Docker provider দিয়ে আসল container", "Module + for_each দিয়ে পুনর্ব্যবহার",
                "Cloud config validate, token environment-এ"])

if __name__ == "__main__":
    c.build()
