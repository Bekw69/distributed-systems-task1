import argparse
import socket
import sys


def receive_line(sock: socket.socket) -> str:
    """Reads characters from the socket until a complete line ending with '\n' is received."""
    buffer = ""
    while "\n" not in buffer:
        chunk = sock.recv(1024)
        if not chunk:
            raise ConnectionResetError(
                "Connection closed by the server before receiving a full line."
            )
        buffer += chunk.decode("utf-8")
    return buffer.rstrip("\r\n")


def run_client(host: str, port: int) -> None:
    """Connects to the server and manages interactive message exchange."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((host, port))
        print(f"[+] Connected to server at {host}:{port}")
        print("[+] Type your message and press Enter. Send 'QUIT' to disconnect.\n")

        while True:
            # Read input from the terminal
            message = input("Client > ").strip()
            if not message:
                continue

            # Ensure newline delimiter matches protocol requirements
            payload = f"{message}\n".encode("utf-8")
            client_socket.sendall(payload)

            # Receive the response
            response = receive_line(client_socket)
            print(f"Server > {response}")

            if message == "QUIT":
                print("[+] Session terminated gracefully.")
                break

    except ConnectionRefusedError:
        print(
            f"[-] Error: Could not connect to {host}:{port}. Is the server running?"
        )
    except (ConnectionResetError, BrokenPipeError) as err:
        print(f"[-] Network connection lost: {err}")
    except KeyboardInterrupt:
        print("\n[-] Interrupted by user. Closing socket...")
    finally:
        client_socket.close()
        print("[+] Client socket closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP Echo+ Client")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Server host IP (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9090,
        help="Server port (default: 9090)",
    )

    args = parser.parse_args()
    run_client(args.host, args.port)