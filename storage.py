from collections import defaultdict
from datetime import datetime, timedelta
import threading
import time


class Storage:
    def __init__(self):
        self.current_state = {}
        self.history = defaultdict(list)
        self.last_seq = {}
        self.agent_last_seen = {}
        self.total_events = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

    def update_agent_seen(self, agent_id):
        self.agent_last_seen[agent_id] = datetime.now()

    def is_new_message(self, agent_id, delivery_id, seq):
        key = (agent_id, delivery_id)
        last = self.last_seq.get(key, -1)

        if seq <= last:
            return False

        self.last_seq[key] = seq
        return True

    def save_event(self, event):
        with self.lock:
            delivery_id = event["delivery_id"]
            agent_id = event["agent_id"]

            self.current_state[delivery_id] = event
            self.history[delivery_id].append(event)
            self.update_agent_seen(agent_id)
            self.total_events += 1

    def get_status(self, delivery_id):
        with self.lock:
            return self.current_state.get(delivery_id)

    def get_history(self, delivery_id):
        with self.lock:
            return self.history.get(delivery_id, [])

    def list_deliveries(self):
        with self.lock:
            return list(self.current_state.values())

    def get_inactive_agents(self, timeout_seconds=10):
        with self.lock:
            now = datetime.now()
            inactive = []

            for agent_id, last_seen in self.agent_last_seen.items():
                if now - last_seen > timedelta(seconds=timeout_seconds):
                    inactive.append(agent_id)

            return inactive

    def get_metrics(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            throughput = self.total_events / elapsed if elapsed > 0 else 0

            return {
                "total_events": self.total_events,
                "uptime_seconds": round(elapsed, 2),
                "throughput_events_per_sec": round(throughput, 2),
                "active_deliveries": len(self.current_state),
                "known_agents": len(self.agent_last_seen),
            }