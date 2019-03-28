from time import time
from .util import message

class Profiler:
    def __init__(self, name):
        self.name = name
        self.events = []
        self.start()

    def dump_events(self):
        message(f"*** {self.name} ***")

        for e in self.events:
            label = e["label"]
            diff = round(e["diff"], 2)
            time_ = round(e["time"] - self._start, 2)
            message(f"[{self.name}:{label}] {diff} ({time_})")

    def start(self):
        self._start = time()

        self.events.append({
            "label" : "start",
            "diff" : 0,
            "time" : time()
        })

    def stop(self):
        self.tick("stop")

    def tick(self, label):
        now = time()
        last = self.events[-1]
        diff = now - last["time"]

        self.events.append({
            "label" : label,
            "diff" : diff,
            "time" : now
        })