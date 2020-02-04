import logging
import os
import subprocess

log = logging.getLogger(__name__)

class Command:
    def __init__(self, dry_run = False, verbose = False):
        self.dry_run = dry_run
        self.verbose = verbose

    def call(self, cmd, verbose = False):
        log.debug(f"Running shell command '{cmd}'")
        if self.dry_run:
            logging.debug(f"[dry-run] {cmd}")
        else:
            # By default we do a 'quiet' shell run, except if the verbose
            # option is switched on
            if self.verbose or verbose:
                subprocess.check_call(cmd, shell = True)
            else:
                subprocess.check_call(cmd, shell = True,
                    stdout = open(os.devnull, 'wb')
                )