# Monitor UPS state

from pynut2 import nut2 as nut

class UPSState:
    _ups_client = None

    _ups_name = None

    _ls_ups_vars = list()
    _dict_states = dict()

    # Value List: [ current value (str/int/float), has updated (Bool) ]

    def __init__(self, ups_name):
        self._ups_client = nut.PyNUTClient()
        self._ups_name = ups_name

        # Initialize dictionary keys with all available states
        for ups_var in self._ups_client.list_vars(self._ups_name):
            self._ls_ups_vars.append(ups_var)
            self._dict_states[ups_var] = [None, False]

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
                yield [key, value[0]]
