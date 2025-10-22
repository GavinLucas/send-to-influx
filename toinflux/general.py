#!/usr/bin/env python3
"""General functions and classes for sending data to InfluxDB"""
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

    :param source: data source name
    :type name: str
    :return: class object
    :rtype: DataHandler
    """
    class_name = source.capitalize()
    source_name = source.lower()
    try:
        my_class = globals()[class_name](source_name)
    except KeyError:
        print(f"Source {class_name} not found")
        sys.exit(1)
    return my_class
