"""Unit tests for MonitoringService, AlertService, NotificationService, and ReportingService."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path
import pytest

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.domain.alerts import AlertSeverity, AlertStatus
from src.domain.models import Building, Floor, Room
from src.domain.sensors import CO2Sensor, SensorReading, SensorStatus, TemperatureSensor
from src.repository.memory import AlertRepository, ReadingRepository, SensorRepository
from src.service.alert import AlertService
from src.service.monitoring import MonitoringService, ThresholdRule
from src.service.notification import ConsoleNotificationService, EmailNotificationService
from src.service.reporting import ReportingService


@pytest.fixture
def test_setup():
    """Sets up fresh repositories and services for testing."""
    sensor_repo = SensorRepository()
    reading_repo = ReadingRepository()
    alert_repo = AlertRepository()
    notification_svc = ConsoleNotificationService()
    alert_svc = AlertService(
        alert_repository=alert_repo,
        notification_service=notification_svc,
        notification_recipient="test-admin@building.local",
    )
    monitoring_svc = MonitoringService(
        sensor_repository=sensor_repo,
        reading_repository=reading_repo,
        alert_service=alert_svc,
    )
    reporting_svc = ReportingService(
        sensor_repository=sensor_repo,
        reading_repository=reading_repo,
        alert_repository=alert_repo,
    )
    return {
        "sensor_repo": sensor_repo,
        "reading_repo": reading_repo,
        "alert_repo": alert_repo,
        "notification_svc": notification_svc,
        "alert_svc": alert_svc,
        "monitoring_svc": monitoring_svc,
        "reporting_svc": reporting_svc,
    }


def test_monitoring_normal_reading(test_setup):
    """Verify that normal reading generates no alert and is recorded."""
    sensor = TemperatureSensor(id="s1", name="Normal Temp")
    test_setup["sensor_repo"].add(sensor)

    reading = SensorReading("r1", "s1", datetime.now(), 22.0, "C")
    alert = test_setup["monitoring_svc"].process_reading(reading)

    assert alert is None
    assert test_setup["reading_repo"].count() == 1
    assert test_setup["alert_repo"].count() == 0


def test_monitoring_threshold_warning_and_critical(test_setup):
    """Verify threshold evaluation triggering WARNING and CRITICAL alerts."""
    sensor = TemperatureSensor(id="s1", name="Temp Sensor")
    test_setup["sensor_repo"].add(sensor)

    # Warning high threshold default is 26.0°C
    reading_warn = SensorReading("r_warn", "s1", datetime.now(), 27.5, "C")
    alert_warn = test_setup["monitoring_svc"].process_reading(reading_warn)
    assert alert_warn is not None
    assert alert_warn.severity == AlertSeverity.WARNING
    assert alert_warn.status == AlertStatus.OPEN

    # Critical high threshold default is 35.0°C
    reading_crit = SensorReading("r_crit", "s1", datetime.now(), 38.0, "C")
    alert_crit = test_setup["monitoring_svc"].process_reading(reading_crit)
    assert alert_crit is not None
    assert alert_crit.severity == AlertSeverity.CRITICAL

    # Check alert repository contains both alerts
    assert test_setup["alert_repo"].count() == 2


def test_alert_lifecycle_workflow(test_setup):
    """Verify alert acknowledgment and resolution lifecycle."""
    alert_svc = test_setup["alert_svc"]
    alert = alert_svc.create_alert(
        sensor_id="s1",
        message="High temperature warning",
        severity=AlertSeverity.WARNING,
    )
    assert alert.status == AlertStatus.OPEN
    assert alert.acknowledged_at is None
    assert alert.resolved_at is None

    # Acknowledge
    ack_alert = alert_svc.acknowledge_alert(alert.id)
    assert ack_alert is not None
    assert ack_alert.status == AlertStatus.ACKNOWLEDGED
    assert ack_alert.acknowledged_at is not None

    # Resolve
    res_alert = alert_svc.resolve_alert(alert.id)
    assert res_alert is not None
    assert res_alert.status == AlertStatus.RESOLVED
    assert res_alert.resolved_at is not None

    # No open alerts remaining
    assert len(alert_svc.get_open_alerts()) == 0


def test_notification_delivery_dispatch():
    """Verify that notification services receive and process dispatches."""
    alert_repo = AlertRepository()
    email_svc = EmailNotificationService(sender_email="alerts@test.local")
    alert_svc = AlertService(
        alert_repository=alert_repo,
        notification_service=email_svc,
        notification_recipient="ops@test.local",
    )

    alert_svc.create_alert(
        sensor_id="s99",
        message="Critical leak detected",
        severity=AlertSeverity.CRITICAL,
    )
    assert len(email_svc.sent_emails) == 1
    assert email_svc.sent_emails[0]["to"] == "ops@test.local"
    assert email_svc.sent_emails[0]["subject"] == "[CRITICAL] Building Sensor Alert"


def test_detect_offline_sensor(test_setup):
    """Verify offline sensor detection when last_reading_time exceeds timeout."""
    sensor_repo = test_setup["sensor_repo"]
    monitoring_svc = test_setup["monitoring_svc"]

    # Active sensor with fresh reading
    s1 = TemperatureSensor(id="s1", name="Active Sensor")
    s1.last_reading_time = datetime.now()
    sensor_repo.add(s1)

    # Inactive sensor that hasn't reported for 10 minutes
    s2 = TemperatureSensor(id="s2", name="Dead Sensor")
    s2.last_reading_time = datetime.now() - timedelta(minutes=10)
    sensor_repo.add(s2)

    alerts = monitoring_svc.detect_offline_sensor(timeout_seconds=300.0)
    assert len(alerts) == 1
    assert alerts[0].sensor_id == "s2"
    assert alerts[0].severity == AlertSeverity.CRITICAL

    # Verify s2 status is updated to OFFLINE
    assert sensor_repo.get_by_id("s2").status == SensorStatus.OFFLINE


def test_reporting_service_aggregations(test_setup):
    """Verify reporting statistical calculations and report structures."""
    sensor_repo = test_setup["sensor_repo"]
    reading_repo = test_setup["reading_repo"]
    reporting_svc = test_setup["reporting_svc"]

    sensor = TemperatureSensor(id="s_stat", name="Stat Temp Sensor")
    sensor_repo.add(sensor)

    reading_repo.add(SensorReading("r1", "s_stat", datetime.now(), 20.0, "C"))
    reading_repo.add(SensorReading("r2", "s_stat", datetime.now(), 30.0, "C"))
    reading_repo.add(SensorReading("r3", "s_stat", datetime.now(), 25.0, "C"))

    assert reporting_svc.calculate_min_reading("s_stat") == 20.0
    assert reporting_svc.calculate_max_reading("s_stat") == 30.0
    assert reporting_svc.calculate_average_reading("s_stat") == 25.0

    # Sensor report
    sensor_rep = reporting_svc.generate_sensor_report("s_stat")
    assert sensor_rep["sensor_id"] == "s_stat"
    assert sensor_rep["total_readings"] == 3

    # Building report
    bldg = Building("b1", "Alpha Center", "10 Innovation Blvd")
    fl = Floor("f1", 1)
    rm = Room("r1", "Main Hall", 1)
    rm.add_sensor(sensor)
    fl.add_room(rm)
    bldg.add_floor(fl)

    bldg_rep = reporting_svc.generate_building_report(bldg)
    assert bldg_rep["building_id"] == "b1"
    assert bldg_rep["total_sensors"] == 1
    assert bldg_rep["online_sensors"] == 1
