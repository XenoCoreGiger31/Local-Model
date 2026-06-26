import json
import os
from datetime import datetime

MEMORY_DIR = "memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

SHORT_TERM_LIMIT = 50  # max events in session buffer
EPISODIC_LOG = os.path.join(MEMORY_DIR, "episodic.jsonl")
LONG_TERM_LOG = os.path.join(MEMORY_DIR, "longterm.jsonl")


class AgentMemory:
    def __init__(self):
        self.short_term = []  # session buffer, cleared on restart

    # SHORT TERM
    def add(self, event_type, data):
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.short_term.append(event)
        if len(self.short_term) > SHORT_TERM_LIMIT:
            self.short_term.pop(0)  # drop oldest
        self._append_episodic(event)

    def get_recent(self, n=10):
        return self.short_term[-n:]

    # LONG TERM
    def save_long_term(self, key, value):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "key": key,
            "value": value
        }
        with open(LONG_TERM_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def load_long_term(self):
        if not os.path.exists(LONG_TERM_LOG):
            return []
        with open(LONG_TERM_LOG, "r") as f:
            return [json.loads(line) for line in f if line.strip()]

    # EPISODIC
    def _append_episodic(self, event):
        with open(EPISODIC_LOG, "a") as f:
            f.write(json.dumps(event) + "\n")

    def load_episodic(self):
        if not os.path.exists(EPISODIC_LOG):
            return []
        with open(EPISODIC_LOG, "r") as f:
            return [json.loads(line) for line in f if line.strip()]

    def stats(self):
        episodic = self.load_episodic()
        longterm = self.load_long_term()
        print(f"[MEMORY] Short-term buffer: {len(self.short_term)} events")
        print(f"[MEMORY] Episodic log: {len(episodic)} total events")
        print(f"[MEMORY] Long-term log: {len(longterm)} entries")


if __name__ == "__main__":
    m = AgentMemory()
    m.stats()
