import logging
from secsgem.hsms.packets import HsmsPacket
from typing import TYPE_CHECKING

from src.gem.command_rcmd import addlot_fclx, pp_select
if TYPE_CHECKING:
    from src.gem.equipment_hsms import Equipment


logger = logging.getLogger("app_logger")


def fclx_ceid():
    # Events, alarms and variable identifiers
    ceid_code = {
        1: "ProcessProgramChanged",
        2: "ProcessStateChanged",
        3: "TerminalMessageAcknowledge",
        4: "EquipmentConstantChanged",
        5: "SpoolingActivated",
        6: "SpoolingDeactivated",
        7: "ControlStateLocal",
        8: "ControlStateRemote",
        9: "EquipmentOffline",
        10: "EstablishCommunicationsTimeoutChanged",
        26: "MagazineLoaded",
        27: "MagazineOffloaded",
        28: "StripLoaded",
        29: "StripRejected",
        30: "StripPrealigned",
        31: "StripRejectBinEmptied",
        32: "StripSawn",
        33: "StripCleanDried",
        34: "StripProcessed",
        35: "DeviceRejectBinEmptied",
        36: "OkTrayOffloaded",
        37: "OkTrayStackRemoved",
        38: "ReworkTrayOffloaded",
        39: "ReworkTrayStackRemoved",
        40: "LotOpened",
        41: "LotClosed",
        42: "AddLotComplete",
        43: "RemoveLotComplete",
        44: "EditLotComplete",
        45: "InitialStripsProcessed",
        46: "FrontBladeChangeStarted",
        47: "RearBladeChangeStarted",
        48: "FrontBladeChangeCompleted",
        49: "RearBladeChangeCompleted",
        50: "PerformanceReport",
        51: "EquipmentEPTStateChanged",
        52: "LoaderEPTStateChanged",
        53: "SawEPTStateChanged",
        54: "SorterEPTStateChanged",
        55: "LotCleared",
        56: "PPSelected",
        57: "StripLaserMarked",
        58: "LotScanned",
        59: "MissingStrips",
        60: "OffloadMagazineLoaded",
        61: "OffloadMagazineOffloaded",
        62: "StripRemoved",
        63: "StripSeparated",
        64: "UserChanged",
        65: "OkTubeLoaded",
        66: "OkTubeOffloaded",
        67: "<free>",
        68: "TrayLoaded",
        69: "<free>",
        70: "ValidateMagazine",
        71: "ValidateStrip",
        72: "ValidateOffloadMagazine",
        73: "ValidateTray",
        74: "<free>",
        75: "ValidateOkTube",
        76: "KerfCheckCompleted",
        77: "InspectionHeadCalibrated",
        78: "FrontBladeDressingActive",
        79: "RearBladeDressingActive",
    }

    return ceid_code


