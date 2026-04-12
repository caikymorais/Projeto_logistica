import json
from datetime import datetime


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def make_status_message(agent_id, delivery_id, seq, status, latitude, longitude):
    return {
        "type": "status_update",
        "agent_id": agent_id,
        "delivery_id": delivery_id,
        "seq": seq,
        "timestamp": now_iso(),
        "status": status,
        "latitude": latitude,
        "longitude": longitude,
    }


def make_query_status(delivery_id):
    return {
        "type": "query_status",
        "delivery_id": delivery_id,
        "timestamp": now_iso(),
    }


def make_query_history(delivery_id):
    return {
        "type": "query_history",
        "delivery_id": delivery_id,
        "timestamp": now_iso(),
    }


def make_ack(message, detail="ok"):
    return {
        "type": "ack",
        "timestamp": now_iso(),
        "detail": detail,
        "message": message,
    }


def make_error(detail):
    return {
        "type": "error",
        "timestamp": now_iso(),
        "detail": detail,
    }


def encode_message(message):
    return (json.dumps(message) + "\n").encode("utf-8")


def decode_lines(buffer):
    parts = buffer.split("\n")
    complete = parts[:-1]
    remaining = parts[-1]
    messages = []

    for line in complete:
        line = line.strip()
        if not line:
            continue
        messages.append(json.loads(line))

    return messages, remaining