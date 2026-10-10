"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

from typing import List, Optional

from .sensor import Sensor


class Room:
    """Represents a discrete physical room within a building floor.

    A Room acts as an aggregation container for various sensors installed within it.

    Attributes:
        id: Unique identifier for the room.
        name: Descriptive room name (e.g., 'Conference Room A', 'Server Room').
        floor_number: Number of the floor where this room is located.
        sensors: List of sensors installed in this room.
    """

    def __init__(self, id: str, name: str, floor_number: int) -> None:
        self.id: str = id
        self.name: str = name
        self.floor_number: int = floor_number
        self.sensors: List[Sensor] = []

    def add_sensor(self, sensor: Sensor) -> None:
        """Installs a sensor in this room and associates the sensor with this room's ID.

        Args:
            sensor: Sensor instance to attach.
        """
        if sensor not in self.sensors:
            self.sensors.append(sensor)
            sensor.room_id = self.id

    def remove_sensor(self, sensor_id: str) -> bool:
        """Removes a sensor from this room by its identifier.

        Args:
            sensor_id: Identifier of the sensor to remove.

        Returns:
            True if sensor was found and removed; False otherwise.
        """
        for i, sensor in enumerate(self.sensors):
            if sensor.id == sensor_id:
                sensor.room_id = None
                self.sensors.pop(i)
                return True
        return False

    def get_sensor(self, sensor_id: str) -> Optional[Sensor]:
        """Finds a sensor installed in this room by identifier."""
        for sensor in self.sensors:
            if sensor.id == sensor_id:
                return sensor
        return None

    def __repr__(self) -> str:
        return (
            f"Room(id={self.id!r}, name={self.name!r}, floor={self.floor_number}, "
            f"sensor_count={len(self.sensors)})"
        )
