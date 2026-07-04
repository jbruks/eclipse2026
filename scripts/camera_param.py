#!/usr/bin/env python3
"""
camera_control.py

Simple V4L2 camera control utility.

Examples:

    python3 camera_control.py --manual --exposure 200

    python3 camera_control.py --aperture-priority

    python3 camera_control.py \
        --contrast 19 \
        --gamma 100 \
        --brightness 0 \
        --saturation 64 \
        --sharpness 10
"""

import argparse
import subprocess
import sys


class Camera:

    def __init__(self, device="/dev/bresser"):
        self.device = device

    def set_control(self, name, value):
        cmd = [
            "v4l2-ctl",
            "-d",
            self.device,
            "--set-ctrl",
            f"{name}={value}",
        ]

        print(" ".join(cmd))
        subprocess.run(cmd, check=True)

    def manual(self, exposure):
        self.set_control("auto_exposure", 1)
        self.set_control("exposure_time_absolute", exposure)

    def aperture_priority(self):
        self.set_control("auto_exposure", 3)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--device",
        default="/dev/bresser",
        help="Video device",
    )

    parser.add_argument("--manual", action="store_true")
    parser.add_argument("--aperture-priority", action="store_true")

    parser.add_argument("--exposure", type=int)

    parser.add_argument("--contrast", type=int)
    parser.add_argument("--gamma", type=int)
    parser.add_argument("--brightness", type=int)
    parser.add_argument("--saturation", type=int)
    parser.add_argument("--sharpness", type=int)

    args = parser.parse_args()

    cam = Camera(args.device)

    try:

        if args.manual:
            if args.exposure is None:
                parser.error("--manual requires --exposure")
            cam.manual(args.exposure)

        if args.aperture_priority:
            cam.aperture_priority()

        controls = {
            "contrast": args.contrast,
            "gamma": args.gamma,
            "brightness": args.brightness,
            "saturation": args.saturation,
            "sharpness": args.sharpness,
        }

        for name, value in controls.items():
            if value is not None:
                cam.set_control(name, value)

    except subprocess.CalledProcessError as e:
        print(f"Error executing v4l2-ctl: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
