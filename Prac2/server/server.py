import xmlrpc.server
import os

port = int(os.getenv("PORT", "8080"))


def upload(filename, content):
    with open(filename, "wb") as f:
        f.write(content.data)
    return "File uploaded successfully"


def download(filename):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            content = f.read()
        return content
    else:
        return "File not found"


def list():
    files = os.listdir(".")
    return " ".join(files)


def start_server(port):
    server = xmlrpc.server.SimpleXMLRPCServer(("0.0.0.0", port), allow_none=True)
    print(f"Server started and listening on port {port}")
    server.register_function(upload, "upload")
    server.register_function(download, "download")
    server.register_function(list, "list")
    server.serve_forever()


if __name__ == "__main__":
    start_server(port)
