import socket
import threading

PROXY_HOST = '127.0.0.1'
PORT = 8888
WEB_SERVER_HOST = '127.0.0.1'
WEB_SERVER_PORT = 8080
ALLOWED_HOST = 'localhost'
ALLOWED_PORT = 8080

def handle_client(client_socket, client_address):
    request = client_socket.recv(32768).decode('utf-8')
    parts = request.split("\r\n", 1)
    request_line = parts[0]
    headers = parts[1] if len(parts) > 1 else ""

    try:
        method, uri, http_version = request_line.split()
    except ValueError:
        client_socket.close()
        return

    if uri.startswith("http://"):
    # Remove the "http://" prefix and split the rest by "/", getting the first part as host_port
        uri_without_scheme = uri[7:]  # Remove "http://"
        parts = uri_without_scheme.split('/', 1)
        host_port = parts[0]
        relative_path = '/' + parts[1] if len(parts) > 1 else '/'

        # Now split host_port by ":" to separate host and port
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            port = int(port)  # Convert port to integer
        else:
            host = host_port
            port = WEB_SERVER_PORT  # Default port if not specified

    else:
        host = None
        port = None


    port = int(port) if port else None

    if host == ALLOWED_HOST and port == ALLOWED_PORT:
        print(f"Proxy: Connection from {client_address}")
        print(f"Proxy: Allowed request received:\n{request}")

        new_request_line = f"{method} {relative_path} {http_version}"
        host_header = f"Host: {host}:{port}\r\n"
        new_request = new_request_line + "\r\n" + host_header + headers

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as web_socket:
                web_socket.connect((host, port))
                print(f"Proxy: Forwarding request to {host}:{port}")
                web_socket.sendall(new_request.encode('utf-8'))

                while True:
                    response = web_socket.recv(32768)
                    if not response:
                        break
                    client_socket.sendall(response)
        except Exception as e:
            print(f"Proxy: Error connecting to {host}:{port}: {e}")
            client_socket.sendall(f"{http_version} 502 Bad Gateway\r\nContent-Type: text/html\r\n\r\nBad Gateway".encode('utf-8'))
    else:
        # Don't print details for disallowed requests
        error_response = (
            f"HTTP/1.1 403 Forbidden\r\n"
            "Content-Type: text/html\r\n"
            "Content-Length: 9\r\n\r\n"
            "Forbidden"
        )
        client_socket.sendall(error_response.encode("utf-8"))

    client_socket.close()

# Main function to start the proxy server
def start_proxy_server(host, port):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((host, port))
    proxy_socket.listen(100)
    print(f"Proxy server started on {host}:{port}")

    while True:
        client_socket, client_address = proxy_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.daemon = True
        client_handler.start()

start_proxy_server(PROXY_HOST,PORT)  # Start the proxy server on port 8888
