import json
import socket

from protocol import (
    encode_message,
    decode_lines,
    make_query_status,
    make_query_history,
    make_list_deliveries,
    make_list_inactive_agents,
    make_metrics_query,
)

HOST = "127.0.0.1"
PORT = 5000


def send_and_receive(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        client.sendall(encode_message(message))

        data = client.recv(4096).decode("utf-8")
        messages, _ = decode_lines(data)
        return messages


def show_response(responses):
    for response in responses:
        print(json.dumps(response, indent=2, ensure_ascii=False))


def main():
    while True:
        print("\n=== MONITOR ===")
        print("1 - Consultar estado atual de uma entrega")
        print("2 - Consultar histórico de uma entrega")
        print("3 - Listar entregas")
        print("4 - Listar agentes inativos")
        print("5 - Ver métricas")
        print("0 - Sair")

        option = input("Escolha: ").strip()

        if option == "1":
            delivery_id = input("Delivery ID: ").strip()
            show_response(send_and_receive(make_query_status(delivery_id)))

        elif option == "2":
            delivery_id = input("Delivery ID: ").strip()
            show_response(send_and_receive(make_query_history(delivery_id)))

        elif option == "3":
            show_response(send_and_receive(make_list_deliveries()))

        elif option == "4":
            show_response(send_and_receive(make_list_inactive_agents()))

        elif option == "5":
            show_response(send_and_receive(make_metrics_query()))

        elif option == "0":
            break

        else:
            print("Opção inválida")


if __name__ == "__main__":
    main()