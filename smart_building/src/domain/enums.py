"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from enum import Enum


class SensorStatus(str, Enum):
    """Enumeration representing the operational status of a sensor."""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    DISABLED = "DISABLED"


class AlertSeverity(str, Enum):
    """Severity levels for system alerts."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    """Lifecycle status for system alerts."""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
