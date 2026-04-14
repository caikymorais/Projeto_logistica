import random
import socket
import sys
import time

from protocol import encode_message, decode_lines, make_status_message

HOST = "127.0.0.1"
PORT = 5000

AGENT_ID = sys.argv[1] if len(sys.argv) > 1 else "veiculo_01"
DELIVERY_ID = sys.argv[2] if len(sys.argv) > 2 else "entrega_001"
INTERVAL = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0

STATUSES = [
    "coletada",
    "em_centro_distribuicao",
    "em_rota",
    "atrasada",
    "entregue",
]


def run_agent():
    seq = 1
    lat = -1.3617
    lon = -48.2442
    buffer = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        print(f"[AGENTE {AGENT_ID}] conectado em {HOST}:{PORT}")

        
        for status in STATUSES:
            lat += random.uniform(-0.01, 0.01)
            lon += random.uniform(-0.01, 0.01)

            msg = make_status_message(
                AGENT_ID,
                DELIVERY_ID,
                seq,
                status,
                round(lat, 6),
                round(lon, 6),
            )

            start = time.time()
            client.sendall(encode_message(msg))

            data = client.recv(4096).decode("utf-8")
            msgs, remaining = decode_lines(data)

            end = time.time()
            response_time_ms = (end - start) * 1000

            print(f"[{AGENT_ID}] enviado seq={seq} status={status}")
            print(f"[{AGENT_ID}] tempo de resposta: {response_time_ms:.2f} ms")

            for response in msgs:
                print(f"[{AGENT_ID}] resposta: {response}")

            seq += 1
            time.sleep(INTERVAL)

        print(f"[AGENTE {AGENT_ID}] finalizou envio de eventos")


if __name__ == "__main__":
    run_agent()