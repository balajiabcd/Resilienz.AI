"""
alerts/notifier.py — Notification Logic (Email Alerts)

Handles sending alerts to procurement teams using SMTP.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import sys

# ── Import Project Settings ───────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class Notifier:
    """Class to handle all outgoing alerts (Email)."""

    def __init__(self):
        self.smtp_host = config.SMTP_HOST
        self.smtp_port = config.SMTP_PORT
        self.smtp_user = config.ALERT_EMAIL_FROM
        self.smtp_pass = config.SMTP_PASSWORD
        self.target_email = config.ALERT_EMAIL_TO

    def send_risk_alert(self, subject, message, pdf_path=None):
        """Sends an email alert with an optional PDF report attached."""
        
        # Security: Skip if no password set (demo safety)
        if not self.smtp_pass:
            print("🛑 ALERT SIMULATOR: SMTP Password is empty. Printing alert to console:")
            print(f"   TO: {self.target_email}")
            print(f"   SUBJECT: {subject}")
            print(f"   MESSAGE: {message}")
            if pdf_path: print(f"   ATTACHMENT: {pdf_path}")
            return "ALREADY_LOGGED_TO_CONSOLE"

        # Initialize Container
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.smtp_user
        msg['To'] = self.target_email

        # Attach Body
        msg.attach(MIMEText(message, 'plain'))

        # Attach PDF Report if provided
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
                msg.attach(attach)

        # Connect and Send
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Upgrade connection to secure TLS!
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                print(f"✅ SUCCESS: Alert email sent to {self.target_email}")
                return "SENT"
        except Exception as e:
            print(f"❌ ERROR: Failed to send email alert. {str(e)}")
            return "FAILED"

# ── SELF TEST (Optional) ──────────────────────────────────────────────────────
if __name__ == "__main__":
    notifier = Notifier()
    notifier.send_risk_alert(
        subject="🚨 CRITICAL RISK ALERT — Resilienz.AI",
        message="Order PO-2024-001 is at critical risk due to the Port Strike in Hamburg. Please see the attached report for suggested actions."
    )
