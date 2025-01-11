#!/bin/bash

# Create project directories
mkdir -p secsgem/src/{config,core/{events,alarms},secs_gem,mqtt,cli,utils,tests}

# Create main application file
touch secsgem/src/main.py

# Create configuration files
touch secsgem/src/config/{equipments.json,mqtt.json,logging.conf}

# Create core files
touch secsgem/src/core/{equipment_manager.py,host_manager.py,states_manager.py}
touch secsgem/src/core/events/{fcl_event.py,fclx_event.py}
touch secsgem/src/core/alarms/{fcl_alarm.py,fclx_alarm.py}

# Create SECS/GEM protocol files
touch secsgem/src/secs_gem/{gemhost.py,message_handler.py}

# Create MQTT files
touch secsgem/src/mqtt/{mqtt_client.py,mqtt_handle.py,mqtt_manager.py}

# Create CLI files
touch secsgem/src/cli/{cli_command.py,cli_handler.py}

# Create utility files
touch secsgem/src/utils/{app_logger.py,gem_logger.py,config_loader.py}

# Create test files
touch secsgem/src/tests/{test_mqtt.py,test_cli.py,test_manager.py}

# Create project dependencies and documentation files
touch secsgem/src/{requirements.txt,Dockerfile,README.md}

# Output message
echo "Project structure created successfully!"
