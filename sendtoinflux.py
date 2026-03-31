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
import threading
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

    # load settings once for defaults and configured source list
    settings = toinflux.load_settings()
    default_source = settings["default_source"]

    # parse the command line arguments
    arg_parse = argparse.ArgumentParser(description="Send Hue Data to InfluxDB")
    arg_parse.add_argument(
        "-d",
        "--dump",
        required=False,
        action="store_true",
        help=("dump the data to the console one time and exit. This requires a source to be specified"),
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
        dest="source",
        type=str,
        help=(
            "the source of the data to send to InfluxDB (hue, zappi, etc.). "
            "If omitted, all sources in the settings file 'sources' list are started. "
            f"If no source is specified, the default source is used: {default_source}"
        ),
    )
    args = arg_parse.parse_args()

    if args.source:
        run_single_source(args.source, args)
        return

    sources = settings.get("sources")
    if not isinstance(sources, list) or not sources:
        run_single_source(default_source, args)
        return

    if args.dump:
        print("The --dump option requires --source when running in multi-source mode.")
        sys.exit(1)

    run_multi_source(sources, args, settings.get("stagger_seconds", 10))


def run_single_source(source, args):
    """
    Run a single data source in either dump, print, or send mode.

    :param source: source name from settings/get_class mapping
    :type source: str
    :param args: parsed CLI arguments
    :type args: argparse.Namespace
    """
    data_handler = toinflux.get_class(source)

    # dump the data if required and exit
    if args.dump:
        data = data_handler.get_data()
        print(json.dumps(data, indent=4))
        sys.exit(0)

    next_update = time.time()
    while True:
        next_update += data_handler.source_settings["interval"]
        data = data_handler.get_data()

        if args.print:
            blob = {
                "source": source,
                "time": time.strftime("%a, %d %b %Y, %H:%M:%S %Z", time.localtime()),
                "data": data,
            }
            print(json.dumps(blob, indent=4))
        else:
            data_handler.send_data()

        sleep_time = max(0, next_update - time.time())
        time.sleep(sleep_time)


def run_multi_source(sources, args, stagger_seconds):
    """
    Run all configured sources concurrently, with staggered start offsets.

    :param sources: list of source names to run
    :type sources: list[str]
    :param args: parsed CLI arguments
    :type args: argparse.Namespace
    :param stagger_seconds: delay between source start offsets
    :type stagger_seconds: int
    """

    def source_worker(source, source_start_delay):
        data_handler = toinflux.get_class(source)
        next_update = time.time() + source_start_delay
        while True:
            sleep_time = max(0, next_update - time.time())
            time.sleep(sleep_time)

            data = data_handler.get_data()
            if args.print:
                blob = {
                    "source": source,
                    "time": time.strftime("%a, %d %b %Y, %H:%M:%S %Z", time.localtime()),
                    "data": data,
                }
                print(json.dumps(blob, indent=4))
            else:
                data_handler.send_data()

            next_update += data_handler.source_settings["interval"]

    threads = []
    for index, source in enumerate(sources):
        start_delay = max(0, stagger_seconds) * index
        source_thread = threading.Thread(target=source_worker, args=(source, start_delay), daemon=True)
        source_thread.start()
        threads.append(source_thread)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
