import cmd
import ipaddress
import json
import logging
import os

# import src.gem.recipe_manager as recipe
from src.gem.equipment_manager import EquipmentManager
from src.cli.control_cli import Control
from src.cli.config_cli import Config


logger = logging.getLogger("app_logger")


# class Config(cmd.Cmd):
#     def __init__(self, eq_manager: EquipmentManager):
#         super().__init__()
#         self.eq_manager = eq_manager
#         self.prompt = "config > "

#     def emptyline(self):
#         """
#         Do nothing on empty input line.
#         """
#         pass

#     def do_exit(self, arg: str):
#         """
#         Exit configuration mode.
#         Usage: exit
#         """
#         return True

#     def do_list(self, arg: str):
#         """
#         List all equipment instances.
#         Usage: list
#         Sample: list
#         """
#         print("Listing equipments")
#         try:
#             equipments = self.eq_manager.list_equipments()
#             if not isinstance(equipments, list):
#                 print(equipments)
#                 return
#             print(json.dumps(equipments, indent=4))
#         except Exception as e:
#             print(e)

#     def do_add(self, arg: str):
#         """
#         Add a new equipment instance.
#         Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>
#         Args:
#             equipment_name (str): The name of the equipment.
#             equipment_model (str): The model of the equipment.
#             address (str): The IP address of the equipment.
#             port (int): The port of the equipment.
#             session_id (int): The session ID of the equipment.
#             active (bool): Whether the equipment is active.
#             enable (bool): Whether the equipment is enabled.
#         Sample: add TNF-01 192.168.0.1 5000 1 True True
#         """
#         print("Adding equipment")
#         args = arg.split()
#         if len(args) != 7:
#             print("Invalid number of arguments")
#             print(
#                 "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>")
#             return
#         try:

#             equipment_name, equipment_model, address, port, session_id, active, enable = args

#             try:
#                 ipaddress.ip_address(address)
#             except ValueError:
#                 print("Invalid IP address")
#                 return

#             active = active.lower() in ['true', '1', 't', 'y', 'yes']
#             enable = enable.lower() in ['true', '1', 't', 'y', 'yes']
#             rsp = self.eq_manager.add_equipment(equipment_name, equipment_model, address, int(
#                 port), int(session_id), active, enable)

#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Equipment added successfully.", equipment_name)

#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_remove(self, arg: str):
#         """
#         Remove an equipment instance.
#         Usage: remove <equipment_name>
#         Sample: remove TNF-01
#         """
#         print("Removing equipment")
#         args = arg.split()
#         if len(args) != 1:
#             print("Invalid number of arguments")
#             print("Usage: remove <equipment_name>")
#             return

#         try:
#             equipment_name = args[0]
#             rsp = self.eq_manager.remove_equipment(equipment_name)

#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Equipment removed successfully.", equipment_name)
#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_edit(self, arg: str):
#         """
#         Edit and update an equipment instance.
#         Usage: edit <equipment_name> <key1=value1> <key2=value2> ...
#         Args:
#             equipment_name (str): The name of the equipment.
#             equipment_model (str): The model of the equipment.
#             address (str): The IP address of the equipment.
#             port (int): The port of the equipment.
#             session_id (int): The session ID of the equipment.
#             active (bool): Whether the equipment is active.
#             enable (bool): Whether the equipment is enabled.
#         Sample: edit TNF-01 address=192.168.0.1 port=5000
#         """
#         print("Editing equipment")

#         args = arg.split()
#         if len(args) < 2:
#             print("Invalid number of arguments")
#             print(
#                 "Usage: edit <equipment_name> <key1=value1> <key2=value2> ...")
#             return

#         try:
#             equipment_name = args[0]
#             kwargs = {}
#             for arg in args[1:]:
#                 key, value = arg.split('=')
#                 kwargs[key] = value

#             rsp = self.eq_manager.edit_equipment(equipment_name, **kwargs)

#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Equipment edited successfully.", equipment_name)