def fclx_vid():

    vid_code = {

        # Equipment constants
        12: "TimeFormat",
        13: "EstablishCommunicationsTimeout",
        14: "PollDelay",
        15: "MaxSpoolTransmit",
        16: "OverWriteSpool",
        1000: "DefaultOnlineControlState",
        1001: "MaximumStripRejects",
        1002: "LotControlMode",
        1003: "DefaultControlState",
        1004: "DefaultOfflineControlState",
        1005: "AllowAutoReject",
        1006: "ValidateMagazine",
        1007: "ValidateStrip",
        1008: "ValidateTray",
        1009: "<free>",
        1010: "ValidateLot",
        1011: "ValidateOffloadMagazine",
        1012: "ValidateOkTube",

        # Status variables
        1: "AlarmsEnabled",
        2: "AlarmsSet",
        3: "PPError",
        4: "PPFormat",
        7: "PPExecName",
        8: "ProcessState",
        9: "PreviousProcessState",
        10: "LastChangedEquipmentConstant",
        11: "Clock",
        17: "SpoolCountActual",
        18: "SpoolCountTotal",
        19: "SpoolFullTime",
        20: "SpoolStartTime",
        21: "ControlState",
        22: "EventsEnabled",
        2000: "StripRejectCount",
        2001: "PlannedLots",
        2002: "DryRunEnabled",
        2003: "FrontBladeDiameter",
        2004: "RearBladeDiameter",
        2005: "FrontBladeType",
        2006: "RearBladeType",
        2007: "FrontBladeDistanceUsed",
        2008: "RearBladeDistanceUsed",
        2009: "FrontBladeDistanceRemaining",
        2010: "RearBladeDistanceRemaining",
        2011: "FrontBladeLastChange",
        2012: "RearBladeLastChange",
        2013: "PR_RepickID",
        2014: "PR_SawchuckID",
        2015: "PR_CarrierID",
        2016: "PR_PickAndPlaceLeftID",
        2017: "PR_PickAndPlaceRightID",
        2018: "PR_InfeedCavityPlateID",
        2019: "PR_OutfeedCavityPlateID",
        2020: "PR_InspectionHeadID",
        2021: "MaterialPresent",
        2022: "NumberOfActiveLots",
        2023: "ActiveLots",
        2024: "LockEnabled",
        2025: "ProductionCounter",
        2026: "TotalCounter",
        2027: "ActiveSections",
        2028: "RunEmptyMode",
        2029: "MachineRecipeQualified",

        # Data variables
        5: "PPChangeName",
        6: "PPChangeStatus",
        3000: "LoadedMagazineStripCount",
        3001: "LoadedMagazineID",
        3002: "OffloadedMagazineID",
        3003: "OffloadedMagazineLot",
        3004: "OffloadedMagazineReason",
        3005: "OffloadedMagazineStripCount",
        3006: "LoadedStripID",
        3007: "LoadedStripLot",
        3008: "RejectedStripID",
        3009: "RejectedStripLot",
        3010: "RejectedStripReason",
        3011: "PrealignedStripID",
        3012: "PrealignedStripLot",
        3013: "StripRejectRemovedIDs",
        3014: "SawnStripID",
        3015: "SawnStripLot",
        3016: "CleanDriedStripID",
        3017: "CleanDriedStripLot",
        3018: "ProcessedStripID",
        3019: "ProcessedStripLot",
        3020: "DeviceRejectRemovedDevices",
        3021: "OffloadedOkTrayID",
        3022: "OffloadedOkTrayTransferMap",
        3023: "OffloadedReworkTrayID",
        3024: "OffloadedReworkTrayTransferMap",
        3025: "OffloadedReworkTrayBinCodeMap",
        3026: "OpenedLotID",
        3027: "ClosedLotID",
        3028: "ClosedLotReason",
        3029: "AddedLotID",
        3030: "RemovedLotID",
        3031: "EditedLotID",
        3032: "UPH_Report",
        3033: "MTBA_Report",
        3034: "MTBF_Report",
        3035: "EquipmentCurrentEPTState",
        3036: "EquipmentPreviousEPTState",
        3037: "EquipmentEPTStateTime",
        3038: "EquipmentEPTClock",
        3039: "EquipmentEPTTaskName",
        3040: "EquipmentEPTPreviousTaskName",
        3041: "EquipmentEPTTaskType",
        3042: "EquipmentEPTPreviousTaskType",
        3043: "EquipmentEPTBlockReason",
        3044: "EquipmentEPTBlockReasonText",
        3045: "LoaderCurrentEPTState",
        3046: "LoaderPreviousEPTState",
        3047: "LoaderEPTStateTime",
        3048: "LoaderEPTClock",
        3049: "LoaderEPTTaskName",
        3050: "LoaderEPTPreviousTaskName",
        3051: "LoaderEPTTaskType",
        3052: "LoaderEPTPreviousTaskType",
        3053: "LoaderEPTBlockReason",
        3054: "LoaderEPTBlockReasonText",
        3055: "SawCurrentEPTState",
        3056: "SawPreviousEPTState",
        3057: "SawEPTStateTime",
        3058: "SawEPTClock",
        3059: "SawEPTTaskName",
        3060: "SawEPTPreviousTaskName",
        3061: "SawEPTTaskType",
        3062: "SawEPTPreviousTaskType",
        3063: "SawEPTBlockReason",
        3064: "SawEPTBlockReasonText",
        3065: "SorterCurrentEPTState",
        3066: "SorterPreviousEPTState",
        3067: "SorterEPTStateTime",
        3068: "SorterEPTClock",
        3069: "SorterEPTTaskName",
        3070: "SorterEPTPreviousTaskName",
        3071: "SorterEPTTaskType",
        3072: "SorterEPTPreviousTaskType",
        3073: "SorterEPTBlockReason",
        3074: "SorterEPTBlockReasonText",
        3075: "ClearedLotID",
        3076: "SelectedPPName",
        3077: "OffloadedOkTrayLot",
        3078: "OffloadedReworkTrayLot",
        3079: "ProcessedStripBinCodeMap",
        3080: "OperatorID",
        3081: "ScannedLotID",
        3082: "MissingStripsID",
        3083: "MissingStripsLot",
        3084: "PerformanceData",
        3085: "<free>",
        3086: "LoadOffloadMagazineID",
        3087: "OffloadOffloadMagazineID",
        3088: "OffloadOffloadMagazineLot",
        3089: "OffloadOffloadMagazineReason",
        3090: "OffloadOffloadMagazineStripCount",
        3091: "RemoveStripID",
        3092: "RemoveStripLot",
        3093: "RemoveStripBinCodeMap",
        3094: "SeparateStripID",
        3095: "SeparateStripLot",
        3096: "NewOperatorID",
        3097: "LoadOkTubeID",
        3098: "OffloadOkTubeID",
        3099: "OffloadOkTubeTransferMap",
        3100: "OffloadOkTubeLot",
        3101: "LoadTrayID",
        3102: "<free>",
        3103: "ValidateMagazineID",
        3104: "ValidateMagazineLot",
        3105: "ValidateStripID",
        3106: "ValidateStripLot",
        3107: "ValidateOffloadMagazineID",
        3108: "ValidateOffloadMagazineLot",
        3109: "ValidateTrayID",
        3110: "ValidateTrayLot",
        3111: "<free>",
        3112: "<free>",
        3113: "ValidateOkTubeID",
        3114: "ValidateOkTubeLot",
        3115: "LaserMarkedStripID",
        3116: "LaserMarkedStripLot",
    }

    return vid_code


