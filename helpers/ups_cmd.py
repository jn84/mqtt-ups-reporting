# Handle incoming UPS commands

from pynut2 import nut2 as nut


class UPSCommand:
    _ups_client = None
    _ups_name = None

    _ls_ups_cmds = list()


    def __init__(self, ups_name, username, password):
        self._ups_client = nut.PyNUTClient(login=username, password=password)
        self._ups_name = ups_name

        # Initialize available commands list
        for ups_var in self._ups_client.list_commands(self._ups_name):
            self._ls_ups_cmds.append(ups_var)

    # Update state dictionary with latest data
    def all_commands(self):
        for cmd in self._ls_ups_cmds:
            yield cmd

    def run_command(self, command, params=""):
        self._ups_client.run_command(self._ups_name , command + " " + params)
