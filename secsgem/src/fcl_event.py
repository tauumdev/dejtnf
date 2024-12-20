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

class FCLEvent:
    def __init__(self):
        # Initialize any necessary attributes here
        pass

    def handle_ceid(self, ceid, message):
        # Add your logic to handle the CEID here

        try:
            decode = self.settings.streams_functions.decode(message)
        except Exception as e:
            print(f"Error decoding message: {e}")
            return
        ceid_code = fcl_ceid()
        _state = ceid_code.get(ceid, f"Unknown code: {ceid}")

        print(f"Handling CEID: {ceid}, {_state}")
        if ceid in [8, 9, 10]:
            try:
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/controlstate", _state
                )
            except Exception as e:
                print(f"Error publishing to MQTT: {e}")
