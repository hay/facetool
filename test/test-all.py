#!/usr/bin/env python3
from tests import TESTS
import argparse
import subprocess
import sys

def cmd(cmd):
    subprocess.check_call(cmd, shell = True)

def cleanup():
    cmd("""
    cd ../
    rm -rf test/output/*
    """)

def run_test(test):
    cmd(f"cd ../ && ./facetool.py {test['command']} -vv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--group")
    parser.add_argument("-ls", "--list", action = "store_true")
    parser.add_argument("--run", type = int)
    parser.add_argument("-3d", "--three-dee", action = "store_true")
    args = parser.parse_args()

    if args.list:
        for index, test in enumerate(TESTS):
            print(f"[{index}] - {test['label']}")

        sys.exit()

    cleanup()

    for index, test in enumerate(TESTS):
        if (args.run is not None) and args.run != index:
            continue

        if args.group:
            group = test["command"].split(" ")[0]

            if group != args.group:
                continue

        if args.three_dee:
            test["command"] += " --swap-method faceswap3d"

        print(f"\n*** {test['label']} ***\n")
        run_test(test)