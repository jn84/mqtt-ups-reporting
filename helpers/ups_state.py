# Monitor UPS state

class UPSState:
    _ups_client = None

    _ups_name = None

    _ls_ups_vars = list()
    _dict_states = dict()

    # Logger callback
    on_log_message = None

    # Value List: [ current value (str/int/float), has updated (Bool) ]

    def __init__(self, nut_client, ups_name):
        self._ups_name = ups_name
        self._ups_client = nut_client

        # Initialize dictionary keys with all available states
        for ups_var in self._ups_client.list_vars(self._ups_name):
            self._ls_ups_vars.append(ups_var)
            self._dict_states[ups_var] = [None, False]

    def log(self, loglevel, message):
        if self.on_log_message is not None:
            self.on_log_message(loglevel, message)

    # Update state dictionary with latest data
    def _update_states(self):
        for ups_var in self._ls_ups_vars:
            new_state = self._ups_client.get_var(self._ups_name, ups_var)
            if self._dict_states[ups_var][0] != new_state:
                self._dict_states[ups_var] = [new_state, True]
            else:
                self._dict_states[ups_var][1] = False

    def get_state_data(self):
        self._update_states()
        for key, value in self._dict_states.items():
            if value[1]:
                yield key, value[0]
