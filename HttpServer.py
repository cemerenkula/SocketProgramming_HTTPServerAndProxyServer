import socket
import threading
import argparse
import os

def parse_request(request):
    valid_methods = {"GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "TRACE", "CONNECT"}
    
    http_version = request.split()[2]

    lines = request.split("\r\n")
    request_line = lines[0]
    method, uri, _ = request_line.split()

    # Check if the method is valid
    if method not in valid_methods:
        return 400, "Bad Request"
    
    # Control for GET method
    if method != "GET":
        return 501, "Not Implemented"
    
    try:
        # Check if the URI is an integer
        size = int(uri.strip("/"))
        if size < 100 or size > 20000:
            return 400, "Bad Request"
        return 200, size
    except ValueError:
        # Handle non-integer URIs like favicon.ico
        if uri == "/favicon.ico":
            return 200, "Favicon request"
        return 400, "Bad Request"

def generate_response(status_code, content=None):
    if status_code == 200:
        body = f"<HTML><HEAD><TITLE>Response</TITLE></HEAD><BODY>{'O' * (content - 62)}</BODY></HTML>"
        headers = (
            f"HTTP/1.0 200 OK\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(body.encode())}\r\n\r\n"
        )
        response = headers + body
    elif status_code == 400:
        response = "HTTP/1.0 400 Bad Request\r\n\r\nBad Request"
    elif status_code == 501:
        response = "HTTP/1.0 501 Not Implemented\r\n\r\nNot Implemented"
    
    # Save the response to a file in the Responses folder
    os.makedirs("Responses", exist_ok=True)
    with open(os.path.join("Responses", "response.txt"), "w") as file:
        file.write(response)
    
    return response
    


# Function to handle client requests
def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Request received:\n{request}")

        # HTTP Response message
        parsed_URI = parse_request(request)
        print(f"Parsed request - Status code: {parsed_URI[0]}, Content: {parsed_URI[1]}")
        
        response = generate_response(parsed_URI[0], parsed_URI[1])
        print(f"Generated response: {response}")  # Print the response before sending
        
        raw_response = response.encode('utf-8')

        client_socket.sendall(raw_response)
        print(f"Sent response: {response}")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

# Main function to start the server
def start_server(port):
    # Create a socket to listen for incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(100)
    print(f"Server started on 127.0.0.1:{port}")

    # Handle incoming connections with threading
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        
        # Create a new thread to handle the client
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start an HTTP server.')
    parser.add_argument('port', type=int, help='Port number to start the server on')
    args = parser.parse_args()
    
    start_server(args.port)