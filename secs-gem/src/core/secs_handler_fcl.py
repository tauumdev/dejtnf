import logging
import secsgem.common

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gemhsms.equipment_hsms import Equipment

logger = logging.getLogger("config_loader")


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


class HandlerFcl:
    def handle_s6f11(self, handler: 'Equipment', message: secsgem.common.Message):

        logger.info("FCL Handling s6f11")
        decode = handler.settings.streams_functions.decode(message)
        ceid = decode.CEID

        ceid_code = fcl_ceid()
        _state = ceid_code.get(ceid, f"Unknown code: {ceid}")
        logger.info("CEID: %s Message: %s", ceid.get(), _state)

        rpt = decode.RPT
        for report in rpt:
            logger.info("Report: %s", report)
            rptid = report.RPTID
            logger.info("RPTID: %s", rptid)
            values = report.V
            logger.info("Values: %s", values)
