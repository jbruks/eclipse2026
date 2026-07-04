#!/usr/bin/env python3

import argparse
import sys
import time

import PyIndi


INDI_HOST = "localhost"
INDI_PORT = 7624
MOUNT_NAME = "EQMod Mount"


class IndiClient(PyIndi.BaseClient):

    def __init__(self):
        super().__init__()
        self.mount = None

    def newDevice(self, device):
        if device.getDeviceName() == MOUNT_NAME:
            self.mount = device


client = IndiClient()


def wait_switch(name, timeout=10):

    t0 = time.time()

    while time.time() - t0 < timeout:

        prop = client.mount.getSwitch(name)

        if prop is not None:
            return prop

        time.sleep(0.2)

    raise RuntimeError(f"Property {name} not found")


def set_slew_rate(rate):

    prop = wait_switch("TELESCOPE_SLEW_RATE")

    for sw in prop:
        sw.s = PyIndi.ISS_OFF

    if rate < 1 or rate > 9:
        raise ValueError("Speed must be between 1 and 9")

    prop[rate - 1].s = PyIndi.ISS_ON

    client.sendNewSwitch(prop)


def stop_motion():

    ns = wait_switch("TELESCOPE_MOTION_NS")
    we = wait_switch("TELESCOPE_MOTION_WE")

    for sw in ns:
        sw.s = PyIndi.ISS_OFF

    for sw in we:
        sw.s = PyIndi.ISS_OFF

    client.sendNewSwitch(ns)
    client.sendNewSwitch(we)


def move(direction, seconds):

    stop_motion()

    if direction in ("N", "S"):

        prop = wait_switch("TELESCOPE_MOTION_NS")

        prop[0].s = PyIndi.ISS_ON if direction == "N" else PyIndi.ISS_OFF
        prop[1].s = PyIndi.ISS_ON if direction == "S" else PyIndi.ISS_OFF

        client.sendNewSwitch(prop)

    else:

        prop = wait_switch("TELESCOPE_MOTION_WE")

        prop[0].s = PyIndi.ISS_ON if direction == "W" else PyIndi.ISS_OFF
        prop[1].s = PyIndi.ISS_ON if direction == "E" else PyIndi.ISS_OFF

        client.sendNewSwitch(prop)

    time.sleep(seconds)

    stop_motion()


def spiral():

    length = 1

    while True:

        yield ("E", length)
        yield ("N", length)

        length += 1

        yield ("W", length)
        yield ("W", length)

        yield ("S", length)
        yield ("S", length)

        length += 1

        yield ("E", length)
        yield ("E", length)
        yield ("E", length)

        yield ("N", length)
        yield ("N", length)
        yield ("N", length)


parser = argparse.ArgumentParser()

parser.add_argument(
    "--speed",
    type=int,
    default=7,
    help="EQMod slew speed (1..9)"
)

parser.add_argument(
    "--duration",
    type=float,
    default=0.5,
    help="Seconds for one spiral step"
)

args = parser.parse_args()

client.setServer(INDI_HOST, INDI_PORT)

if not client.connectServer():
    sys.exit("Cannot connect to INDI")

print("Connected.")

while client.mount is None:
    time.sleep(0.2)

print("Mount found.")

set_slew_rate(args.speed)

print()
print("Press ENTER to execute next movement.")
print("Type q to quit.")
print()

for direction, count in spiral():

    print(f"{direction}   x{count}")

    cmd = input("> ")

    if cmd.lower() == "q":
        break

    for _ in range(count):
        move(direction, args.duration)

print("Finished.")
