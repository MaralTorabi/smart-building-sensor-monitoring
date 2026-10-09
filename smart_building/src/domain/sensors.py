"""Sensor domain models, enumerations, and concrete sensor implementations.

This module defines the sensor hierarchy for the Smart Building Monitoring System.
Explicit object-oriented design and strong typing are used to facilitate
UML reverse-engineering and round-trip engineering.
"""

from __future__ import annotations

import math
import random
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional


class SensorStatus(str, Enum):
    """Enumeration representing the operational status of a sensor."""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    DISABLED = "DISABLED"


class SensorReading:
    """Represents a discrete measurement produced by a sensor at a specific timestamp.

    Attributes:
        id: Unique identifier for the reading.
        sensor_id: Identifier of the sensor that generated this reading.
        timestamp: Time at which the reading was captured.
        value: Numeric measurement value.
        unit: Measurement unit (e.g., 'C', '%', 'ppm', 'kWh').
    """

    def __init__(
        self,
        id: str,
        sensor_id: str,
        timestamp: datetime,
        value: float,
        unit: str,
    ) -> None:
        self.id: str = id
        self.sensor_id: str = sensor_id
        self.timestamp: datetime = timestamp
        self.value: float = value
        self.unit: str = unit

    def is_valid(self) -> bool:
        """Validates that the reading value is a valid numeric measurement."""
        return not (math.isnan(self.value) or math.isinf(self.value))

    def convert_unit(self, target_unit: str) -> float:
        """Converts the reading value into a target unit of measurement.

        Args:
            target_unit: The desired target unit symbol.

        Returns:
            The converted numeric value.

        Raises:
            ValueError: If conversion between the units is unsupported.
        """
        if self.unit == target_unit:
            return self.value

        # Temperature conversions
        if self.unit == "C" and target_unit == "F":
            return (self.value * 9.0 / 5.0) + 32.0
        if self.unit == "F" and target_unit == "C":
            return (self.value - 32.0) * 5.0 / 9.0
        if self.unit == "C" and target_unit == "K":
            return self.value + 273.15
        if self.unit == "K" and target_unit == "C":
            return self.value - 273.15

        # Power/Energy conversions
        if self.unit == "W" and target_unit == "kW":
            return self.value / 1000.0
        if self.unit == "kW" and target_unit == "W":
            return self.value * 1000.0

        raise ValueError(f"Conversion from unit '{self.unit}' to '{target_unit}' is not supported.")

    def __repr__(self) -> str:
        return (
            f"SensorReading(id={self.id!r}, sensor_id={self.sensor_id!r}, "
            f"value={self.value:.2f}{self.unit}, timestamp={self.timestamp.isoformat()})"
        )


class Sensor(ABC):
    """Abstract base class representing a generic smart sensor.

    Attributes:
        id: Unique identifier for the sensor.
        name: Human-readable name of the sensor.
        status: Current operational status (ONLINE, OFFLINE, MAINTENANCE, DISABLED).
        room_id: Identifier of the room where the sensor is installed (if any).
        last_reading_time: Timestamp of the most recent reading produced.
        enabled: Flag indicating whether sensor data collection is active.
        unit: Measurement unit produced by this sensor type.
    """

    def __init__(
        self,
        id: str,
        name: str,
        unit: str,
        room_id: Optional[str] = None,
        status: SensorStatus = SensorStatus.ONLINE,
        enabled: bool = True,
    ) -> None:
        self.id: str = id
        self.name: str = name
        self.unit: str = unit
        self.room_id: Optional[str] = room_id
        self.status: SensorStatus = status
        self.last_reading_time: Optional[datetime] = None
        self.enabled: bool = enabled
        self._simulated_value: Optional[float] = None

    @abstractmethod
    def read_value(self) -> float:
        """Obtain a measurement value from the physical or simulated sensor."""
        pass

    def create_reading(self, reading_id: Optional[str] = None) -> SensorReading:
        """Generates a new SensorReading based on current sensor state.

        Args:
            reading_id: Optional explicit reading ID; generates a UUID if not provided.

        Returns:
            A populated SensorReading instance.

        Raises:
            RuntimeError: If the sensor is disabled or not online.
        """
        if not self.is_online():
            raise RuntimeError(f"Cannot generate reading: Sensor '{self.name}' ({self.id}) is not online.")

        now = datetime.now()
        val = self.read_value()
        self.last_reading_time = now

        r_id = reading_id or str(uuid.uuid4())
        return SensorReading(
            id=r_id,
            sensor_id=self.id,
            timestamp=now,
            value=val,
            unit=self.unit,
        )

    def is_online(self) -> bool:
        """Checks if the sensor is active and ready to produce readings."""
        return self.enabled and self.status == SensorStatus.ONLINE

    def enable(self) -> None:
        """Enables the sensor and sets status to ONLINE."""
        self.enabled = True
        self.status = SensorStatus.ONLINE

    def disable(self) -> None:
        """Disables the sensor and sets status to DISABLED."""
        self.enabled = False
        self.status = SensorStatus.DISABLED

    def set_simulated_value(self, value: Optional[float]) -> None:
        """Sets a fixed simulated value for testing and demonstration purposes."""
        self._simulated_value = value

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r}, "
            f"status={self.status.value}, room_id={self.room_id!r})"
        )


