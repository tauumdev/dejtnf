import logging
import threading
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.functionbase import SecsStreamFunction
from secsgem.hsms.packets import HsmsPacket
from secsgem.secs.dataitems import DATAID, RCMD, CPNAME, CPVAL, HCACK, CPACK, OBJSPEC, ACKC7


from src.gemhost.events.events_receive import HandlerEventsReceive
from src.gemhost.alarm.alarm_receive import HandlerAlarmsReceive
from src.gemhost.control.secs_control import SecsControl
from src.utils.logger.gem_logger import CommunicationLogFileHandler

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.mqtt.mqtt_client import MqttClient

logger = logging.getLogger("app_logger")


class Equipment(secsgem.gem.GemHostHandler):
    """
    Class for handling equipment
    """

    def __init__(self, equipment_name, equipment_model, address, port, session_id, active, enable, mqtt_client_instant: 'MqttClient', custom_connection_handler=None):
        super().__init__(address, port, active, session_id,
                         equipment_name, custom_connection_handler)
        self.mqtt_client = mqtt_client_instant
        self.equipment_name = equipment_name
        self.equipment_model = equipment_model
        self.is_enabled = enable
        self.lot_active = None
        self.process_state = None
        self.process_program = None
        self.custom_stream_function = self.CustomStreamFunction
        self.secsStreamsFunctions[2].update(
            {49: self.custom_stream_function.SecsS02F49, 50: self.custom_stream_function.SecsS02F50})

        self.register_callbacks = self.CommunicationCallbacks(self)
        self.register_stream_function(1, 14, self.register_callbacks.s01f14)
        self.register_stream_function(9, 1, self.register_callbacks.s09f1)
        self.register_stream_function(9, 3, self.register_callbacks.s09f3)
        self.register_stream_function(9, 5, self.register_callbacks.s09f5)
        self.register_stream_function(9, 7, self.register_callbacks.s09f7)
        self.register_stream_function(9, 9, self.register_callbacks.s09f9)
        self.register_stream_function(9, 11, self.register_callbacks.s09f11)

        self.handle_event = HandlerEventsReceive(self)
        self.register_stream_function(6, 11, self.handle_event.events_receive)

        self.handle_alarm = HandlerAlarmsReceive(self)
        self.register_stream_function(5, 1, self.handle_alarm.s05f01)

        self.secs_control = SecsControl(self)
        self._control_state = self.secs_control.get_control_state()

        self.register_stream_function(
            7, 1, self.secs_control.recipe_management.receive_load_query)
        self.register_stream_function(
            7, 3, self.secs_control.recipe_management.recipe_upload)

    @property
    def mdln(self):
        """ Get equipment model """
        return self.secs_control.get_mdln()

    @property
    def is_online(self):
        """ Get equipment is online """
        return self.equipment_is_online()

    # @property
    # def control_state(self):
    #     """ Get control state """
    #     return self.secs_control.get_control_state()

    @property
    def control_state(self):
        """ Get control state """
        return self._control_state

    @control_state.setter
    def control_state(self, value):
        if not isinstance(value, str):
            logger.warning("control_state must be a string value.")
        else:
            self._control_state = value

    @property
    def ppid(self):
        """ Get ppid """
        return self.secs_control.get_ppid()

    def delayed_task(self):
        """
        Delayed task for subscribe lot
        """
        wait_seconds = 0.05
        logger.info("Task started, waiting for %s seconds...", wait_seconds)
        threading.Event().wait(wait_seconds)  # Non-blocking wait
        logger.info("%s seconds have passed!\n", wait_seconds)

        self.secs_control.get_control_state()
        self.secs_control.get_process_state()

        self.mqtt_client.client.publish(
            f"equipments/status/control_state/{self.equipment_name}", self.control_state, qos=1, retain=True
        )

        self.mqtt_client.client.publish(
            f"equipments/status/process_program/{self.equipment_name}", self.ppid, qos=1, retain=True
        )

        self.mqtt_client.client.publish(
            f"equipments/status/process_state/{self.equipment_name}", self.process_state, qos=1, retain=True)

        self.secs_control.unsubscribe_all_events()
        self.secs_control.subscribe_lot_control()

    def _on_state_communicating(self, _):

        super()._on_state_communicating(_)
        current_state = self.communicationState.current
        logger.info("%s On communication state: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)

        # Start the thread
        thread = threading.Thread(target=self.delayed_task)
        thread.start()

    def on_connection_closed(self, connection):
        super().on_connection_closed(connection)

        current_state = self.communicationState.current
        logger.info("%s On connection close: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)

    def _on_state_disconnect(self):
        super()._on_state_disconnect()

        current_state = "NOT_COMMUNICATING"
        logger.info("%s On state disconnect: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)

    def _on_hsms_packet_received(self, packet):
        decode = self.secs_decode(packet)
        self.mqtt_client.client.publish(
            f"equipments/status/secs_message/{self.equipment_name}", str(decode))
        return super()._on_hsms_packet_received(packet)

    def equipment_is_online(self):
        """
        equipment is online
        """
        # offline_state = ['Off-line', 'Off-Line/Equipment Off-Line', 'Off-Line/Attempt On-Line',
        #                  'Off-Line/Host Off-Line']  # ,'On-Line/Local','On-Line/Remote'

        online_state = ['On-Line', 'On-Line/Local', 'On-Line/Remote']
        if not self.is_enabled:  # Check if equipment is enabled
            return False
        if self.communicationState.current != "COMMUNICATING":  # Check if equipment is communicating
            return False
        if self.control_state not in online_state:
            return False
        return True

    commLogFileHandler = CommunicationLogFileHandler("logs/gem")
    commLogFileHandler.setFormatter(
        logging.Formatter('%(asctime)s: %(message)s'))
    logging.getLogger("hsms_communication").addHandler(commLogFileHandler)
    logging.getLogger("hsms_communication").propagate = False

    # Configure basic logging format and level
    logging.basicConfig(
        format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.INFO)

    class CustomStreamFunction:
        """
        Class for custom stream functions
        """
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

    class CommunicationCallbacks:
        """
        Class for handling communication callbacks
        """

        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment

        def s01f14(self, handle, packet):
            """
            Handle S01F14
            """
            logger.info("<<-- S01F14")
            # print("<<-- S01F14")

        def s09f1(self, handle, packet):
            logger.warning("s09f1:Unrecognized Device ID (UDN): %s",
                           self.equipment.equipment_name)

        def s09f3(self, handle, packet):
            logger.warning("s09f3:Unrecognized Stream Function (SFCD): %s",
                           self.equipment.equipment_name)

        def s09f5(self, handle, packet):
            logger.warning("s09f5:Unrecognized Function Type (UFN): %s",
                           self.equipment.equipment_name)

        def s09f7(self, handle, packet):
            logger.warning("s09f7:Illegal Data (IDN): %s",
                           self.equipment.equipment_name)

        def s09f9(self, handle, packet):
            logger.warning("s09f9:Transaction Timer Timeout (TTN): %s",
                           self.equipment.equipment_name)

        def s09f11(self, handle, packet):
            logger.warning("s09f11:Data Too Long (DLN): %s",
                           self.equipment.equipment_name)
