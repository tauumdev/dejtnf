# Description: Configuration file for SECS/GEM subscribe events

"""
Description: Configuration file for FCL & FCLX equipment models  
"""

SUBSCRIBE_LOT_CONTROL_FCL = [
    {"ceid": 20, "dvs": [81, 33], "report_id": 1000},
    {"ceid": 21, "dvs": [82, 33], "report_id": 1001},
    {"ceid": 22, "dvs": [83, 33], "report_id": 1002},
]

SUBSCRIBE_LOT_CONTROL_FCLX = [
    {"ceid": 58, "dvs": [3081, 7], "report_id": 1000},
    {"ceid": 40, "dvs": [3026, 7], "report_id": 1001},
    {"ceid": 41, "dvs": [3027, 7], "report_id": 1002},
]
