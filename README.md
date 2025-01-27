# SECS/GEM Project

## Overview
Project for managing SECS/GEM equipment communication with MQTT integration and CLI control.

## Features
- SECS/GEM protocol support
- MQTT control interface
- Equipment state management
- Configuration management
- CLI tools

## Project Structure
```
secsgem/
├── src/
│   ├── main.py                     # Application entry point
│   ├── config/
│   │   ├── equipments.json         # Equipment configuration file
│   │   ├── mqtt.json               # MQTT settings file
│   │   ├── logging.conf            # Logging configuration file
│   ├── core/
│   │   ├── equipment_manager.py    # Manages all connected equipment
│   │   ├── host_manager.py         # Handles SECS/GEM connections
│   │   ├── states_manager.py       # Manages device states
│   │   ├── events/
│   │   │   ├── fcl_event.py        # Handles FCL events
│   │   │   ├── fclx_event.py       # Handles FCLX events
│   ├── alarms/
│   │   │   ├── fcl_alarm.py        # Handles FCL alarms
│   │   │   ├── fclx_alarm.py       # Handles FCLX alarms
│   ├── secs_gem/
│   │   ├── gemhost.py              # SECS/GEM protocol implementation
│   │   ├── message_handler.py      # Processes SECS/GEM messages
│   ├── mqtt/
│   │   ├── mqtt_client.py          # Manages MQTT connections
│   │   ├── mqtt_handle.py          # Handles MQTT commands
│   │   ├── mqtt_manager.py         # Controls MQTT subscribe/publish operations
│   ├── cli/
│   │   ├── cli_command.py          # CLI commands for equipment control
│   │   ├── cli_handler.py          # Processes CLI commands
│   ├── utils/
│   │   ├── logger.py               # Utility for logging operations
│   │   ├── config_loader.py        # Utility for loading configuration files
│   ├── tests/
│   │   ├── test_mqtt.py            # Unit tests for MQTT
│   │   ├── test_cli.py             # Unit tests for CLI functionality
│   │   ├── test_manager.py         # Unit tests for Equipment Manager
│   ├── requirements.txt            # Dependency requirements
│   ├── Dockerfile                  # Docker build file
│   ├── README.md                   # Project documentation
```

## Setup Instructions

### 1. Create Project Structure
Run the script to generate the folder and file structure:
```bash
chmod +x create_project.sh
./create_project.sh
```

### 2. Install Dependencies
Create a virtual environment and install depend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r secsgem/src/requirements.txt
```

### 3. Run the Application
Start the application with:
```bash
python secsgem/src/main.py
```

### 4. Testing
Run unit tests:
```bash
pytest secsgem/src/tests
```

### 5. Docker Build
Build a Docker image:
```bash
docker build -t secsgem:latest -f secsgem/src/Dockerfile .
```

## Notes
- Review configuration files in the `config` folder before starting the application.
- Customize MQTT and Logging settings as needed.
- CLI commands can be accessed and executed via the `cli` folder.

## MQTT Topics Structure

### Equipment Config
- add_equipment
- delete_equipment
- edit_equipment
- get_equipment

### Equipment Status
- enable                    ** by equipment name
- communication_state       ** by equipment name
    - equipment_status/communication_state/<machine> <state>
- control_state             ** by equipment name
    - equipment_status/control_state/<machine> <state>
- equipment_event           ** by equipment name
    - equipment_status/event/<machine> <message>
- equipment_alarm           ** by equipment name
    - equipment_status/alarm/<machine> <message>

### Equipment Control
- enable                    ** by equipment name
    - topic mqtt/control/enable payload <machine>
- disable                   ** by equipment name
    - topic mqtt/control/disable payload <machine>
- online                    ** by equipment name    
    - topic mqtt/control/online payload <machine>
- offline                   ** by equipment name
    - topic mqtt/control/offline payload <machine>

## License
MIT License
