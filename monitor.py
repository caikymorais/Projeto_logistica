import socket

from protocol import encode_message, decode_lines, make_query_status, make_query_history

HOST = "127.0.0.1"
PORT = 5000


def send_and_receive(message):
    buffer = ""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        client.sendall(encode_message(message))

        data = client.recv(4096)
        buffer += data.decode("utf-8")
        messages, buffer = decode_lines(buffer)

        return messages


def main():
    while True:
        print("\n1 - Consultar estado atual")
        print("2 - Consultar histórico")
        print("3 - Listar entregas")
        print("0 - Sair")

        option = input("Escolha: ").strip()

        if option == "1":
            delivery_id = input("Delivery ID: ").strip()
            responses = send_and_receive(make_query_status(delivery_id))
            print(responses)

        elif option == "2":
            delivery_id = input("Delivery ID: ").strip()
            responses = send_and_receive(make_query_history(delivery_id))
            print(responses)

        elif option == "3":
            responses = send_and_receive({"type": "list_deliveries"})
            print(responses)

        elif option == "0":
            break


if __name__ == "__main__":
    main()