"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

import math
from datetime import datetime


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
