"""General functions and classes for sending data to InfluxDB"""

__author__ = "Gavin Lucas"
__copyright__ = "Copyright (C) 2025 Gavin Lucas"
__license__ = "MIT License"
__version__ = "1.0"

# pylint: disable=unused-import
import sys
import urllib3
from toinflux.influx import DataHandler
from toinflux.philipshue import Hue
from toinflux.myenergi import MyEnergi, Zappi

# disable SSL warnings for requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_class(source):
    """
    Create and return a class object for the given data source name

    This function modifies the case of the source so that the user can
    input this in any case and it will still work.

    :param source: data source name
    :type name: str
    :return: class object
    :rtype: DataHandler
    """
    # Use a Capitalised name for the class name
    class_name = source.capitalize() if source.islower() else source
    # Use a lower case name for the source to match the settings file entries
    source_name = source.lower()
    try:
        # Create an instance of the class
        my_class = globals()[class_name](source_name)
    except KeyError:
        print(f"Source {class_name} not found")
        sys.exit(1)
    return my_class
