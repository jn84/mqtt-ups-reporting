import configparser

class UPSConfigurationHandler:
    config = None
    config_file = None

    UPS_NAME = None
    UPDATE_INTERVAL = None

    MQTT_HOST = None
    MQTT_PORT = None
    MQTT_CLIENT_ID = None
    MQTT_USE_AUTHENTICATION = None
    MQTT_USERNAME = None
    MQTT_PASSWORD = None
    MQTT_USE_SSL = None
    MQTT_PORT_SSL = None

    MQTT_TOPIC_REPORT_UPS_DATA = None

    def generate_client_id(self):
        self.MQTT_CLIENT_ID = 'UPS_' + str(self.UPS_NAME)

    # Config parsing helpers
    @staticmethod
    def bool_parse(str_value: str, var_name: str, default: bool) -> object:
        val = str.lower(str_value)
        if val == '':
            return default
        if val == 'true' or val == 'high' or val == '1':
            return True
        if val == 'false' or val == 'low' or val == '0':
            return False
        raise TypeError('Config value "' + str_value + '" is invalid for ' + var_name)

    @staticmethod
    def int_parse(str_value: str, var_name: str, can_be_none: bool) -> object:
        if (str_value == '' or str_value is None) and can_be_none:
            return None
        if (str_value == '' or str_value is None) and not can_be_none:
            raise ValueError("Config value cannot be empty for " + var_name)
        return int(str_value)

    @staticmethod
    def float_parse(str_value: str, var_name: str, can_be_none: bool) -> object:
        if (str_value == '' or str_value is None) and can_be_none:
            return None
        if (str_value == '' or str_value is None) and not can_be_none:
            raise ValueError("Config value cannot be empty for " + var_name)
        return float(str_value)

    @staticmethod
    def str_parse(str_value: str, var_name: str, can_be_none: bool) -> object:
        if str_value == '' and can_be_none:
            return None
        if str_value == '' and not can_be_none:
            raise TypeError('Config value is invalid for ' + var_name + ': value cannot be empty')
        return str(str_value)

    def get_port(self):
        if self.MQTT_USE_SSL:
            return self.MQTT_PORT_SSL
        return self.MQTT_PORT

    def __init__(self, config_file):

        self.config_file = config_file

        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        self.UPS_NAME = self.str_parse(
            self.config['General']['ups_name'],
            'ups_name',
            False)

        self.NUT_LOGIN = self.str_parse(
            self.config['General']['nut_login'],
            'nut_login',
            True)

        self.NUT_PASSWORD = self.str_parse(
            self.config['General']['nut_password'],
            'nut_password',
            True)

        self.UPDATE_INTERVAL = self.int_parse(
            self.config['General']['update_interval'],
            'update_interval',
             False)

        self.MQTT_HOST = self.str_parse(
            self.config['MQTTBrokerConfig']['mqtt_host'],
            'mqtt_host',
            False)

        self.MQTT_PORT = self.int_parse(
            self.config['MQTTBrokerConfig']['mqtt_port'],
            'mqtt_port',
            False)

        self.MQTT_CLIENT_ID = self.str_parse(
            self.config['MQTTBrokerConfig']['mqtt_client_id'],
            'mqtt_client_id',
            True)

        self.MQTT_USE_AUTHENTICATION = self.bool_parse(
            self.config['MQTTBrokerConfig']['mqtt_use_authentication'],
            'mqtt_use_authentication',
            False)

        self.MQTT_USERNAME = self.str_parse(
            self.config['MQTTBrokerConfig']['mqtt_username'],
            'mqtt_username',
            not self.MQTT_USE_AUTHENTICATION)

        self.MQTT_PASSWORD = self.str_parse(
            self.config['MQTTBrokerConfig']['mqtt_password'],
            'mqtt_password',
            not self.MQTT_USE_AUTHENTICATION)

        self.MQTT_USE_SSL = self.bool_parse(
            self.config['MQTTBrokerConfig']['mqtt_use_ssl'],
            'mqtt_use_ssl',
            False)

        self.MQTT_PORT_SSL = self.int_parse(
            self.config['MQTTBrokerConfig']['mqtt_port_ssl'],
            'mqtt_port_ssl',
            not self.MQTT_USE_SSL)

        self.MQTT_TOPIC_REPORT_UPS_DATA = self.str_parse(
            self.config['MQTTTopicConfig']['mqtt_topic_report_ups_data'],
            'mqtt_topic_report_ups_data',
            False)

        self.MQTT_TOPIC_ISSUED_COMMANDS = self.str_parse(
            self.config['MQTTTopicConfig']['mqtt_topic_issued_commands'],
            'mqtt_topic_issued_commands',
            False)

        if self.MQTT_CLIENT_ID == '' or self.MQTT_CLIENT_ID is None:
            self.generate_client_id()