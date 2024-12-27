# secsgem/src/cli/cli_main.py
import cmd
import logging
import socket
import sys

import secsgem.hsms
import secsgem.common

from core.equipment_manager import EquipmentManager

# from core import equipment_manager
# from core.equipment_manager import EquipmentManager

# Initialize the logger
logger = logging.getLogger("app_logger")


class HostCmd(cmd.Cmd):
    # Set the command line prompt
    prompt = "> "

    def __init__(self, equipment_manager: EquipmentManager):
        # Initialize the command prompt with the given equipment manager
        super().__init__()
        self.equipment_manager: EquipmentManager = equipment_manager

    def do_quit(self, arg):
        """Exit the CLI gracefully. Usage: quit"""
        logger.info("Exiting program...")
        self.equipment_manager.save_equipments_config()
        self.equipment_manager.disable_all_exit()
        logger.info("All equipment disabled. Program exited.")
        sys.exit(0)  # Normal exit code

    def do_status(self, arg):
        """Display the status of all equipment. Usage: status"""
        try:
            statuses = self.equipment_manager.get_statuses()
            for status in statuses:
                logger.info(status)
        except Exception as e:
            logger.error(f"Error fetching statuses: {e}")

    def do_online(self, equipment_name):
        """Set equipment online. Usage: online <equipment_name>"""
        result = self.equipment_manager.online(equipment_name)
        logger.info(result)

    def do_offline(self, equipment_name):
        """Set equipment offline. Usage: offline <equipment_name>"""
        result = self.equipment_manager.offline(equipment_name)
        logger.info(result)

    def do_add(self, arg):
        """Add new equipment. Usage: add <address> <port> <session_id> <connect_mode> <device_type> <equipment_name> <equipment_model> <enable>"""
        try:
            args = arg.split()
            if len(args) != 8:
                logger.error(
                    "Invalid number of arguments. Usage: add <address> <port> <session_id> <connect_mode> <device_type> <equipment_name> <equipment_model> <enable>")
                return

            address, port, session_id, connect_mode, device_type, equipment_name, equipment_model, enable = args

            # Validate address (check if it's a valid IP address)
            try:
                # This will raise an exception if the address is invalid
                socket.inet_aton(address)
            except socket.error:
                logger.error(f"Invalid IP address: {
                             address}. Please provide a valid address.")
                return

            # Validate port (ensure it's a valid integer and within the range)
            try:
                port = int(port)
                if port < 1 or port > 65535:
                    raise ValueError("Port must be between 1 and 65535.")
            except ValueError:
                logger.error(f"Invalid port: {
                             port}. Please provide a valid port number (1-65535).")
                return

            # Validate session_id (ensure it's a valid integer)
            try:
                session_id = int(session_id)
            except ValueError:
                logger.error(f"Invalid session_id: {
                             session_id}. Please provide a valid integer.")
                return

            # Validate connect_mode (ensure it's a valid connect mode enum)
            connect_mode = connect_mode.upper()
            valid_connect_modes = [
                mode.name for mode in secsgem.hsms.HsmsConnectMode]
            if connect_mode not in valid_connect_modes:
                logger.error(f"Invalid connect_mode: {connect_mode}. Allowed values are: {
                             ', '.join(valid_connect_modes)}")

            # Validate device_type (ensure it's a valid device type enum)
            device_type = device_type.upper()
            valid_device_types = [
                dtype.name for dtype in secsgem.common.DeviceType]
            if device_type not in valid_device_types:
                logger.error(f"Invalid device_type: {device_type}. Allowed values are: {
                             ', '.join(valid_device_types)}")
                return

            # Check if equipment already exists in the equipment list
            for eq in self.equipment_manager.equipment_list:
                if eq.equipment_name == equipment_name:
                    logger.error(f"Equipment {equipment_name} already exists.")
                    return

            enable = enable.lower() in ['true', '1', 'yes']

            equipment_config = {
                'address': address,
                'port': port,
                'session_id': session_id,
                'connect_mode': connect_mode,
                'device_type': device_type,
                'equipment_name': equipment_name,
                'equipment_model': equipment_model,
                'enable': enable
            }

            result = self.equipment_manager.add_equipment(equipment_config)
            logger.info(result)
        except ValueError as e:
            logger.error(f"Invalid argument type: {e}")
        except Exception as e:
            logger.error(f"Error adding equipment: {e}")
