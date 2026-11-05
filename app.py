"""Cloud Guestbook: a small Flask app used to practise deploying to the cloud.

Everything environment-specific comes from environment variables:
  APP_ENV       development | production
  SECRET_KEY    required in production (never hard-code it)
  DATABASE_URL  sqlite:///guestbook.db (default) or postgresql://user:pass@host:5432/dbname
  LOG_LEVEL     DEBUG | INFO | WARNING | ERROR (default INFO)
"""
import logging
import os
import sqlite3
import sys
from contextlib import closing
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

load_dotenv()  # loads .env for local development only; real servers use real env vars

APP_ENV = os.getenv("APP_ENV", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///guestbook.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
USE_POSTGRES = DATABASE_URL.startswith(("postgres://", "postgresql://"))
PLACEHOLDER = "%s" if USE_POSTGRES else "?"

# ---------- Logging (stdout for cloud log collectors + rotating file) ----------
logger = logging.getLogger("guestbook")
logger.setLevel(LOG_LEVEL)
_fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
_stdout = logging.StreamHandler(sys.stdout)
_stdout.setFormatter(_fmt)
logger.addHandler(_stdout)
try:
    os.makedirs("logs", exist_ok=True)
    _file = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=3)
    _file.setFormatter(_fmt)
    logger.addHandler(_file)
except OSError:
    logger.warning("File logging unavailable; using stdout only")

# ---------- App and secrets ----------
app = Flask(__name__)
_secret = os.getenv("SECRET_KEY")
if not _secret:
    if APP_ENV == "production":
        raise RuntimeError("SECRET_KEY must be set in production")
    _secret = "dev-only-insecure-key"
    logger.warning("Using insecure development SECRET_KEY")
app.secret_key = _secret


# ---------- Database helpers ----------
def get_conn():
    if USE_POSTGRES:
        import psycopg2  # imported lazily so local SQLite runs need no driver

        return psycopg2.connect(DATABASE_URL.replace("postgres://", "postgresql://", 1))
    return sqlite3.connect(DATABASE_URL.replace("sqlite:///", "", 1))


def init_db():
    pk = "SERIAL PRIMARY KEY" if USE_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS entries ("
            f"id {pk}, name VARCHAR(60) NOT NULL, message VARCHAR(280) NOT NULL, "
            f"created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )
        conn.commit()
    logger.info("Database ready (%s)", "postgres" if USE_POSTGRES else "sqlite")


try:
    init_db()
except Exception:
    logger.exception("Database initialisation failed")


# ---------- Routes ----------
@app.get("/")
def index():
    try:
        with closing(get_conn()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, message, created_at FROM entries ORDER BY id DESC LIMIT 50")
            entries = cur.fetchall()
    except Exception:
        logger.exception("Could not load entries")
        entries = []
        flash("Database is unavailable right now.")
    return render_template("index.html", entries=entries, env=APP_ENV)


@app.post("/sign")
def sign():
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()
    if not (1 <= len(name) <= 60 and 1 <= len(message) <= 280):
        logger.info("Rejected invalid submission")
        flash("Name (1-60 chars) and message (1-280 chars) are required.")
        return redirect(url_for("index"))
    try:
        with closing(get_conn()) as conn:
            cur = conn.cursor()
            cur.execute(
                f"INSERT INTO entries (name, message) VALUES ({PLACEHOLDER}, {PLACEHOLDER})",
                (name, message),
            )
            conn.commit()
        logger.info("New entry saved (name length=%d)", len(name))  # never log secrets/PII
        flash("Thanks for signing!")
    except Exception:
        logger.exception("Could not save entry")
        flash("Could not save your entry. Please try again.")
    return redirect(url_for("index"))


@app.get("/health")
def health():
    """Used by load balancers and monitoring to check the app and database."""
    try:
        with closing(get_conn()) as conn:
            conn.cursor().execute("SELECT 1")
        return jsonify(status="ok", db="ok", env=APP_ENV)
    except Exception:
        logger.exception("Health check failed")
        return jsonify(status="error", db="down"), 503


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=(APP_ENV == "development"))
