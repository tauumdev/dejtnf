from secsgem.secs.functionbase import SecsStreamFunction
from secsgem.secs.dataitems import MDLN, SVID, SV, SVNAME, UNITS, COMMACK, OFLACK, ONLACK, ECID, ECV, EAC, TIME, ECNAME, ECMIN, \
    ECMAX, ECDEF, DATAID, RPTID, VID, DRACK, CEID, LRACK, CEED, ERACK, RCMD, CPNAME, CPVAL, HCACK, CPACK, ALCD, ALID, \
    ALTX, ACKC5, ALED, TIMESTAMP, EXID, EXTYPE, EXMESSAGE, EXRECVRA, ACKA, ERRCODE, ERRTEXT, DATALENGTH, GRANT6, DSID, \
    DVNAME, DVVAL, V, ACKC6, PPID, LENGTH, PPGNT, PPBODY, ACKC7, MHEAD, SHEAD, MEXP, EDID, TID, TEXT, ACKC10, MID, \
    IDTYP, FNLOC, FFROT, ORLOC, RPSEL, REFP, DUTMS, XDIES, YDIES, ROWCT, COLCT, NULBC, PRDCT, PRAXI, SDACK, MAPFT, \
    BCEQU, MLCL, GRNT1, RSINF, BINLT, MDACK, STRP, XYPOS, SDBIN, MAPER, DATLC, OBJSPEC, OBJTYPE, OBJID, ATTRID, \
    ATTRDATA, ATTRRELN, OBJACK


class SecsS02F49(SecsStreamFunction):
    """
    host command - send.

    **Data Items**
    - :class:`DATAID <secsgem.secs.dataitems.DATAID>`
    - :class:`OBJSPEC <secsgem.secs.dataitems.OBJSPEC>`
    - :class:`RCMD <secsgem.secs.dataitems.RCMD>`
    - :class:`CPNAME <secsgem.secs.dataitems.CPNAME>`
    - :class:`CPVAL <secsgem.secs.dataitems.CPVAL>`

    **Structure**::

        >>> import secsgem
        >>> secsgem.SecsS02F49
        {
            DATAID: U4
            OBJSPEC: A
            RCMD: U1/I1/A
            PARAMS: [
                {
                    CPNAME: U1/U2/U4/U8/I1/I2/I4/I8/A
                    CPVAL: BOOLEAN/U1/U2/U4/U8/I1/I2/I4/I8/A/B
                }
                ...
            ]
        }

    **Example**::

        >>> import secsgem
        >>> secsgem.SecsS02F49({DATAID": 123,OBJSPEC": "OBJ","RCMD": "ADD_LOT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": "lot001"}]})
        S2F49 W
          <L [2]
            <U 123>
            <A "OBJ">
            <A "ADD_LOT">
            <L [2]
              <L [2]
                <A "LotID">
                <A "lot001">
              >
            >
          > .

    :param value: parameters for this function (see example)
    :type value: list
    """

    _stream = 2
    _function = 49

    _dataFormat = [
        DATAID,
        OBJSPEC,
        RCMD,
        [
            [
                "PARAMS",   # name of the list
                CPNAME,
                CPVAL
            ]
        ]
    ]

    _toHost = False
    _toEquipment = True

    _hasReply = True
    _isReplyRequired = True

    _isMultiBlock = False


class SecsS02F50(SecsStreamFunction):
    """
    host command - acknowledge.

    **Data Items**

    - :class:`HCACK <secsgem.secs.dataitems.HCACK>`
    - :class:`CPNAME <secsgem.secs.dataitems.CPNAME>`
    - :class:`CPACK <secsgem.secs.dataitems.CPACK>`

    **Structure**::

        >>> import secsgem
        >>> secsgem.SecsS02F50
        {
            HCACK: B[1]
            PARAMS: [
                {
                    CPNAME: U1/U2/U4/U8/I1/I2/I4/I8/A
                    CPACK: B[1]
                }
                ...
            ]
        }

    **Example**::

        >>> import secsgem
        >>> secsgem.SecsS02F50({ \
            "HCACK": secsgem.HCACK.INVALID_COMMAND, \
            "PARAMS": [ \
                {"CPNAME": "PARAM1", "CPACK": secsgem.CPACK.CPVAL_ILLEGAL_VALUE}, \
                {"CPNAME": "PARAM2", "CPACK": secsgem.CPACK.CPVAL_ILLEGAL_FORMAT}]})
        S2F50
          <L [2]
            <B 0x1>
            <L [2]
              <L [2]
                <A "PARAM1">
                <B 0x2>
              >
              <L [2]
                <A "PARAM2">
                <B 0x3>
              >
            >
          > .

    :param value: parameters for this function (see example)
    :type value: list
    """

    _stream = 2
    _function = 50

    _dataFormat = [
        HCACK,
        [
            [
                "PARAMS",   # name of the list
                CPNAME,
                CPACK
            ]
        ]
    ]

    _toHost = True
    _toEquipment = False

    _hasReply = False
    _isReplyRequired = False

    _isMultiBlock = False
