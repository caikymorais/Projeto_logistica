import random
import socket
import time

from protocol import encode_message, decode_lines, make_status_message

HOST = "127.0.0.1"
PORT = 5000

AGENT_ID = "veiculo_01"
DELIVERY_ID = "entrega_001"

STATUSES = [
    "coletada",
    "em_centro_distribuicao",
    "em_rota",
    "atrasada",
    "entregue",
]


def run_agent():
    seq = 1
    lat = -3.7319
    lon = -38.5267
    buffer = ""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        print(f"[AGENTE] conectado em {HOST}:{PORT}")

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

            client.sendall(encode_message(msg))
            print(f"[ENVIADO] {msg}")

            data = client.recv(4096)
            buffer += data.decode("utf-8")
            messages, buffer = decode_lines(buffer)

            for message in messages:
                print(f"[RESPOSTA] {message}")

            seq += 1
            time.sleep(2)


if __name__ == "__main__":
    run_agent()