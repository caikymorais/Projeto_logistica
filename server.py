import socket
import threading

from protocol import decode_lines, encode_message, make_ack, make_error
from storage import Storage

HOST = "127.0.0.1"
PORT = 5000
TIMEOUT_SECONDS = 10

storage = Storage()


def handle_message(message):
    msg_type = message.get("type")

    if msg_type == "status_update":
        agent_id = message.get("agent_id")
        delivery_id = message.get("delivery_id")
        seq = message.get("seq")

        if not agent_id or not delivery_id or seq is None:
            return make_error("mensagem incompleta")

        if not storage.is_new_message(agent_id, delivery_id, seq):
            return make_error("mensagem duplicada ou fora de ordem")

        storage.save_event(message)
        return make_ack("evento registrado com sucesso")

    elif msg_type == "query_status":
        delivery_id = message.get("delivery_id")
        return {
            "type": "query_status_response",
            "delivery_id": delivery_id,
            "data": storage.get_status(delivery_id),
        }

    elif msg_type == "query_history":
        delivery_id = message.get("delivery_id")
        return {
            "type": "query_history_response",
            "delivery_id": delivery_id,
            "data": storage.get_history(delivery_id),
        }

    elif msg_type == "list_deliveries":
        return {
            "type": "list_deliveries_response",
            "data": storage.list_deliveries(),
        }

    elif msg_type == "list_inactive_agents":
        return {
            "type": "list_inactive_agents_response",
            "timeout_seconds": TIMEOUT_SECONDS,
            "data": storage.get_inactive_agents(TIMEOUT_SECONDS),
        }

    elif msg_type == "query_metrics":
        return {
            "type": "query_metrics_response",
            "data": storage.get_metrics(),
        }

    return make_error("tipo de mensagem desconhecido")


def client_thread(conn, addr):
    print(f"[NOVA CONEXAO] {addr}")
    buffer = ""

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode("utf-8")
            messages, buffer = decode_lines(buffer)

            for message in messages:
                print(f"[RECEBIDO] {message}")
                response = handle_message(message)
                conn.sendall(encode_message(response))

    except Exception as e:
        print(f"[ERRO] conexao {addr}: {e}")
    finally:
        conn.close()
        print(f"[DESCONECTADO] {addr}")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"[SERVIDOR] escutando em {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client_thread, args=(conn, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    start_server()