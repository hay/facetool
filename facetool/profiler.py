from time import time

class Profiler:
    def __init__(self, name):
        self.name = name
        self.events = []
        self.start()

    def dump_events(self):
        print(f"*** {self.name} ***")
        for e in self.events:
            label = e["label"]
            diff = e["diff"]
            print(f"[{self.name}:{label}] {round(diff, 2)}")

    def start(self):
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