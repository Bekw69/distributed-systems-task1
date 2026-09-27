import argparse
from datetime import datetime
import logging
import socket
import sys

# Configure logging format and level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def handle_client(client_socket: socket.socket, client_address: tuple) -> None:
    """Handles an active client session implementing the Echo+ protocol."""
    logging.info(f"Client connected: {client_address[0]}:{client_address[1]}")

    buffer = ""
    try:
        while True:
            # Read incoming data up to 1024 bytes
            data = client_socket.recv(1024)

            # 1. Detect graceful client closure (EOF)
            if not data:
                logging.warning(
                    f"Client {client_address} closed connection unexpectedly."
                )
                break

            # 2. Handle malformed data (non UTF-8 payload)
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                logging.error(f"Malformed bytes received from {client_address}")
                error_response = (
                    "ERROR: Malformed data (UTF-8 required)\n".encode("utf-8")
                )
                client_socket.sendall(error_response)
                continue

            buffer += text

            # Process complete lines delimited by '\n'
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip("\r")

                # 3. Handle QUIT command
                if line.strip() == "QUIT":
                    logging.info(
                        f"Client {client_address} requested termination (QUIT)."
                    )
                    client_socket.sendall(b"BYE\n")
                    return

                # 4. Echo+ response: [timestamp] UPPERCASE
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                response_text = f"[{timestamp}] {line.upper()}\n"

                logging.info(f"Received: '{line}' -> Sent: '{response_text.strip()}'")
                client_socket.sendall(response_text.encode("utf-8"))

    except ConnectionResetError:
        # 5. Handle abrupt connection drop (e.g. process killed)
        logging.error(f"Connection reset by peer: {client_address}")
    finally:
        client_socket.close()
        logging.info(f"Connection with {client_address} closed.")


def run_server(host: str, port: int) -> None:
    """Sets up the server socket and processes incoming connections sequentially."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Enable immediate port reuse after termination (bypasses TIME_WAIT)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, port))
    except OSError as err:
        logging.critical(f"Failed to bind socket to {host}:{port}: {err}")
        server_socket.close()
        sys.exit(1)

    server_socket.listen(5)
    logging.info(f"Server is listening on {host}:{port}")

    try:
        while True:
            # Blocks until an incoming connection arrives
            client_socket, client_address = server_socket.accept()
            handle_client(client_socket, client_address)
    except KeyboardInterrupt:
        logging.info("Server shutdown requested via keyboard interrupt.")
    finally:
        server_socket.close()
        logging.info("Server socket released.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP Echo+ Server")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9090,
        help="Port to listen on (default: 9090)",
    )

    args = parser.parse_args()
    run_server(args.host, args.port)