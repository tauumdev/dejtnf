import logging
from secsgem.hsms.packets import HsmsPacket
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gem.equipment_hsms import Equipment

logger = logging.getLogger("app_logger")


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


class HandlerEventFcl:

    def __init__(self, equipment: 'Equipment'):
        self.equipment = equipment

    def handle_s6f11(self, handler: 'Equipment', message: HsmsPacket):

        # logger.info("FCL Handling s6f11")
        decode = handler.secs_decode(message)
        ceid = decode.CEID

        ceid_code = fcl_ceid()
        ceid_message = ceid_code.get(ceid, f"Unknown code: {ceid}")

        logger.info("FCL Handle s6f11 CEID: %s Message: %s",
                    ceid.get(), ceid_message)

        # Publish control state to MQTT
        if ceid.get() in [8, 9, 10]:
            handler.mqtt_client.client.publish(
                f"equipments/status/control_state/{handler.equipment_name}", payload=ceid_message, qos=1, retain=True)

        if decode.RPT:
            for rpt in decode.RPT:
                if rpt:
                    logger.info("RPT: %s", rpt.get())
                    rptid = rpt.RPTID
                    values = rpt.V
                    lot_id, ppname = values
                    if rptid.get() == 1000:
                        print("Lot validate: ", lot_id.get())
                        handler.send_remote_command(
                            rcmd="LOT_ACCEPT", params=[["LotID", lot_id.get()]])
                    elif rptid.get() == 1001:
                        logger.info("Lot open: %s", lot_id.get())
                    elif rptid.get() == 1002:
                        print("Lot closed: ", lot_id.get())
