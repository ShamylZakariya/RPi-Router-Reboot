#!/usr/bin/env python3

import argparse
import subprocess
import sys
import time
from datetime import datetime


class Configuration:
    def __init__(self, sites, attempts, delay_between_pings, delay_between_tests, router_shutdown_delay, router_boot_delay, verbose):
        self.sites = sites
        self.attempts = attempts
        self.delay_between_pings = delay_between_pings
        self.delay_between_tests = delay_between_tests
        self.router_shutdown_delay = router_shutdown_delay
        self.router_boot_delay = router_boot_delay
        self.verbose = verbose


def test_offline_configuration(verbose):
    return Configuration(
        ["google.blah", "comcast.blah"],
        1,  # attempts
        1,  # delay_between_pings
        10,  # delay_between_tests
        5,  # router_shutdown_delay
        5,  # router_boot_delay
        verbose
    )


def default_configuration(verbose):
    return Configuration(
        ["8.8.8.8", "1.1.1.1"],  # google dns and cloudflare
        4,  # attempts
        1,  # delay_between_pings
        10,  # delay_between_tests
        10,  # router_shutdown_delay
        120,  # router_start_delay
        verbose
    )


def ping(site: str, verbose: bool):
    cmd = "/bin/ping -c 1 " + site
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError:
        debug_message(verbose, site + ": not reachable")
        return 0
    else:
        return 1


def ping_sites(config: Configuration):
    successful_pings = 0
    attempted_pings = config.attempts * len(config.sites)
    for t in range(0, config.attempts):
        for s in config.sites:
            successful_pings += ping(s, config.verbose)
            time.sleep(config.delay_between_pings)

    if successful_pings != attempted_pings:
        debug_message(config.verbose, "Percentage successful: " +
                    str(int(100 * (successful_pings / float(attempted_pings)))) + "%")

    return True if successful_pings > 0 else False


def turn_off_router(config: Configuration):
    cmd = "sudo uhubctl -l 1-1 -a off"
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True)
        debug_message(config.verbose, output.decode("utf-8"))
    except subprocess.CalledProcessError:
        debug_message(config.verbose, cmd + ": error")
        return 0


def turn_on_router(config: Configuration):
    cmd = "sudo uhubctl -l 1-1 -a on"
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True)
        debug_message(config.verbose, output.decode("utf-8"))
    except subprocess.CalledProcessError:
        debug_message(config.verbose, cmd + ": error")
        return 0


def reboot_router(config: Configuration):
    turn_off_router(config)
    time.sleep(config.router_shutdown_delay)
    turn_on_router(config)
    time.sleep(config.router_boot_delay)


def debug_message(debug_indicator, output_message):
    if debug_indicator:
        print(output_message)


def run(config: Configuration):
    tests = 0
    reboots = 0
    while True:
        success = ping_sites(config)
        debug_message(config.verbose,
                      f"Test {str(tests)} | Reboots {reboots} | Online: {str(success)} ")
        tests += 1
        if success == 0:
          timestamp = datetime.now().strftime('%B %d, %Y %I:%M:%S %p')
          debug_message(config.verbose, f"Offline: restarting router at {timestamp}")
          reboots += 1
          reboot_router(config)
          with open('reboot_log.txt', 'a') as f:
            f.write(timestamp + "\n")

        debug_message(
            config.verbose, f"Waiting {str(config.delay_between_tests)} seconds...")
        time.sleep(config.delay_between_tests)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true",
                        help="Print whats going on to stdout")
    parser.add_argument("--test_offline", action="store_true",
                        help="Run in test mode, where pings to outside world will fail")
    args = parser.parse_args()
    print(
        f"rpi-internet-monitor starting...\nverbose: {args.verbose} test_offline: {args.test_offline}\n\n")
    configuration = test_offline_configuration(
        args.verbose) if args.test_offline else default_configuration(args.verbose)
    run(configuration)


if __name__ == "__main__":
    main()

# # main loop: ping sites, turn appropriate lamp on, wait, repeat
# test = 0
# reboot = -1
# while True:
#   test+=1
#   debug_message(debug, "----- Test " + str(test) + " -----")
#   try:
#       sys.argv[2] == "-test" # force a router reboot
#       success = 0
#   except:
#       success = ping_sites(SITES, DELAY_BETWEEN_PINGS, 2)
#   if success == 0:
#       debug_message(debug, "---- No internet - restarting router ----")
#       reboot+=1
#       ret_reboot = turn_off_usb(reboot)
#       if ret_reboot == 0:
#           with open('reboot_flg.txt', 'w') as f:
#               f.write(datetime.now().strftime('%B %d, %Y %I:%M:%S %p'))
#   else:
#       debug_message(debug, "---- Internet is working fine ----")
#       reboot = -1
#   debug_message(debug, "Waiting " + str(DELAY_BETWEEN_TESTS) + " seconds until next test.")
#   time.sleep(DELAY_BETWEEN_TESTS)
