"""Speedtest class to send data to InfluxDB"""

__author__ = "Gavin Lucas"
__copyright__ = "Copyright (C) 2025 Gavin Lucas"
__license__ = "MIT License"
__version__ = "1.0"

import sys
import socket
import speedtest
from toinflux.influx import DataHandler


class Speedtest(DataHandler):
    """
    Speedtest class to send data to InfluxDB

    :return: data
    :rtype: dict
    """

    def get_data(self):
        """Run and get the data from Speedtest"""
        try:
            st = speedtest.Speedtest(timeout=self.settings["speedtest"].get("timeout", 120))

            # run the download test
            st.download()

            # run the upload test
            st.upload()

            # get the results
            st_data = st.results.dict()
        except speedtest.SpeedtestException as e:
            print(f"Error running Speedtest - {e}")
            sys.exit(2)
        if not isinstance(st_data, dict):
            print("Error running Speedtest - invalid results")
            sys.exit(2)

        # just extract the specific fields we want here
        if "fields" in self.settings["speedtest"]:
            self.data = {k: st_data[k] for k in self.settings["speedtest"]["fields"] if k in st_data}
        else:
            self.data = st_data

        # use the local hostname as the host tag
        self.influx_header = f"speedtest,host={socket.gethostname().split(".")[0]} "

        return self.data
