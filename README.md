# Cloud Guestbook: Deploying a Web Application on the Cloud

A small Flask web app deployed through the full path:

**Application Code -> Cloud Compute -> Database/Storage -> Networking -> Live Web Application**

- **Live URL:** https://cloud-web-app-deployment.onrender.com
- **Cloud provider:** Render (web service + managed PostgreSQL)
- **Region:** Singapore
## Architecture

```
User (browser)
   |  HTTPS
   v
Render public URL (HTTPS handled by the platform)
   |
   v
Web service: Gunicorn + Flask app
(config and secrets come from environment variables)
   |  internal connection
   v
Render managed PostgreSQL (Singapore)
```

## Features that map to the module objectives

| Objective | Where it is in this repo |
|---|---|
| Compute | `Procfile` and the Render web service (Gunicorn) |
| Managed database | `DATABASE_URL` selects Render PostgreSQL in the cloud, SQLite locally |
| Virtual networking | The app reaches the database over Render's internal network using the Internal Database URL |
| IAM | Least-privilege notes in `docs/DEPLOYMENT.md` |
| Cloud monitoring | `/health` endpoint plus CPU alarm steps |
| Environment variables | `.env.example`, all config read in `app.py` |
| Secrets | `SECRET_KEY` and DB password never in code; `.env` is git-ignored |
| Application logging | Logs to stdout and `logs/app.log` (no secrets logged) |
| Resource quotas | Budget alert and quota check in `docs/DEPLOYMENT.md` |

`deploy/guestbook.service` and `deploy/nginx.conf` are for deploying to an AWS VM instead of Render.
## Run locally

```bash
aniketmagade042/cloud-web-app-deployment
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
| Render web service showing Live and the deploy logs | `screenshots/01-render-deploy.png` |
| Managed PostgreSQL database showing Available | `screenshots/02-database.png` |
| Live site with a guestbook entry | `screenshots/03-live-site.png` |
| `/health` output | `screenshots/04-health.png` |

## Challenges and fixes

“The first deploy showed ‘Database is unavailable’. I checked the environment variables and logs, corrected the configuration, redeployed, and confirmed with /health returning db ok.”
## Clean-up

Delete the compute instance, database, and any storage when finished to avoid charges.

## Author

Aniket Magade | [LinkedIn](https://www.linkedin.com/in/aniket-magade-959601448/)
