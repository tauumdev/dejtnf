# Description: Configuration file for SECS/GEM subscribe events

"""
Description: Configuration file for FCL & FCLX equipment models
"""

VID_CONTROL_STATE = {"FCL": 28, "FCLX": 21, "STI": 28}
VID_MODEL = {"FCL": 32, "FCLX": 24, "STI": 32}
VID_PP_NAME = {"FCL": 33, "FCLX": 7, "STI": 33}
VID_ALARM_SET = {"FCL": 24, "FCLX": 2}

CONTROL_STATE_VID = {
    "FCL": {"VID": 28, "STATE": {
        1: "Off-Line/Equipment Off-Line",
        2: "Off-Line/Attempt On-Line",
        3: "Off-Line/Host Off-Line",
        4: "On-Line/Local",
        5: "On-Line/Remote"}},
    "FCLX": {"VID": 21, "STATE": {
        1: "Off-Line/Equipment Off-Line",
        2: "Off-Line/Attempt On-Line",
        3: "Off-Line/Host Off-Line",
        4: "On-Line/Local",
        5: "On-Line/Remote"}},
    "STI": {"VID": 28, "STATE": {
        1: "Off-Line/Equipment Off-Line",
        2: "Off-Line/Attempt On-Line",
        3: "Off-Line/Host Off-Line",
        4: "On-Line/Local",
        5: "On-Line/Remote"}},
}

CONTROL_STATE_EVENT = {
    "FCL": {8: "Off-Line", 9: "On-Line/Local", 10: "On-Line/Remote"},
    "FCLX": {9: "Off-Line", 7: "On-Line/Local", 8: "On-Line/Remote"},
    "STI": {3: "Off-Line", 4: "On-Line/Local", 5: "On-Line/Remote"}
}

PROCESS_STATE_CHANG_EVENT = {
    "FCL": {"CEID": 2000, "VID": 38, "STATE": [
        {0: "No State"}, {1: "Initialize"}, {2: "Not Standby"}, {3: "Standby"},
        {4: "Running Executing"}, {5: "Running Pause"}, {6: "Running Empty"},
        {7: "Specific Running"}, {10: "Error Waiting"}, {11: "Error Assisting"}
    ]},
    "FCLX": {"CEID": 2, "VID": 8, "STATE": [
        {0: "Idle"}, {1: "Starting"}, {2: "Running"}, {3: "Stopping"},
        {4: "Pausing"}, {5: "Alarm Paused"}, {6: "Engineering"}
    ]},
    "STI": {"CEID": 11, "VID": 39, "STATE": [
        {0: "Idle"}, {1: "Setting up/Initializing"}, {2: "Ready/Initialized"},
        {3: "Run"}, {4: "Stop"}, {5: "Abort"}, {6: "E-Stop"}, {7: "Alarm/Jam"}
    ]},
}

PP_CHANGE_EVENT = {
    "FCL": {"CEID": 1, "VID": 33},
    "FCLX": {"CEID": 56, "VID": 7},
    "STI": {"CEID": 201, "VID": 33},
}

SUBSCRIBE_LOT_CONTROL = {
    "FCL": [
        # subscribe request validate lot 81 lot id, 33 ppid
        {"CEID": 20, "DVS": [81, 33], "REPORT_ID": 1000},
        # subscribe lot open 82 lot id, 33 ppid
        {"CEID": 21, "DVS": [82, 33], "REPORT_ID": 1001},
        # subscribe lot close 83 lot id, 33 ppid
        {"CEID": 22, "DVS": [83, 33], "REPORT_ID": 1002},
        # subscribe process program change 33 ppid
        {"CEID": 1, "DVS": [33], "REPORT_ID": 1003},
        # subscribe process state change 38 process state
        {"CEID": 2000, "DVS": [38], "REPORT_ID": 1004}
    ],
    "FCLX": [
        # subscribe request validate lot 3081 lot id, 7 ppid 2001 PlannedLots 2023 ActiveLots
        {"CEID": 58, "DVS": [3081, 7, 2001, 2023], "REPORT_ID": 1000},
        # subscribe lot open 3082 lot id, 7 ppid
        {"CEID": 40, "DVS": [3026, 7], "REPORT_ID": 1001},
        # subscribe lot close 3083 lot id, 7 ppid
        {"CEID": 41, "DVS": [3027, 7], "REPORT_ID": 1002},
        # subscribe process program change
        {"CEID": 56, "DVS": [7], "REPORT_ID": 1003},
        # subscribe process state change
        {"CEID": 2, "DVS": [8], "REPORT_ID": 1004}
    ],
}

