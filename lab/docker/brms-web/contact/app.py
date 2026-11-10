"""Contact form handler for the Boab Ridge Mining Services lab website.

Receives the form POST from /contact/send, checks it, and emails it to the office through the lab's mail server.
Standard library only, so the image has nothing to patch but Python itself.
"""
import os
import re
import smtplib
import sys
import time
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

SMTP_HOST = os.environ.get("SMTP_HOST", "mail.lab.internal")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))
MAIL_FROM = os.environ.get("MAIL_FROM", "website@lab.internal")
MAIL_TO = os.environ.get("MAIL_TO", "info@lab.internal")
MAX_BODY = 10_000
LIMITS = {"name": 100, "email": 200, "phone": 40, "message": 3000}
RATE_MAX, RATE_WINDOW = 5, 600  # five messages per address every ten minutes
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
hits = {}


def log(msg):
    # Never log the message text or the sender's address, only what happened and from which client.
    print(msg, file=sys.stderr, flush=True)


def clean(value, limit):
    return " ".join(value.split())[:limit] if value else ""


def too_many(ip):
    now = time.time()
    recent = [t for t in hits.get(ip, []) if now - t < RATE_WINDOW]
    hits[ip] = recent + [now]
    return len(recent) >= RATE_MAX


def send(name, email, phone, message, ip):
    msg = EmailMessage()
    msg["From"] = MAIL_FROM
    msg["To"] = MAIL_TO
    msg["Reply-To"] = email
    msg["Subject"] = f"Website enquiry from {name}"
    msg.set_content(f"Name: {name}\nEmail: {email}\nPhone: {phone or '(not given)'}\nClient: {ip}\n\n{message}\n")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
        smtp.send_message(msg)


class Handler(BaseHTTPRequestHandler):
    server_version = "contact"
    sys_version = ""

    def page(self, code, text):
        body = (f"<!doctype html><meta charset=utf-8><title>Contact</title>"
                f"<p>{text}</p><p><a href=/contact/>Back to the contact page</a></p>").encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            self.page(200, "ok")
        else:
            self.page(405, "Please use the contact form.")

    def do_POST(self):
        if self.path != "/contact/send":
            return self.page(404, "Not found.")
        ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if not 0 < length <= MAX_BODY:
            return self.page(413, "That message is too large.")
        form = parse_qs(self.rfile.read(length).decode("utf-8", "replace"))
        field = lambda k: form.get(k, [""])[0]

        if field("website"):  # the hidden field only a bot fills in: pretend it worked
            log(f"spam-trap ip={ip}")
            return self.redirect()
        if too_many(ip):
            log(f"rate-limited ip={ip}")
            return self.page(429, "Too many messages. Please try again later.")

        name, email = clean(field("name"), LIMITS["name"]), clean(field("email"), LIMITS["email"])
        phone, message = clean(field("phone"), LIMITS["phone"]), field("message").strip()[:LIMITS["message"]]
        if not name or not message or not EMAIL_RE.match(email):
            return self.page(400, "Please give your name, a valid email address and a message.")
        try:
            send(name, email, phone, message, ip)
        except (OSError, smtplib.SMTPException) as exc:
            log(f"mail-failed ip={ip} error={type(exc).__name__}")
            return self.page(502, "Sorry, we could not send your message. Please try again later or phone us.")
        log(f"sent ip={ip}")
        self.redirect()

    def redirect(self):
        self.send_response(303)
        self.send_header("Location", "/contact/thanks/")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args):
        pass  # the app's own log lines above replace the default access log


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
