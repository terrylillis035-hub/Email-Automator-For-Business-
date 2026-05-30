# Weekly Email Automator

Sends a customisable weekly alert to a list of recipients — ideal for notifying
partners and customers when internal system changes require website updates.

---

## Files

| File | Purpose |
|---|---|
| `email_automator.py` | Main script — run this |
| `setup.py` | First-time wizard to create `config.json` |
| `config.json` | Your SMTP credentials, recipients & schedule (git-ignored) |
| `config.example.json` | Template — copy → `config.json` and fill in |
| `message.txt` | The email body that gets sent each week |
| `requirements.txt` | Python dependencies |
| `email_automator.log` | Auto-created log of every send attempt |

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure
Run the interactive wizard:
```bash
python setup.py
```
Or manually copy and edit:
```bash
cp config.example.json config.json
# open config.json and fill in your details
```

### 3. Write your message
```bash
python email_automator.py --edit
```

### 4. Test it
```bash
python email_automator.py --send
```

### 5. Start the weekly scheduler
```bash
python email_automator.py
```
Leave this running (e.g. in a tmux session, systemd service, or as a cron job).

---

## CLI Reference

| Command | Description |
|---|---|
| `python email_automator.py` | Start scheduler (runs continuously) |
| `python email_automator.py --send` | Send email immediately |
| `python email_automator.py --edit` | Edit the message interactively |

---

## config.json Fields

```json
{
  "smtp": {
    "host":     "smtp.gmail.com",
    "port":     587,
    "use_tls":  true,
    "use_ssl":  false,
    "username": "you@gmail.com",
    "password": "app-password"
  },
  "sender_email": "you@gmail.com",
  "recipients":   ["a@example.com", "b@example.com"],
  "subject":      "⚠️ Weekly System Update Alert",
  "send_day":     "monday",
  "send_time":    "09:00"
}
```

To add or remove recipients just edit the `recipients` list — no restart needed.

---

## Gmail Setup (App Password)

Google blocks plain passwords for SMTP. Use an App Password instead:

1. Enable 2-Step Verification on your Google account.
2. Go to **myaccount.google.com/apppasswords**.
3. Generate a password for "Mail" → copy the 16-character string.
4. Paste it as the `password` value in `config.json`.

---

## Running as a Background Service (Linux)

Create `/etc/systemd/system/email-automator.service`:
```ini
[Unit]
Description=Weekly Email Automator
After=network.target

[Service]
WorkingDirectory=/path/to/email_automator
ExecStart=/usr/bin/python3 email_automator.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
Then:
```bash
sudo systemctl enable --now email-automator
```

---

## Security Note

`config.json` contains your SMTP password. Never commit it to version control.
Add it to `.gitignore`:
```
config.json
*.log
```
