# Monitor UPS state

class UPSState:

    _state_dict = None

    _poll_interval =

    # Value List: [ current value (str/int/float), has updated (Bool) ]

    def __init__(self, init_vars):
        self._dict_base = dict()
        for var in init_vars:
            self._dict_base[var] = [None, True]

    async def loop_forever(self):
        # do loopy stuff


