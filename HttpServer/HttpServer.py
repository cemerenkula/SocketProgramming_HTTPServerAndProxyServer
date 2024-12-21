import socket
import threading
from HttpParseAndValidation import parse_request


# Define the server's address and port
HOST = '127.0.0.1'
PORT = 8080

def generate_response(status_code, content=None):
    if status_code == 200:
        body = f"<HTML><HEAD><TITLE>{content}</TITLE></HEAD><BODY>{'a ' * (content // 2)}</BODY></HTML>"
        headers = (
            f"HTTP/1.0 200 OK\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(body.encode())}\r\n\r\n"
        )
        return headers + body
    elif status_code == 400:
        return "HTTP/1.0 400 Bad Request\r\n\r\nBad Request"
    elif status_code == 501:
        return "HTTP/1.0 501 Not Implemented\r\n\r\nNot Implemented"
    
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
        
        client_socket.sendall(response.encode('utf-8'))
        print(f"Sent response: {response}")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

# Main function to start the server
def start_server():
    # Create a socket to listen for incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server started on {HOST}:{PORT}")

    # Handle incoming connections with threading
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        
        # Create a new thread to handle the client
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()