#         except ValueError:
#             logger.error("Invalid argument type")
#             return


# class Control(cmd.Cmd):
#     def __init__(self, eq_manager: EquipmentManager):
#         super().__init__()
#         self.eq_manager = eq_manager
#         self.prompt = "control > "

#     # communication
#     def emptyline(self):
#         """
#         Do nothing on empty input line.
#         """
#         pass

#     def do_exit(self, arg: str):
#         """
#         Exit control mode.
#         Usage: exit
#         """
#         return True

#     def do_enable(self, arg: str):
#         """
#         Enable an equipment instance.
#         Usage: enable <equipment_name>
#         Sample: enable TNF-01
#         """
#         print("Enabling equipment")

#         args = arg.split()
#         if len(args) != 1:
#             print("Invalid number of arguments")
#             print("Usage: enable <equipment_name>")
#             return
#         try:
#             equipment_name = args[0]
#             rsp = self.eq_manager.enable_equipment(equipment_name)

#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Equipment enabled successfully.", equipment_name)
#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_disable(self, arg: str):
#         """
#         Disable an equipment instance.
#         Usage: disable <equipment_name>
#         Sample: disable TNF-01
#         """
#         print("Disabling equipment")
#         args = arg.split()
#         if len(args) != 1:
#             print("Invalid number of arguments")
#             print("Usage: disable <equipment_name>")
#             return
#         try:
#             equipment_name = args[0]
#             rsp = self.eq_manager.disable_equipment(equipment_name)

#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Equipment disabled successfully.", equipment_name)
#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_online(self, arg: str):
#         """
#         Online an equipment instance.
#         Usage: online <equipment_name>
#         Sample: online TNF-01
#         """
#         print("Online equipment")
#         args = arg.split()
#         if len(args) != 1:
#             print("Invalid number of arguments")
#             print("Usage: online <equipment_name>")
#             return
#         try:
#             equipment_name = args[0]
#             rsp = self.eq_manager.online_equipment(equipment_name)

#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Equipment online successfully.", equipment_name)
#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_offline(self, arg: str):
#         """
#         Offline an equipment instance.
#         Usage: offline <equipment_name>
#         Sample: offline TNF-01
#         """
#         print("Offline equipment")
#         args = arg.split()
#         if len(args) != 1:
#             print("Invalid number of arguments")
#             print("Usage: offline <equipment_name>")
#             return
#         try:
#             equipment_name = args[0]
#             rsp = self.eq_manager.offline_equipment(equipment_name)

#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Equipment offline successfully.", equipment_name)
#         except ValueError:
#             print("Invalid argument type")
#             return

#     # event

#     def do_disable_ceids(self, arg: str):
#         """
#         Disable all collection events of an equipment instance.
#         Usage: disable_ceids <equipment_name> <ceid1, ceid2, ...>
#         Sample: disable_ceids TNF-01 1,2,3
#         """
#         print("Disabling collection events")
#         args = arg.split()
#         if len(args) < 1:
#             print("Invalid number of arguments")
#             print("Usage: disable_ceids <equipment_name> <ceid1, ceid2, ...>")
#             return
#         try:
#             equipment_name = args[0]
#             ceid = list(map(int, args[1].strip('[]').split(','))) if len(
#                 args) > 1 else []
#             rsp = self.eq_manager.disable_ceids(equipment_name, ceid)

#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Collection events disabled successfully.", equipment_name)
#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_enable_ceids(self, arg: str):
#         """
#         Enable collection events of an equipment instance.
#         Usage: enable_ceids <equipment_name> <ceid1, ceid2, ...>
#         Sample: enable_ceids TNF-01 1,2,3
#         """
#         print("Enabling collection events")
#         args = arg.split()
#         if len(args) < 1:
#             print("Invalid number of arguments")
#             print("Usage: enable_ceids <equipment_name> <ceid1, ceid2, ...>")
#             return
#         try:
#             equipment_name = args[0]
#             ceid = list(map(int, args[1].strip('[]').split(','))) if len(
#                 args) > 1 else []
#             rsp = self.eq_manager.enable_ceids(equipment_name, ceid)

