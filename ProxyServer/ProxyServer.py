import socket
import threading

def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    print(f"Received request: {request}")
    # Handle the request
    client_socket.close()

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', port))
    server.listen(5)
    print(f"Server running on port {port}")
    
    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

start_server(8888)  # Example port
