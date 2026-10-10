"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

from typing import List, Optional

from .floor import Floor
from .sensor import Sensor


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
