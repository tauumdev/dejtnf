CEIDS_CONTROL_STATE = {
    "FCL": {8: "Off-Line", 9: "On-Line/Local", 10: "On-Line/Remote"},
    "FCLX": {9: "Off-Line", 7: "On-Line/Local", 8: "On-Line/Remote"},
    "STI": {3: "Off-Line", 4: "On-Line/Local", 5: "On-Line/Remote"}
}

vid = 3
model = "FCLXx"

state = CEIDS_CONTROL_STATE.get(model, {}).get(vid)
if state:
    print(state)
else:
    print("Unknown state")
