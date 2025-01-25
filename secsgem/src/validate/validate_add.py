import ipaddress
from typing import Dict, Union


def validateAddEquipment(arg: str) -> Dict[str, Union[str, int, bool]]:
    """Validates equipment parameters and returns normalized values.

    Args:
        arg (str): Space-separated string with equipment parameters:
            equipment_name equipment_model address port session_id active enable

    Returns:
        Dict containing validated parameters or error message
    """
    if not isinstance(arg, str):
        return {"error": "Invalid argument type."}

    arg_parts = arg.split()

    if len(arg_parts) != 7:
        return {"error": "Invalid number of arguments."}

    equipment_name, equipment_model, address, port, session_id, active, enable = arg_parts

    # Validate non-empty strings
    if not equipment_name or not equipment_model:
        return {"error": "Equipment name and model cannot be empty"}

    # Validate IP address
    try:
        ipaddress.ip_address(address)
    except ValueError:
        return {"error": "Invalid IP address"}

    # Validate port and session_id
    try:
        port = int(port)
        session_id = int(session_id)

        if not (1 <= port <= 65535):
            return {"error": "Port must be between 1-65535"}

        if session_id < 1:
            return {"error": "Session ID must be positive"}

    except ValueError:
        return {"error": "Invalid port or session ID"}

    # Convert active/enable to bool
    active = active.lower() in ['true', '1', 't', 'y', 'yes']
    enable = enable.lower() in ['true', '1', 't', 'y', 'yes']

    return {
        "equipment_name": equipment_name,
        "equipment_model": equipment_model,
        "address": address,
        "port": port,
        "session_id": session_id,
        "active": active,
        "enable": enable
    }

    # return [equipment_name, equipment_model, address, port, session_id, active, enable]
