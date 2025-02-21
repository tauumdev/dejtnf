import logging
import time
from typing import TYPE_CHECKING, Optional, Tuple, List, Dict, Any
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.data_items import ACKC6

from config.status_variable_define import CONTROL_STATE_EVENT, PROCESS_STATE_NAME
from src.host.handler.lot_management.validate import ValidateLot

if TYPE_CHECKING:
    from src.host.gemhost import SecsGemHost

logger = logging.getLogger("app_logger")

# Define constants for RPTIDs
RPTID_VALIDATE_LOT = 1000
RPTID_LOT_OPEN = 1001
RPTID_LOT_CLOSE = 1002
RPTID_PROGRAM_CHANGE = 1003
RPTID_STATE_CHANGE = 1004


class HandlerEvent:
    """
    Class for handling events in the GEM host.
    """

    def __init__(self, gem_host: 'SecsGemHost'):
        self.gem_host = gem_host

    def receive_event(self, _, message: secsgem.common.Message):
        """
        Receive and process an event from the GEM host.
        """
        try:
            decode = self.gem_host.settings.streams_functions.decode(message)
            for rpt in decode.RPT:
                if rpt:
                    self._process_report(rpt.RPTID.get(), rpt.V.get())

            ceid = decode.CEID.get()
            self._control_state(ceid)
        except Exception as e:
            logger.error("Error processing event: %s", e, exc_info=True)

    def _process_report(self, rptid: int, values: List[Any]):
        """
        Process a report based on its RPTID.
        """
        event_handlers = {
            RPTID_VALIDATE_LOT: self._req_validate_lot,
            RPTID_LOT_OPEN: self._lot_open,
            RPTID_LOT_CLOSE: self._lot_close,
            RPTID_PROGRAM_CHANGE: self._process_program_change,
            RPTID_STATE_CHANGE: self._process_state_change,
        }
        handler = event_handlers.get(rptid)
        if handler:
            handler(values)
        else:
            logger.error("No handler for RPTID: %s", rptid)

    # Event handlers
    def _control_state(self, ceid: int):
        """
        Handle control state event.
        """
        control_state = CONTROL_STATE_EVENT.get(
            self.gem_host.equipment_model, {}).get(ceid)
        if control_state:
            self.gem_host.control_state = control_state
            self.gem_host.mqtt_client.client.publish(
                "equipments/status/control_state/%s", self.gem_host.equipment_name, self.gem_host.control_state, qos=2, retain=True)

    def _lot_open(self, values: list):
        """
        Handle lot open event.
        """
        if values and len(values) == 2:
            lot_id, ppid = values
            self.gem_host.active_lot = lot_id
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/active_lot/{self.gem_host.equipment_name}", self.gem_host.active_lot, qos=2, retain=True)
            logger.info("Lot opened: %s, %s, %s", lot_id,
                        ppid, self.gem_host.equipment_name)

    def _lot_close(self, values: list):
        """
        Handle lot close event.
        """
        if values and len(values) == 2:
            lot_id, ppid = values
            self.gem_host.active_lot = None
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/active_lot/{self.gem_host.equipment_name}", self.gem_host.active_lot, qos=2, retain=True)
            logger.info("Lot closed: %s, %s, %s", lot_id,
                        ppid, self.gem_host.equipment_name)

    def _process_program_change(self, values: list):
        """
        Handle process program change event.
        """
        if values:
            self.gem_host.process_program = values[0]
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/process_program/{self.gem_host.equipment_name}", self.gem_host.process_program, qos=2, retain=True)

    def _process_state_change(self, values: list):
        """
        Handle process state change event.
        """
        if values:
            model_state = PROCESS_STATE_NAME.get(
                self.gem_host.equipment_model, {})
            if model_state:
                state_name = model_state.get(values[0])
                if state_name:
                    self.gem_host.process_state = state_name
                    self.gem_host.mqtt_client.client.publish(
                        f"equipments/status/process_state/{self.gem_host.equipment_name}", self.gem_host.process_state, qos=2, retain=True)

    # process validate lot and recipe request
    def _reject_lot(self, lot_id: str, reason: str):
        """
        Reject a lot.
        """
        logger.error("Reject lot: %s, %s, %s", lot_id,
                     reason, self.gem_host.equipment_name)
        if self.gem_host.equipment_model == "FCL":
            return self.gem_host.secs_control.reject_lot(lot_id)
        elif self.gem_host.equipment_model == "FCLX":
            return self.gem_host.secs_control.reject_lot_fclx(lot_id, reason)

    def _accept_lot(self, lot_id: str):
        """
        Accept a lot.
        """
        logger.info("Accept lot: %s", lot_id)
        if self.gem_host.equipment_model == "FCL":
            return self.gem_host.secs_control.accept_lot(lot_id)
        elif self.gem_host.equipment_model == "FCLX":
            return self.gem_host.secs_control.add_lot_fclx(lot_id)

    def _remove_lot(self, lot_id: str):
        """
        Remove a lot.
        """
        logger.info("Remove lot: %s", lot_id)
        params = [{'CPNAME': 'LotID', 'CPVAL': lot_id}]

        return self.gem_host.secs_control.send_remote_command(
            "REMOVE_LOT", params)

    def _process_lot_id(self, lot_id: str) -> Tuple[Optional[str], bool]:
        """
        Process and validate the lot ID.
        """
        if "," in lot_id:
            parts = lot_id.split(",")
            lot_id = parts[0].upper()
            if len(parts) > 1 and parts[1].strip().lower() == "recipe":
                logger.info(
                    "Request recipe for lot: %s, %s", lot_id, self.gem_host.equipment_name)
                return lot_id, True
            logger.error(
                "Invalid request: %s, %s", lot_id, self.gem_host.equipment_name)
            return None, False
        return lot_id.upper(), False

    def _validate_lot_id(self, values: List[Any]) -> Optional[Tuple[str, str, Optional[str], Optional[str]]]:
        """
        Validate the lot ID and extract values.
        """
        if not values:
            logger.error("No values provided")
            return None

        if len(values) == 4:
            lot_id, ppid, planned_lots, active_lots = values
        elif len(values) == 2:
            lot_id, ppid = values
            planned_lots, active_lots = None, None
        else:
            logger.error("Invalid number of values")
            return None

        if not lot_id:
            logger.error("Lot ID is required")
            return None

        return lot_id, ppid, planned_lots, active_lots

    # recipe request
    def _handle_fcl_recipe(self, lot_id: str, recipe_name: str) -> Optional[ValidateLot]:
        """
        Handle recipe for FCL equipment.
        """
        pp_select_result = self.gem_host.secs_control.pp_select(recipe_name)
        if pp_select_result not in ["OK", "Initiated for Asynchronous Completion"]:
            logger.error(
                "Select recipe failed: %s, %s, %s", lot_id, pp_select_result, self.gem_host.equipment_name)
            self._reject_lot(lot_id, pp_select_result)
            return None

        # logger.info("Select recipe success: %s", recipe_name)
        # time.sleep(0.2)
        # get recipe from equipment
        self.gem_host.secs_control.get_process_program()
        # logger.info("Recipe on equipment: %s", self.gem_host.process_program)
        return ValidateLot(self.gem_host.equipment_name, self.gem_host.process_program, lot_id)

    def _handle_fclx_recipe(self, lot_id: str, recipe_name: str, ppid: str, active_lots: Optional[str], request_lot_id: str) -> Optional[ValidateLot]:
        """
        Handle recipe for FCLX equipment.
        """
        if active_lots:
            self._reject_lot(request_lot_id, "Lot is active on equipment")
            return None

        if not self._process_send_recipe(recipe_name, request_lot_id, ppid):
            return None

        # response validate lot to equipment
        self._accept_lot(request_lot_id)
        self._remove_lot(request_lot_id)

        # get recipe from equipment
        self.gem_host.secs_control.get_process_program()
        return ValidateLot(self.gem_host.equipment_name, self.gem_host.process_program, lot_id)

    def _process_send_recipe(self, recipe_name: str, request_lot_id: str, old_ppid: str) -> bool:
        """
        Process sending, selecting, and deleting a recipe.
        """
        if self.gem_host.secs_control.pp_send(recipe_name) != "Accepted":
            logger.error(
                "Send recipe failed: %s, Send failed, %s", request_lot_id, self.gem_host.equipment_name)
            self._reject_lot(request_lot_id, "Send recipe failed")
            return False

        if self.gem_host.secs_control.pp_select(recipe_name) not in ["OK", "Initiated for Asynchronous Completion"]:
            logger.error(
                "Select recipe failed: %s, Select failed, %s", request_lot_id, self.gem_host.equipment_name)
            self._reject_lot(request_lot_id, "Select recipe failed")
            return False

        if self.gem_host.secs_control.pp_delete([old_ppid]) != "Accepted":
            logger.error(
                "Delete recipe failed: %s, Delete failed, %s", request_lot_id, self.gem_host.equipment_name)
            self._reject_lot(request_lot_id, "Delete recipe failed")
            return False

        return True

    def _handle_recipe_request(self, lot_id: str, ppid: str, active_lots: Optional[str], request_lot_id: str) -> Optional[ValidateLot]:
        """
        Handle a recipe request for a lot.
        """
        validate_lot = ValidateLot(self.gem_host.equipment_name, ppid, lot_id)
        recipe_result = validate_lot.get_recipe_by_lotid()

        if not isinstance(recipe_result, dict):
            logger.error("Recipe not found for lot: %s", lot_id)
            return None

        recipe_name = recipe_result.get("recipe_name")
        if self.gem_host.equipment_model == "FCL":
            return self._handle_fcl_recipe(lot_id, recipe_name)
        elif self.gem_host.equipment_model == "FCLX":
            return self._handle_fclx_recipe(lot_id, recipe_name, ppid, active_lots, request_lot_id)

    # validate lot
    def _validate_lot(self, validate_lot: ValidateLot, planned_lots: Optional[str]):
        """
        Validate a lot and accept or reject it.
        """
        validate_result = validate_lot.validate()

        if isinstance(validate_result, (str, type(None))):
            if validate_result is None:
                logger.error(
                    "Validation result is None for lot: %s", validate_lot.lot_id)
                self._reject_lot(validate_lot.lot_id,
                                 "Validation result is None")
            else:
                logger.error("Reject lot: %s", validate_result)
                self._reject_lot(validate_lot.lot_id, validate_result)
        else:
            logger.info("Process accept lot")
            if self.gem_host.equipment_model == "FCLX" and planned_lots:
                self._reject_lot(validate_lot.lot_id,
                                 "Equipment is not ready to accept lot")
                return
            logger.info(validate_result)
            self._accept_lot(validate_lot.lot_id)

    def _req_validate_lot(self, values: List[Any]):
        """
        Request to validate a lot.
        """
        validated_values = self._validate_lot_id(values)
        if not validated_values:
            return

        lot_id, ppid, planned_lots, active_lots = validated_values
        request_lot_id = lot_id
        lot_id, is_recipe_request = self._process_lot_id(lot_id)

        if lot_id is None:
            logger.error("Invalid request for lot: %s", lot_id)
            self._reject_lot(lot_id, "Invalid request")
            return

        if is_recipe_request:

            validate_lot = self._handle_recipe_request(
                lot_id, ppid, active_lots, request_lot_id)

            if not validate_lot:
                self._reject_lot(request_lot_id, "Recipe not found")
                return
        else:
            validate_lot = ValidateLot(
                self.gem_host.equipment_name, ppid, lot_id)

        self._validate_lot(validate_lot, planned_lots)
