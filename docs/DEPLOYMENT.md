# Deployment Guide

Check each provider's **current free-tier terms** first; they change.

## Before you start (both options)

1. Push this repo to GitHub. Confirm `.env` is **not** in the repo.
2. Generate a secret key and keep it somewhere safe:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
3. Set a **billing/budget alert** in your cloud account.

---

## Option A: Quick PaaS deploy (fastest live URL)

Works on Render, Railway, or similar platforms.

1. Create a **Web Service** from your GitHub repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app`
4. Add environment variables in the dashboard (not in code):
   - `APP_ENV=production`
   - `SECRET_KEY=<your generated key>`
   - `DATABASE_URL=<connection string of the managed PostgreSQL you create on the same platform>`
5. Create a managed **PostgreSQL** instance on the same platform and copy its connection string into `DATABASE_URL`.
6. Deploy, open the generated URL, add an entry, and visit `/health`.

Free web services may sleep when idle, and free databases may expire. Check the platform's current terms and say so in your report.

---

## Option B: AWS EC2 + RDS PostgreSQL (full cloud path)

### 1. Networking and security groups
Create two security groups in the default VPC:

| Group | Inbound rules |
|---|---|
| `web-sg` (EC2) | TCP 80 from `0.0.0.0/0`; TCP 22 from **My IP only** |
| `db-sg` (RDS) | TCP 5432 with source = **`web-sg`** (not an IP, not the internet) |

### 2. Managed database
1. RDS -> Create database -> **PostgreSQL**, **Free tier** template.
2. Set a master username and a strong password. Set **Initial database name** to `guestbook`.
3. **Public access: No.** Attach `db-sg`.
4. Note the **endpoint** once it is available.

### 3. Compute
1. Launch an Ubuntu 22.04 EC2 instance (free-tier eligible type), attach `web-sg`, use your key pair.
2. **IAM**: do not use the root account for daily work. If the app later needs AWS services, attach an IAM **role** to the instance with only the permissions it needs (least privilege); never put access keys on the server.

### 4. Install the app
```bash
ssh -i mykey.pem ubuntu@<EC2_PUBLIC_IP>
sudo apt update && sudo apt install -y python3-venv nginx git
sudo adduser --disabled-password --gecos "" deploy
sudo mkdir /opt/guestbook && sudo chown deploy:deploy /opt/guestbook
sudo -u deploy git clone https://github.com/<your-username>/<repo-name>.git /opt/guestbook
cd /opt/guestbook
sudo -u deploy python3 -m venv venv
sudo -u deploy venv/bin/pip install -r requirements.txt
```

### 5. Environment variables and secrets
```bash
sudo nano /etc/guestbook.env
```
```
APP_ENV=production
SECRET_KEY=<your generated key>
DATABASE_URL=postgresql://<user>:<password>@<RDS_ENDPOINT>:5432/guestbook
LOG_LEVEL=INFO
```
If the password has special characters, URL-encode them. Then lock the file down:
```bash
sudo chmod 600 /etc/guestbook.env && sudo chown root:root /etc/guestbook.env
```
For a stronger setup, store the password in **AWS Secrets Manager** and read it at startup (mention this in your report even if you use the env file for the lab).

### 6. Run as a service behind Nginx
```bash
sudo cp deploy/guestbook.service /etc/systemd/system/guestbook.service
sudo systemctl daemon-reload
sudo systemctl enable --now guestbook
sudo cp deploy/nginx.conf /etc/nginx/sites-available/guestbook
sudo ln -sf /etc/nginx/sites-available/guestbook /etc/nginx/sites-enabled/guestbook
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

### 7. Test
- Open `http://<EC2_PUBLIC_IP>`, add an entry, refresh.
- `curl http://<EC2_PUBLIC_IP>/health` should return `{"db":"ok",...}`.
- Prove the DB is private: it should not be reachable from your laptop.

### 8. Logging, monitoring, quotas
- App logs: `journalctl -u guestbook -n 50` and `/opt/guestbook/logs/app.log`.
- Monitoring: CloudWatch -> Alarms -> create an alarm on EC2 `CPUUtilization` > 70% with an email notification.
- Quotas: open **Service Quotas** and note the EC2 and RDS limits for your region; mention one in your report.

### 9. Clean up
Terminate the EC2 instance, delete the RDS instance (skip the final snapshot for the lab), and remove unused security groups and any Elastic IP.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| 502 Bad Gateway | Gunicorn not running: `sudo systemctl status guestbook` |
| Site times out | Port 80 missing from `web-sg` |
| App cannot reach DB | `db-sg` source is not `web-sg`, wrong endpoint, or bad password encoding |
| `RuntimeError: SECRET_KEY must be set` | `/etc/guestbook.env` missing or `APP_ENV=production` without a key |
| `/health` returns 503 | Database unreachable; check logs |
