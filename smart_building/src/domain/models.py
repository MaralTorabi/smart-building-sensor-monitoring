"""Spatial and architectural domain models: Building, Floor, and Room.

This module models the physical hierarchy of a smart facility:
Building -> Floor -> Room -> Sensor.
"""

from __future__ import annotations

from typing import List, Optional

from .sensors import Sensor


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


class Floor:
    """Represents a floor level within a smart building.

    A Floor contains multiple rooms and belongs to a parent Building.

    Attributes:
        id: Unique identifier for the floor.
        number: Numerical floor index (e.g., 1, 2, 3).
        rooms: List of rooms located on this floor.
        building_id: Identifier of the parent building (optional until assigned).
    """

    def __init__(self, id: str, number: int, building_id: Optional[str] = None) -> None:
        self.id: str = id
        self.number: int = number
        self.rooms: List[Room] = []
        self.building_id: Optional[str] = building_id

    def add_room(self, room: Room) -> None:
        """Adds a room to this floor.

        Args:
            room: Room instance to add.
        """
        if room not in self.rooms:
            self.rooms.append(room)
            room.floor_number = self.number

    def remove_room(self, room_id: str) -> bool:
        """Removes a room from this floor by identifier.

        Args:
            room_id: Identifier of the room to remove.

        Returns:
            True if room was found and removed; False otherwise.
        """
        for i, room in enumerate(self.rooms):
            if room.id == room_id:
                self.rooms.pop(i)
                return True
        return False

    def get_room(self, room_id: str) -> Optional[Room]:
        """Finds a room on this floor by its identifier."""
        for room in self.rooms:
            if room.id == room_id:
                return room
        return None

    def __repr__(self) -> str:
        return (
            f"Floor(id={self.id!r}, number={self.number}, "
            f"building_id={self.building_id!r}, room_count={len(self.rooms)})"
        )


class Building:
    """Represents an entire physical building managed by the monitoring system.

    Building exhibits a composite relationship with Floor objects.

    Attributes:
        id: Unique identifier for the building.
        name: Name of the building.
        address: Physical location / street address.
        floors: List of floors belonging to this building.
    """

    def __init__(self, id: str, name: str, address: str) -> None:
        self.id: str = id
        self.name: str = name
        self.address: str = address
        self.floors: List[Floor] = []

    def add_floor(self, floor: Floor) -> None:
        """Adds a floor to this building and binds floor's building reference.

        Args:
            floor: Floor instance to include in the building.
        """
        if floor not in self.floors:
            self.floors.append(floor)
            floor.building_id = self.id

    def remove_floor(self, floor_id: str) -> bool:
        """Removes a floor from this building by its identifier.

        Args:
            floor_id: Identifier of the floor to remove.

        Returns:
            True if floor was found and removed; False otherwise.
        """
        for i, floor in enumerate(self.floors):
            if floor.id == floor_id:
                floor.building_id = None
                self.floors.pop(i)
                return True
        return False

    def get_floor(self, floor_id: str) -> Optional[Floor]:
        """Finds a floor in this building by identifier."""
        for floor in self.floors:
            if floor.id == floor_id:
                return floor
        return None

    def get_all_sensors(self) -> List[Sensor]:
        """Collects all sensors across all floors and rooms within this building."""
        sensors: List[Sensor] = []
        for floor in self.floors:
            for room in floor.rooms:
                sensors.extend(room.sensors)
        return sensors

    def __repr__(self) -> str:
        return (
            f"Building(id={self.id!r}, name={self.name!r}, "
            f"address={self.address!r}, floor_count={len(self.floors)})"
        )
