# Handle incoming UPS commands

from logging import ERROR
from logging import INFO

from pynut2 import nut2 as nut

class UPSCommand:
    _ups_client = None
    _ups_name = None

    _ls_ups_cmds = list()

    # Logging callback
    on_log_message = None

    def __init__(self, nut_client, ups_name):
        self._ups_client = nut_client
        self._ups_name = ups_name

        # Initialize available commands list
        for ups_var in self._ups_client.list_commands(self._ups_name):
            self._ls_ups_cmds.append(ups_var)

    def log(self, loglevel, message):
        if self.on_log_message is not None:
            self.on_log_message(loglevel, message)

    # Update state dictionary with latest data
    def all_commands(self):
        for cmd in self._ls_ups_cmds:
            yield cmd

    def run_command(self, command, params=""):
        try:
            # Check if valid command
            if command not in self._ls_ups_cmds:
                self.log(ERROR, "UPSCommand: invalid command: " + command)
                return
            self.log(INFO, "UPSCommand: Command: " + command)
            self.log(INFO, "UPSCommand: Params: " + params)
            if type(params) is str and params is not "":
                self._ups_client.run_command(self._ups_name, command + " " + params)
            else:
                self._ups_client.run_command(self._ups_name, command)
        except nut.PyNUTError as e:
            print(str(e.args))
