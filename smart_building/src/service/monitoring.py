"""Monitoring service for analyzing sensor readings and device health.

Coordinates sensor threshold checks, offline device detection, and alert generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..domain.alerts import Alert, AlertSeverity
from ..domain.sensors import Sensor, SensorReading, SensorStatus
from ..repository.memory import ReadingRepository, SensorRepository
from .alert import AlertService


@dataclass
class ThresholdRule:
    """Configurable boundaries for sensor measurements."""
    warning_min: Optional[float] = None
    warning_max: Optional[float] = None
    critical_min: Optional[float] = None
    critical_max: Optional[float] = None


class MonitoringService:
    """Orchestrates stream processing of readings, threshold validation, and device monitoring.

    Attributes:
        sensor_repository: Repository for querying and updating sensors.
        reading_repository: Repository for recording readings.
        alert_service: Service responsible for managing alerts and dispatching notifications.
        rules: Map of unit/type to configured ThresholdRule.
    """

    def __init__(
        self,
        sensor_repository: SensorRepository,
        reading_repository: ReadingRepository,
        alert_service: AlertService,
        rules: Optional[Dict[str, ThresholdRule]] = None,
    ) -> None:
        self.sensor_repository: SensorRepository = sensor_repository
        self.reading_repository: ReadingRepository = reading_repository
        self.alert_service: AlertService = alert_service
        self.rules: Dict[str, ThresholdRule] = rules if rules is not None else self._default_rules()

    @staticmethod
    def _default_rules() -> Dict[str, ThresholdRule]:
        """Provides sensible facility threshold defaults."""
        return {
            "C": ThresholdRule(warning_min=18.0, warning_max=26.0, critical_min=10.0, critical_max=35.0),
            "%": ThresholdRule(warning_min=30.0, warning_max=65.0, critical_min=20.0, critical_max=80.0),
            "ppm": ThresholdRule(warning_max=1000.0, critical_max=2000.0),
            "kWh": ThresholdRule(warning_max=20.0, critical_max=35.0),
        }

    def set_threshold_rule(self, unit: str, rule: ThresholdRule) -> None:
        """Configures or updates a threshold rule for a given measurement unit."""
        self.rules[unit] = rule

    def process_reading(self, reading: SensorReading) -> Optional[Alert]:
        """Processes an incoming sensor reading.

        1. Validates and stores the reading.
        2. Updates the sensor's last_reading_time and ensures ONLINE status.
        3. Evaluates thresholds and triggers an alert if violated.

        Args:
            reading: Newly generated SensorReading.

        Returns:
            An Alert if a threshold was violated, otherwise None.
        """
        if not reading.is_valid():
            sensor = self.sensor_repository.get_by_id(reading.sensor_id)
            sensor_name = sensor.name if sensor else reading.sensor_id
            return self.alert_service.create_alert(
                sensor_id=reading.sensor_id,
                message=f"Invalid reading value ({reading.value}) produced by sensor '{sensor_name}'",
                severity=AlertSeverity.WARNING,
                reading_id=reading.id,
            )

        # Persist reading
        self.reading_repository.add(reading)

        # Update sensor heartbeat and status
        sensor = self.sensor_repository.get_by_id(reading.sensor_id)
        if sensor is not None:
            sensor.last_reading_time = reading.timestamp
            if sensor.status == SensorStatus.OFFLINE:
                sensor.status = SensorStatus.ONLINE
            self.sensor_repository.update(sensor)

        # Check threshold condition
        return self.create_alert_if_needed(reading)

    def check_threshold(self, reading: SensorReading) -> Optional[Tuple[str, AlertSeverity]]:
        """Inspects a reading against configured rules.

        Returns:
            Tuple of (alert_message, severity) if violated; None if within normal range.
        """
        rule = self.rules.get(reading.unit)
        if rule is None:
            return None

        val = reading.value

        # Check CRITICAL bounds first
        if rule.critical_max is not None and val >= rule.critical_max:
            return (
                f"Critical high measurement: {val:.2f}{reading.unit} exceeds limit ({rule.critical_max}{reading.unit})",
                AlertSeverity.CRITICAL,
            )
        if rule.critical_min is not None and val <= rule.critical_min:
            return (
                f"Critical low measurement: {val:.2f}{reading.unit} falls below limit ({rule.critical_min}{reading.unit})",
                AlertSeverity.CRITICAL,
            )

        # Check WARNING bounds
        if rule.warning_max is not None and val >= rule.warning_max:
            return (
                f"Warning high measurement: {val:.2f}{reading.unit} exceeds threshold ({rule.warning_max}{reading.unit})",
                AlertSeverity.WARNING,
            )
        if rule.warning_min is not None and val <= rule.warning_min:
            return (
                f"Warning low measurement: {val:.2f}{reading.unit} falls below threshold ({rule.warning_min}{reading.unit})",
                AlertSeverity.WARNING,
            )

        return None

    def create_alert_if_needed(self, reading: SensorReading) -> Optional[Alert]:
        """Evaluates thresholds and triggers an alert via AlertService if violated."""
        violation = self.check_threshold(reading)
        if violation is None:
            return None

        message, severity = violation
        return self.alert_service.create_alert(
            sensor_id=reading.sensor_id,
            message=message,
            severity=severity,
            reading_id=reading.id,
        )

    def detect_offline_sensor(self, timeout_seconds: float = 300.0) -> List[Alert]:
        """Identifies sensors that have not produced a reading within the configured timeout.

        Transitions unresponsive online sensors to OFFLINE and raises CRITICAL alerts.

        Args:
            timeout_seconds: Duration in seconds beyond which a sensor is deemed offline.

        Returns:
            List of generated offline alerts.
        """
        now = datetime.now()
        offline_alerts: List[Alert] = []
        sensors = self.sensor_repository.get_enabled_sensors()

        for sensor in sensors:
            is_unresponsive = False
            if sensor.last_reading_time is None:
                is_unresponsive = True
            elif (now - sensor.last_reading_time).total_seconds() > timeout_seconds:
                is_unresponsive = True

            if is_unresponsive and sensor.status == SensorStatus.ONLINE:
                sensor.status = SensorStatus.OFFLINE
                self.sensor_repository.update(sensor)

                alert = self.alert_service.create_alert(
                    sensor_id=sensor.id,
                    message=f"Sensor '{sensor.name}' ({sensor.id}) has stopped reporting data (offline timeout > {timeout_seconds}s).",
                    severity=AlertSeverity.CRITICAL,
                )
                offline_alerts.append(alert)

        return offline_alerts
