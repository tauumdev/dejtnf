#!/bin/bash

# สร้างโฟลเดอร์และไฟล์
mkdir -p secsgem/src/cli
mkdir -p secsgem/src/mqtt
mkdir -p secsgem/src/hosthandler
mkdir -p secsgem/src/utils
mkdir -p secsgem/src/settings
mkdir -p secsgem/tests/cli
mkdir -p secsgem/tests/mqtt
mkdir -p secsgem/tests/hosthandler
mkdir -p secsgem/tests/utils

# สร้างไฟล์ใน src/cli
touch secsgem/src/cli/cli_main.py
touch secsgem/src/cli/cli_handler.py
touch secsgem/src/cli/cli_parser.py

# สร้างไฟล์ใน src/mqtt
touch secsgem/src/mqtt/mqtt_client.py
touch secsgem/src/mqtt/mqtt_handler.py
touch secsgem/src/mqtt/topics.py

# สร้างไฟล์ใน src/hosthandler
touch secsgem/src/hosthandler/host_handler.py
touch secsgem/src/hosthandler/command_processor.py
touch secsgem/src/hosthandler/state_manager.py

# สร้างไฟล์ใน src/utils
touch secsgem/src/utils/logger.py
touch secsgem/src/utils/config_loader.py
touch secsgem/src/utils/message_decoder.py
touch secsgem/src/utils/communication_log_file_handler.py

# สร้างไฟล์ใน src/settings
touch secsgem/src/settings/config.yaml

# สร้าง main.py
touch secsgem/src/main.py

touch secsgem/src/__init__.py
touch secsgem/tests/__init__.py

# สร้างไฟล์ใน tests/cli
touch secsgem/tests/cli/test_cli_main.py
touch secsgem/tests/cli/test_cli_handler.py
touch secsgem/tests/cli/test_cli_parser.py

# สร้างไฟล์ใน tests/mqtt
touch secsgem/tests/mqtt/test_mqtt_client.py
touch secsgem/tests/mqtt/test_mqtt_handler.py
touch secsgem/tests/mqtt/test_topics.py

# สร้างไฟล์ใน tests/hosthandler
touch secsgem/tests/hosthandler/test_host_handler.py
touch secsgem/tests/hosthandler/test_command_processor.py
touch secsgem/tests/hosthandler/test_state_manager.py

# สร้างไฟล์ใน tests/utils
touch secsgem/tests/utils/test_logger.py
touch secsgem/tests/utils/test_config_loader.py
touch secsgem/tests/utils/test_message_decoder.py
touch secsgem/tests/utils/test_communication_log_file_handler.py

# สร้างไฟล์ integration test
touch secsgem/tests/test_integration.py

# สร้างไฟล์เสริมใน root directory
touch secsgem/README.md
touch secsgem/requirements.txt
touch secsgem/.env
touch secsgem/Dockerfile

# แสดงผลโครงสร้าง
tree secsgem/
