"""Parent class for data handlers to send data to InfluxDB"""

# pylint: disable=too-few-public-methods
import sys
import os
import requests
import yaml


class Settings:
    """Class to manage the settings from the settings file"""

    def __init__(self, settings_file="settings.yml"):
        self.toinflux = None
        self.base_dir = os.path.abspath(os.path.dirname(__file__) + "/..")
        self.settings_file = os.path.join(self.base_dir, settings_file)

        self.load()

    def load(self):
        """Load the settings from the settings file

        :return: None
        """
        try:
            with open(self.settings_file, encoding="utf8") as f:
                self.toinflux = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"{self.settings_file} not found.")
            print("Make sure you copy settings.yml.example to settings.yml and edit it.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error in settings.yml - {e}")
            sys.exit(1)


class DataHandler:
    """Class to send data to InfluxDB"""

    def __init__(self, source=None):
        self.settings = Settings().toinflux
        self.source = source
        self.influx_header = None

        if self.source and self.source in self.settings:
            self.source_settings = self.settings[self.source]
        else:
            print(f"Source {self.source} not found in settings")
            sys.exit(1)

    def send_data(self, data):
        """
        Sends data to influxDB

        :param data: data to send to InfluxDB
        :type data: dict
        :return: None
        """

        # minimalist activity indicator
        print(" ^", end="\r")

        # format the data to send
        data_to_send = self.influx_header + ",".join([f"{key}={value}" for key, value in data.items()])

        # send to InfluxDB
        url = f'{self.settings["influx"]["url"]}/write?db={self.source_settings["db"]}&precision=s'
        try:
            response = requests.post(
                url,
                auth=(self.settings["influx"]["user"], self.settings["influx"]["password"]),
                data=data_to_send,
                timeout=self.settings["influx"].get("timeout", 5),
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error sending data to InfluxDB - {e}")

        # minimalist activity indicator
        print(" _", end="\r")
