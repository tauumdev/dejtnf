# secsgem Project Setup

## Concept
The "secsgem" project is designed to manage communication between industrial equipment using the SECS/GEM protocol and supports remote control via MQTT and CLI. Its goal is to enable efficient control and monitoring of equipment states and operations.

### Key Features:
- **SECS/GEM Protocol Support:** Implements SECS/GEM standards for industrial automation.
- **MQTT Integration:** Allows IoT and Industry 4.0 compatibility with MQTT broker support.
- **Command Line Interface (CLI):** Provides tools to control and monitor devices.
- **Flexible Configuration:** Supports customizable settings through config files and logging.
- **Testing Framework:** Includes unit tests to ensure code quality and reliability.

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
│   │   ├── alarms/
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
Create a virtual environment and install dependencies:
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

## License
MIT License


- secs/gem
    - src
        - main.py
        - config
            - equipments.json
            - mqtt.json
        - core 
            - host_manager.py
            - handle_event
                - fcl_event.py
                - fclx_event.py
            - handle_alarm
                - fcl_alarm.py
                - fclx_alarm.py
        - secs-gem
            - gemhost.py
        - mqtt
            - mqtt_client.py
            - mqtt_handle.py
        - cli
            - cli_command.py

- function manager
    - add equipment
    - delete equipment
    - edit equipment
    - get equipment
    - enable equipment
    - disable equipment
    - online equipment
    - offline equipment
    - list equipment
    - get status equipment by machine
    - gets status equipment all machine
    - secs-gem
        - define function secs-gem

- mqtt
    - equipment_config
        - add_equipment
        - delete_equipment
        - edit_equipment
        - get_equipment
        
    - equipment_status 
        - enable                    ** by equipment name
        - communication_state       ** by equipment name
            - equipment_status/communication_state/<machine> <state>
        - control_state             ** by equipment name
            - equipment_status/control_state/<machine> <state>
        - equipment_event           ** by equipment name
            - equipment_status/event/<machine> <message>
        - equipment_alarm           ** by equipment name
            - equipment_status/alarm/<machine> <message>

    - equipment_control
        - enable                    ** by equipment name
            - topic mqtt/control/enable payload <machine>
        - disable                   ** by equipment name
            - topic mqtt/control/disable payload <machine>
        - online                    ** by equipment name    
            - topic mqtt/control/online payload <machine>
        - offline                   ** by equipment name
            - topic mqtt/control/offline payload <machine>
            
- cli
    - call all function manager



- Mqtt
    - equipments/status
    - mqtt/config
        - mqtt/response/config
    - mqtt/control
        - mqtt/response/control