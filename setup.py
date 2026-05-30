"""
setup.py  –  First-time configuration wizard for the Weekly Email Automator.
Run once:  python setup.py
"""

import json
import os
import getpass

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value if value else default


def prompt_list(text: str) -> list:
    print(f"\n{text}")
    print("Enter one email address per line. Press ENTER on a blank line when done.")
    items = []
    while True:
        val = input("  > ").strip()
        if not val:
            break
        items.append(val)
    return items


def main():
    print("\n" + "═" * 60)
    print("  Weekly Email Automator – Setup Wizard")
    print("═" * 60 + "\n")

    # ── SMTP provider shortcuts ────────────────────────────────────────────────
    print("Choose your email provider (or enter custom SMTP details):")
    print("  1  Gmail  (smtp.gmail.com)")
    print("  2  Outlook / Hotmail  (smtp-mail.outlook.com)")
    print("  3  Yahoo  (smtp.mail.yahoo.com)")
    print("  4  Custom SMTP server")
    choice = prompt("Provider", "1")

    providers = {
        "1": {"host": "smtp.gmail.com",          "port": 587, "use_tls": True,  "use_ssl": False},
        "2": {"host": "smtp-mail.outlook.com",   "port": 587, "use_tls": True,  "use_ssl": False},
        "3": {"host": "smtp.mail.yahoo.com",     "port": 587, "use_tls": True,  "use_ssl": False},
    }

    if choice in providers:
        smtp = providers[choice].copy()
        print(f"\nUsing: {smtp['host']}:{smtp['port']}")
    else:
        smtp = {
            "host":    prompt("SMTP host"),
            "port":    int(prompt("SMTP port", "587")),
            "use_tls": prompt("Use STARTTLS? (y/n)", "y").lower() == "y",
            "use_ssl": prompt("Use SSL (port 465)? (y/n)", "n").lower() == "y",
        }

    smtp["username"] = prompt("\nSMTP username (usually your email address)")
    smtp["password"] = getpass.getpass("SMTP password (input hidden): ")

    sender = prompt("\nFrom address (shown to recipients)", smtp["username"])

    recipients = prompt_list("Recipient email addresses")
    if not recipients:
        print("No recipients entered – you can add them later in config.json")

    subject = prompt("\nEmail subject line", "⚠️ Weekly System Update Alert")

    print("\nSchedule the weekly send:")
    days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    for i, d in enumerate(days, 1):
        print(f"  {i}  {d.capitalize()}")
    day_choice = prompt("Day to send (1-7)", "1")
    send_day   = days[int(day_choice) - 1] if day_choice.isdigit() and 1 <= int(day_choice) <= 7 else "monday"
    send_time  = prompt("Time to send (HH:MM, 24h)", "09:00")

    config = {
        "smtp":         smtp,
        "sender_email": sender,
        "recipients":   recipients,
        "subject":      subject,
        "send_day":     send_day,
        "send_time":    send_time,
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅  Config saved to {CONFIG_FILE}")
    print("\nNext steps:")
    print("  • Edit your message:   python email_automator.py --edit")
    print("  • Send a test email:   python email_automator.py --send")
    print("  • Start the scheduler: python email_automator.py")
    print("\n⚠️  Gmail users: use an App Password, not your regular password.")
    print("   https://myaccount.google.com/apppasswords\n")


if __name__ == "__main__":
    main()