class TemperatureSensor(Sensor):
    """Specialized sensor for ambient temperature monitoring (in Celsius)."""

    def __init__(
        self,
        id: str,
        name: str,
        room_id: Optional[str] = None,
        status: SensorStatus = SensorStatus.ONLINE,
        enabled: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            unit="C",
            room_id=room_id,
            status=status,
            enabled=enabled,
        )

    def read_value(self) -> float:
        """Reads the temperature value (returns simulated value or random ~21.5°C)."""
        if self._simulated_value is not None:
            return float(self._simulated_value)
        return round(random.uniform(20.0, 24.0), 2)


class HumiditySensor(Sensor):
    """Specialized sensor for relative humidity monitoring (percentage)."""

    def __init__(
        self,
        id: str,
        name: str,
        room_id: Optional[str] = None,
        status: SensorStatus = SensorStatus.ONLINE,
        enabled: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            unit="%",
            room_id=room_id,
            status=status,
            enabled=enabled,
        )

    def read_value(self) -> float:
        """Reads relative humidity (returns simulated value or random ~45%)."""
        if self._simulated_value is not None:
            return float(self._simulated_value)
        return round(random.uniform(40.0, 55.0), 1)


class CO2Sensor(Sensor):
    """Specialized sensor for Carbon Dioxide concentration monitoring (in ppm)."""

    def __init__(
        self,
        id: str,
        name: str,
        room_id: Optional[str] = None,
        status: SensorStatus = SensorStatus.ONLINE,
        enabled: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            unit="ppm",
            room_id=room_id,
            status=status,
            enabled=enabled,
        )

    def read_value(self) -> float:
        """Reads CO2 levels in ppm (returns simulated value or random ~650 ppm)."""
        if self._simulated_value is not None:
            return float(self._simulated_value)
        return round(random.uniform(500.0, 800.0), 1)


class MotionSensor(Sensor):
    """Specialized sensor for occupancy / motion detection (1.0 for detected, 0.0 for idle)."""

    def __init__(
        self,
        id: str,
        name: str,
        room_id: Optional[str] = None,
        status: SensorStatus = SensorStatus.ONLINE,
        enabled: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            unit="motion",
            room_id=room_id,
            status=status,
            enabled=enabled,
        )

    def read_value(self) -> float:
        """Reads motion state (1.0 = motion detected, 0.0 = no motion)."""
        if self._simulated_value is not None:
            return float(self._simulated_value)
        return float(random.choice([0.0, 1.0]))


class EnergySensor(Sensor):
    """Specialized sensor for electrical energy consumption (in kWh)."""

    def __init__(
        self,
        id: str,
        name: str,
        room_id: Optional[str] = None,
        status: SensorStatus = SensorStatus.ONLINE,
        enabled: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            unit="kWh",
            room_id=room_id,
            status=status,
            enabled=enabled,
        )

    def read_value(self) -> float:
        """Reads energy consumption in kWh (returns simulated value or random ~12.5 kWh)."""
        if self._simulated_value is not None:
            return float(self._simulated_value)
        return round(random.uniform(5.0, 18.0), 2)
