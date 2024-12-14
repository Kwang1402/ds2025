from mpi4py import MPI
import os


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def server():
    print(f"[Server] Running on process {rank}. Waiting for requests...")

    file_directory = "server"
    os.makedirs(file_directory, exist_ok=True)

    while True:
        request = comm.recv(source=MPI.ANY_SOURCE, tag=0)
        operation = request.get("operation")
        client_rank = request.get("source")

        print(f"[Server] Received {operation} request from rank {client_rank}")

        if operation == "UPLOAD":
            filename = request["filename"]
            content = request["content"]

            with open(os.path.join(file_directory, filename), "wb") as f:
                f.write(content)
            response = f"File '{filename}' uploaded successfully."

        elif operation == "DOWNLOAD":
            filename = request["filename"]
            filepath = os.path.join(file_directory, filename)

            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    content = f.read()
                response = content
            else:
                response = "File not found"

        elif operation == "LIST":
            files = os.listdir(file_directory)
            response = files if files else "No files available."

        elif operation == "EXIT":
            print(f"[Server] Shutting down as requested by rank {client_rank}.")
            break

        else:
            response = "Invalid operation."

        comm.send(response, dest=client_rank, tag=0)


def client():
    client_directory = f"client{rank}"
    os.makedirs(client_directory, exist_ok=True)

    def send_request(request):
        comm.send(request, dest=0, tag=0)
        response = comm.recv(source=0, tag=0)
        return response

    def upload():
        filename = input(
            "Enter filename to upload (must be in client directory): "
        ).strip()
        filepath = os.path.join(client_directory, filename)

        if not os.path.exists(filepath):
            return f"File '{filename}' does not exist in directory {client_directory}."

        with open(filepath, "rb") as file:
            content = file.read()

        request = {
            "operation": "UPLOAD",
            "filename": filename,
            "content": content,
            "source": rank,
        }
        response = send_request(request)
        return response

    def download():
        filename = input("Enter filename to download: ").strip()
        request = {"operation": "DOWNLOAD", "filename": filename, "source": rank}
        response = send_request(request)

        if isinstance(response, bytes):
            filepath = os.path.join(client_directory, filename)
            with open(filepath, "wb") as f:
                f.write(response)
            response = f"File '{filename}' downloaded successfully and saved to {client_directory}."

        return response

    def list_files():
        request = {"operation": "LIST", "source": rank}
        response = send_request(request)
        if isinstance(response, list):
            return " ".join(response)
        return response

    options = {"UPLOAD": upload, "DOWNLOAD": download, "LIST": list_files}

    while True:
        try:
            operation = (
                input(
                    f"[Client #{rank}] Enter operation (UPLOAD, DOWNLOAD, LIST) or QUIT to exit: "
                )
                .strip()
                .upper()
            )
            if operation == "QUIT":
                send_request({"operation": "EXIT", "source": rank})
                break

            if operation not in options:
                print("Invalid operation")
                continue
            else:
                response = options[operation]()
                print("Response from server:", response)
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    if rank == 0:
        server()
    else:
        client()
