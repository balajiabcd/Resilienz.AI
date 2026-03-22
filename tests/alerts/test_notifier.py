"""
tests/alerts/test_notifier.py — Tests for alerts/notifier.py

Tests email notification and console fallback behavior.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from alerts.notifier import Notifier


class TestNotifierInit:
    """Unit tests for Notifier initialization."""

    def test_init_loads_config(self, monkeypatch):
        monkeypatch.setattr("config.SMTP_HOST", "smtp.test.com")
        monkeypatch.setattr("config.SMTP_PORT", 587)
        monkeypatch.setattr("config.ALERT_EMAIL_FROM", "from@test.com")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "to@test.com")
        monkeypatch.setattr("config.SMTP_PASSWORD", "secret")

        notifier = Notifier()

        assert notifier.smtp_host == "smtp.test.com"
        assert notifier.smtp_port == 587
        assert notifier.smtp_user == "from@test.com"
        assert notifier.target_email == "to@test.com"

    def test_init_stores_password(self, monkeypatch):
        monkeypatch.setattr("config.SMTP_PASSWORD", "mypassword")
        notifier = Notifier()
        assert notifier.smtp_pass == "mypassword"


class TestSendRiskAlert:
    """Tests for send_risk_alert method."""

    def test_console_mode_when_no_password(self, monkeypatch, capsys):
        monkeypatch.setattr("config.SMTP_PASSWORD", "")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "test@example.com")

        notifier = Notifier()
        result = notifier.send_risk_alert(subject="Test Alert", message="Test message")

        assert result == "ALREADY_LOGGED_TO_CONSOLE"
        captured = capsys.readouterr()
        assert "ALERT SIMULATOR" in captured.out
        assert "test@example.com" in captured.out
        assert "Test Alert" in captured.out

    def test_console_mode_with_pdf(self, monkeypatch, capsys):
        monkeypatch.setattr("config.SMTP_PASSWORD", "")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "procurement@company.de")

        notifier = Notifier()
        result = notifier.send_risk_alert(
            subject="Critical Alert",
            message="PO-2024-001 at risk",
            pdf_path="/path/to/report.pdf",
        )

        assert result == "ALREADY_LOGGED_TO_CONSOLE"
        captured = capsys.readouterr()
        assert "/path/to/report.pdf" in captured.out

    @patch("alerts.notifier.smtplib.SMTP")
    def test_email_sent_successfully(self, mock_smtp_class, monkeypatch):
        monkeypatch.setattr("config.SMTP_PASSWORD", "valid_password")
        monkeypatch.setattr("config.SMTP_HOST", "smtp.gmail.com")
        monkeypatch.setattr("config.SMTP_PORT", 587)
        monkeypatch.setattr("config.ALERT_EMAIL_FROM", "agent@resilienz.ai")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "procurement@company.de")

        mock_smtp_instance = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(
            return_value=mock_smtp_instance
        )
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        notifier = Notifier()
        result = notifier.send_risk_alert(subject="Risk Alert", message="Order at risk")

        assert result == "SENT"
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.send_message.assert_called_once()

    @patch("alerts.notifier.smtplib.SMTP")
    def test_email_with_pdf_attachment(self, mock_smtp_class, monkeypatch):
        monkeypatch.setattr("config.SMTP_PASSWORD", "password")
        monkeypatch.setattr("config.SMTP_HOST", "smtp.gmail.com")
        monkeypatch.setattr("config.SMTP_PORT", 587)
        monkeypatch.setattr("config.ALERT_EMAIL_FROM", "agent@resilienz.ai")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "procurement@company.de")

        mock_smtp_instance = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(
            return_value=mock_smtp_instance
        )
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        with patch("builtins.open", mock_open(read_data=b"PDF content")):
            with patch("os.path.exists", return_value=True):
                notifier = Notifier()
                result = notifier.send_risk_alert(
                    subject="Alert", message="Message", pdf_path="/path/to/report.pdf"
                )

        assert result == "SENT"
        assert mock_smtp_instance.send_message.called

    @patch("alerts.notifier.smtplib.SMTP")
    def test_email_fails_gracefully(self, mock_smtp_class, monkeypatch):
        monkeypatch.setattr("config.SMTP_PASSWORD", "password")
        monkeypatch.setattr("config.SMTP_HOST", "smtp.gmail.com")
        monkeypatch.setattr("config.SMTP_PORT", 587)
        monkeypatch.setattr("config.ALERT_EMAIL_FROM", "from@test.com")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "to@test.com")

        mock_smtp_class.side_effect = Exception("Connection refused")

        notifier = Notifier()
        result = notifier.send_risk_alert(subject="Alert", message="Message")

        assert result == "FAILED"

    @patch("alerts.notifier.smtplib.SMTP")
    def test_email_login_fails(self, mock_smtp_class, monkeypatch):
        monkeypatch.setattr("config.SMTP_PASSWORD", "wrong_password")
        monkeypatch.setattr("config.SMTP_HOST", "smtp.gmail.com")
        monkeypatch.setattr("config.SMTP_PORT", 587)
        monkeypatch.setattr("config.ALERT_EMAIL_FROM", "from@test.com")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "to@test.com")

        mock_smtp_instance = MagicMock()
        mock_smtp_instance.login.side_effect = Exception("Authentication failed")
        mock_smtp_class.return_value.__enter__ = MagicMock(
            return_value=mock_smtp_instance
        )
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        notifier = Notifier()
        result = notifier.send_risk_alert(subject="Alert", message="Message")

        assert result == "FAILED"


class TestNotifierEdgeCases:
    """Edge case tests for Notifier."""

    def test_empty_subject(self, monkeypatch, capsys):
        monkeypatch.setattr("config.SMTP_PASSWORD", "")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "test@test.com")

        notifier = Notifier()
        result = notifier.send_risk_alert(subject="", message="Message")

        assert result == "ALREADY_LOGGED_TO_CONSOLE"

    def test_empty_message(self, monkeypatch, capsys):
        monkeypatch.setattr("config.SMTP_PASSWORD", "")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "test@test.com")

        notifier = Notifier()
        result = notifier.send_risk_alert(subject="Subject", message="")

        assert result == "ALREADY_LOGGED_TO_CONSOLE"

    def test_pdf_path_none(self, monkeypatch, capsys):
        monkeypatch.setattr("config.SMTP_PASSWORD", "")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "test@test.com")

        notifier = Notifier()
        result = notifier.send_risk_alert(
            subject="Subject", message="Message", pdf_path=None
        )

        assert result == "ALREADY_LOGGED_TO_CONSOLE"
        captured = capsys.readouterr()
        assert "ATTACHMENT" not in captured.out

    @patch("alerts.notifier.smtplib.SMTP")
    def test_pdf_not_exists(self, mock_smtp_class, monkeypatch):
        monkeypatch.setattr("config.SMTP_PASSWORD", "pass")
        monkeypatch.setattr("config.SMTP_HOST", "smtp.test.com")
        monkeypatch.setattr("config.SMTP_PORT", 587)
        monkeypatch.setattr("config.ALERT_EMAIL_FROM", "from@test.com")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "to@test.com")

        mock_smtp_instance = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(
            return_value=mock_smtp_instance
        )
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        with patch("os.path.exists", return_value=False):
            notifier = Notifier()
            result = notifier.send_risk_alert(
                subject="Subject", message="Message", pdf_path="/nonexistent/path.pdf"
            )

        assert result == "SENT"

    @patch("alerts.notifier.smtplib.SMTP")
    def test_special_characters_in_subject(self, mock_smtp_class, monkeypatch):
        monkeypatch.setattr("config.SMTP_PASSWORD", "pass")
        monkeypatch.setattr("config.SMTP_HOST", "smtp.test.com")
        monkeypatch.setattr("config.SMTP_PORT", 587)
        monkeypatch.setattr("config.ALERT_EMAIL_FROM", "from@test.com")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "to@test.com")

        mock_smtp_instance = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(
            return_value=mock_smtp_instance
        )
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        notifier = Notifier()
        result = notifier.send_risk_alert(
            subject="🚨 RESILIENCE ALERT: PO-2024-001 (Score: 85)",
            message="Critical risk detected",
        )

        assert result == "SENT"


class TestNotifierStress:
    """Stress tests for Notifier."""

    def test_many_console_alerts(self, monkeypatch, capsys):
        monkeypatch.setattr("config.SMTP_PASSWORD", "")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "test@test.com")

        notifier = Notifier()

        for i in range(100):
            result = notifier.send_risk_alert(
                subject=f"Alert {i}", message=f"Message {i}"
            )
            assert result == "ALREADY_LOGGED_TO_CONSOLE"

    @patch("alerts.notifier.smtplib.SMTP")
    def test_many_email_alerts(self, mock_smtp_class, monkeypatch):
        monkeypatch.setattr("config.SMTP_PASSWORD", "pass")
        monkeypatch.setattr("config.SMTP_HOST", "smtp.test.com")
        monkeypatch.setattr("config.SMTP_PORT", 587)
        monkeypatch.setattr("config.ALERT_EMAIL_FROM", "from@test.com")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "to@test.com")

        mock_smtp_instance = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(
            return_value=mock_smtp_instance
        )
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        notifier = Notifier()

        for i in range(50):
            result = notifier.send_risk_alert(
                subject=f"Alert {i}", message=f"Message {i}"
            )
            assert result == "SENT"

    @patch("alerts.notifier.smtplib.SMTP")
    def test_long_message_content(self, mock_smtp_class, monkeypatch):
        monkeypatch.setattr("config.SMTP_PASSWORD", "pass")
        monkeypatch.setattr("config.SMTP_HOST", "smtp.test.com")
        monkeypatch.setattr("config.SMTP_PORT", 587)
        monkeypatch.setattr("config.ALERT_EMAIL_FROM", "from@test.com")
        monkeypatch.setattr("config.ALERT_EMAIL_TO", "to@test.com")

        mock_smtp_instance = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(
            return_value=mock_smtp_instance
        )
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        long_message = "x" * 10000
        notifier = Notifier()
        result = notifier.send_risk_alert(subject="Long Alert", message=long_message)

        assert result == "SENT"
