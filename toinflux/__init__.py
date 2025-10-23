"""Module for sending data to InfluxDB from various sources"""

__author__ = "Gavin Lucas"
__copyright__ = "Copyright (C) 2025 Gavin Lucas"
__license__ = "MIT License"
__version__ = "1.0"

from .general import get_class
from .influx import Settings, DataHandler
from .philipshue import Hue
from .myenergi import MyEnergi, Zappi
