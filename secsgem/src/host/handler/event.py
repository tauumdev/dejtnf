import logging
import threading
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.data_items import ACKC6

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.host.gemhost import SecsGemHost

from config.status_variable_define import CONTROL_STATE_EVENT, PROCESS_STATE_NAME

# from lot_management.validate import ValidateLot
from src.host.handler.lot_management.validate import ValidateLot
logger = logging.getLogger("app_logger")


class HandlerEvent:
    """
    Class for handling events
    """

    def __init__(self, gem_host: 'SecsGemHost'):
        self.gem_host = gem_host

    def receive_event(self, handler: secsgem.secs.SecsHandler, message: secsgem.common.Message):
        """
        Method for receiving event
        """
        handler.send_response(self.gem_host.stream_function(
            6, 12)(ACKC6.ACCEPTED), message.header.system)
        decode = self.gem_host.settings.streams_functions.decode(message)

        for rpt in decode.RPT:
            if rpt:
                rptid = rpt.RPTID.get()
                values = rpt.V.get()
                # print(f"RPTID: {rptid}")
                # print(f"Values: {values}")

                if rptid == 1000:
                    self._req_validate_lot(values)
                if rptid == 1001:
                    self._lot_open(values)
                if rptid == 1002:
                    self._lot_close(values)
                if rptid == 1003:
                    self._process_program_change(values)
                if rptid == 1004:
                    self._process_state_change(values)

        ceid = decode.CEID.get()

        self._control_state(ceid)

    def _req_validate_lot(self, values: list):
        """
        Validate lot event
        """
        def process_lot_id(lot_id):
            if "," in lot_id:
                parts = lot_id.split(",")
                lot_id = parts[0].upper()
                if len(parts) > 1 and parts[1].strip().lower() == "recipe":
                    # Recipe request
                    logger.info("Request recipe for lot: %s, %s",
                                lot_id, self.gem_host.equipment_name)
                    return lot_id, True
                logger.error("Invalid request: %s, %s", lot_id,
                             self.gem_host.equipment_name)
                return None, False
            return lot_id.upper(), False

        if values and len(values) == 5:
            lot_id, ppid, PlannedLots, NumberOfActiveLots, ActiveLots = values
            if not lot_id:
                print("Lot ID is required")
                return
        elif values and len(values) == 2:
            lot_id, ppid = values
            if not lot_id:
                print("Lot ID is required")
                return
        else:
            print("Invalid number of values")
            threading.Timer(0.5, self._reject_lot, args=(
                lot_id, "Invalid number of values")).start()
            return

        lot_id, is_recipe_request = process_lot_id(lot_id)
        if lot_id is None:
            print("Invalid request")
            threading.Timer(0.5, self._reject_lot, args=(
                lot_id, "Invalid request")).start()
            return

        # Define validate_lot object
        validate_lot = ValidateLot(self.gem_host.equipment_name, ppid, lot_id)

        if is_recipe_request:

            print(f"{self.gem_host.equipment_name} request recipe with lot: {lot_id}")
            recipe = validate_lot.get_recipe_by_lot()
            if isinstance(recipe, dict):
                # Send recipe to equipment
                recipe_name = recipe.get("recipe_name")
                print("Recipe found: ", recipe_name)
                print("Continue to send recipe")
                return

            # Recipe not found
            print(recipe)
            threading.Timer(0.5, self._reject_lot, args=(
                lot_id, "Recipe not found")).start()
            return

        # Validate lot
        result = validate_lot.validate()
        if isinstance(result, str):
            print("Reject lot", result)
            threading.Timer(0.5, self._reject_lot, args=(
                lot_id, result)).start()
        else:
            # Accept lot
            # Check if machine is FCLX is ready to accept lot before accepting
            print("Accept lot")
            print(result)
            threading.Timer(0.5, self._accept_lot, args=(
                lot_id, result.product_name, result.recipe_name)).start()

    def _reject_lot(self, lot_id: str, reason: str):
        """
        Reject lot event
        """
        logger.error("Reject lot: %s, %s, %s", lot_id,
                     reason, self.gem_host.equipment_name)
        if self.gem_host.equipment_model == "FCL":
            self.gem_host.secs_control.reject_lot(lot_id)
        elif self.gem_host.equipment_model == "FCLX":
            self.gem_host.secs_control.reject_lot_fclx(lot_id, reason)

    def _accept_lot(self, lot_id: str, product_name: str, recipe_name: str):
        """
        Accept lot event
        """
        if self.gem_host.equipment_model == "FCL":
            self.gem_host.secs_control.accept_lot(lot_id)
        elif self.gem_host.equipment_model == "FCLX":
            self.gem_host.secs_control.add_lot_fclx(lot_id)

    def _lot_open(self, values: list):
        """
        Lot open event
        """
        if values:
            if len(values) == 2:
                lot_id, ppid = values
                self.gem_host.active_lot = lot_id
                self.gem_host.mqtt_client.client.publish(
                    f"equipments/status/active_lot/{self.gem_host.equipment_name}", self.gem_host.active_lot, retain=True)

                logger.info("Lot opened: %s, %s, %s", lot_id,
                            ppid, self.gem_host.equipment_name)

    def _lot_close(self, values: list):
        """
        Lot close event
        """
        if values:
            if len(values) == 2:
                lot_id, ppid = values
                self.gem_host.active_lot = None
                self.gem_host.mqtt_client.client.publish(
                    f"equipments/status/active_lot/{self.gem_host.equipment_name}", self.gem_host.active_lot, retain=True)

                logger.info("Lot closed: %s, %s, %s", lot_id,
                            ppid, self.gem_host.equipment_name)

    def _control_state(self, ceid: int):
        """
        Control state event
        """

        control_state = CONTROL_STATE_EVENT.get(
            self.gem_host.equipment_model, {}).get(ceid)
        if control_state:
            self.gem_host.control_state = control_state
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/control_state/{self.gem_host.equipment_name}", self.gem_host.control_state, retain=True)

    def _process_program_change(self, values: list):
        """
        Process program change event
        """
        if values:
            self.gem_host.process_program = values[0]
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/process_program/{self.gem_host.equipment_name}", self.gem_host.process_program, retain=True)

    def _process_state_change(self, values: list):
        """
        Process state change event
        """
        if values:
            model_state = PROCESS_STATE_NAME.get(
                self.gem_host.equipment_model, {})
            if not model_state:
                return
            state_name = model_state.get(values[0])
            if not state_name:
                return
            self.gem_host.process_state = state_name
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/process_state/{self.gem_host.equipment_name}", self.gem_host.process_state, retain=True)
