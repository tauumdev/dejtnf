import logging
from secsgem.hsms.packets import HsmsPacket
from secsgem.secs.dataitems import ACKC6
from src.utils.config.status_variable_define import CONTROL_STATE_EVENT, PP_CHANGE_EVENT, PROCESS_STATE_CHANG_EVENT
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

        # check subscription for lot control
        for rpt in decode.RPT:
            if rpt:
                rptid = rpt.RPTID.get()
                values = rpt.V.get()
                try:
                    if rptid == 1000:
                        lot_id, pp_name = values
                        lot_id = str(lot_id).upper()
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

                        # validate lot
                        # validate_result = ValidateLot(
                        #     self.equipment.equipment_name, pp_name, lot_id)
                        # if not validate_result.result.get("status"):
                        #     message = validate_result.result.get("message")
                        #     self.reject_lot(lot_id, message)
                        #     return

                        # accept lot
                        self.accept_lot(lot_id)
                        # self.reject_lot(lot_id, "Not implemented")

                    elif rptid == 1001:
                        lot_id, pp_name = values
                        lot_id = lot_id.upper()
                        self.lot_open(lot_id)
                    elif rptid == 1002:
                        lot_id, pp_name = values
                        lot_id = lot_id.upper()
                        self.lot_close(lot_id)
                    # elif rptid == 1003:
                    #     self.recipe_init(values)
                    else:
                        logger.warning("Unknown RPTID: %s", rptid)
                except Exception as e:
                    logger.error("Error handling event: %s", e)

        # handle CEID
        ceid = decode.CEID.get()
        if ceid:
            try:
                # control state
                control_state = CONTROL_STATE_EVENT.get(
                    self.equipment.equipment_model, {}).get(ceid)
                if control_state:
                    self.equipment.control_state = control_state
                    logger.info("Control state: %s on %s",
                                control_state, self.equipment.equipment_name)
                    self.equipment.mqtt_client.client.publish(
                        f"equipments/status/control_state/{self.equipment.equipment_name}", control_state, 0, retain=True)

                # process state
                model_process_state = PROCESS_STATE_CHANG_EVENT.get(
                    self.equipment.equipment_model, {})
                model_process_state_ceid = model_process_state.get("CEID")
                model_process_state_vid = model_process_state.get("VID")
                model_process_state_state = model_process_state.get("STATE")

                if model_process_state:
                    if ceid == model_process_state_ceid:
                        s1f4 = self.equipment.secs_control.select_equipment_status_request(
                            [model_process_state_vid]).get()
                        state_code = s1f4[0]
                        state_name = next(
                            (state_dict[state_code]
                             for state_dict in model_process_state_state if state_code in state_dict),
                            # Default if code not found
                            f"Unknown State ({state_code})"
                        )
                        # print(f"Current State: {state_name}")
                        self.equipment.process_state = state_name
                        logger.info("Process state: %s on %s",
                                    state_name, self.equipment.equipment_name)
                        self.equipment.mqtt_client.client.publish(
                            f"equipments/status/process_state/{self.equipment.equipment_name}", state_name, 0, retain=True)

                # process program change
                model_pp_change = PP_CHANGE_EVENT.get(
                    self.equipment.equipment_model, {})
                if model_pp_change:
                    if ceid == model_pp_change.get("CEID"):
                        s1f4 = self.equipment.secs_control.select_equipment_status_request(
                            [model_pp_change.get("VID")]).get()
                        ppid = s1f4[0]
                        print(f"Process Program Change: {ppid}")
                        self.equipment.process_program = ppid
                        self.equipment.mqtt_client.client.publish(
                            f"equipments/status/process_program/{self.equipment.equipment_name}", ppid, 0, retain=True)

            except Exception as e:
                logger.error("Error handling event: %s", e)

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
            # !first check if lot is already added or lot active
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
