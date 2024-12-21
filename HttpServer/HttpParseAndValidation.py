def parse_request(request):
    lines = request.split("\r\n")
    request_line = lines[0]
    method, uri, _ = request_line.split()
    
    if method != "GET":
        return 501, "Not Implemented"
    
    try:
        size = int(uri.strip("/"))
        if size < 100 or size > 20000:
            return 400, "Bad Request"
        return 200, size
    except ValueError:
        return 400, "Bad Request"
