import xmlrpc.client
import os
from typing import Dict, Callable

ip = os.getenv("IP", "localhost")
port = int(os.getenv("PORT", 8080))


def upload(server):
    filename = input("Enter filename to upload: ").strip()

    if not os.path.exists(filename):
        return "File does not exist"

    with open(filename, "rb") as file:
        content = file.read()

    response = server.upload(filename, content)

    return response


def download(server):
    filename = input("Enter filename to download: ").strip()
    content = server.download(filename)

    if content == "File not found":
        return content
    else:
        with open(filename, "wb") as f:
            f.write(content.data)
        return f"File {filename} downloaded successfully."


def list(server):
    files = server.list()
    return files


if __name__ == "__main__":
    server = xmlrpc.client.ServerProxy(f"http://{ip}:{port}/", allow_none=True)
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
                response = options[operation](server)
                print("Response from server:", response)

        except Exception as e:
            print(f"Error: {e}")
            continue
