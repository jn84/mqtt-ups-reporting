# Route and relay information between controller and state/cmd modules

from pynut2.nut2 import PyNUTClient


class UPSHandler:
    ups_name = None

    # State change callback
    # Signature on_state_change(state: bool)
    on_state_change = None

    # Logger callback
    on_log_message = None

    def __init__(self, )