import logging
from typing import TYPE_CHECKING


from src.equipment_manager.equipment.core.rcmd_fclfclx import fcl_accept_lot_cmd

from src.utils.config.secsgem_subscribe import SUBSCRIBE_LOT_CONTROL_FCL, SUBSCRIBE_LOT_CONTROL_FCLX

if TYPE_CHECKING:
    from src.equipment_manager.equipment.equipment import Equipment

logger = logging.getLogger("app_logger")


class fcl:
    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def accept_lot(self, lot_id: str):
        """
        Sends a request to accept a lot (FCL LOT_ACCEPT command) and processes the response.
        """
        logger.info("Processing lot acceptance request: %s", lot_id)

        params = {
            "RCMD": "LOT_ACCEPT",
            "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}]
        }

        response_codes = {
            0x0: "ok,complete",
            0x1: "invalid command",
            0x2: "cannot do now",
            0x3: "parameter error",
            0x4: "initiated for asynchronous completion",
            0x5: "rejected, already in desired condition",
            0x6: "invalid object"
        }

        try:
            s2f42 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 41)(params)
            )

            s2f42_decoded = self.equipment.secs_decode(s2f42)
            hack = s2f42_decoded.HCACK.get()
            response_message = response_codes.get(
                hack, "Unknown response code")

            if hack == 0:
                logger.info("Lot successfully accepted: %s", lot_id)
                return {"status": "success", "message": f"Lot {lot_id} was successfully accepted."}
            else:
                logger.error("Lot acceptance failed for %s: %s",
                             lot_id, response_message)
                return {
                    "status": "failed",
                    "message": f"Lot acceptance failed for {lot_id} on equipment {self.equipment.equipment_name}: {response_message}"
                }

        except Exception as e:
            logger.exception(
                "An error occurred while accepting lot %s", lot_id)
            return {"status": "error", "message": f"An error occurred while accepting lot {lot_id}: {str(e)}"}


class fclx:
    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def add_lot(self, lot_id: str):
        """
        Sends a request to add a lot (S2F49 ADD_LOT command) and processes the response.
        """
        logger.info("Processing lot addition request: %s", lot_id)

        params = {
            "DATAID": 100,
            "OBJSPEC": "LOTCONTROL",
            "RCMD": "ADD_LOT",
            "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}]
        }

        response_codes = {
            0x0: "ok,complete",
            0x1: "invalid command",
            0x2: "cannot do now",
            0x3: "parameter error",
            0x4: "initiated for asynchronous completion",
            0x5: "rejected, already in desired condition",
            0x6: "invalid object"
        }

        try:
            s2f49 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 49)(params)
            )

            s2f49_decoded = self.equipment.secs_decode(s2f49)
            hack = s2f49_decoded.HCACK.get()
            response_message = response_codes.get(
                hack, "Unknown response code")

            if hack == 0:
                logger.info("Lot successfully added: %s", lot_id)
                return {"status": "success", "message": f"Lot {lot_id} was successfully added."}
            else:
                logger.error("Lot addition failed for %s: %s",
                             lot_id, response_message)
                return {
                    "status": "failed",
                    "message": f"Lot addition failed for {lot_id} on equipment {self.equipment.equipment_name}: {response_message}"
                }

        except Exception as e:
            logger.exception("An error occurred while adding lot %s", lot_id)
            return {"status": "error", "message": f"An error occurred while adding lot {lot_id}: {str(e)}"}


class FunctionControl:
    """
    Class to handle function control
    """

    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment
        self.fcl = fcl(equipment)
        self.fclx = fclx(equipment)

    def subscribe_lot_control(self):
        """
        Subscribe lot control
        """

        logger.info("Subscribe lot control... %s %s",
                    self.equipment.equipment_name, self.equipment.equipment_model)

        if self.equipment.equipment_model == "FCL":
            self.equipment.disable_ceid_reports()
            self.enable_all_events()
            for subscribe in SUBSCRIBE_LOT_CONTROL_FCL:
                self.equipment.subscribe_collection_event(
                    subscribe["ceid"],
                    subscribe["dvs"],
                    subscribe["report_id"]
                )
        elif self.equipment.equipment_model == "FCLX":
            self.equipment.disable_ceid_reports()
            self.enable_all_events()
            for subscribe in SUBSCRIBE_LOT_CONTROL_FCLX:
                self.equipment.subscribe_collection_event(
                    subscribe["ceid"],
                    subscribe["dvs"],
                    subscribe["report_id"]
                )
        else:
            logger.warning("Unknown equipment model: %s for equipment: %s",
                           self.equipment.equipment_model, self.equipment.equipment_name)

    def enable_all_events(self):
        """
        Enable all events
        """
        logger.info("Disable all collection events")

        return self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 37)({"CEED": True, "CEID": []}))

    def disable_all_events(self):
        """
        Disable all events
        """
        logger.info("Disable all collection events")

        return self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 37)({"CEED": False, "CEID": []}))

    def enable_event(self, ceid):
        """
        Enable event
        """
        logger.info("Enable collection event %s", ceid)

        return self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 37)({"CEED": True, "CEID": [ceid]}))

    def disable_event(self, ceid):
        """
        Disable event
        """
        logger.info("Disable collection event %s", ceid)

        return self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 37)({"CEED": False, "CEID": [ceid]}))

    # def fcl_accept_lot(self, lot_id: str):
    #     """
    #     FCL accept lot
    #     """
    #     logger.info("FCL accept lot")

    #     return self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 41)(fcl_accept_lot_cmd(lot_id)))
