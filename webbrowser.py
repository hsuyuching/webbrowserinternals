import sys
import ssl
import socket


class Url:
    scheme: str
    host: str
    port: int
    path: str
    def __str__(self) -> str:
        return f"[Scheme: {self.scheme}]\n[Host: {self.host}]\n[port: {self.port}]\n[path: {self.path}]"

def request(url):
    scheme, url = url.split("://", 1)
    assert scheme in ["http", "https"], "Unknown scheme {}".format(scheme)
    port = 80 if scheme == "http" else 443

    
    s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
    if url.find("/") != -1:
        host, path = url.split("/", 1)
        path = "/" + path
    else:
        host = url
        path = ""
    if scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)
        url = url = url[len("https://"):]
    else:
        url = url[len("http://"):]
    
    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)
    
    s.connect((host, port))
    req_header = "GET "+ path +" HTTP/1.0\r\n" + "Host: " + host + "\r\n\r\n"
    req_header = str.encode(req_header)
    s.send(req_header)
    response = s.makefile("r", encoding="latin1", newline="\r\n")

    statusline = response.readline()
    version, status, explanation = statusline.split(" ", 2)
    assert status == "200", "{}: {}".format(status, explanation)

    headers = {}
    while True:
        line = response.readline()
        if line == "\r\n": break
        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()

    body = response.read()
    s.close()
    return headers, body

def show(body):
    in_angle = False
    for c in body:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            print(c, end="")

if __name__ == "__main__":
    request_url = sys.argv[1]
    headers, body = request(request_url)
    print(headers)
    # show(body)
