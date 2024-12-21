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
