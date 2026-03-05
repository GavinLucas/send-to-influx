"""General functions and classes for sending data to InfluxDB"""

__author__ = "Gavin Lucas"
__copyright__ = "Copyright (C) 2025 Gavin Lucas"
__license__ = "MIT License"
__version__ = "1.0"

# pylint: disable=import-outside-toplevel
import os
import sys
import urllib3
import yaml

# disable SSL warnings for requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_class(source):
    """
    Create and return a class object for the given data source name

    This function modifies the case of the source so that the user can
    input this in any case and it will still work.

    When adding a new data source, add the class to the classes dictionary
    and add the import to the imports section below.

    :param source: data source name
    :type name: str
    :return: class object
    :rtype: DataHandler
    """
    from toinflux.influx import DataHandler
    from toinflux.myenergi import MyEnergi, Zappi
    from toinflux.philipshue import Hue

    classes = {"DataHandler": DataHandler, "Hue": Hue, "MyEnergi": MyEnergi, "Zappi": Zappi}

    # Use a Capitalised name for the class name
    class_name = source.capitalize() if source.islower() else source
    # Use a lower case name for the source to match the settings file entries
    source_name = source.lower()
    try:
        my_class = classes[class_name](source_name)
    except KeyError:
        print(f"Source {class_name} not found")
        sys.exit(1)
    return my_class


def load_settings(settings_file="settings.yml"):
    """Load settings from a YAML file and return as a dictionary.

    :param settings_file: path to the settings file (absolute, or relative to the project root)
    :type settings_file: str
    :return: parsed settings dictionary
    :rtype: dict
    """
    base_dir = os.path.abspath(os.path.dirname(__file__) + "/..")
    settings_path = os.path.join(base_dir, settings_file)

    try:
        with open(settings_path, encoding="utf8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{settings_path} not found.")
        print("Make sure you copy settings.yml.example to settings.yml and edit it.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error in settings.yml - {e}")
        sys.exit(1)
