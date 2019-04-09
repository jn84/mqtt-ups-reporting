# Route and relay information between controller and state/cmd modules

from logging import CRITICAL
from logging import ERROR
from logging import WARNING
from logging import INFO
from logging import DEBUG
from logging import NOTSET

from helpers.ups_state import UPSState
from helpers.ups_cmd import UPSCommand

class UPSHandler:
    _ups_name = None

    _ups_state = None
    _ups_cmd = None

    # Logger callback
    on_log_message = None

    def __init__(self, ups_name, upsd_username=None, upsd_password=None):
        self._ups_name = ups_name
        self._ups_state = UPSState(self._ups_name)
        self._ups_cmd = UPSCommand(self._ups_name, upsd_username, upsd_password)

        self._ups_state.on_log_message = self.log
        self._ups_cmd.on_log_message = self.log

    # Send logs up the chain. The object creator chooses what to do with them
    def log(self, loglevel, message):
        if self.on_log_message is not None:
            self.on_log_message(loglevel, message)

    def get_commands(self):
        for cmd in self._ups_cmd.all_commands():
            yield cmd

    def run_command(self, command, params=""):
        print("Entered run_command in ups_handler")
        print("command: " + command)
        print("params:  " + params)
        self._ups_cmd.run_command(command, params)

    def get_updated_states(self):
        for key, value in self._ups_state.get_state_data():
            yield key, value