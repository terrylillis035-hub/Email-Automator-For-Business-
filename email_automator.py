"""
Weekly Email Automator
======================
Sends a customizable weekly alert to multiple recipients.
Usage:
  python email_automator.py          # Start the scheduler (runs continuously)
  python email_automator.py --send   # Send immediately right now
  python email_automator.py --edit   # Edit the message interactively
"""

import smtplib
import json
import os
import argparse
import schedule
import time
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE  = os.path.join(BASE_DIR, "config.json")
MESSAGE_FILE = os.path.join(BASE_DIR, "message.txt")
LOG_FILE     = os.path.join(BASE_DIR, "email_automator.log")

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Config helpers
# ══════════════════════════════════════════════════════════════════════════════

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(
            f"config.json not found at {CONFIG_FILE}.\n"
            "Run  python setup.py  first, or copy config.example.json → config.json and fill it in."
        )
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_message() -> str:
    if not os.path.exists(MESSAGE_FILE):
        return (
            "Hello,\n\n"
            "This is your weekly system-update alert.\n\n"
            "Please update the relevant information on the website at your earliest convenience.\n\n"
            "Regards,\nYour Automation System"
        )
    with open(MESSAGE_FILE) as f:
        return f.read()


def save_message(text: str) -> None:
    with open(MESSAGE_FILE, "w") as f:
        f.write(text)
    log.info("Message saved to %s", MESSAGE_FILE)


# ══════════════════════════════════════════════════════════════════════════════
# Email sending
# ══════════════════════════════════════════════════════════════════════════════

def build_email(sender: str, recipient: str, subject: str, body: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["From"]    = sender
    msg["To"]      = recipient
    msg["Subject"] = subject

    # Plain-text part
    msg.attach(MIMEText(body, "plain"))

    # Simple HTML part (preserves newlines, styled lightly)
    html_body = "<br>".join(body.splitlines())
    html = f"""
    <html><body style="font-family:Arial,sans-serif;font-size:14px;color:#333;line-height:1.6;">
      <div style="max-width:600px;margin:auto;padding:24px;border:1px solid #ddd;border-radius:6px;">
        {html_body}
      </div>
    </body></html>
    """
    msg.attach(MIMEText(html, "html"))
    return msg


def send_emails() -> None:
    cfg     = load_config()
    message = load_message()

    smtp_cfg    = cfg["smtp"]
    sender      = cfg["sender_email"]
    recipients  = cfg["recipients"]          # list of strings
    subject     = cfg.get("subject", "Weekly System Update Alert")

    if not recipients:
        log.warning("No recipients configured – skipping send.")
        return

    log.info("Connecting to %s:%s …", smtp_cfg["host"], smtp_cfg["port"])

    try:
        if smtp_cfg.get("use_ssl", False):
            server = smtplib.SMTP_SSL(smtp_cfg["host"], smtp_cfg["port"])
        else:
            server = smtplib.SMTP(smtp_cfg["host"], smtp_cfg["port"])
            if smtp_cfg.get("use_tls", True):
                server.starttls()

        server.login(smtp_cfg["username"], smtp_cfg["password"])
        log.info("Authenticated as %s", smtp_cfg["username"])

        success, failed = 0, 0
        for addr in recipients:
            try:
                email = build_email(sender, addr, subject, message)
                server.sendmail(sender, addr, email.as_string())
                log.info("  ✓  Sent → %s", addr)
                success += 1
            except Exception as exc:
                log.error("  ✗  Failed → %s  (%s)", addr, exc)
                failed += 1

        server.quit()
        log.info("Done – %d sent, %d failed  [%s]", success, failed,
                 datetime.now().strftime("%Y-%m-%d %H:%M"))

    except smtplib.SMTPAuthenticationError:
        log.error("SMTP authentication failed. Check username/password in config.json.")
    except Exception as exc:
        log.error("SMTP error: %s", exc)


# ══════════════════════════════════════════════════════════════════════════════
# Interactive message editor
# ══════════════════════════════════════════════════════════════════════════════

def edit_message() -> None:
    current = load_message()
    print("\n" + "═" * 60)
    print("  CURRENT MESSAGE")
    print("═" * 60)
    print(current)
    print("═" * 60)
    print("\nEnter your new message below.")
    print("Type  END  on its own line when finished, or CANCEL to abort.\n")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        if line.strip().upper() == "CANCEL":
            print("Cancelled – message unchanged.")
            return
        lines.append(line)

    new_message = "\n".join(lines)
    if not new_message.strip():
        print("Empty message – unchanged.")
        return

    save_message(new_message)
    print("\nMessage updated successfully!\n")

    preview = input("Send a test email now? (y/N): ").strip().lower()
    if preview == "y":
        send_emails()


# ══════════════════════════════════════════════════════════════════════════════
# Scheduler
# ══════════════════════════════════════════════════════════════════════════════

def start_scheduler() -> None:
    cfg      = load_config()
    day_map  = {
        "monday": schedule.every().monday,
        "tuesday": schedule.every().tuesday,
        "wednesday": schedule.every().wednesday,
        "thursday": schedule.every().thursday,
        "friday": schedule.every().friday,
        "saturday": schedule.every().saturday,
        "sunday": schedule.every().sunday,
    }

    send_day  = cfg.get("send_day", "monday").lower()
    send_time = cfg.get("send_time", "09:00")

    if send_day not in day_map:
        log.warning("Invalid send_day '%s' – defaulting to monday.", send_day)
        send_day = "monday"

    day_map[send_day].at(send_time).do(send_emails)
    log.info("Scheduler started — emails will send every %s at %s.", send_day.capitalize(), send_time)
    log.info("Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(30)


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(description="Weekly Email Automator")
    parser.add_argument("--send",  action="store_true", help="Send the email immediately")
    parser.add_argument("--edit",  action="store_true", help="Edit the message interactively")
    args = parser.parse_args()

    if args.send:
        send_emails()
    elif args.edit:
        edit_message()
    else:
        start_scheduler()


if __name__ == "__main__":
    main()
