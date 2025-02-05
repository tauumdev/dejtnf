import logging
from secsgem.hsms.packets import HsmsPacket
from secsgem.secs.dataitems import ACKC6
from src.gemhost.events.fcl.handler_ceids_fclx import HandlerCeidFclx
from src.gemhost.events.fcl.handler_ceids_fcl import HandlerCeidFcl
from src.validate.validate_lot import ValidateLot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gemhost.equipment import Equipment

logger = logging.getLogger("app_logger")


class HandlerEventsReceive:
    """
    Class for handling events
    """

    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def events_receive(self, handler, packet: HsmsPacket):
        """
        Handle S06F11
        """
        self.equipment.send_response(self.equipment.stream_function(6, 12)(
            ACKC6.ACCEPTED), packet.header.system)
        decode = self.equipment.secs_decode(packet)
        ceid = decode.CEID.get()

        if self.equipment.equipment_model == "FCL":
            HandlerCeidFcl(ceid, self.equipment).handle_ceid()
        elif self.equipment.equipment_model == "FCLX":
            HandlerCeidFclx(ceid, self.equipment).handle_ceid()

        for rpt in decode.RPT:
            if rpt:
                rptid = rpt.RPTID.get()
                values = rpt.V.get()
                try:
                    if rptid == 1000:
                        lot_id, pp_name = values
                        lot_id = lot_id.upper()
                        if not lot_id:
                            logger.warning(
                                "Requsest validate lot but lot_id is empty")
                            return

                        request_recipe = lot_id.split(",")
                        if len(request_recipe) > 1 and request_recipe[1] == "RECIPE":
                            logger.info(
                                "Equipment request Recipe with lot_id: %s", lot_id)
                            return

                        logger.info("Validate lot: %s on %s", lot_id,
                                    self.equipment.equipment_name)
                        validate_result = ValidateLot(
                            self.equipment.equipment_name, pp_name, lot_id)
                        if not validate_result.result.get("status"):
                            message = validate_result.result.get("message")
                            self.reject_lot(lot_id, message)
                            return
                        self.accept_lot(lot_id)

                    elif rptid == 1001:
                        lot_id, pp_name = values
                        lot_id = lot_id.upper()
                        self.lot_open(lot_id)
                    elif rptid == 1002:
                        lot_id, pp_name = values
                        lot_id = lot_id.upper()
                        self.lot_close(lot_id)
                    elif rptid == 1003:
                        self.recipe_init(values)
                    else:
                        logger.warning("Unknown RPTID: %s", rptid)
                except Exception as e:
                    logger.error("Error handling event: %s", e)

    def recipe_init(self, pp_name: str):
        """
        Init recipe
        """
        if isinstance(pp_name, list):
            self.equipment.ppid = pp_name[0]
            pp_name = pp_name[0]
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/ppid/{self.equipment.equipment_name}", pp_name, 0, retain=True)

    def lot_open(self, lot_id: str):
        """
        Open lot
        """
        self.equipment.lot_active = lot_id
        logger.info("Open lot: %s on %s", lot_id,
                    self.equipment.equipment_name)
        self.equipment.mqtt_client.client.publish(
            f"equipments/status/lot_active/{self.equipment.equipment_name}", lot_id, 0, retain=True)

    def lot_close(self, lot_id: str):
        """
        Close lot
        """
        self.equipment.lot_active = None
        logger.info("Close lot: %s on %s", lot_id,
                    self.equipment.equipment_name)
        self.equipment.mqtt_client.client.publish(
            f"equipments/status/lot_active/{self.equipment.equipment_name}", "", 0, retain=True)

    def accept_lot(self, lot_id: str):
        """
        Accept lot based on equipment model
        """
        if self.equipment.equipment_model == "FCL":
            self.equipment.secs_control.lot_management.accept_lot_fcl(
                lot_id)
        elif self.equipment.equipment_model == "FCLX":
            self.equipment.secs_control.lot_management.add_lot_fclx(lot_id)
        else:
            logger.error("Unknown equipment model: %s",
                         self.equipment.equipment_model)

    def reject_lot(self, lot_id: str, reason: str = "Reason"):
        """
        Reject lot based on equipment model
        """
        if self.equipment.equipment_model == "FCL":
            self.equipment.secs_control.lot_management.reject_lot_fcl(
                lot_id)
        elif self.equipment.equipment_model == "FCLX":
            self.equipment.secs_control.lot_management.reject_lot_fclx(
                lot_id, reason)
        else:
            logger.error("Unknown equipment model: %s, equipment_name: %s",
                         self.equipment.equipment_model, self.equipment.equipment_name)
