# Handle incoming UPS commands

from logging import CRITICAL
from logging import ERROR
from logging import WARNING
from logging import INFO
from logging import DEBUG
from logging import NOTSET

from pynut2 import nut2 as nut


class UPSCommand:
    _ups_client = None
    _ups_name = None

    _ls_ups_cmds = list()

    # Logging callback
    on_log_message = None

    def __init__(self, ups_name, username=None, password=None):
        if username is None or password is None:
            self._ups_client = nut.PyNUTClient()
            self.log(WARNING,
                     "UPSCommand: NUT Client connected without authentication."
                     "Running commands will most likely not work.")
        else:
            self._ups_client = nut.PyNUTClient(login=username, password=password)
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

    def run_command(self, command, params=None):
        # Check if valid command
        if command not in self._ls_ups_cmds:
            self.log(ERROR, "UPSCommand: invalid command: " + command)
            return
        if params is not None and type(params) is str:
            self._ups_client.run_command(self._ups_name, command + " " + params)
        else:
            self._ups_client.run_command(self._ups_name, command)
