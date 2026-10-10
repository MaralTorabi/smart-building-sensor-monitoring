"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path
import pytest

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.domain.alert import Alert
from src.domain.enums import AlertSeverity, AlertStatus, SensorStatus
from src.domain.sensor import TemperatureSensor
from src.domain.sensor_reading import SensorReading
from src.repository.memory import (
    AlertRepository,
    InMemoryRepository,
    ReadingRepository,
    SensorRepository,
)


def test_in_memory_repository_crud():
    """Verify general CRUD behavior of InMemoryRepository."""
    repo = InMemoryRepository[TemperatureSensor]()
    sensor1 = TemperatureSensor(id="s1", name="Sensor One")
    sensor2 = TemperatureSensor(id="s2", name="Sensor Two")

    # Add
    repo.add(sensor1)
    repo.add(sensor2)
    assert repo.count() == 2

    # Get by ID
    fetched = repo.get_by_id("s1")
    assert fetched == sensor1
    assert repo.get_by_id("non-existent") is None

    # Get all
    all_sensors = repo.get_all()
    assert len(all_sensors) == 2
    assert sensor1 in all_sensors

    # Update
    sensor1.name = "Sensor One Renamed"
    updated = repo.update(sensor1)
    assert updated is True
    assert repo.get_by_id("s1").name == "Sensor One Renamed"

    # Delete
    deleted = repo.delete("s1")
    assert deleted is True
    assert repo.get_by_id("s1") is None
    assert repo.count() == 1

    # Clear
    repo.clear()
    assert repo.count() == 0


def test_sensor_repository_queries():
    """Verify custom query methods on SensorRepository."""
    repo = SensorRepository()
    s1 = TemperatureSensor(id="s1", name="Room A Temp", room_id="rm-A")
    s2 = TemperatureSensor(id="s2", name="Room B Temp", room_id="rm-B")
    s3 = TemperatureSensor(id="s3", name="Room A Backup", room_id="rm-A")
    s3.status = SensorStatus.OFFLINE

    repo.add(s1)
    repo.add(s2)
    repo.add(s3)

    # get_by_room_id
    room_a_sensors = repo.get_by_room_id("rm-A")
    assert len(room_a_sensors) == 2
    assert s1 in room_a_sensors
    assert s3 in room_a_sensors

    # get_by_status
    offline_sensors = repo.get_by_status(SensorStatus.OFFLINE)
    assert len(offline_sensors) == 1
    assert offline_sensors[0] == s3

    # get_offline_sensors convenience method
    assert repo.get_offline_sensors() == [s3]


def test_reading_repository_queries():
    """Verify custom query methods on ReadingRepository."""
    repo = ReadingRepository()
    t0 = datetime.now() - timedelta(minutes=10)
    t1 = datetime.now() - timedelta(minutes=5)
    t2 = datetime.now()

    r1 = SensorReading(id="r1", sensor_id="s1", timestamp=t0, value=20.0, unit="C")
    r2 = SensorReading(id="r2", sensor_id="s1", timestamp=t1, value=22.0, unit="C")
    r3 = SensorReading(id="r3", sensor_id="s1", timestamp=t2, value=25.0, unit="C")
    r4 = SensorReading(id="r4", sensor_id="s2", timestamp=t2, value=50.0, unit="%")

    repo.add(r1)
    repo.add(r2)
    repo.add(r3)
    repo.add(r4)

    # get_by_sensor_id
    s1_readings = repo.get_by_sensor_id("s1")
    assert len(s1_readings) == 3

    # get_latest_reading
    latest_s1 = repo.get_latest_reading("s1")
    assert latest_s1 is not None
    assert latest_s1.id == "r3"
    assert latest_s1.value == 25.0

    # get_readings_since
    recent = repo.get_readings_since("s1", since=datetime.now() - timedelta(minutes=7))
    assert len(recent) == 2
    assert r2 in recent
    assert r3 in recent


def test_alert_repository_queries():
    """Verify query methods on AlertRepository."""
    repo = AlertRepository()
    a1 = Alert(id="a1", sensor_id="s1", message="Warning 1", severity=AlertSeverity.WARNING, status=AlertStatus.OPEN)
    a2 = Alert(id="a2", sensor_id="s1", message="Critical 1", severity=AlertSeverity.CRITICAL, status=AlertStatus.OPEN)
    a3 = Alert(id="a3", sensor_id="s2", message="Info 1", severity=AlertSeverity.INFO, status=AlertStatus.RESOLVED)

    repo.add(a1)
    repo.add(a2)
    repo.add(a3)

    assert len(repo.get_by_sensor_id("s1")) == 2
    assert len(repo.get_open_alerts()) == 2
    assert len(repo.get_by_severity(AlertSeverity.CRITICAL)) == 1
    assert repo.get_by_severity(AlertSeverity.CRITICAL)[0] == a2
    assert len(repo.get_by_status(AlertStatus.RESOLVED)) == 1
