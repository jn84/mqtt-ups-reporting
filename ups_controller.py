import argparse
import json
import logging
import string
import sys
import time
import traceback
from os import access
from os import path
from os import mkdir
from os import R_OK

import paho.mqtt.client as mqtt


import config_handler
import ups_handler

from configparser import Error as ConfigError
from logging.handlers import TimedRotatingFileHandler


# MAJOR.MINOR.BUGFIX
VERSION = '0.1.0'

LOG_LEVEL = logging.DEBUG

client = None
logger = None
ups = None

_is_mqtt_connected = False

def get_timed_rotating_logger(ups_name, log_level):
    log_file = 'ups.log'

    # Remove punctuation and directorize Instance Name
    translator = str.maketrans('', '', string.punctuation)

    log_dir = ups_name.translate(translator)
    log_dir = log_dir.replace(' ', '_')
    log_dir += '/'

    # Create the directory if it doesn't exist
    if not path.exists(log_dir):
        mkdir(log_dir)

    log_obj = logging.getLogger(ups_name)
    log_obj.setLevel(log_level)

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    handler = TimedRotatingFileHandler(log_dir + log_file,
                                       when='midnight',
                                       backupCount=14)

    handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setFormatter(formatter)

    log_obj.addHandler(handler)

    log_obj.addHandler(console_handler)

    return log_obj


# Get the config file name
parser = argparse.ArgumentParser(description='Monitor and control UPS via MQTT',
                                 epilog='Electricity is really just organized lightning',
                                 prog='ups_controller.py')
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)
parser.add_argument('-c', '--config', type=str, default='example.config', dest='config_file',
                    help='File name of the config file used to launch the daemon.'
                         'The program must be run using a config file. If one is not '
                         'specified, the default example.config (not recommended) will be used. Make a '
                         'copy of example.config and modify the settings to suit your needs.')

# Get the config file name
args = parser.parse_args()

if not path.isfile(args.config_file) or not access(args.config_file, R_OK):
    print('The configuration file could not be found or read access was denied by the system.')
    sys.exit('Unable to access config file: ' + args.config_file)

# Parse the config file

try:
    config = config_handler.UPSConfigurationHandler(args.config_file)
except ConfigError as e:
    print(str(e))
    sys.exit('Error parsing the config file')
except TypeError as e:
    print(str(e))
    sys.exit('Error converting config variable to correct type. Check that all configuration variables '
             'are in the correct format.')


logger = get_timed_rotating_logger(config.UPS_NAME,
                                   LOG_LEVEL)
logger.log(logging.INFO, 'Configuration file successfully loaded')

logger.log(logging.INFO, 'Initializing handlers...')

if not config.NUT_USE_AUTH:
    logger.log(logging.WARNING, "UPS Controller: NUT authentication not used. Commands unavailable.")
    ups = ups_handler.UPSHandler(config.UPS_NAME)
else:
    ups = ups_handler.UPSHandler(config.UPS_NAME, config.NUT_LOGIN, config.NUT_PASSWORD)


logger.log(logging.INFO, 'Defining definitions...')

def log(loglevel, message):
    logger.log(loglevel, message)

def on_connect(client_local, userdata, flags, rc):
    global _is_mqtt_connected
    if rc == 0:  # Successful connection
        logger.log(logging.INFO, 'Setting up MQTT subscriptions')
        client_local.subscribe(config.MQTT_TOPIC_ISSUED_COMMANDS)
        logger.log(logging.INFO, 'MQTT successfully connected on port:' + str(config.get_port()))
        _is_mqtt_connected = True
    else:
        _is_mqtt_connected = False


def on_disconnect(client_local, userdata, rc):
    global _is_mqtt_connected
    _is_mqtt_connected = False


# Incoming UPS command messages
def on_message(client_local, userdata, msg):
    if not config.NUT_USE_AUTH:
        logger.log(logging.WARNING, "UPS Controller: NUT authentication not used. Commands unavailable.")
        return
    if msg.topic == config.MQTT_TOPIC_ISSUED_COMMANDS:
        try:
            print(msg.payload)
            command_data = json.loads(msg.payload)
        except ValueError:
            log(logging.ERROR, "UPS Controller: MQTT parsing error. UPS command data improperly formatted."
                               "Expected json k/v pairs, got something else. Ignoring command message."
                               "Message: " + msg.payload)
            return
        except Exception as e:
            logger.log(logging.ERROR, e.args)
            return

        if command_data["params"] == "":
            ups.run_command(command_data["command"], params="")
        else:
            ups.run_command(command_data["command"], command_data["params"])
    else:
        log(logging.ERROR,
            'Received message from non subscribed topic. This should never happen...: ' + str(msg.topic))


logger.info('Definitions successfully defined')
logger.info('Configuring MQTT client...')

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

if config.MQTT_USE_SSL:
    logger.info('MQTT SSL Enabled')
    client.tls_set()
else:
    logger.info('MQTT connection will not be using SSL')

if config.MQTT_USE_AUTHENTICATION:
    logger.info('Setting MQTT username and password')
    client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
else:
    logger.info('Setting MQTT to anonymous login')

logger.info('MQTT successfully configured')
logger.info('Creating MQTT connection to host: ' + config.MQTT_HOST)

client.connect_async(config.MQTT_HOST, port=config.get_port(), keepalive=60)

# noinspection PyBroadException
try:
    client.loop_start()

    # Publish available commands
    ls_cmds = dict()
    i = 0
    for cmd in ups.get_commands():
        ls_cmds[str(i)] = cmd
        i += 1
    json_cmds = json.dumps(ls_cmds)

    client.publish(
        config.MQTT_TOPIC_REPORT_UPS_DATA + "/available-commands",
        json_cmds,
        qos=2,
        retain=True
    )

    while True:
        for key, value in ups.get_updated_states():
            st = dict()
            st["state"] = key
            st["data"] = value
            json_data = json.dumps(st)
            client.publish(
                config.MQTT_TOPIC_REPORT_UPS_DATA + "/" + key,
                json_data,
                qos=1,
                retain=True)

        time.sleep(config.UPDATE_INTERVAL)

except KeyboardInterrupt:
    client.loop_stop()
    logger.info('UPS controller stopped by keyboard input. Cleaning up and exiting...')
except:  # Phooey at your PEP 8 rules. I have no idea what exceptions I might run into
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error('Unhandled exception. Quitting...')