import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["APP_ENV"] = "development"

import app as guestbook  # noqa: E402


def client():
    guestbook.app.config["TESTING"] = True
    return guestbook.app.test_client()


def test_health():
    r = client().get("/health")
    assert r.status_code == 200 and r.get_json()["db"] == "ok"


def test_sign_and_list():
    c = client()
    c.post("/sign", data={"name": "Asha", "message": "Hello cloud"})
    page = c.get("/").get_data(as_text=True)
    assert "Asha" in page and "Hello cloud" in page


def test_rejects_empty_and_escapes_html():
    c = client()
    c.post("/sign", data={"name": "", "message": "x"})
    c.post("/sign", data={"name": "<b>Bob</b>", "message": "<script>alert(1)</script>"})
    page = c.get("/").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
