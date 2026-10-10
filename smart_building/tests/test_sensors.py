"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

import math
import sys
from datetime import datetime
from pathlib import Path
import pytest

# Ensure import paths resolve correctly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.domain.building import Building
from src.domain.enums import SensorStatus
from src.domain.floor import Floor
from src.domain.room import Room
from src.domain.sensor import (
    CO2Sensor,
    EnergySensor,
    HumiditySensor,
    MotionSensor,
    TemperatureSensor,
)
from src.domain.sensor_reading import SensorReading


def test_sensor_instantiation_and_inheritance():
    """Verify that concrete sensor subclasses instantiate with appropriate units and inheritance."""
    temp_s = TemperatureSensor(id="t1", name="Temp 1")
    assert temp_s.id == "t1"
    assert temp_s.name == "Temp 1"
    assert temp_s.unit == "C"
    assert temp_s.status == SensorStatus.ONLINE
    assert temp_s.is_online() is True

    co2_s = CO2Sensor(id="c1", name="CO2 1")
    assert co2_s.unit == "ppm"

    hum_s = HumiditySensor(id="h1", name="Hum 1")
    assert hum_s.unit == "%"

    mot_s = MotionSensor(id="m1", name="Motion 1")
    assert mot_s.unit == "motion"

    eng_s = EnergySensor(id="e1", name="Energy 1")
    assert eng_s.unit == "kWh"


def test_sensor_state_transitions():
    """Verify sensor enable and disable transitions."""
    sensor = TemperatureSensor(id="t1", name="Temp 1")
    assert sensor.is_online() is True

    sensor.disable()
    assert sensor.enabled is False
    assert sensor.status == SensorStatus.DISABLED
    assert sensor.is_online() is False

    sensor.enable()
    assert sensor.enabled is True
    assert sensor.status == SensorStatus.ONLINE
    assert sensor.is_online() is True


def test_room_and_sensor_association():
    """Verify that adding a sensor to a room links the sensor to the room ID."""
    room = Room(id="rm-101", name="Lab A", floor_number=1)
    sensor = TemperatureSensor(id="t1", name="Lab Temp")

    assert sensor.room_id is None
    room.add_sensor(sensor)

    assert sensor in room.sensors
    assert sensor.room_id == "rm-101"
    assert room.get_sensor("t1") == sensor

    # Remove sensor
    removed = room.remove_sensor("t1")
    assert removed is True
    assert sensor.room_id is None
    assert sensor not in room.sensors


def test_building_floor_room_hierarchy():
    """Verify multi-level spatial hierarchy composition."""
    bldg = Building(id="b1", name="Tower A", address="123 Tech St")
    fl1 = Floor(id="f1", number=1)
    rm1 = Room(id="r1", name="Server Room", floor_number=1)
    s1 = TemperatureSensor(id="s1", name="Rack Temp")
    s2 = HumiditySensor(id="s2", name="Rack Humidity")

    rm1.add_sensor(s1)
    rm1.add_sensor(s2)
    fl1.add_room(rm1)
    bldg.add_floor(fl1)

    assert fl1.building_id == "b1"
    assert rm1.floor_number == 1
    assert len(bldg.get_all_sensors()) == 2
    assert s1 in bldg.get_all_sensors()
    assert s2 in bldg.get_all_sensors()

    # Removal checks
    assert fl1.remove_room("r1") is True
    assert fl1.get_room("r1") is None
    assert len(bldg.get_all_sensors()) == 0


def test_sensor_create_reading():
    """Verify generating readings from an online sensor."""
    sensor = TemperatureSensor(id="t1", name="Temp Sensor")
    sensor.set_simulated_value(22.5)

    reading = sensor.create_reading(reading_id="rd-01")
    assert isinstance(reading, SensorReading)
    assert reading.id == "rd-01"
    assert reading.sensor_id == "t1"
    assert reading.value == 22.5
    assert reading.unit == "C"
    assert sensor.last_reading_time is not None


def test_sensor_create_reading_offline_error():
    """Verify that disabled or offline sensor raises an error when creating a reading."""
    sensor = TemperatureSensor(id="t1", name="Temp Sensor")
    sensor.disable()

    with pytest.raises(RuntimeError):
        sensor.create_reading()


def test_reading_validation_and_unit_conversion():
    """Verify is_valid logic and unit conversions for readings."""
    valid_reading = SensorReading("r1", "t1", datetime.now(), 25.0, "C")
    assert valid_reading.is_valid() is True

    # Celsius to Fahrenheit: (25 * 9/5) + 32 = 77.0
    f_val = valid_reading.convert_unit("F")
    assert round(f_val, 2) == 77.0

    # Celsius to Kelvin: 25 + 273.15 = 298.15
    k_val = valid_reading.convert_unit("K")
    assert round(k_val, 2) == 298.15

    # Power conversion: kW to W
    power_reading = SensorReading("r2", "e1", datetime.now(), 5.0, "kW")
    w_val = power_reading.convert_unit("W")
    assert w_val == 5000.0

    # Invalid reading check
    nan_reading = SensorReading("r3", "t1", datetime.now(), float("nan"), "C")
    assert nan_reading.is_valid() is False

    # Unsupported conversion
    with pytest.raises(ValueError):
        valid_reading.convert_unit("meter")
