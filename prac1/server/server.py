import socket
import os

port = int(os.getenv("PORT", "8080"))


def handle_request(request, conn):
    parts = request.split(" ", 2)
    operation = parts[0]

    # TODO: stop using if else statements
    if operation == "UPLOAD":
        filename = parts[1]
        content = parts[2]

        # TODO: save file in bytes (if possible)
        with open(filename, "w") as f:
            f.write(content)
        return "File uploaded successfully"

    elif operation == "DOWNLOAD":
        filename = parts[1]

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                content = f.read()
            conn.sendall(content)
            return ""
        else:
            return "File not found"

    elif operation == "LIST":
        files = os.listdir(".")
        return " ".join(files)

    else:
        return "Invalid operation"


def start_server(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", port))  # Bind to all available interfaces
        s.listen(5)
        print(f"Server started and listening on port {port}")

        while True:
            conn, addr = s.accept()
            try:
                request = conn.recv(1024).decode()
                response = handle_request(request, conn)
                if response:
                    conn.sendall(response.encode())
                print(f"Request: {request} | Response: {response}")
            except Exception as e:
                conn.sendall(f"Error processing request: {e}".encode("utf-8"))
                print(f"Request: {request} | Error processing request: {e}")
            finally:
                conn.close()
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        s.close()


if __name__ == "__main__":
    start_server(port)