PROCESS_STATE_NAME = {
    "FCL":
        {0: "No State", 1: "Initialize", 2: "Not Standby", 3: "Standby",
         4: "Running Executing", 5: "Running Pause", 6: "Running Empty",
         7: "Specific Running", 10: "Error Waiting", 11: "Error Assisting"},
    "FCLX":
        {0: "Idle", 1: "Starting", 2: "Running", 3: "Stopping",
         4: "Pausing", 5: "Alarm Paused", 6: "Engineering"},
    "STI":
        {0: "Idle", 1: "Setting up/Initializing", 2: "Ready/Initialized",
         3: "Run", 4: "Stop", 5: "Abort", 6: "E-Stop", 7: "Alarm/Jam"}
}

CONTROL_STATE_NAME = {
    "FCL": {
        1: "Off-Line/Equipment Off-Line",
        2: "Off-Line/Attempt On-Line",
        3: "Off-Line/Host Off-Line",
        4: "On-Line/Local",
        5: "On-Line/Remote"},
    "FCLX":  {
        1: "Off-Line/Equipment Off-Line",
        2: "Off-Line/Attempt On-Line",
        3: "Off-Line/Host Off-Line",
        4: "On-Line/Local",
        5: "On-Line/Remote"},
    "STI": {
        1: "Off-Line/Equipment Off-Line",
        2: "Off-Line/Attempt On-Line",
        3: "Off-Line/Host Off-Line",
        4: "On-Line/Local",
        5: "On-Line/Remote"},
}

