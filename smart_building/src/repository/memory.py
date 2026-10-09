"""In-memory concrete repository implementations.

This module provides in-memory data storage implementations of Repository[T]
for sensors, readings, and alerts.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Generic, List, Optional, TypeVar

from ..domain.alerts import Alert, AlertSeverity, AlertStatus
from ..domain.sensors import Sensor, SensorReading, SensorStatus
from .base import Repository

T = TypeVar("T")


class InMemoryRepository(Repository[T], Generic[T]):
    """Generic in-memory repository backed by a dictionary storage."""

    def __init__(self) -> None:
        self._storage: Dict[str, T] = {}

    def add(self, entity: T) -> None:
        """Stores the entity using its 'id' attribute as the primary key."""
        entity_id = getattr(entity, "id", None)
        if entity_id is None:
            raise AttributeError("Entity must have an 'id' attribute to be stored.")
        self._storage[str(entity_id)] = entity

    def get_by_id(self, id: str) -> Optional[T]:
        """Retrieves entity by id string."""
        return self._storage.get(str(id))

    def get_all(self) -> List[T]:
        """Retrieves a list of all stored entities."""
        return list(self._storage.values())

    def update(self, entity: T) -> bool:
        """Updates an entity if it already exists in storage."""
        entity_id = getattr(entity, "id", None)
        if entity_id is not None and str(entity_id) in self._storage:
            self._storage[str(entity_id)] = entity
            return True
        return False

    def delete(self, id: str) -> bool:
        """Deletes an entity from storage by id."""
        if str(id) in self._storage:
            del self._storage[str(id)]
            return True
        return False

    def clear(self) -> None:
        """Removes all stored records."""
        self._storage.clear()

    def count(self) -> int:
        """Returns the total number of records currently stored."""
        return len(self._storage)


class SensorRepository(InMemoryRepository[Sensor]):
    """In-memory repository specializing in Sensor domain entities."""

    def get_by_room_id(self, room_id: str) -> List[Sensor]:
        """Finds all sensors installed inside a specific room."""
        return [s for s in self._storage.values() if s.room_id == room_id]

    def get_by_status(self, status: SensorStatus) -> List[Sensor]:
        """Finds all sensors with a specific operational status."""
        return [s for s in self._storage.values() if s.status == status]

    def get_offline_sensors(self) -> List[Sensor]:
        """Retrieves all sensors that are currently marked as OFFLINE."""
        return [s for s in self._storage.values() if s.status == SensorStatus.OFFLINE]

    def get_enabled_sensors(self) -> List[Sensor]:
        """Retrieves all sensors whose monitoring is enabled."""
        return [s for s in self._storage.values() if s.enabled]


class ReadingRepository(InMemoryRepository[SensorReading]):
    """In-memory repository specializing in SensorReading domain entities."""

    def get_by_sensor_id(self, sensor_id: str) -> List[SensorReading]:
        """Finds all readings produced by a specific sensor."""
        return [r for r in self._storage.values() if r.sensor_id == sensor_id]

    def get_latest_reading(self, sensor_id: str) -> Optional[SensorReading]:
        """Retrieves the most recent reading for a given sensor."""
        readings = self.get_by_sensor_id(sensor_id)
        if not readings:
            return None
        return max(readings, key=lambda r: r.timestamp)

    def get_readings_since(self, sensor_id: str, since: datetime) -> List[SensorReading]:
        """Retrieves readings for a sensor recorded after a specific timestamp."""
        return [
            r for r in self._storage.values()
            if r.sensor_id == sensor_id and r.timestamp >= since
        ]


class AlertRepository(InMemoryRepository[Alert]):
    """In-memory repository specializing in Alert domain entities."""

    def get_by_sensor_id(self, sensor_id: str) -> List[Alert]:
        """Finds all alerts associated with a specific sensor."""
        return [a for a in self._storage.values() if a.sensor_id == sensor_id]

    def get_by_status(self, status: AlertStatus) -> List[Alert]:
        """Finds all alerts currently matching a given lifecycle status."""
        return [a for a in self._storage.values() if a.status == status]

    def get_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Finds all alerts matching a given severity level."""
        return [a for a in self._storage.values() if a.severity == severity]

    def get_open_alerts(self) -> List[Alert]:
        """Retrieves all active OPEN alerts."""
        return self.get_by_status(AlertStatus.OPEN)
