
def fcl_accept_lot_cmd(lot_id: str):
    """
    Accept lot.
    :param lot_id: lot id to accept
    :type lot_id: str
    use on s2f41
    """

    return {"RCMD": "LOT_ACCEPT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}]}


def fcl_reject_lot_cmd(lot_id: str):
    """
    Reject lot.
    :param lot_id: lot id to reject
    :type lot_id: str
    use on s2f41
    """

    return {"RCMD": "LOT_REJECT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}]}


def pp_select(ppid: str):
    """
    Select process program.
    :param ppid: process program id to select
    :type ppid: str
    use on s2f41
    """

    return {"RCMD": "PP-SELECT", "PARAMS": [{"CPNAME": "PPID", "CPVAL": ppid}]}


def fclx_add_lot(lot_id: str):
    """
    Add lot.
    :param lot_id: lot id to add
    :type lot_id: str
    use on s2f49
    """

    return {"DATAID": 100, "OBJSPEC": "LOTCONTROL", "RCMD": "ADD_LOT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}]}


def fclx_reject_lot(lot_id: str, reason: str):
    """
    Reject lot.
    :param lot_id: lot id to reject
    :reason: reason to reject
    :type lot_id: str
    use on s2f49
    """

    return {"DATAID": 101, "OBJSPEC": "LOTCONTROL", "RCMD": "REJECT_LOT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}, {"CPNAME": "LotID", "CPVAL": reason}]}
