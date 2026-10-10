"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from ..domain.alert import Alert
from ..domain.enums import AlertSeverity, AlertStatus
from ..repository.memory import AlertRepository
from .notification import NotificationService


class AlertService:
    """Service managing domain alerts and notifying stakeholders.

    Attributes:
        alert_repository: Injected repository storing alerts.
        notification_service: Optional injected notification delivery service.
        notification_recipient: Default recipient for automated notifications.
    """

    def __init__(
        self,
        alert_repository: AlertRepository,
        notification_service: Optional[NotificationService] = None,
        notification_recipient: str = "facilities@smartbuilding.local",
    ) -> None:
        self.alert_repository: AlertRepository = alert_repository
        self.notification_service: Optional[NotificationService] = notification_service
        self.notification_recipient: str = notification_recipient

    def create_alert(
        self,
        sensor_id: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        reading_id: Optional[str] = None,
    ) -> Alert:
        """Creates, stores, and optionally announces a new system alert.

        Args:
            sensor_id: Target sensor identifier.
            message: Explanation of the alert condition.
            severity: Severity level (INFO, WARNING, CRITICAL).
            reading_id: Associated reading identifier.

        Returns:
            The created Alert instance.
        """
        alert = Alert(
            id=str(uuid.uuid4()),
            sensor_id=sensor_id,
            reading_id=reading_id,
            message=message,
            severity=severity,
            status=AlertStatus.OPEN,
            created_at=datetime.now(),
        )
        self.alert_repository.add(alert)

        if self.notification_service is not None:
            self.notification_service.send_notification(
                message=f"[Sensor {sensor_id}] {message}",
                recipient=self.notification_recipient,
                severity=severity,
            )

        return alert

    def acknowledge_alert(self, alert_id: str) -> Optional[Alert]:
        """Marks an active alert as acknowledged.

        Args:
            alert_id: Identifier of the alert to acknowledge.

        Returns:
            The updated Alert instance, or None if not found.
        """
        alert = self.alert_repository.get_by_id(alert_id)
        if alert is None:
            return None

        alert.acknowledge()
        self.alert_repository.update(alert)
        return alert

    def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        """Marks an alert as resolved.

        Args:
            alert_id: Identifier of the alert to resolve.

        Returns:
            The updated Alert instance, or None if not found.
        """
        alert = self.alert_repository.get_by_id(alert_id)
        if alert is None:
            return None

        alert.resolve()
        self.alert_repository.update(alert)
        return alert

    def get_open_alerts(self) -> List[Alert]:
        """Retrieves all unresolved and unacknowledged OPEN alerts."""
        return self.alert_repository.get_open_alerts()

    def get_critical_alerts(self) -> List[Alert]:
        """Retrieves all alerts flagged with CRITICAL severity."""
        return self.alert_repository.get_by_severity(AlertSeverity.CRITICAL)

    def get_alerts_for_sensor(self, sensor_id: str) -> List[Alert]:
        """Retrieves all alerts associated with a specific sensor."""
        return self.alert_repository.get_by_sensor_id(sensor_id)
