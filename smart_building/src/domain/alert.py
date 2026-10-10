"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from .enums import AlertSeverity, AlertStatus


class Alert:
    """Represents an alert triggered by a threshold violation or sensor condition.

    Attributes:
        id: Unique identifier for the alert.
        sensor_id: Identifier of the sensor associated with this alert.
        reading_id: Identifier of the reading that triggered the alert (if applicable).
        message: Explanatory alert description.
        severity: Severity level (INFO, WARNING, CRITICAL).
        status: Current alert lifecycle status (OPEN, ACKNOWLEDGED, RESOLVED).
        created_at: Timestamp when the alert was generated.
        acknowledged_at: Timestamp when the alert was acknowledged.
        resolved_at: Timestamp when the alert was resolved.
    """

    def __init__(
        self,
        id: str,
        sensor_id: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        reading_id: Optional[str] = None,
        status: AlertStatus = AlertStatus.OPEN,
        created_at: Optional[datetime] = None,
        acknowledged_at: Optional[datetime] = None,
        resolved_at: Optional[datetime] = None,
    ) -> None:
        self.id: str = id
        self.sensor_id: str = sensor_id
        self.reading_id: Optional[str] = reading_id
        self.message: str = message
        self.severity: AlertSeverity = severity
        self.status: AlertStatus = status
        self.created_at: datetime = created_at if created_at is not None else datetime.now()
        self.acknowledged_at: Optional[datetime] = acknowledged_at
        self.resolved_at: Optional[datetime] = resolved_at

    def acknowledge(self, timestamp: Optional[datetime] = None) -> None:
        """Transitions alert to ACKNOWLEDGED state and records timestamp."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = timestamp if timestamp is not None else datetime.now()

    def resolve(self, timestamp: Optional[datetime] = None) -> None:
        """Transitions alert to RESOLVED state and records timestamp."""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = timestamp if timestamp is not None else datetime.now()

    def reopen(self) -> None:
        """Reopens an alert, transitioning back to OPEN state."""
        self.status = AlertStatus.OPEN
        self.acknowledged_at = None
        self.resolved_at = None

    def __repr__(self) -> str:
        return (
            f"Alert(id={self.id!r}, sensor_id={self.sensor_id!r}, "
            f"severity={self.severity.value}, status={self.status.value}, "
            f"message={self.message!r})"
        )