class HandlerEventFclx:

    def __init__(self, equipment: 'Equipment'):
        self.equipment = equipment

    def handle_s6f11(self, handler: 'Equipment', message: HsmsPacket):

        # logger.info("FCLX Handling s6f11")
        decode = handler.secs_decode(message)
        ceid = decode.CEID

        ceid_code = fclx_ceid()
        ceid_message = ceid_code.get(ceid, f"Unknown code: {ceid}")

        logger.info("FCLX Handle s6f11 CEID: %s Message: %s",
                    ceid.get(), ceid_message)

        # Publish control state to MQTT
        if ceid.get() in [7, 8, 9, 10]:
            handler.mqtt_client.client.publish(
                f"equipments/status/control_state/{handler.equipment_name}", payload=ceid_message, qos=1, retain=True)

        if decode.RPT:
            for rpt in decode.RPT:
                if rpt:
                    logger.info("RPT: %s", rpt.get())
                    rptid = rpt.RPTID
                    values = rpt.V
                    lot_id, ppname = values
                    if rptid.get() == 2000:  # collection scan lot
                        logger.info("Scan lot %s, %s", lot_id.get(),
                                    self.equipment.equipment_name)
                        # handler.send_remote_command(addlot_fclx(lot_id.get()))
                        handler.send_and_waitfor_response(
                            handler.stream_function(2, 49)(addlot_fclx(lot_id.get())))
                    elif rptid.get() == 2001:  # collection open lot
                        logger.info("Open lot %s, %s", lot_id.get(),
                                    self.equipment.equipment_name)
                    elif rptid.get() == 2002:  # collection closed lot
                        logger.info("Closed lot %s, %s", lot_id.get(),
                                    self.equipment.equipment_name)
                else:
                    logger.info("No RPT")
