# TCP Echo+ Lab — Run Instructions

## Requirements
- Python 3.x
- Standard library only (`socket`, `argparse`, `logging`, `datetime`) — no extra installs needed

## Files
- `server.py` — TCP server implementing the Echo+ protocol
- `client.py` — interactive TCP client
- `test_sequential.py` — automated test that connects 5 clients one after another

## 1. Start the server
```
python server.py --host 127.0.0.1 --port 9090
```
Both `--host` and `--port` are optional (defaults shown above). The server logs every connection, message, and error to the console with a timestamp.

## 2. Connect with the interactive client
In a separate terminal:
```
python client.py --host 127.0.0.1 --port 9090
```
Type a message and press Enter — the server echoes it back in uppercase with a receipt timestamp. Type `QUIT` to close the connection gracefully.

## 3. Run the automated 5-client test
With the server still running, in another terminal:
```
python test_sequential.py
```
This connects `Client-1` through `Client-5` one after another (not concurrently), sends each client's scripted messages, prints the server's replies, and closes each socket cleanly before moving to the next client. This satisfies the "test with 5 clients connecting sequentially" requirement.

## Protocol summary (Echo+)
- Messages are UTF-8 text terminated with `\n`.
- Server response format: `[YYYY-MM-DD HH:MM:SS] <MESSAGE IN UPPERCASE>\n`
- `QUIT` → server replies `BYE\n`, then closes the connection and returns to accepting new clients.

## Error handling implemented
| Scenario | Where | Behavior |
|---|---|---|
| Port already in use | `server.py` (`bind`) | Logs a critical error and exits (`sys.exit(1)`) instead of crashing with a traceback |
| Client disconnects abruptly (EOF) | `server.py` | Empty `recv()` is detected, logged as a warning, connection cleaned up |
| Connection reset by peer | both | `ConnectionResetError` caught and logged/printed |
| Broken pipe (server died mid-send) | `client.py` | `BrokenPipeError` caught, friendly message shown |
| Non-UTF-8 / malformed bytes | `server.py` | Caught with `UnicodeDecodeError`, replies `ERROR: Malformed data (UTF-8 required)` and keeps the connection open |
| Server not running | `client.py` | `ConnectionRefusedError` caught, friendly message shown |
| Ctrl+C during operation | both | `KeyboardInterrupt` caught, sockets closed cleanly |
