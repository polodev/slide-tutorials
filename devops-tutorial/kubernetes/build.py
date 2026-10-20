"""Kubernetes — a real kind cluster: Pod, Deployment, self-healing, scaling, Service, ConfigMap/Secret, probes,
resources, rolling update/rollback, PVC, namespace, Ingress, debugging, Helm, Laravel layout.
Every manifest is validated with kubeconform; every `$` command runs against the cluster. Run: python3 build.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tutorial-kit"))
sys.path.insert(0, str(HERE.parent))
import devops_env  # noqa: E402
from kit import Course, code, php_note, points, quiz, say, shell, table, task, term, tip, warn  # noqa: E402

API_SRC = (ROOT / "go-tutorial/go-web-development/go-shop-api/main.go").read_text()
GO_MOD = "module shop-api\n\ngo 1.25\n\nrequire modernc.org/sqlite v1.40.1\n"
DOCKERFILE = '''FROM golang:1.25 AS build
WORKDIR /src
COPY . .
RUN go mod tidy && CGO_ENABLED=0 go build -ldflags="-s -w" -o /shop-api .

FROM gcr.io/distroless/static-debian12
COPY --from=build /shop-api /shop-api
ENV APP_ADDR=0.0.0.0:3000 DATABASE_PATH=/data/shop.db
USER nonroot
EXPOSE 3000
ENTRYPOINT ["/shop-api"]'''
KUBE = dict(save=True, validate="kube")

c = Course(slug="kubernetes", title="Kubernetes — অনেক container একসাথে", folder=HERE,
           subtitle="আসল cluster-এ: Pod, Deployment, self-healing, Service, ConfigMap, probe, rolling update, storage, Ingress আর Helm",
           series="Kubernetes", shell=True, shell_env=devops_env.docker_env(),
           next_course=("../ci-cd/index.html", "CI/CD — GitHub Actions"))
c.shell_setup = devops_env.ensure_docker
c.shell_teardown = lambda: __import__("subprocess").run(["kind", "delete", "cluster", "--name", "shop"], capture_output=True,
                                                         env={**__import__("os").environ, **devops_env.docker_env()})

c.cover("Kubernetes<br>অনেক container একসাথে",
        "Docker একটা container চালায়। Kubernetes শত শত container চালায় — কোনোটা মরলে নিজে আবার চালায়, ভিড় বাড়লে copy বাড়ায়, নতুন version দেয় downtime ছাড়া। এই কোর্সের সব command একটা আসল (kind) cluster-এ চালানো।",
        learn=["Kubernetes কেন, cluster-এর গঠন", "Pod আর Deployment", "Self-healing আর scaling", "Service দিয়ে খুঁজে পাওয়া",
               "ConfigMap, Secret, probe, resource", "Rolling update আর rollback", "Volume, namespace, Ingress", "Debug আর Helm"],
        need="Docker কোর্স (image, container, port, volume)।")

c.section("শুরু")
c.lesson("Kubernetes কেন?",
    table(["সমস্যা", "Kubernetes-এর উত্তর"], [
        ["Container crash করল", "নিজে থেকে নতুন container চালায় (self-healing)"],
        ["ভিড় বাড়ল", "<code>replicas: 3</code> → ১০ — এক লাইনে"],
        ["নতুন version দিতে হবে", "Rolling update: একটা একটা করে বদলায়, downtime নেই"],
        ["ভুল version গেল", "<code>kubectl rollout undo</code> — আগেরটায় ফেরত"],
        ["অনেক server", "Kubernetes ঠিক করে কোন container কোন server-এ চলবে"]]),
    php_note("Laravel Forge/Envoyer একটা-দুটো server সামলায়। Kubernetes বড় system-এর জন্য — ছোট app-এ একটা VPS + Docker Compose-ই যথেষ্ট, সেটাও মনে রাখুন।"))

c.lesson("Cluster-এর গঠন",
    table(["অংশ", "কাজ"], [
        ["Control plane", "Cluster-এর মাথা: কী চলা উচিত মনে রাখে আর সেই অবস্থায় রাখে"],
        ["Node", "একটা machine (VM/server) যেখানে container চলে"], ["Pod", "সবচেয়ে ছোট একক: এক বা একাধিক container একসাথে"],
        ["Deployment", "\"এই image-এর ৩টা Pod সবসময় চালু রাখো\""], ["Service", "Pod-গুলোর জন্য একটা স্থির নাম আর IP"],
        ["kubectl", "Cluster-কে নির্দেশ দেওয়ার command"]]),
    tip("মূল ভাবনা: আপনি YAML-এ লেখেন <b>কী চান</b> (desired state), Kubernetes বারবার মিলিয়ে দেখে আর সেই অবস্থায় আনে। কীভাবে করবে সেটা তার কাজ।"))

c.lesson("Cluster বানানো (kind)",
    say("<b>kind</b> = Kubernetes in Docker — নিজের computer-এ শেখার জন্য আসল cluster। Port 8095-কে cluster-এর ভিতরের 80-তে জুড়ে দিচ্ছি, পরে Ingress-এ লাগবে।"),
    code('''
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: shop
nodes:
  - role: control-plane
    labels:
      ingress-ready: "true"
    extraPortMappings:
      - containerPort: 80
        hostPort: 8095
''', "yaml", file="kind.yaml", save=True),
    term("$ kind create cluster --config kind.yaml --wait 120s 2>&1 | grep -E '✓|Set kubectl'\n$ kubectl get nodes", timeout=1200),
    points("Production-এ: DigitalOcean (DOKS), AWS (EKS), Google (GKE) — managed cluster", "শেখার জন্য: kind, minikube, k3d, Docker Desktop"))

c.section("Workload")
c.lesson("প্রথম Pod",
    code('''
apiVersion: v1
kind: Pod
metadata:
  name: hello
  labels:
    app: hello
spec:
  containers:
    - name: web
      image: nginx:1.27-alpine
      ports:
        - containerPort: 80
''', "yaml", file="pod.yaml", **KUBE),
    term('''$ kubectl apply -f pod.yaml
$ kubectl wait --for=condition=Ready pod/hello --timeout=180s
$ kubectl get pods -o wide | cut -c1-70
$ kubectl exec hello -- nginx -v
$ kubectl delete pod hello --wait=false''', timeout=600),
    warn("সরাসরি Pod বানানো শুধু শেখার জন্য — Pod মরলে কেউ আবার চালায় না। আসল কাজে সবসময় Deployment।"))

c.lesson("আমাদের API-র image cluster-এ",
    say("Docker কোর্সের Shop API image বানিয়ে kind cluster-এ ঢুকিয়ে দিই (আসল জীবনে cluster image নেয় registry থেকে)।"),
    code(API_SRC, "go", file="shop-api/main.go", save=True, hidden=True),
    code(GO_MOD, "text", file="shop-api/go.mod", save=True, hidden=True),
    code(DOCKERFILE, "dockerfile", file="shop-api/Dockerfile", save=True, hidden=True),
    term('''$ docker build -q -t shop-api:1.0 shop-api >/dev/null && echo "image তৈরি"
$ kind load docker-image shop-api:1.0 --name shop 2>&1 | tail -1''', timeout=1800))

c.lesson("Deployment",
    code('''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shop-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: shop-api
  template:
    metadata:
      labels:
        app: shop-api
    spec:
      containers:
        - name: api
          image: shop-api:1.0
          ports:
            - containerPort: 3000
''', "yaml", file="deployment.yaml", **KUBE),
    term('''$ kubectl apply -f deployment.yaml
$ kubectl rollout status deployment/shop-api --timeout=180s
$ kubectl get deployment,pods -l app=shop-api''', timeout=600),
    points("<code>replicas: 2</code> — সবসময় ২টা Pod", "<code>selector</code> + <code>labels</code> — কোন Pod এই Deployment-এর", "<code>template</code> — Pod দেখতে কেমন হবে"))

c.lesson("Self-healing: Pod মুছে দেখি",
    term('''$ kubectl delete pod -l app=shop-api --wait=false | head -1
$ kubectl wait --for=condition=Available deployment/shop-api --timeout=120s
$ kubectl get pods -l app=shop-api'''),
    say("Pod মুছে দিলাম — Deployment দেখল ২টা থাকার কথা, সাথে সাথে নতুন Pod বানাল (নাম আর AGE দেখুন)। Server-এ app crash করলে রাতে উঠে restart করতে হয় না।"))

c.lesson("Scaling",
    term('''$ kubectl scale deployment/shop-api --replicas=4
$ kubectl rollout status deployment/shop-api --timeout=120s
$ kubectl get pods -l app=shop-api --no-headers | wc -l
$ kubectl scale deployment/shop-api --replicas=2'''),
    tip("HorizontalPodAutoscaler (HPA) CPU দেখে নিজেই replicas বাড়ায়-কমায় — পরে দেখব।"))

c.section("Network ও Config")
c.lesson("Service: একটা স্থির নাম",
    say("Pod-এর IP বদলায়। <b>Service</b> সব Pod-এর সামনে একটা স্থির নাম (<code>shop-api</code>) আর load balance করে।"),
    code('''
apiVersion: v1
kind: Service
metadata:
  name: shop-api
spec:
  selector:
    app: shop-api
  ports:
    - port: 80
      targetPort: 3000
''', "yaml", file="service.yaml", **KUBE),
    term('''$ kubectl apply -f service.yaml
$ kubectl get service shop-api
$ kubectl run curl --rm -i --restart=Never --image=curlimages/curl:8.10.1 -- -s http://shop-api/api/v1/products 2>/dev/null | head -1''', timeout=600),
    php_note("Docker Compose-এ যেমন container নাম দিয়ে খুঁজে পাওয়া যেত, Kubernetes-এ Service নাম দিয়ে — Laravel-এর <code>DB_HOST=mysql</code> এখানে Service-এর নাম।"))

c.lesson("port-forward: নিজের computer থেকে",
    term('''$ kubectl port-forward service/shop-api 8091:80 >/dev/null 2>&1 &
$ sleep 2 && curl -s -X POST localhost:8091/api/v1/products -H 'X-Api-Key: secret-123' -H 'Content-Type: application/json' -d '{"name":"Redmi 13","brand":"Xiaomi","price":17500,"stock":5}'
$ kill %1'''),
    warn("লক্ষ্য করুন: ২টা Pod-এর প্রতিটির নিজের SQLite file — একটায় লেখা data অন্যটায় নেই! Stateless app-এর data বাইরে (MySQL/PostgreSQL) রাখতে হয়। এটা পরের পাঠগুলোর বড় শিক্ষা।"))

c.lesson("ConfigMap আর Secret",
    say("Setting কোডে বা image-এ না — ConfigMap-এ। Password/API key Secret-এ। দুটোই Pod-এ environment variable হয়ে ঢোকে।"),
    code('''
apiVersion: v1
kind: ConfigMap
metadata:
  name: shop-config
data:
  APP_ADDR: "0.0.0.0:3000"
  DATABASE_PATH: "/data/shop.db"
---
apiVersion: v1
kind: Secret
metadata:
  name: shop-secret
type: Opaque
stringData:
  API_KEY: "k8s-secret-123"
''', "yaml", file="config.yaml", **KUBE),
    term('''$ kubectl apply -f config.yaml
$ kubectl get secret shop-secret -o jsonpath='{.data.API_KEY}' && echo
$ kubectl get secret shop-secret -o jsonpath='{.data.API_KEY}' | base64 -d && echo'''),
    warn("Secret শুধু base64 — encryption না! যার cluster-এ পড়ার অনুমতি আছে সে দেখতে পায়। Production-এ RBAC দিয়ে সীমিত করুন, বা External Secrets/Sealed Secrets ব্যবহার করুন।"))

c.lesson("Probe আর resource limit",
    say("<b>readinessProbe</b>: তৈরি হলে তবেই traffic। <b>livenessProbe</b>: আটকে গেলে restart। <b>resources</b>: কত CPU/memory চাই আর সর্বোচ্চ কত।"),
    code('''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shop-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: shop-api
  template:
    metadata:
      labels:
        app: shop-api
    spec:
      containers:
        - name: api
          image: shop-api:1.0
          ports:
            - containerPort: 3000
          envFrom:
            - configMapRef:
                name: shop-config
            - secretRef:
                name: shop-secret
          readinessProbe:
            httpGet:
              path: /api/v1/products
              port: 3000
            periodSeconds: 5
          livenessProbe:
            tcpSocket:
              port: 3000
            periodSeconds: 10
          resources:
            requests:
              cpu: 50m
              memory: 32Mi
            limits:
              cpu: 500m
              memory: 128Mi
''', "yaml", file="deployment-v2.yaml", **KUBE),
    term('''$ kubectl apply -f deployment-v2.yaml
$ kubectl rollout status deployment/shop-api --timeout=180s
$ kubectl exec deploy/shop-api -- /shop-api -h 2>/dev/null; kubectl get pods -l app=shop-api -o jsonpath='{range .items[*]}{.metadata.name}{"  ready="}{.status.containerStatuses[0].ready}{"\\n"}{end}' '''),
    php_note("<code>memory: 128Mi</code> ছাড়ালে Kubernetes container মেরে ফেলে (OOMKilled) — PHP-র <code>memory_limit</code>-এর মতো, কিন্তু পুরো container-এর জন্য।"))

c.section("Update ও Storage")
c.lesson("Rolling update",
    say("নতুন image (<code>1.1</code>) দিলে Kubernetes একটা নতুন Pod চালু করে, ready হলে একটা পুরনো বন্ধ করে — এভাবে একটা একটা। User কোনো downtime টের পায় না।"),
    term('''$ docker tag shop-api:1.0 shop-api:1.1 && kind load docker-image shop-api:1.1 --name shop >/dev/null 2>&1 && echo "1.1 লোড হলো"
$ kubectl set image deployment/shop-api api=shop-api:1.1
$ kubectl rollout status deployment/shop-api --timeout=180s
$ kubectl rollout history deployment/shop-api''', timeout=900))

c.lesson("ভুল version: rollback",
    term('''$ kubectl set image deployment/shop-api api=shop-api:9.9
$ sleep 20 && kubectl get pods -l app=shop-api | grep -E 'NAME|ErrImage|ImagePull|Running'
$ kubectl rollout undo deployment/shop-api
$ kubectl rollout status deployment/shop-api --timeout=180s
$ kubectl get deploy shop-api -o jsonpath='{.spec.template.spec.containers[0].image}' && echo''', timeout=600),
    say("<code>9.9</code> image নেই — নতুন Pod <code>ErrImagePull</code>/<code>ImagePullBackOff</code>-এ আটকে গেল, কিন্তু পুরনো Pod-গুলো চলতেই থাকল (readiness probe-এর কল্যাণে)। <code>rollout undo</code> দিয়ে এক command-এ আগের version।"))

c.lesson("PersistentVolumeClaim: স্থায়ী data",
    say("Pod মুছলে তার file যায়। <b>PVC</b> দিয়ে disk চাই, Pod সেটা mount করে। এক replica SQLite-এর জন্য যথেষ্ট (বেশি replica হলে আসল database লাগে)।"),
    code('''
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shop-data
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 1Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shop-db-api
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: shop-db-api
  template:
    metadata:
      labels:
        app: shop-db-api
    spec:
      containers:
        - name: api
          image: shop-api:1.0
          env:
            - name: API_KEY
              value: secret-123
          volumeMounts:
            - name: data
              mountPath: /data
      securityContext:
        fsGroup: 65532
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: shop-data
''', "yaml", file="pvc.yaml", **KUBE),
    term('''$ kubectl apply -f pvc.yaml && kubectl rollout status deploy/shop-db-api --timeout=180s
$ kubectl exec deploy/shop-db-api -- /shop-api 2>/dev/null; kubectl port-forward deploy/shop-db-api 8092:3000 >/dev/null 2>&1 & sleep 2
$ curl -s -o /dev/null -w 'POST %{http_code}\\n' -X POST localhost:8092/api/v1/products -H 'X-Api-Key: secret-123' -H 'Content-Type: application/json' -d '{"name":"Vivo Y28","brand":"Vivo","price":18000,"stock":4}'
$ kill %1; kubectl delete pod -l app=shop-db-api --wait=true >/dev/null && kubectl rollout status deploy/shop-db-api --timeout=180s >/dev/null && echo "পুরনো Pod মুছে নতুন Pod চালু"
$ kubectl port-forward deploy/shop-db-api 8092:3000 >/dev/null 2>&1 & sleep 2; curl -s localhost:8092/api/v1/products; kill %1
$ kubectl get pvc shop-data''', timeout=900),
    tip("MySQL/PostgreSQL cluster-এর ভিতরে চালাতে StatefulSet লাগে — কিন্তু অনেকে managed database (RDS, DigitalOcean Managed DB) নেন, আর শুধু app Kubernetes-এ রাখেন। নতুনদের জন্য সেটাই ভালো।"))

c.lesson("Namespace",
    term('''$ kubectl create namespace staging
$ kubectl -n staging create deployment web --image=nginx:1.27-alpine >/dev/null
$ kubectl get deployments --all-namespaces | grep -E 'NAMESPACE|web|shop'
$ kubectl delete namespace staging --wait=false'''),
    points("একই cluster-এ staging আর production আলাদা রাখা", "প্রতিটি team-এর জন্য আলাদা namespace আর resource quota",
           "<code>kubectl config set-context --current --namespace=staging</code> — ডিফল্ট বদলানো"))

c.section("Ingress, Debug ও Helm")
c.lesson("Ingress: domain দিয়ে বাইরে থেকে",
    say("Ingress controller (এখানে ingress-nginx) cluster-এর দরজা: host/path দেখে ঠিক Service-এ পাঠায়, HTTPS সামলায়। Nginx reverse proxy-র Kubernetes রূপ।"),
    term('''$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/kind/deploy.yaml >/dev/null
$ kubectl -n ingress-nginx wait --for=condition=Ready pod -l app.kubernetes.io/component=controller --timeout=300s''', timeout=900),
    code('''
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shop
spec:
  ingressClassName: nginx
  rules:
    - host: shop.localhost
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: shop-api
                port:
                  number: 80
''', "yaml", file="ingress.yaml", **KUBE),
    term('''$ kubectl apply -f ingress.yaml && sleep 15
$ curl -s -o /dev/null -w '%{http_code}\\n' -H 'Host: shop.localhost' localhost:8095/api/v1/products
$ curl -s -o /dev/null -w '%{http_code}\\n' -H 'Host: other.localhost' localhost:8095/api/v1/products''', timeout=600),
    tip("HTTPS-এর জন্য cert-manager + Let's Encrypt — Ingress-এ শুধু একটা annotation আর <code>tls</code> block।"))

c.lesson("Debug: কী ভুল হলো",
    term('''$ kubectl create deployment broken --image=nginx:does-not-exist >/dev/null
$ sleep 25 && kubectl get pods -l app=broken
$ kubectl describe pod -l app=broken | grep -E 'Failed|Back-off' | head -2 | cut -c1-110
$ kubectl delete deployment broken''', timeout=600),
    table(["অবস্থা", "মানে", "দেখুন"], [
        ["<code>ImagePullBackOff</code>", "Image নামাতে পারছে না", "নাম/tag, registry login"],
        ["<code>CrashLoopBackOff</code>", "চালু হয়েই মরে যাচ্ছে", "<code>kubectl logs POD --previous</code>"],
        ["<code>Pending</code>", "কোথাও জায়গা নেই", "<code>kubectl describe pod</code> → Events"],
        ["<code>OOMKilled</code>", "Memory limit ছাড়িয়েছে", "<code>resources.limits.memory</code>"]]))

c.lesson("Helm: Kubernetes-এর Composer",
    say("এত YAML বারবার লেখা ক্লান্তিকর। <b>Helm chart</b> হলো template + মান (<code>values.yaml</code>) — একই chart দিয়ে staging আর production, শুধু মান আলাদা। MySQL, Redis, Grafana — সবার তৈরি chart আছে।"),
    term('''$ helm create shopchart >/dev/null && ls shopchart
$ helm install shop ./shopchart --set image.repository=nginx --set image.tag=1.27-alpine --wait --timeout 180s >/dev/null && echo "installed"
$ helm list --short
$ helm upgrade shop ./shopchart --reuse-values --set replicaCount=2 --wait --timeout 180s >/dev/null && kubectl get deploy shop-shopchart
$ helm uninstall shop''', timeout=900),
    php_note("<code>composer require</code>-এর মতো: <code>helm install redis oci://registry-1.docker.io/bitnamicharts/redis</code> — এক লাইনে Redis cluster।"))

c.lesson("Laravel on Kubernetes: কোন অংশ কোথায়",
    table(["Laravel অংশ", "Kubernetes object"], [
        ["Web (php-fpm + nginx)", "Deployment (২+ replicas) + Service + Ingress"], ["Queue worker", "আলাদা Deployment: <code>php artisan queue:work</code>"],
        ["Scheduler", "CronJob: প্রতি মিনিট <code>php artisan schedule:run</code>"], ["Migration", "Job (deploy-এর আগে একবার)"],
        ["<code>.env</code>", "ConfigMap + Secret"], ["Session/cache", "Redis (পাশে চালানো বা managed)"],
        ["Upload file", "S3/R2 — Pod-এর disk-এ না"], ["Database", "Managed MySQL/PostgreSQL"]]),
    code('''
apiVersion: batch/v1
kind: CronJob
metadata:
  name: laravel-scheduler
spec:
  schedule: "* * * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: scheduler
              image: ghcr.io/rahim/shop-laravel:1.0
              command: ["php", "artisan", "schedule:run"]
              envFrom:
                - secretRef:
                    name: laravel-env
''', "yaml", file="laravel-scheduler.yaml", **KUBE))

c.lesson("পরিষ্কার আর এরপর",
    term("$ kind delete cluster --name shop 2>&1 | tail -1"),
    table(["শিখুন", "কেন"], [["HPA + metrics-server", "চাপ অনুযায়ী নিজে scale"], ["cert-manager", "স্বয়ংক্রিয় HTTPS"],
        ["Argo CD / Flux (GitOps)", "Git-এ YAML বদলালেই cluster বদলায়"], ["Kustomize", "Environment অনুযায়ী YAML বদল"],
        ["RBAC, NetworkPolicy", "কে কী করতে পারবে, কে কার সাথে কথা বলবে"]]),
    tip("প্রথম production cluster managed নিন (DOKS/EKS/GKE) — control plane তারা সামলায়, আপনি app-এ মন দেন।"))

c.finish("Kubernetes শেষ! 🎉",
         "আসল cluster-এ app চালানো, নিজে সেরে ওঠা, scale, update, rollback, storage, Ingress আর Helm — সব হাতে-কলমে। এবার এই সব কাজ প্রতিটি git push-এ স্বয়ংক্রিয়: CI/CD।",
         recap=["Deployment = desired state; Pod মরলে নতুন Pod", "Service = স্থির নাম; Ingress = বাইরের দরজা",
                "ConfigMap/Secret → env; probe আর resource limit", "Rolling update আর <code>rollout undo</code>",
                "Stateless app; data PVC বা managed DB-তে", "Helm = template + values"])

if __name__ == "__main__":
    c.build()
