import logging

command_logger = logging.getLogger("command_logger")


def fcl_ceid():
    ceid_code = {
        1: "event fixup GemPPChangeEvent",
        2: "event GemBadDownloadEvent",
        8: "offline",
        9: "online/local",
        10: "online/remote",
        20: "event GemLotValidate",
        21: "event GemLotOpened",
        22: "event GemLotClosed",
        2000: "event ProcessStateChangeEvent",
        2001: "event NoStateToInit",
        2002: "event InitToStandby",
        2003: "event StandbyToExecuting",
        2004: "event ExecutingToStandby",
        2005: "event RunningToWaiting",
        2006: "event WaitingToAssisting",
        2007: "event StandbyToWaiting",
        2008: "event AssistingToStandby",
        2009: "event NotStandbyToSpecRun",
        2010: "event NotStandbyToWaiting",
        2011: "event SpecRunToWaiting",
        2012: "event SpecRunToStandby",
        2013: "event StandbyToSpecRun",
        2014: "event NotStandbyToStandby",
        2015: "event StandbyToNotStandby",
        2016: "event ExecutingToPause",
        2017: "event PauseToExecuting",
        2018: "event ExecutingToRunEmpty",
        2019: "event RunEmptyToExecuting",
        3000: "event UnitStateChangeEvent",
    }

    return ceid_code


def fcl_vid():
    vid_code = {
        1: "CONFIGALARMS",
        7: "PPExecName",
        22: "ALARMID",
        23: "ALARMSENABLED",
        24: "ALARMSSET",
        25: "ALARMSTATE",
        26: "ALARMSERIAL",
        32: "GemMDLN",
        33: "GemPPExecName",
        39: "GemSOFTREV",
        40: "GemTime",
        37: "PREVIOUSPROCESSSTATE",
        38: "PROCESSSTATE",
        81: "LotValidate_LotID",
        82: "LotOpened_LotID",
        83: "LotClosed_LotID",
        20001: "PREVIOUSUNITSTATE",
        20000: "UNITSTATE",
        20002: "UNITID",
    }

    return vid_code


class Fcl_handle:
    def __init__(self, equipment):
        """
        Initialize Fcl_handle with the equipment instance.
        """
        self.equipment = equipment  # Store reference to equipment

        # Event handler map for CEIDs
        self.event_handlers = {
            8: self._handle_control_state,
            9: self._handle_control_state,
            10: self._handle_control_state,
            20: self.process_event_20,
        }

    def handle_ceid(self, ceid, message):
        """
        Handle CEID messages dynamically.
        """
        ceid_code = fcl_ceid()
        _state = ceid_code.get(ceid, f"Unknown code: {ceid}")
        command_logger.info(f"Received CEID {ceid} is {_state}")

        # Find and execute the handler if available
        handler = self.event_handlers.get(ceid, self._handle_unknown_ceid)
        handler(message)

    def _handle_control_state(self, ceid, message):
        """
        Handle control state changes (CEID 8, 9, 10).
        """
        ceid_code = fcl_ceid()
        _state = ceid_code.get(ceid, f"Unknown code: {ceid}")
        try:
            self.equipment.mqtt_client.publish(
                "equipment/control_state", _state)
            command_logger.info(f"Published control state: {_state}")
        except Exception as e:
            command_logger.error(f"MQTT publish error: {e}")

    def process_event_20(self, message):
        """
        Process CEID 20 event for Lot Validation.
        """
        command_logger.info("Processing CEID 20 event.")
        try:
            # Decode message
            decode = self.equipment.settings.streams_functions.decode(message)
            command_logger.info(f"Decoded message: {decode}")
            command_logger.info(f"RPT: {decode.RPT}")

            # Publish decoded data
            self.equipment.mqtt_client.publish(
                "equipment/events", "Event 20 processed")
        except Exception as e:
            command_logger.error(f"Error processing CEID 20: {e}")

    def _handle_unknown_ceid(self, ceid, message):
        """
        Handle unknown CEIDs gracefully.
        """
        command_logger.warning(f"Unknown CEID: {ceid}. Message ignored.")
        try:
            self.equipment.mqtt_client.publish(
                "equipment/events", f"Unknown CEID {ceid} received")
        except Exception as e:
            command_logger.error("MQTT publish error for unknown CEID: %s", e)