#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Collection events enabled successfully.", equipment_name)
#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_disable_ceid_report(self, arg: str):
#         """
#         Disable all Collection Event Reports.
#         Usage: disable_ceid_report <equipment_name>
#         Sample: disable_ceid_report TNF-01
#         """
#         print("Disabling collection event reports")
#         args = arg.split()
#         if len(args) != 1:
#             print("Invalid number of arguments")
#             print("Usage: disable_ceid_report <equipment_name>")
#             return
#         try:
#             equipment_name = args[0]
#             rsp = self.eq_manager.disable_ceid_report(equipment_name)

#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Collection event reports disabled successfully.", equipment_name)
#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_subscribe_collection_event(self, arg: str):
#         """
#         Subscribe to a collection event.
#         Usage: subscribe_collection_event <equipment_name> <ceid> <dvs> [<report_id>]
#         Sample: subscribe_collection_event TNF-01 20 1,2,3
#         """
#         print("Subscribing to collection event")
#         args = arg.split()
#         if len(args) < 3:
#             print("Invalid number of arguments")
#             print(
#                 "Usage: subscribe_collection_event <equipment_name> <ceid> <dvs> [<report_id>]")
#             return
#         try:
#             equipment_name = args[0]
#             ceid = int(args[1])
#             dvs = list(map(int, args[2].strip('[]').split(',')))
#             rsp = self.eq_manager.subscribe_collection_event(
#                 equipment_name, ceid, dvs, int(args[3]) if len(args) > 3 else None)
#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#             print("Subscribed to collection event successfully.", equipment_name)
#         except ValueError:
#             print("Invalid argument type")
#             return

#     # recipe management on server
#     def do_get_current_recipes(self, arg: str):
#         """
#         Get current recipes recipe store.
#         Usage: do_get_current_recipes <equipment_name> [<recipe_name>]
#         Sample: do_get_current_recipes TNF-01
#         Return:
#         - Recipe data if recipe_name is provided
#         - List of recipes if recipe_name is not provided
#         """
#         print("Getting current recipe store")
#         arg = arg.split(maxsplit=1)
#         if len(arg) < 1:
#             print("Invalid number of arguments")
#             print(
#                 "Usage: do_get_current_recipes <equipment_name> [<recipe_name>]")
#             return
#         try:
#             equipment_name = arg[0]
#             recipe_name = arg[1] if len(arg) > 1 else None
#             rec_receive = recipe.get_current_recipes(
#                 equipment_name, recipe_name)

#             if isinstance(rec_receive, list):
#                 for rec in rec_receive:
#                     print(rec)
#                 return
#             else:
#                 print(rec_receive)
#                 return
#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_get_upload_recipes(self, arg: str):
#         """
#         Get upload recipes recipe store.
#         Usage: do_get_upload_recipes <equipment_name> [<recipe_name>]
#         Sample: do_get_upload_recipes TNF-01
#         Return:
#         - Recipe data if recipe_name is provided
#         - List of recipes if recipe_name is not provided
#         """
#         print("Getting upload recipe store")
#         arg = arg.split(maxsplit=1)
#         if len(arg) < 1:
#             print("Invalid number of arguments")
#             print(
#                 "Usage: do_get_upload_recipes <equipment_name> [<recipe_name>]")
#             return
#         try:
#             equipment_name = arg[0]
#             recipe_name = arg[1] if len(arg) > 1 else None
#             rec_receive = recipe.get_upload_recipes(
#                 equipment_name, recipe_name)

#             if isinstance(rec_receive, list):
#                 for rec in rec_receive:
#                     print(rec)
#                 return
#             else:
#                 print(rec_receive)
#                 return
#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_get_recipe_version(self, arg: str):
#         """
#         Get recipe version from server.
#         Usage: get_recipe_version <equipment_name> <recipe_name>
#         Sample: get_recipe_version TNF-01 recipe1
#         """
#         print("Getting recipe version")
#         arg = arg.split(maxsplit=1)
#         if len(arg) < 1:
#             print("Invalid number of arguments")
#             print("Usage: get_recipe_version <equipment_name> <recipe_name>")
#             return
#         try:
#             equipment_name = arg[0]
#             recipe_name = arg[1] if len(arg) > 1 else None

