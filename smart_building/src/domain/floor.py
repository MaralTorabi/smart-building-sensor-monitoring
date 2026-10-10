"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

from typing import List, Optional

from .room import Room


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
