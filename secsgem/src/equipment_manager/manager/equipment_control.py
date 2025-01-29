import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from src.equipment_manager.eq_manager import EquipmentManager

logger = logging.getLogger("app_logger")


class EquipmentControl:
    """
    This class handles the control of equipment, including enabling, disabling, setting online, and setting offline equipment
    """

    def __init__(self, manager: 'EquipmentManager'):
        self.manager = manager

    def enable_equipment(self, equipment_name: str):
        """
        Enable an equipment instance.
        Args:
            equipment_name (str): Equipment name.
        """
        try:
            for equipment in self.manager.equipments:
                if equipment.equipment_name == equipment_name:
                    if equipment.is_enabled:
                        return {"status": "error", "message": f"Equipment {equipment_name} is already enabled."}
                    equipment.enable()
                    equipment.is_enabled = True
                    self.manager.config.save_equipments()
                    logger.info("Equipment %s enabled", equipment_name)
                    return {"status": "success", "message": f"Equipment {equipment_name} enabled"}
            logger.error("Equipment %s not found", equipment_name)
            return {"status": "error", "message": f"Equipment {equipment_name} not found"}
        except Exception as e:
            logger.error("Error enabling equipment: %s", e)
            return {"status": "error", "message": f"Error enabling equipment: {e}"}

    def disable_equipment(self, equipment_name: str):
        """
        Disable an equipment instance.
        Args:
            equipment_name (str): Equipment name.
        """
        try:
            for equipment in self.manager.equipments:
                if equipment.equipment_name == equipment_name:
                    if not equipment.is_enabled:
                        return {"status": "error", "message": f"Equipment {equipment_name} is already disabled."}
                    equipment.disable()
                    equipment.is_enabled = False
                    self.manager.config.save_equipments()
                    logger.info("Equipment %s disabled", equipment_name)
                    return {"status": "success", "message": f"Equipment {equipment_name} disabled"}
            logger.error("Equipment %s not found", equipment_name)
            return {"status": "error", "message": f"Equipment {equipment_name} not found"}
        except Exception as e:
            logger.error("Error disabling equipment: %s", e)
            return {"status": "error", "message": f"Error disabling equipment: {e}"}

    def online_equipment(self, equipment_name: str):
        """
        Set an equipment instance to online.
        Args:
            equipment_name (str): Equipment name.
        """
        try:
            for equipment in self.manager.equipments:
                if equipment.equipment_name == equipment_name:
                    logger.debug("Checking equipment %s status: is_enabled=%s",
                                 equipment_name, equipment.is_enabled)
                    if not equipment.is_enabled:
                        return {"status": "error", "message": f"Equipment {equipment_name} is disabled. Enable it first."}
                    rsp_code = {0x0: "ok", 0x1: "refused",
                                0x2: "already online"}
                    rsp = equipment.go_online()
                    error_message = rsp_code.get(rsp, "unknown error")
                    if rsp == 0:
                        logger.info("Equipment %s set to online",
                                    equipment_name)
                        return {"status": "success", "message": f"Equipment {equipment_name} set to online"}
                    logger.error(
                        "Error setting equipment to online: %s", error_message)
                    return {"status": "error", "message": f"Error setting equipment to online: {error_message}"}
            logger.error("Equipment %s not found", equipment_name)
            return {"status": "error", "message": f"Equipment {equipment_name} not found"}
        except Exception as e:
            logger.exception("Error setting equipment to online: %s", e)
            return {"status": "error", "message": f"Error setting equipment to online: {e}"}

    def offline_equipment(self, equipment_name: str):
        """
        Set an equipment instance to offline.
        Args:
            equipment_name (str): Equipment name.
        """
        try:
            for equipment in self.manager.equipments:
                if equipment.equipment_name == equipment_name:
                    logger.debug("Checking equipment %s status: is_enabled=%s",
                                 equipment_name, equipment.is_enabled)
                    if not equipment.is_enabled:
                        return {"status": "error", "message": f"Equipment {equipment_name} is disabled. Enable it first."}
                    rsp_code = {0x0: "ok", 0x1: "refused",
                                0x2: "already offline"}
                    rsp = equipment.go_offline()
                    error_message = rsp_code.get(rsp, "unknown error")
                    if rsp == 0:
                        logger.info("Equipment %s set to offline",
                                    equipment_name)
                        return {"status": "success", "message": f"Equipment {equipment_name} set to offline"}
                    logger.error(
                        "Error setting equipment to offline: %s", error_message)
                    return {"status": "error", "message": f"Error setting equipment to offline: {error_message}"}
            logger.error("Equipment %s not found", equipment_name)
            return {"status": "error", "message": f"Equipment {equipment_name} not found"}
        except Exception as e:
            logger.exception("Error setting equipment to offline: %s", e)
            return {"status": "error", "message": f"Error setting equipment to offline: {e}"}