#             _recipe = recipe.get_upload_recipes(equipment_name, recipe_name)
#             ppid = _recipe["recipe_name"]
#             ppbody = _recipe["recipe_data"]
#             print(type(ppbody))
#             rsp = recipe.get_version_receipe(ppbody)
#             print(rsp)
#         except ValueError:
#             print("Invalid argument type")
#             return

#     # recipe management from equipment
#     def do_send_recipe(self, arg: str):
#         """
#         Send recipe to equipment.
#         Usage: send_recipe <equipment_name> <recipe_name>
#         Sample: send_recipe TNF-01 recipe1
#         """
#         print("Sending recipe")
#         arg = arg.split(maxsplit=1)
#         if len(arg) != 2:
#             print("Invalid number of arguments")
#             print("Usage: send_recipe <equipment_name> <recipe_name>")
#             return
#         try:
#             equipment_name, recipe_name = arg
#             rsp = self.eq_manager.send_recipe_to_equipment(
#                 equipment_name, recipe_name)
#             if not isinstance(rsp, bool):
#                 print(rsp)
#                 return
#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_request_recipe(self, arg: str):
#         """
#         Request recipe from equipment.
#         Usage: request_recipe <equipment_name> [<recipe_name>]
#         Return:
#             - receive recipe data if recipe_name is provided
#             - receive list of recipes if recipe_name is not provided
#         """
#         print("Requesting recipe")

#         arg = arg.split(maxsplit=1)
#         if len(arg) < 1:
#             print("Invalid number of arguments")
#             print("Usage: request_recipe <equipment_name> [<recipe_name>]")
#             return
#         try:
#             equipment_name = arg[0]
#             recipe_name = arg[1] if len(arg) > 1 else None
#             rec_receive = self.eq_manager.request_recipe_from_equipment(
#                 equipment_name, recipe_name)

#             if isinstance(rec_receive, list):
#                 for rec in rec_receive:
#                     print(rec)
#                 return
#             else:
#                 print(rec_receive)
#                 # recipe.save_recipe(equipment_name, rec_receive)
#                 return
#         except ValueError:
#             print("Invalid argument type")
#             return

#     # stream function
#     def do_doc_stream_function(self, arg: str):
#         """
#         Display documentation for a Stream Function.
#         Usage: doc_stream_function <stream> <function>
#         """
#         print("Displaying documentation for Stream Function")
#         args = arg.split()
#         if len(args) != 2:
#             print("Invalid number of arguments")
#             print("Usage: doc_stream_function <stream> <function>")
#             return

#         try:
#             stream = int(args[0])
#             function = int(args[1])

#             sf = self.eq_manager.equipments[0].secsStreamsFunctions.get(
#                 stream, {}).get(function)
#             # sf = secsStreamsFunctions.get(stream, {}).get(function)
#             if not sf:
#                 print(f"S{stream}F{function} not found.")
#                 return

#             print(
#                 f"Found Stream Function:\nName: {sf.__name__}\nDocumentation: {sf.__doc__}")

#         except ValueError:
#             print("Invalid argument type")
#             return

#     def do_send_stream_function(self, arg: str):
#         """
#         Send Stream Function.
#         Args:
#             arg (str): Command-line argument string containing equipment name, stream, function, and parameters.
#         Usage: do_send_stream_function <equipment_name> <stream> <function> <params>
#         """
#         print("Sending Stream Function")
#         parts = arg.split(maxsplit=3)
#         if len(parts) < 3:
#             print(
#                 "Usage: do_send_stream_function <equipment_name> <stream> <function> <params>")
#             return

