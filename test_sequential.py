import socket
import time

HOST = "127.0.0.1"
PORT = 9090

TEST_CLIENTS = [
    {
        "name": "Client-1",
        "messages": ["first message from client 1", "echo check", "QUIT"],
    },
    {"name": "Client-2", "messages": ["hello from client 2", "QUIT"]},
    {
        "name": "Client-3",
        "messages": ["testing data flow", "another string", "QUIT"],
    },
    {"name": "Client-4", "messages": ["distributed systems lab", "QUIT"]},
    {"name": "Client-5", "messages": ["final client message", "goodbye", "QUIT"]},
]


def receive_line(sock: socket.socket) -> str:
    """Reads from the socket until a full '\n'-terminated line is received."""
    buffer = ""
    while "\n" not in buffer:
        chunk = sock.recv(1024)
        if not chunk:
            raise ConnectionResetError("Server closed the connection unexpectedly.")
        buffer += chunk.decode("utf-8")
    return buffer.rstrip("\r\n")


def run_sequential_test():
    for client_data in TEST_CLIENTS:
        client_name = client_data["name"]
        print(f"\n=== Starting {client_name} ===")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))

        try:
            for msg in client_data["messages"]:
                print(f"[{client_name} ->] {msg}")
                sock.sendall(f"{msg}\n".encode("utf-8"))

                response = receive_line(sock)
                print(f"[{client_name} <-] {response}")

                if msg == "QUIT":
                    break

                time.sleep(0.3)
        finally:
            sock.close()
            print(f"=== {client_name} finished, socket closed ===")

        # Small pause so the server has fully released the previous connection
        # before the next client connects.
        time.sleep(0.5)


if __name__ == "__main__":
    run_sequential_test()
