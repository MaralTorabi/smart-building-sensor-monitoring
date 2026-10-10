"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List

from ..domain.enums import AlertSeverity


class NotificationService(ABC):
    """Abstract interface defining notification delivery contracts."""

    @abstractmethod
    def send_notification(
        self,
        message: str,
        recipient: str,
        severity: AlertSeverity = AlertSeverity.INFO,
    ) -> bool:
        """Dispatches an alert notification to a specified recipient.

        Args:
            message: Text body of the alert.
            recipient: Target recipient address/identifier.
            severity: Severity level of the alert.

        Returns:
            True if dispatch succeeded; False otherwise.
        """
        pass


class ConsoleNotificationService(NotificationService):
    """Outputs alert notifications directly to standard output / console."""

    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = []

    def send_notification(
        self,
        message: str,
        recipient: str,
        severity: AlertSeverity = AlertSeverity.INFO,
    ) -> bool:
        """Prints a color-formatted alert line to console and tracks history."""
        timestamp_str: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record: Dict[str, Any] = {
            "timestamp": timestamp_str,
            "severity": severity.value,
            "recipient": recipient,
            "message": message,
        }
        self.history.append(record)

        print(
            f"[{timestamp_str}] [NOTIFICATION - {severity.value}] "
            f"To: {recipient} | Message: {message}"
        )
        return True


class EmailNotificationService(NotificationService):
    """Simulates email-based alert notifications with SMTP configuration."""

    def __init__(
        self,
        smtp_host: str = "smtp.smartbuilding.local",
        sender_email: str = "no-reply@smartbuilding.local",
    ) -> None:
        self.smtp_host: str = smtp_host
        self.sender_email: str = sender_email
        self.sent_emails: List[Dict[str, Any]] = []

    def send_notification(
        self,
        message: str,
        recipient: str,
        severity: AlertSeverity = AlertSeverity.INFO,
    ) -> bool:
        """Simulates dispatching an email to the specified address."""
        email_record: Dict[str, Any] = {
            "from": self.sender_email,
            "to": recipient,
            "subject": f"[{severity.value}] Building Sensor Alert",
            "body": message,
            "sent_at": datetime.now(),
        }
        self.sent_emails.append(email_record)
        return True
