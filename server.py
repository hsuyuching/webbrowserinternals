import socket
ENTRIES = [ 'Pavel was here' ]

def main():
    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP,
    )
    s.bind(('', 8000))
    s.listen()

    while True:
        conx, addr = s.accept()
        handle_connection(conx) 

def handle_connection(conx):
    req = conx.makefile("rb")
    reqline = req.readline().decode('utf8')
    method, url, version = reqline.split(" ", 2)
    assert method in ["GET", "POST"]
    body = ""
    headers = {}
    for line in req:
        line = line.decode('utf8')
        if line == '\r\n': break
        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()
    
    if 'content-length' in headers:
        length = int(headers['content-length'])
        body = req.read(length).decode('utf8')
    else:
        body = None

    body = handle_request(method, url, headers, body)
    response = "HTTP/1.0 200 OK\r\n"
    response += "Content-Length: {}\r\n".format(len(body))
    response += "\r\n" + body
    conx.send(response.encode('utf8'))
    conx.close()

def handle_request(method, url, headers, body):
    if method == 'POST':
        params = form_decode(body)
        if url == '/add':
            return add_entry(params)
        else:
            return show_comments()
    else:
        if url == '/comment.js':
            with open("comment.js") as f:
                return f.read()
        elif url == '/comment.css':
            with open("comment.css") as f: return f.read()
        else:
            return show_comments()

def add_entry(params):
    if 'guest' in params and len(params['guest']) <= 100:
        ENTRIES.append(params["guest"])
    return show_comments()

def show_comments():
    out = "<!doctype html>"
    out += "<script src=/comment.js></script>"
    out += "<link rel='stylesheet' href='/comment.css'>"

    # entries
    for entry in ENTRIES:
        out += "<p>" + entry + "</p>"
    # form
    out += "<form action=add method=post>"
    out +=   "<p><input name=guest value='value'></p>"
    out +=   "<p><button>Sign the book!</button></p>"
    out += "</form>"

    # errors
    out += '<p id="errors">No errors</p>'

    return out

def form_decode(body):
    params = {}
    for field in body.split("&"):
        name, value = field.split("=", 1)
        params[name] = value.replace("%20", " ")
    return params

if __name__ == "__main__":
    main()