#         try:
#             equipment_name, stream, function = parts[0], int(
#                 parts[1]), int(parts[2])
#             try:
#                 # Try parsing params as JSON
#                 params = json.loads(parts[3]) if len(parts) > 3 else []
#             except json.JSONDecodeError:
#                 # If JSON parsing fails, try parsing as a list of integers
#                 params = [int(x) for x in parts[3].strip(
#                     '[]').split(',')] if len(parts) > 3 else []
#         except ValueError as e:
#             print(f"Invalid arguments: {e}")
#             return

#         for equipment in self.eq_manager.equipments:
#             if equipment.name == equipment_name:
#                 sf = equipment.secsStreamsFunctions.get(
#                     stream, {}).get(function)
#                 if sf and getattr(sf, '_toEquipment', False):
#                     print(
#                         f"Sending S{stream}F{function} Params: {params} to {equipment_name}")
#                     params = [params] if isinstance(params, int) else params
#                     try:
#                         rsp = equipment.send_and_waitfor_response(
#                             equipment.stream_function(stream, function)(params)
#                         )
#                         print(f"Response: {equipment.secs_decode(rsp)}")
#                     except Exception as e:
#                         print(f"Error while sending request: {e}")
#                     return
#                 elif not sf:
#                     print(f"S{stream}F{function} not found.")
#                     return
#                 else:
#                     print(
#                         f"_toEquipment is False for S{stream}F{function}, skipping request.")
#                     return

#         print(f"Equipment {equipment_name} not found.")

#     # remote command
#     def do_rcmd(self, arg: str):
#         """
#         Send a remote command to an equipment instance.
#         Usage: rcmd <equipment_name> <rcmd> <params>

#         Args:
#             arg (str): Command-line argument string containing equipment name, rcmd, and parameters.

#         Sample: rcmd TNF-61 LOT_ACCEPT LotID=123456
#         """
#         print("Sending remote command")

#         args = arg.split()
#         if len(args) < 2:
#             print("Invalid number of arguments")
#             print("Usage: rcmd <equipment_name> <rcmd> <key=value ...>")
#             return

#         equipment_name = args[0]
#         rcmd = args[1]
#         params = []

#         # Parse parameters into a list of lists
#         for param in args[2:]:
#             if '=' in param:
#                 key, value = param.split('=', 1)
#                 params.append([key, value])  # Convert to list format
#             else:
#                 print(f"Invalid parameter format: {param}")
#                 return
#         print("Parsed command: equipment_name={}, rcmd={}, params={}".format(
#             equipment_name, rcmd, params
#         ))
#         try:
#             # Send the command
#             rsp = self.eq_manager.send_remote_command(
#                 equipment_name, rcmd, params)

#             if rsp is not True:
#                 print(rsp)
#                 return
#             print("Remote command sent successfully.", equipment_name)
#         except ValueError:
#             print("Invalid argument type")
#             return


class CommandCli(cmd.Cmd):
    """
    Command line interface for managing equipment instances.
    List of commands:
        - list: List all equipment instances.
        - add: Add a new equipment instance.
        - remove: Remove an equipment instance.
        - edit: Edit an equipment instance.
        - enable: Enable an equipment instance.
        - disable: Disable an equipment instance.
        - exit: Exit the program.
    """

    def __init__(self, eq_manager: EquipmentManager):
        super().__init__()
        self.eq_manager = eq_manager
        self.prompt = "secsgem > "

    def emptyline(self):
        """
        Do nothing on empty input line.
        """
        pass

    def do_exit(self, arg: str):
        """
        Exit the program.
        Usage: exit
        """
        rsp = self.eq_manager.exit()

        if not isinstance(rsp, bool):
            print(rsp)
        return True

    def do_config(self, arg: str):
        """
        Enter configuration mode to config equipment.
        Usage: config
        """
        Config(self.eq_manager).cmdloop()

    def do_control(self, arg: str):
        """
        Enter control mode to control equipment.
        Usage: control
        """
        Control(self.eq_manager).cmdloop()
