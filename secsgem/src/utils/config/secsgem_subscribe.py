# Description: Configuration file for SECS/GEM subscribe events

"""
Description: Configuration file for FCL & FCLX equipment models  
"""

VID_CONTROL_STATE = {"FCL": 28, "FCLX": 4}
VID_MODEL = {"FCL": 32, "FCLX": 24}
VID_PP_NAME = {"FCL": 33, "FCLX": 7}

SUBSCRIBE_LOT_CONTROL_FCL = [
    # subscribe request validate lot
    {"ceid": 20, "dvs": [81, 33], "report_id": 1000},
    # subscribe lot open
    {"ceid": 21, "dvs": [82, 33], "report_id": 1001},
    # subscribe lot close
    {"ceid": 22, "dvs": [83, 33], "report_id": 1002},
    # subscribe recipe init
    # {"ceid": 1, "dvs": [33], "report_id": 1003}
]

SUBSCRIBE_LOT_CONTROL_FCLX = [
    # subscribe request validate lot
    {"ceid": 58, "dvs": [3081, 7], "report_id": 1000},
    # subscribe lot open
    {"ceid": 40, "dvs": [3026, 7], "report_id": 1001},
    # subscribe lot close
    {"ceid": 41, "dvs": [3027, 7], "report_id": 1002},
    # subscribe recipe init
    # {"ceid": 10, "dvs": [7], "report_id": 1003}
]
