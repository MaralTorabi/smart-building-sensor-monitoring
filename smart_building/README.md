# Smart Building Sensor Monitoring System

A modular, object-oriented Python application designed for monitoring smart facilities, analyzing environmental sensor telemetry, detecting threshold anomalies, tracking device lifecycles, and dispatching facility alerts.

This project is architected with clear structural boundaries, strong typing, generic repositories, and explicit object-oriented relationships tailored for **UML reverse engineering** and **round-trip engineering**.

---

## 1. Project Overview

Modern smart buildings rely on hundreds of specialized sensors (measuring temperature, humidity, CO₂, motion, and electrical power) distributed across multiple floors and rooms. The **Smart Building Sensor Monitoring System** provides:
* **Spatial Facility Modeling**: Hierarchical structure representing Buildings, Floors, and Rooms.
* **Sensor Hierarchy**: Polymorphic sensor implementations capable of unit-specific telemetry generation and status tracking.
* **Stream Monitoring**: Continuous threshold evaluation against multi-tiered warning and critical limits.
* **Device Health Detection**: Heartbeat monitoring that flags unresponsive sensors as `OFFLINE`.
* **Alert Lifecycle Management**: Tracking alerts through `OPEN`, `ACKNOWLEDGED`, and `RESOLVED` states.
* **Notification Decoupling**: Pluggable delivery mechanisms (Console, Email) via dependency inversion.
* **Facility Reporting**: Statistical metric calculations (min, max, average) and aggregate health scoring.

---

## 2. Architecture Overview

The system strictly adheres to a **Layered Architecture** ensuring clean separation of concerns and high maintainability:

```
+---------------------------------------------------------------+
|                       Presentation Layer                      |
|                  (main.py / CLI / Entry Points)               |
+---------------------------------------------------------------+
                               |
                               v
+---------------------------------------------------------------+
|                         Service Layer                         |
|   (MonitoringService, AlertService, ReportingService, etc.)   |
+---------------------------------------------------------------+
                 |                               |
                 v                               v
+-----------------------------------+    +----------------------+
|         Repository Layer          |    |     Notification     |
| (Repository[T], Memory Repos)     |    |  (Interface & Impls) |
+-----------------------------------+    +----------------------+
                 |
                 v
+---------------------------------------------------------------+
|                         Domain Layer                          |
|  - Spatial Models (Building, Floor, Room)                     |
|  - Sensor Hierarchy (Sensor, Temp, Hum, CO2, Motion, Energy)  |
|  - Alert & Reading Entities (Alert, SensorReading, Enums)     |
+---------------------------------------------------------------+
```

1. **Domain Layer (`src/domain/`)**: Pure domain models and business rules. Completely independent of persistence and external frameworks.
2. **Repository Layer (`src/repository/`)**: Encapsulates data persistence using the Generic Repository Pattern (`Repository[T]`), decoupled from storage engines.
3. **Service Layer (`src/service/`)**: Coordinates business workflows, threshold evaluation, offline detection, and reporting.
4. **Interface / Notification Layer (`src/service/notification.py`)**: Abstract delivery interfaces following the Dependency Inversion Principle.

---

## 3. Directory Structure

```
smart_building/
├── src/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py       # Building, Floor, Room
│   │   ├── sensors.py      # Sensor hierarchy, SensorStatus, SensorReading
│   │   └── alerts.py       # Alert, AlertSeverity, AlertStatus
│   ├── repository/
│   │   ├── __init__.py
│   │   ├── base.py         # Repository[T] generic abstraction
│   │   └── memory.py       # SensorRepository, ReadingRepository, AlertRepository
│   ├── service/
│   │   ├── __init__.py
│   │   ├── monitoring.py   # MonitoringService, ThresholdRule
│   │   ├── alert.py        # AlertService
│   │   ├── reporting.py    # ReportingService
│   │   └── notification.py # NotificationService abstraction and implementations
│   └── main.py             # Application entry point (demo scenario)
├── tests/
│   ├── __init__.py
│   ├── test_sensors.py     # Domain hierarchy and unit conversion tests
│   ├── test_monitoring.py  # Monitoring, alerts, offline detection, reporting tests
│   └── test_repositories.py# Generic CRUD and query tests
├── requirements.txt
└── README.md
```

---

## 4. Main Domain Concepts

* **Physical Structure**:
  * `Building`: Contains one or more floors.
  * `Floor`: Represents a physical building level containing multiple rooms.
  * `Room`: Container for deployed sensor hardware.
* **Sensor Telemetry**:
  * `Sensor`: Abstract base class providing common identity, status, heartbeat, and reading generation contracts.
  * `TemperatureSensor`, `HumiditySensor`, `CO2Sensor`, `MotionSensor`, `EnergySensor`: Polymorphic subclasses defining unit standards and simulation behaviors.
  * `SensorReading`: Discrete measurement record with value, unit, timestamp, and conversion capabilities.
* **Alerting**:
  * `Alert`: An incident entity capturing threshold violations or device offline transitions.
  * `AlertSeverity`: `INFO`, `WARNING`, `CRITICAL`.
  * `AlertStatus`: `OPEN`, `ACKNOWLEDGED`, `RESOLVED`.

---

## 5. How to Install

### Prerequisites
* Python 3.9+ (Python 3.10+ recommended)

### Installation
Clone or navigate to the project directory:

```bash
cd smart_building
```

(Optional) Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

Install requirements:
```bash
pip install -r requirements.txt
```

---

## 6. How to Run

Execute the end-to-end demonstration script:

