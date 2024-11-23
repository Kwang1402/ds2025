import socket
import os
from typing import Dict, Callable

ip = os.getenv("IP", "localhost")
port = int(os.getenv("PORT", 8080))


def send_request(request):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.sendall(request.encode())

        response = s.recv(1024).decode()
        s.close()
        return response
    except ConnectionRefusedError:
        return "Connection refused. Make sure the server is running."
    except socket.error as e:
        return f"Socket error: {e}"
    finally:
        s.close()


def upload():
    filename = input("Enter filename to upload: ").strip()

    if not os.path.exists(filename):
        return "File does not exist"

    with open(filename, "r") as file:
        content = file.read()

    # TODO: upload file in bytes (if possible)
    request = f"UPLOAD {filename} {content}"
    response = send_request(request)

    return response


def download():
    filename = input("Enter filename to download: ").strip()
    request = f"DOWNLOAD {filename}"
    response = send_request(request)

    if "File not found" not in response:
        with open(filename, "wb") as f:
            f.write(response.encode())
        response = f"File {filename} downloaded successfully."

    return response


def list():
    request = "LIST"
    response = send_request(request)

    return response


if __name__ == "__main__":
    options: Dict[str, Callable] = {
        "UPLOAD": upload,
        "DOWNLOAD": download,
        "LIST": list,
    }
    while True:
        try:
            operation = (
                input("Enter operation (UPLOAD, DOWNLOAD, LIST) or QUIT to exit: ")
                .strip()
                .upper()
            )
            if operation == "QUIT":
                break

            if operation not in options:
                print("Invalid operation")
                continue
            else:
                response = options[operation]()
                print("Response from server:", response)

        except Exception as e:
            print(f"Error: {e}")
            continue
