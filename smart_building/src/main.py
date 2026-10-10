"""
Project: Smart Building Sensor Monitoring System
Author: Maral Torabi
Student ID: 40213312
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure root package can be imported regardless of execution context
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
for p in (str(project_root), str(current_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from src.domain.alert import Alert
    from src.domain.building import Building
    from src.domain.enums import AlertSeverity, AlertStatus, SensorStatus
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
    from src.repository.memory import AlertRepository, ReadingRepository, SensorRepository
    from src.service.alert import AlertService
    from src.service.monitoring import MonitoringService
    from src.service.notification import ConsoleNotificationService
    from src.service.reporting import ReportingService
except ModuleNotFoundError:
    from domain.alert import Alert
    from domain.building import Building
    from domain.enums import AlertSeverity, AlertStatus, SensorStatus
    from domain.floor import Floor
    from domain.room import Room
    from domain.sensor import (
        CO2Sensor,
        EnergySensor,
        HumiditySensor,
        MotionSensor,
        TemperatureSensor,
    )
    from domain.sensor_reading import SensorReading
    from repository.memory import AlertRepository, ReadingRepository, SensorRepository
    from service.alert import AlertService
    from service.monitoring import MonitoringService
    from service.notification import ConsoleNotificationService
    from service.reporting import ReportingService


def print_header(title: str) -> None:
    """Helper to print formatted section banners."""
    print("\n" + "=" * 75)
    print(f"  {title.upper()}")
    print("=" * 75)


def run_demo() -> None:
    """Executes the end-to-end building monitoring scenario."""
    print_header("1. Constructing Physical Facility Hierarchy")

    # 1. Create Building
    building = Building(
        id="bldg-01",
        name="Innovation Tower",
        address="100 Technology Parkway, Tech District",
    )
    print(f"[+] Initialized Building: '{building.name}' ({building.id})")

    # 2. Create Floor
    floor_2 = Floor(id="fl-02", number=2)
    building.add_floor(floor_2)
    print(f"[+] Added Floor {floor_2.number} to '{building.name}'")

    # 3. Create at least two Rooms
    server_room = Room(id="rm-201", name="Primary Data Center / Server Room", floor_number=2)
    boardroom = Room(id="rm-202", name="Executive Boardroom", floor_number=2)

    floor_2.add_room(server_room)
    floor_2.add_room(boardroom)
    print(f"[+] Added Rooms to Floor 2: '{server_room.name}' and '{boardroom.name}'")

    # Initialize Repositories and Services
    sensor_repo = SensorRepository()
    reading_repo = ReadingRepository()
    alert_repo = AlertRepository()

    notification_svc = ConsoleNotificationService()
    alert_svc = AlertService(
        alert_repository=alert_repo,
        notification_service=notification_svc,
        notification_recipient="facilities-oncall@innovationtower.com",
    )
    monitoring_svc = MonitoringService(
        sensor_repository=sensor_repo,
        reading_repository=reading_repo,
        alert_service=alert_svc,
    )
    reporting_svc = ReportingService(
        sensor_repository=sensor_repo,
        reading_repository=reading_repo,
        alert_repository=alert_repo,
    )

    print_header("2. Deploying Specialized Sensors to Rooms")

    # 4. Create different sensor types
    temp_sensor = TemperatureSensor(id="temp-01", name="Server Rack A Thermal Sensor")
    humidity_sensor = HumiditySensor(id="hum-01", name="Server Room Hygrometer")
    co2_sensor = CO2Sensor(id="co2-01", name="Boardroom Indoor Air Quality CO2")
    motion_sensor = MotionSensor(id="mot-01", name="Boardroom PIR Motion Sensor")
    energy_sensor = EnergySensor(id="eng-01", name="Floor 2 Main Substation Power Meter")

    sensors = [temp_sensor, humidity_sensor, co2_sensor, motion_sensor, energy_sensor]

    # 5. Attach sensors to rooms and register in repository
    server_room.add_sensor(temp_sensor)
    server_room.add_sensor(humidity_sensor)
    server_room.add_sensor(energy_sensor)

    boardroom.add_sensor(co2_sensor)
    boardroom.add_sensor(motion_sensor)

    for sensor in sensors:
        sensor_repo.add(sensor)
        print(f"  * Sensor '{sensor.name}' ({sensor.id}) -> Room: {sensor.room_id}")

    print_header("3. Generating and Processing Nominal Sensor Readings")

    # 6. Generate nominal sensor readings
    temp_reading_normal = temp_sensor.create_reading()
    hum_reading_normal = humidity_sensor.create_reading()
    co2_reading_normal = co2_sensor.create_reading()
    motion_reading = motion_sensor.create_reading()
    energy_reading = energy_sensor.create_reading()

    nominal_readings = [
        temp_reading_normal,
        hum_reading_normal,
        co2_reading_normal,
        motion_reading,
        energy_reading,
    ]

    for reading in nominal_readings:
        alert = monitoring_svc.process_reading(reading)
        status_msg = "OK (Normal)" if alert is None else f"ALERT: {alert.message}"
        print(f"  [Reading Processed] {reading.sensor_id}: {reading.value:.2f} {reading.unit} -> Status: {status_msg}")

    print_header("4. Simulating Threshold Violations (WARNING & CRITICAL)")

    # 7 & 8. Trigger WARNING and CRITICAL alerts
    # A) Trigger CRITICAL Alert: Server Room overheating to 38.5°C (Critical Max is 35.0°C)
    temp_sensor.set_simulated_value(38.5)
    temp_reading_hot = temp_sensor.create_reading()
    print("\n[-] Ingesting high temperature reading into MonitoringService...")
    crit_alert = monitoring_svc.process_reading(temp_reading_hot)

    # B) Trigger WARNING Alert: Boardroom CO2 spikes to 1250 ppm (Warning Max is 1000.0 ppm)
    co2_sensor.set_simulated_value(1250.0)
    co2_reading_high = co2_sensor.create_reading()
    print("\n[-] Ingesting elevated CO2 reading into MonitoringService...")
    warn_alert = monitoring_svc.process_reading(co2_reading_high)

    print_header("5. Displaying Active Open Alerts")

    # 9. Display open alerts
    open_alerts = alert_svc.get_open_alerts()
    print(f"Current open alerts count: {len(open_alerts)}\n")
    for a in open_alerts:
        print(f"  [Alert ID: {a.id[:8]}] Severity: {a.severity.value:<8} | Sensor: {a.sensor_id:<8} | Status: {a.status.value:<12} | Message: {a.message}")

    print_header("6. Alert Lifecycle Workflow (Acknowledge & Resolve)")

    # 10. Acknowledge an alert
    if crit_alert:
        print(f"[-] Acknowledging Critical Alert {crit_alert.id[:8]}...")
        alert_svc.acknowledge_alert(crit_alert.id)
        print(f"    Alert Status is now: {crit_alert.status.value} (Acknowledged at: {crit_alert.acknowledged_at})")

    # 11. Resolve an alert
    if crit_alert:
        print(f"[-] Resolving Critical Alert {crit_alert.id[:8]} after HVAC cooling adjustment...")
        alert_svc.resolve_alert(crit_alert.id)
        print(f"    Alert Status is now: {crit_alert.status.value} (Resolved at: {crit_alert.resolved_at})")

    # Remaining open alerts
    remaining_open = alert_svc.get_open_alerts()
    print(f"\nRemaining OPEN alerts count: {len(remaining_open)}")
    for a in remaining_open:
        print(f"  * {a.severity.value} - Sensor: {a.sensor_id} - '{a.message}'")

    print_header("7. Generating Analytical Reports (ReportingService)")

    # 12. Generate reports
    # A) Sensor Report
    temp_report = reporting_svc.generate_sensor_report(temp_sensor.id)
    print("\n--- [SENSOR REPORT: Server Rack Temp] ---")
    print(f"  Sensor ID:       {temp_report['sensor_id']} ({temp_report['name']})")
    print(f"  Total Readings:  {temp_report['total_readings']}")
    print(f"  Min Reading:     {temp_report['min_reading']} {temp_report['unit']}")
    print(f"  Max Reading:     {temp_report['max_reading']} {temp_report['unit']}")
    print(f"  Avg Reading:     {temp_report['avg_reading']} {temp_report['unit']}")
    print(f"  Total Alerts:    {temp_report['total_alerts']} (Open: {temp_report['open_alerts']})")

    # B) Room Report
    room_report = reporting_svc.generate_room_report(server_room)
    print(f"\n--- [ROOM REPORT: {room_report['name']}] ---")
    print(f"  Room ID:         {room_report['room_id']} (Floor {room_report['floor_number']})")
    print(f"  Sensors Count:   {room_report['sensor_count']}")
    print(f"  Total Alerts:    {room_report['total_alerts']} (Open: {room_report['open_alerts']})")

    # C) Building Report
    bldg_report = reporting_svc.generate_building_report(building)
    print(f"\n--- [BUILDING EXECUTIVE SUMMARY: {bldg_report['building_name']}] ---")
    print(f"  Address:         {bldg_report['address']}")
    print(f"  Floors:          {bldg_report['total_floors']}")
    print(f"  Rooms:           {bldg_report['total_rooms']}")
    print(f"  Total Sensors:   {bldg_report['total_sensors']} (Online: {bldg_report['online_sensors']})")
    print(f"  Total Readings:  {bldg_report['total_readings_stored']}")
    print(f"  Open Alerts:     {bldg_report['open_alerts']}")
    print(f"  Overall Health:  {bldg_report['system_health']}")

    print_header("Demonstration Completed Successfully")


if __name__ == "__main__":
    run_demo()
