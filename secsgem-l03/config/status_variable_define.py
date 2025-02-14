# Description: Configuration file for SECS/GEM subscribe events

"""
Description: Configuration file for FCL & FCLX equipment models  
"""

VID_CONTROL_STATE = {"FCL": 28, "FCLX": 21, "STI": 28}
VID_MODEL = {"FCL": 32, "FCLX": 24, "STI": 32}
VID_PP_NAME = {"FCL": 33, "FCLX": 7, "STI": 33}

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
        # subscribe request validate lot
        {"CEID": 20, "DVS": [81, 33], "REPORT_ID": 1000},
        # subscribe lot open
        {"CEID": 21, "DVS": [82, 33], "REPORT_ID": 1001},
        # subscribe lot close
        {"CEID": 22, "DVS": [83, 33], "REPORT_ID": 1002},
        # subscribe process program change
        {"CEID": 1, "DVS": [33], "REPORT_ID": 1003},
        # subscribe process state change
        {"CEID": 2000, "DVS": [38], "REPORT_ID": 1004}
    ],
    "FCLX": [
        # subscribe request validate lot
        {"CEID": 58, "DVS": [3081, 7], "REPORT_ID": 1000},
        # subscribe lot open
        {"CEID": 40, "DVS": [3026, 7], "REPORT_ID": 1001},
        # subscribe lot close
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
