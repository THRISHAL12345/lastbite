"""Rebuild the capstone PDF deck: pip install reportlab; python demo/build_slides.py."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit

ROOT = Path(__file__).resolve().parent
W, H = 960, 540
slides = [
    ("LastBite", "Good food. Second chance.", [
        "DevSecOps capstone | Python, React and PostgreSQL",
        "Surplus meal listings, stock reservations and code-verified pickup",
    ]),
    ("The application", "Restaurant surplus becomes someone's next meal", [
        "Publish a meal box with stock, prices, allergens and a pickup window.",
        "Reserve available boxes; prevent overselling with atomic stock updates.",
        "Cancel to release stock, or confirm collection using the pickup code.",
        "Only collected boxes count toward meals rescued and savings.",
    ]),
    ("Technology stack", "A complete application and delivery platform", [
        "Interface: React and Vite, served by unprivileged Nginx.",
        "API and data: FastAPI, SQLAlchemy, PostgreSQL and Alembic.",
        "Delivery: GitHub Actions, Docker, Trivy, GHCR and Argo CD.",
        "Operations: Terraform, AWS EKS, Helm, Prometheus and Grafana.",
    ]),
    ("Runtime architecture", "One browser origin; separate application services", [
        "Browser requests enter through the Kubernetes Ingress controller.",
        "The / route serves React; /api routes to the FastAPI service.",
        "FastAPI persists listings and reservations in PostgreSQL on a volume.",
        "Prometheus scrapes /metrics; Grafana displays traffic and latency.",
    ]),
    ("CI and release promotion", "Only scanned images reach the registry", [
        "A push or pull request runs API tests, a UI build and infrastructure checks.",
        "CI builds both images, then scans each for HIGH and CRITICAL findings.",
        "A successful main build pushes those exact images using the source SHA.",
        "A reviewed release-values commit tells Argo CD which images to deploy.",
    ]),
    ("AWS infrastructure", "Terraform defines the network and cluster", [
        "Two public and two private subnets span two availability zones.",
        "Private EKS worker nodes use a NAT gateway for outbound access.",
        "The API permits only configured administrator CIDRs.",
        "The EBS CSI driver provides encrypted gp3 persistent storage.",
    ]),
    ("Kubernetes and GitOps", "Database readiness precedes application traffic", [
        "Argo CD first creates PostgreSQL, then runs an Alembic migration job.",
        "Backend readiness requires the migrated database; liveness stays cheap.",
        "Two frontend replicas and a backend HPA support the deployment demo.",
        "Passwords come from a Kubernetes Secret created outside Git.",
    ]),
    ("Observability", "Metrics make failures and load visible", [
        "Dashboard panels show request rate, P95 latency, errors and replicas.",
        "ServiceMonitor labels connect the backend to Prometheus discovery.",
        "Alert rules detect sustained errors and missing scrape targets.",
        "The load script creates API traffic; CPU scaling depends on actual load.",
    ]),
    ("Engineering lessons", "The details between tools determine reliability", [
        "A security scan needs an explicit nonzero exit code to stop promotion.",
        "Service names, ingress ports and Nginx upstreams must agree.",
        "Schema migration belongs in one job, not every application replica.",
        "Concurrent API tests verify stock, pickup rules and migration behavior.",
    ]),
    ("Live demonstration", "Evidence to capture in the final recording", [
        "Publish, reserve, cancel and collect a meal box; show updated impact.",
        "Show a real CI run, image scans, SHA tags and Argo CD sync.",
        "Show Terraform output, healthy pods, Prometheus targets and Grafana.",
        "Explain the isolated failure lab, then record infrastructure cleanup.",
    ]),
]
c = canvas.Canvas(str(ROOT/'slides.pdf'), pagesize=(W,H))
c.setTitle('LastBite - DevSecOps Capstone')
c.setAuthor('LastBite project')
for number, (title, subtitle, points) in enumerate(slides, 1):
    c.setFillColor(HexColor('#101512')); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor('#b0c39a')); c.setFont('Helvetica',10)
    c.drawString(60,H-48,'LASTBITE  /  DEVSECOPS CAPSTONE')
    c.setFillColor(HexColor('#d0f683')); c.setFont('Helvetica-Bold',44 if number==1 else 34)
    c.drawString(60,H-118,title)
    c.setFillColor(HexColor('#b6c5ab')); c.setFont('Helvetica',18)
    c.drawString(60,H-156,subtitle)
    y=H-218
    if number == 4:
        def box(x, y, title, detail, width=150):
            c.setStrokeColor(HexColor('#43533d')); c.setFillColor(HexColor('#243021'))
            c.roundRect(x,y,width,62,8,fill=1,stroke=1)
            c.setFillColor(HexColor('#d0f683')); c.setFont('Helvetica-Bold',15)
            c.drawCentredString(x+width/2,y+36,title)
            c.setFillColor(HexColor('#b6c5ab')); c.setFont('Helvetica',11)
            c.drawCentredString(x+width/2,y+17,detail)
        def connect(x1,y1,x2,y2):
            c.setStrokeColor(HexColor('#a7c980')); c.setLineWidth(1.5)
            c.line(x1,y1,x2,y2)
        box(60,230,'Browser','Same-origin requests')
        box(270,230,'Ingress','Traefik')
        box(480,300,'Frontend','React / Nginx')
        box(480,160,'API','FastAPI')
        box(690,160,'Database','PostgreSQL / PVC')
        connect(210,261,270,261)
        connect(420,261,450,261);connect(450,261,450,331);connect(450,331,480,331)
        connect(450,261,450,191);connect(450,191,480,191)
        connect(630,191,690,191)
        c.setFont('Helvetica',12);c.setFillColor(HexColor('#b0c39a'))
        c.drawString(431,345,'/')
        c.drawString(423,174,'/api')
        c.drawString(60,95,'Prometheus scrapes the API. Grafana visualizes traffic, errors and latency.')
        points=[]
    for i,point in enumerate(points,1):
        c.setFillColor(HexColor('#a7c980')); c.setFont('Helvetica',11)
        c.drawString(60,y,f'{i:02}')
        c.setFillColor(HexColor('#e3eadc')); c.setFont('Helvetica',18)
        lines=simpleSplit(point,'Helvetica',18,W-160)
        for line in lines:
            c.drawString(98,y,line); y-=26
        y-=23
    assert y>40, (number,y)
    c.setFillColor(HexColor('#93a485')); c.setFont('Helvetica',10)
    c.drawString(60,29,'Application / Delivery / Operations')
    c.drawRightString(W-60,29,f'{number:02} / {len(slides):02}')
    c.showPage()
c.save()
print(ROOT/'slides.pdf')
