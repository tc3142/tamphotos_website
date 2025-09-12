# app.py
import os, smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, PlainTextResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Load env (.env for local; Render uses dashboard vars) ---
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
CONTACT_TO_EMAIL = os.getenv("CONTACT_TO_EMAIL", "")
MAIL_DOMAIN = os.getenv("MAIL_DOMAIN", "tcphotos.studio")

# --- Resolve paths robustly ---
BASE_DIR = Path(__file__).resolve().parent
PUBLIC = BASE_DIR / "public"

app = FastAPI(title="tcphotos")

# --- Static assets (CSS/JS/IMG) under /assets → maps to /public ---
app.mount("/assets", StaticFiles(directory=str(PUBLIC), check_dir=True), name="assets")

def page(filename: str) -> FileResponse:
    """
    Serve an HTML file from /public with no-store so the browser
    doesn't cache stale pages while you're iterating.
    """
    f = PUBLIC / filename
    if not f.exists():
        return PlainTextResponse(f"Not found: {f}", status_code=404)
    return FileResponse(str(f), headers={"Cache-Control": "no-store"})

# --- Page routes (explicit + a few aliases) ---
@app.get("/")
def home():
    return page("index.html")

@app.get("/index.html")
def home_alias():
    return page("index.html")

@app.get("/singles.html")
def singles_page():
    return page("singles.html")

@app.get("/projects.html")
def projects_page():
    return page("projects.html")

@app.get("/about.html")
def about_page():
    return page("about.html")

@app.get("/contact")
def contact_short():
    return RedirectResponse("/contact.html", status_code=307)

@app.get("/contact.html")
def contact_full():
    return page("contact.html")

# Example project page routes (add more as needed)
@app.get("/projects/soccer")
def soccer_short():
    return RedirectResponse("/projects/soccer.html", status_code=307)

@app.get("/projects/soccer.html")
def soccer_page():
    return page("projects/soccer.html")

# --- Contact payload & email helper (SMTP) ---
class ContactPayload(BaseModel):
    name: str | None = ""
    message: str

def send_via_smtp(payload: ContactPayload) -> None:
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and CONTACT_TO_EMAIL):
        raise RuntimeError("SMTP or CONTACT_TO_EMAIL not configured")

    subject = f"New message from {payload.name or 'Anonymous'}"

    msg = MIMEMultipart("alternative")
    from_addr = SMTP_USER  # must be your authenticated mailbox (e.g., Gmail or your domain inbox)
    msg["From"] = f"Portfolio Contact <{from_addr}>"
    msg["To"] = CONTACT_TO_EMAIL
    msg["Subject"] = subject

    plain = payload.message
    html = (
        f"<p><strong>Name:</strong> {payload.name or '(not provided)'}</p>"
        f"<p><strong>Message:</strong></p>"
        f"<pre style='white-space:pre-wrap;font-family:inherit;'>{payload.message}</pre>"
    )
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    if SMTP_PORT == 465:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(from_addr, [CONTACT_TO_EMAIL], msg.as_string())
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo()
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(from_addr, [CONTACT_TO_EMAIL], msg.as_string())

@app.post("/api/contact")
async def contact_api(payload: ContactPayload):
    try:
        send_via_smtp(payload)
        return {"ok": True}
    except Exception as e:
        print("Contact error:", e)
        raise HTTPException(status_code=500, detail="Failed to send")

# --- Debug helpers (optional; remove in prod) ---
@app.get("/__debug_index_path")
def __debug_index_path():
    f = PUBLIC / "index.html"
    mtime = f.stat().st_mtime if f.exists() else "N/A"
    return PlainTextResponse(f"Serving: {f}\nExists: {f.exists()}\nMTime: {mtime}")

@app.get("/__debug_index_raw", response_class=PlainTextResponse)
def __debug_index_raw():
    f = PUBLIC / "index.html"
    return f.read_text(encoding="utf-8") if f.exists() else "index.html not found"

from datetime import datetime

@app.get("/__debug_ls_public", response_class=PlainTextResponse)
def __debug_ls_public():
    out = [f"PUBLIC dir: {PUBLIC}\n"]
    for p in sorted(PUBLIC.rglob("*")):
        try:
            mtime = datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds")
            out.append(f"{p.relative_to(PUBLIC)}\t{mtime}")
        except Exception as e:
            out.append(f"{p} <stat error: {e}>")
    return "\n".join(out)