```bash
python src/main.py
```
Or from the project parent directory:
```bash
python -m smart_building.src.main
```

---

## 7. How to Run Tests

Run the complete test suite using `pytest`:

```bash
pytest
```

For verbose output with test names:
```bash
pytest -v
```

For test coverage analysis:
```bash
pytest --cov=src -v
```

---

## 8. Example Scenario

When `src/main.py` is executed, the following automated sequence takes place:
1. **Facility Setup**: "Innovation Tower" is provisioned with Floor 2, containing a Server Room and an Executive Boardroom.
2. **Sensor Deployment**: Five specialized sensors are installed into the rooms and registered in the `SensorRepository`.
3. **Nominal Ingestion**: Regular telemetry is captured and analyzed; no alerts are raised.
4. **Threshold Anomalies**:
   * Server Room temperature hits **38.5°C** (exceeds critical threshold of 35.0°C) -> **CRITICAL Alert**.
   * Boardroom CO₂ spikes to **1250 ppm** (exceeds warning threshold of 1000.0 ppm) -> **WARNING Alert**.
5. **Console Notification**: The `ConsoleNotificationService` logs real-time dispatches with timestamps and recipients.
6. **Incident Remediation**: Facility personnel acknowledge and resolve the critical overheating alert.
7. **Reporting**: The `ReportingService` aggregates statistics and displays room and building diagnostic health summaries.

---

## 9. Explanation of Main Classes

| Class | Layer | Responsibility |
|---|---|---|
| `Building` | Domain | Represents physical building; owns multiple `Floor` objects via composite relation. |
| `Floor` | Domain | Represents a level; owns multiple `Room` objects; references parent `Building`. |
| `Room` | Domain | Aggregates multiple `Sensor` instances located within its physical boundaries. |
| `Sensor` (ABC) | Domain | Base abstraction for all hardware sensors; manages status, heartbeat, and reading creation. |
| `TemperatureSensor` | Domain | Sensor subclass measuring ambient temperature in Celsius (`C`). |
| `HumiditySensor` | Domain | Sensor subclass measuring relative humidity (`%`). |
| `CO2Sensor` | Domain | Sensor subclass measuring carbon dioxide concentration in ppm (`ppm`). |
| `MotionSensor` | Domain | Sensor subclass detecting presence/motion (`motion`). |
| `EnergySensor` | Domain | Sensor subclass measuring electrical energy consumption in kilowatt-hours (`kWh`). |
| `SensorReading` | Domain | Immutable record of sensor output with unit conversion and validation. |
| `Alert` | Domain | Models operational issues and manages lifecycle transitions (`OPEN` -> `ACKNOWLEDGED` -> `RESOLVED`). |
| `Repository[T]` (ABC) | Repository | Generic CRUD interface defining persistence contracts. |
| `InMemoryRepository[T]` | Repository | Dictionary-backed generic repository implementation. |
| `SensorRepository` | Repository | Specialized repository with queries by room, status, and online health. |
| `ReadingRepository` | Repository | Specialized repository with queries by sensor and temporal filters. |
| `AlertRepository` | Repository | Specialized repository with queries by sensor, severity, and lifecycle status. |
| `NotificationService` (ABC) | Service | Abstract contract for outbound alerting mechanisms. |
| `ConsoleNotificationService` | Service | Concrete notification service printing alerts to stdout. |
| `EmailNotificationService` | Service | Concrete notification service simulating SMTP delivery. |
| `MonitoringService` | Service | Core engine checking thresholds, identifying offline devices, and raising alerts. |
| `AlertService` | Service | Coordinates alert lifecycle updates and notification dispatches. |
| `ReportingService` | Service | Performs mathematical aggregations (min/max/avg) and compiles structured reports. |

---

## 10. Explanation of Relationships Between Classes

1. **Composition (`Building` *-- `Floor` *-- `Room`)**:
   * A `Building` is composed of `Floor` objects. Floors cannot exist independently of their facility context.
   * A `Floor` is composed of `Room` objects.
2. **Aggregation (`Room` o-- `Sensor`)**:
   * A `Room` aggregates `Sensor` objects. Sensors can be installed, moved between rooms, or removed without destroying the room.
3. **Generalization / Inheritance (`Sensor` <|-- `TemperatureSensor`, etc.)**:
   * Concrete sensors inherit identity, lifecycle, and reading logic from the abstract `Sensor` base class while specializing units and measurement behavior.
4. **Association (`Sensor` --> `SensorReading`)**:
   * A `Sensor` produces multiple `SensorReading` instances (one-to-many association).
5. **Association (`Alert` --> `Sensor`, `Alert` --> `SensorReading`)**:
   * An `Alert` associates with the offending `Sensor` (by `sensor_id`) and optionally the specific `SensorReading` (by `reading_id`) that triggered the anomaly.
6. **Interface Realization (`Repository[T]` <|.. `InMemoryRepository[T]` <|-- `SensorRepository`, etc.)**:
   * Concrete repositories realize the abstract generic CRUD interface.
7. **Interface Realization (`NotificationService` <|.. `ConsoleNotificationService`, `EmailNotificationService`)**:
   * Concrete delivery mechanisms realize the abstract notification interface.
8. **Dependency / Collaboration (`MonitoringService` --> `SensorRepository`, `ReadingRepository`, `AlertService`)**:
   * The monitoring service coordinates data access and delegates alert management.
9. **Dependency / Collaboration (`AlertService` --> `AlertRepository`, `NotificationService`)**:
   * The alert service manages persistence and dispatches alerts via the notification abstraction.
