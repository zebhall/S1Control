import socket


def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Listening on {host}:{port}")

        while True:
            connection, address = server_socket.accept()
            print(f"Connection from {address}")

            data = connection.recv(4096)  # Adjust the buffer size as needed
            while data:
                print(data.decode("utf-8"))
                data = connection.recv(4096)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    host = "192.168.137.38"  # Replace with the actual IP address
    port = 57129  # Replace with the actual port number

    start_server(host, port)
