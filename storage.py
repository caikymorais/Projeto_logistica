from collections import defaultdict
from datetime import datetime


class Storage:
    def __init__(self):
        self.current_state = {}
        self.history = defaultdict(list)
        self.last_seq = {}
        self.agent_last_seen = {}

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
        delivery_id = event["delivery_id"]
        self.current_state[delivery_id] = event
        self.history[delivery_id].append(event)
        self.update_agent_seen(event["agent_id"])

    def get_status(self, delivery_id):
        return self.current_state.get(delivery_id)

    def get_history(self, delivery_id):
        return self.history.get(delivery_id, [])

    def list_deliveries(self):
        return list(self.current_state.values())