FCLX_CEID = {
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
    64: "UserChanged"
}
FCLX_EC = [
    {12: "TimeFormat", "type": "UINT1"},
    {13: "EstablishCommunicationsTimeout", "type": "UINT2"},
    {14: "PollDelay", "type": "UINT2"},
    {15: "MaxSpoolTransmit", "type": "UINT4"},
    {16: "OverWriteSpool", "type": "Boolean"},
    {1000: "DefaultOnlineControlState", "type": "UINT1"},
    {1001: "MaximumStripRejects", "type": "UINT1"},
    {1002: "LotControlMode", "type": "UINT1"},
    {1003: "DefaultControlState", "type": "UINT1"},
    {1004: "DefaultOfflineControlState", "type": "UINT1"},
    {1005: "AllowAutoReject", "type": "Boolean"},
    {1006: "ValidateMagazine", "type": "Boolean"},
    {1007: "ValidateStrip", "type": "Boolean"},
    {1008: "ValidateTray", "type": "Boolean"},
    {1009: "<free>", "type": "UINT1"},
    {1010: "ValidateLot", "type": "Boolean"},
    {1011: "ValidateOffloadMagazine", "type": "Boolean"},
    {1012: "ValidateOkTube", "type": "Boolean"},
    {1014: "LimitsMonitoringInterval", "type": "UINT2"}
]
FCLX_SVID = [
    {1: "AlarmsEnabled", "type": "List"},
    {2: "AlarmsSet", "type": "List"},
    {3: "PPError", "type": "ASCII"},
    {4: "PPFormat", "type": "UINT1"},
    {7: "PPExecName", "type": "ASCII"},
    {8: "ProcessState", "type": "UINT1"},
    {9: "PreviousProcessState", "type": "UINT1"},
    {10: "LastChangedEquipmentConstant", "type": "UINT4"},
    {11: "Clock", "type": "ASCII"},
    {17: "SpoolCountActual", "type": "UINT4"},
    {18: "SpoolCountTotal", "type": "UINT4"},
    {19: "SpoolFullTime", "type": "ASCII"},
    {20: "SpoolStartTime", "type": "ASCII"},
    {21: "ControlState", "type": "UINT1"},
    {22: "EventsEnabled", "type": "List"},
    {2001: "PlannedLots", "type": "List"},
    {2022: "NumberOfActiveLots", "type": "UINT4"},
    {2023: "ActiveLots", "type": "List"},
    {2024: "LockEnabled", "type": "Boolean"},
    {2025: "ProductionCounter", "type": "UINT4"},
    {2026: "TotalCounter", "type": "UINT8"},
    {2027: "ActiveSections", "type": "ASCII"},
    {2028: "RunEmptyMode", "type": "UINT4"},
]
FCLX_DVID = [
    {5: "PPChangeName", "type": "ASCII"},
    {6: "PPChangeStatus", "type": "UINT1"},
    {3026: "OpenedLotID", "type": "ASCII"},
    {3027: "ClosedLotID", "type": "ASCII"},
    {3028: "ClosedLotReason", "type": "ASCII"},
    {3029: "AddedLotID", "type": "ASCII"},
    {3030: "RemovedLotID", "type": "ASCII"},
    {3031: "EditedLotID", "type": "ASCII"},
    {3075: "ClearedLotID", "type": "ASCII"},
    {3076: "SelectedPPName", "type": "ASCII"},
    {3032: "UPH_Report", "type": "UINT4"},
    {3033: "MTBA_Report", "type": "ASCII"},
    {3034: "MTBF_Report", "type": "ASCII"}

]

FCL_VID = {
    21: "ABORTLEVEL",
    23: "ALARMSENABLED",
    24: "ALARMSSET",
    25: "ALARMSTATE",
    26: "ALARMSERIAL",
    27: "CLOCK",
    28: "CONTROLSTATE",
    29: "DATAID",
    30: "EVENTSENABLED",
    31: "LINKSTATE",
    32: "MDLN",
    33: "PPEXECNAME",
    34: "PREVIOUSCEID",
    35: "PREVIOUSCOMMAND",
    36: "PREVIOUSCONTROLSTATE",
    37: "PREVIOUSPROCESSSTATE",
    38: "PROCESSSTATE",
    39: "SOFTREV",
    40: "TIME",
    49: "SPOOLCOUNTACTUAL",
    50: "SPOOLCOUNTTOTAL",
    51: "SPOOLFULLTIME",
    52: "SPOOLLOADSUBSTATE",
    53: "SPOOLSTARTTIME",
    54: "SPOOLSTATE",
    55: "SPOOLUNLOADSUBSTATE",
    100: "REMOTE_CMD_STATE",
    200: "LOT_STATE",
    300: "FRAMES_MARKED_CNT",
    20000: "UNITSTATE",
    20001: "PREVIOUSUNITSTATE",
    20002: "UNITID"
}
FCL_CEID = {
    20: "LotValidate",
    21: "LotOpened",
    22: "LotClosed",
    23: "MagazineLoaderValidate",
    24: "MagazineOffloaderValidate",
    25: "StripPress1Validate",
    26: "StripPress2Validate",
    27: "StripPress3Validate",
    28: "StripSeparatorValidate",
    29: "StripsToGoValidate",
    30: "StripLaserValidate",
    61: "StripPress1Processed",
    63: "StripPress2Processed",
    65: "StripPress3Processed",
    67: "StripSeparatorProcessed",
    68: "StripLaserMarked",
    69: "StripLaserInspected",
    70: "StripLaserProcessed",
    71: "StripLaserUploadMarkingData"
}
