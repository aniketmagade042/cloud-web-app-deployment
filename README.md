# Cloud Guestbook: Deploying a Web Application on the Cloud

A small Flask web app deployed through the full path:

**Application Code -> Cloud Compute -> Database/Storage -> Networking -> Live Web Application**

- **Live URL:** https://cloud-web-app-deployment.onrender.com
- **Cloud provider:** Render (web service + managed PostgreSQL)
- **Region:** Singapore
## Architecture

```
User (browser)
   |  HTTPS/HTTP
   v
Internet --> Security group / firewall (80, 443 open; 22 only from my IP)
   |
   v
Cloud compute (VM running Nginx + Gunicorn + Flask app)
   |  port 5432, allowed ONLY from the app's security group
   v
Managed PostgreSQL database
```

## Features that map to the module objectives

| Objective | Where it is in this repo |
|---|---|
| Compute | `deploy/guestbook.service`, `Procfile` (Gunicorn on a VM / PaaS) |
| Managed database | `DATABASE_URL` selects PostgreSQL in the cloud, SQLite locally |
| Virtual networking | Security group rules in `docs/DEPLOYMENT.md` |
| IAM | Least-privilege notes in `docs/DEPLOYMENT.md` |
| Cloud monitoring | `/health` endpoint plus CPU alarm steps |
| Environment variables | `.env.example`, all config read in `app.py` |
| Secrets | `SECRET_KEY` and DB password never in code; `.env` is git-ignored |
| Application logging | Logs to stdout and `logs/app.log` (no secrets logged) |
| Resource quotas | Budget alert and quota check in `docs/DEPLOYMENT.md` |

## Run locally

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
python3 -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # Windows: copy .env.example .env
python app.py                                          # open http://127.0.0.1:5000
```

Health check: `http://127.0.0.1:5000/health`

## Deploy

Step-by-step guides are in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md):
- **Option A**: quick PaaS deploy (fastest live URL)
- **Option B**: AWS EC2 + RDS PostgreSQL (full compute, database, networking path)

## Learning notes

See [docs/learning-notes.md](docs/learning-notes.md).

## Evidence (add your screenshots to `screenshots/`)

| What | File |
|---|---|
| Cloud console showing the running compute resource | `screenshots/01-compute.png` |
| Managed database and its security group rule | `screenshots/02-database.png` |
| Live site in the browser with an entry added | `screenshots/03-live-site.png` |
| `/health` output | `screenshots/04-health.png` |
| Logs and monitoring alarm | `screenshots/05-logs-monitoring.png` |

## Challenges and fixes

- `<Problem you hit and how you solved it>`

## Clean-up

Delete the compute instance, database, and any storage when finished to avoid charges.

## Author

`<Your name>` | `<LinkedIn URL>`
