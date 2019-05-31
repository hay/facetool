#!/usr/bin/env python3
import subprocess
from tests import TESTS

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
    cleanup()

    for test in TESTS:
        print(f"\n*** {test['label']} ***\n")
        run_test(test)