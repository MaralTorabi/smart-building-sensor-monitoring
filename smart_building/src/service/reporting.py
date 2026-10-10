"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..domain.building import Building
from ..domain.enums import AlertStatus
from ..domain.room import Room
from ..repository.memory import AlertRepository, ReadingRepository, SensorRepository


class ReportingService:
    """Provides statistical aggregations and domain reports across system entities.

    Attributes:
        sensor_repository: Injected sensor repository.
        reading_repository: Injected reading repository.
        alert_repository: Injected alert repository.
    """

    def __init__(
        self,
        sensor_repository: SensorRepository,
        reading_repository: ReadingRepository,
        alert_repository: AlertRepository,
    ) -> None:
        self.sensor_repository: SensorRepository = sensor_repository
        self.reading_repository: ReadingRepository = reading_repository
        self.alert_repository: AlertRepository = alert_repository

    def calculate_average_reading(self, sensor_id: str) -> Optional[float]:
        """Calculates arithmetic mean of recorded values for a given sensor."""
        readings = self.reading_repository.get_by_sensor_id(sensor_id)
        if not readings:
            return None
        return round(sum(r.value for r in readings) / len(readings), 2)

    def calculate_min_reading(self, sensor_id: str) -> Optional[float]:
        """Calculates minimum recorded value for a given sensor."""
        readings = self.reading_repository.get_by_sensor_id(sensor_id)
        if not readings:
            return None
        return round(min(r.value for r in readings), 2)

    def calculate_max_reading(self, sensor_id: str) -> Optional[float]:
        """Calculates maximum recorded value for a given sensor."""
        readings = self.reading_repository.get_by_sensor_id(sensor_id)
        if not readings:
            return None
        return round(max(r.value for r in readings), 2)

    def generate_sensor_report(self, sensor_id: str) -> Dict[str, Any]:
        """Compiles a diagnostic status report for an individual sensor."""
        sensor = self.sensor_repository.get_by_id(sensor_id)
        if sensor is None:
            return {"error": f"Sensor '{sensor_id}' not found"}

        readings = self.reading_repository.get_by_sensor_id(sensor_id)
        alerts = self.alert_repository.get_by_sensor_id(sensor_id)
        latest_reading = self.reading_repository.get_latest_reading(sensor_id)

        return {
            "sensor_id": sensor.id,
            "name": sensor.name,
            "unit": sensor.unit,
            "status": sensor.status.value,
            "is_online": sensor.is_online(),
            "total_readings": len(readings),
            "latest_reading": {
                "value": latest_reading.value,
                "unit": latest_reading.unit,
                "timestamp": latest_reading.timestamp.isoformat(),
            } if latest_reading else None,
            "min_reading": self.calculate_min_reading(sensor_id),
            "max_reading": self.calculate_max_reading(sensor_id),
            "avg_reading": self.calculate_average_reading(sensor_id),
            "total_alerts": len(alerts),
            "open_alerts": len([a for a in alerts if a.status == AlertStatus.OPEN]),
        }

    def generate_room_report(self, room: Room) -> Dict[str, Any]:
        """Compiles an environmental summary for a specific room."""
        sensor_summaries: List[Dict[str, Any]] = []
        for sensor in room.sensors:
            sensor_summaries.append(self.generate_sensor_report(sensor.id))

        room_alerts = []
        for sensor in room.sensors:
            room_alerts.extend(self.alert_repository.get_by_sensor_id(sensor.id))

        return {
            "room_id": room.id,
            "name": room.name,
            "floor_number": room.floor_number,
            "sensor_count": len(room.sensors),
            "sensors": sensor_summaries,
            "total_alerts": len(room_alerts),
            "open_alerts": len([a for a in room_alerts if a.status == AlertStatus.OPEN]),
        }

    def generate_building_report(self, building: Building) -> Dict[str, Any]:
        """Compiles an executive status and health report for an entire building."""
        all_sensors = building.get_all_sensors()
        all_alerts: List[Any] = []
        for sensor in all_sensors:
            all_alerts.extend(self.alert_repository.get_by_sensor_id(sensor.id))

        open_alerts = [a for a in all_alerts if a.status == AlertStatus.OPEN]
        online_count = sum(1 for s in all_sensors if s.is_online())

        return {
            "building_id": building.id,
            "building_name": building.name,
            "address": building.address,
            "total_floors": len(building.floors),
            "total_rooms": sum(len(f.rooms) for f in building.floors),
            "total_sensors": len(all_sensors),
            "online_sensors": online_count,
            "offline_sensors": len(all_sensors) - online_count,
            "total_readings_stored": self.reading_repository.count(),
            "total_alerts": len(all_alerts),
            "open_alerts": len(open_alerts),
            "system_health": "OPTIMAL" if not open_alerts else ("CRITICAL" if any(a.severity.value == "CRITICAL" for a in open_alerts) else "WARNING"),
        }
