import secsgem
import secsgem.gem
import secsgem.secs


class GemCommands:
    """
    Class to handle common GEM commands.
    """

    @staticmethod
    def send_equipment_status_request(host, svids=None):
        """
        Send an S1F3 (Equipment Status Request) command to the equipment.
        """
        try:
            print(f"Sending S1F3 (Equipment Status Request) to {host.machine_name}.")
            # response = host.stream_function(1, 3)([svids])  # S1F3
            response = host.settings.streams_functions.decode(
                host.send_and_waitfor_response(host.stream_function(1, 3)(svids)),
            ).get()

            return {"status": "success", "data": response}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def send_equipment_constant_request(host, cids=None):
        """
        Send an S2F13 (Equipment Constant Request) command to the equipment.
        """
        try:
            print(f"Sending S2F13 (Equipment Constant Request) to {host.machine_name}.")
            # Send the S2F13 command
            response = host.settings.streams_functions.decode(
                host.send_and_waitfor_response(host.stream_function(2, 13)(cids)),
            ).get()

            return {"status": "success", "data": response}
        except Exception as e:
            return {"status": "error", "message": str(e)}
