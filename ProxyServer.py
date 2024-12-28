import socket
import threading
import time

PORT = 8888
WEB_SERVER_HOST = '127.0.0.1'
WEB_SERVER_PORT = 8080

def handle_client(client_socket):
    try:
        # Receive the request from the client
        request = client_socket.recv(1024).decode()
        print(f"Received request: {request}")

        # Extract the first line of the request
        lines = request.split("\r\n")
        first_line = lines[0].split()
        method = first_line[0]
        url = first_line[1]

        # Handle CONNECT method
        if method == "CONNECT":
            client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                client_socket.sendall(data)
            client_socket.close()
            return

        # Check if the method is GET
        if method != "GET":
            response = "HTTP/1.0 501 Not Implemented\r\n\r\nNot Implemented"
            client_socket.sendall(response.encode())
            client_socket.close()
            return

        # Extract the URI and check its size
        uri = url.split("://")[1].split("/", 1)[1]
        try:
            size = int(uri.strip("/"))
            if size > 9999:
                response = "HTTP/1.0 414 Request-URI Too Long\r\n\r\nRequest-URI Too Long"
                client_socket.sendall(response.encode())
                client_socket.close()
                return
        except ValueError:
            pass

        # Create a relative URL and add the Host header
        relative_url = "/" + uri
        host_header = f"Host: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}\r\n"

        # Forward the request to the web server
        web_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            web_server_socket.connect((WEB_SERVER_HOST, WEB_SERVER_PORT))
            print("Web server is reachable.")
        except socket.error:
            print("Web server is not reachable.")
            response = "HTTP/1.0 404 Not Found\r\n\r\nNot Found"
            client_socket.sendall(response.encode())
            client_socket.close()
            return

        web_server_request = f"{method} {relative_url} HTTP/1.0\r\n{host_header}\r\n"
        print(f"Request to web server:\n{web_server_request}")
        web_server_socket.sendall(web_server_request.encode())

        # Receive the response from the web server and forward it to the client
        while True:
            response = web_server_socket.recv(4096)
            if len(response) > 0:
                client_socket.sendall(response)
            else:
                break

        web_server_socket.close()
        client_socket.close()
    except Exception as e:
        print(f"Error handling client: {e}")
        client_socket.close()

# Main function to start the proxy server
def start_proxy_server(port):
    # Create a socket to listen for incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(100)
    print(f"Proxy server started on 127.0.0.1:{port}")

    # Handle incoming connections with threading
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        
        # Create a new thread to handle the client
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

start_proxy_server(PORT)  # Start the proxy server on port 8888