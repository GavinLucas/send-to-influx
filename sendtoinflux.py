#!/usr/bin/env python3
"""Script to get data from a variety of sources and send it to InfluxDB"""

__author__ = "Gavin Lucas"
__copyright__ = "Copyright (C) 2025 Gavin Lucas"
__license__ = "MIT License"
__version__ = "1.0"

import sys
import time
import json
import signal
import argparse
import toinflux


def signal_handler(sig, frame):
    """
    Signal handler to exit gracefully
    """
    # avoid unused variable warning
    if frame:
        pass

    # print a message and exit
    print(f"\nExiting on signal {sig}")
    sys.exit(0)


def main():
    """
    The main function
    """
    # register the signal handler for ctrl-c
    signal.signal(signal.SIGINT, signal_handler)

    # get the default source from the settings
    default_source = toinflux.Settings().toinflux["default_source"]

    # parse the command line arguments
    arg_parse = argparse.ArgumentParser(description="Send Hue Data to InfluxDB")
    arg_parse.add_argument(
        "-d",
        "--dump",
        required=False,
        action="store_true",
        help="dump the data to the console one time and exit",
    )
    arg_parse.add_argument(
        "-p",
        "--print",
        required=False,
        action="store_true",
        help="print the raw data rather than sending it to InfluxDB",
    )
    arg_parse.add_argument(
        "-s",
        "--source",
        required=False,
        default=default_source,
        dest="source",
        type=str,
        help=f'the source of the data to send to InfluxDB (hue, zappi, etc.) - default is "{default_source}"',
    )
    args = arg_parse.parse_args()

    # get the data source class
    data_handler = toinflux.get_class(args.source)

    # dump the data if required and exit
    if args.dump:
        data = data_handler.get_data()
        print(json.dumps(data, indent=4))
        sys.exit(0)

    # main loop to collect data and send it to InfluxDB
    next_update = time.time()
    while True:
        next_update += data_handler.source_settings["interval"]

        # get the parsed data
        data = data_handler.get_data()

        # print or send the data
        if args.print:
            blob = {"time": time.strftime("%a, %d %b %Y, %H:%M:%S %Z", time.localtime()), "data": data}
            print(json.dumps(blob, indent=4))
        else:
            data_handler.send_data()

        # Sleep until the next interval
        sleep_time = max(0, next_update - time.time())
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
