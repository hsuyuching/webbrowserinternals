import sys
import ssl
import socket
import tkinter

import browser
import parse

import cProfile
from pstats import SortKey

class Url:
    scheme: str
    host: str
    port: int
    path: str
    def __init__(self, scheme, host, port, path):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.path = path

    def __str__(self) -> str:
        return f"[Scheme: {self.scheme}]\n[Host: {self.host}]\n[port: {self.port}]\n[path: {self.path}]"

class Response:
    http_version: str
    status: int
    explanation: str
    headers: {}
    body: str
    def __init__(self, http_version, status, explanation, headers, body):
        self.http_version = http_version
        self.status = status
        self.explanation = explanation
        self.headers = headers
        self.body = body

    def __str__(self) -> str:
        output = f"[Version: {self.http_version}]\n[Status: {self.status}]\n[Explanation: {self.explanation}]\n[Headers: "
        if len(self.headers) == 0:
            output += "None"
        for header in self.headers:
            output += f"\n\t({header}: {self.headers[header]})"
        return output + "]"

def stripoutUrl(url: str) -> Url:
    assert url.find("://")!=-1, "URL should include ://"
    scheme, url = url.split("://", 1)
    assert scheme in ["http", "https"], "Unknown scheme {}".format(scheme)

    port = 80 if scheme == "http" else 443
    # connect to form server
    if url.rsplit("/")[1] in ["submit", "add"]: 
        port = 8000

    host, path = url.split("/", 1)
    path = "/" + path
    
    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)
    return Url(scheme, host, port, path)
    
def request(url: Url, payload=None):
    method = "POST" if payload else "GET"
    # Connect
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    s.connect((url.host, url.port))
    if url.scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=url.host)

    # Request
    if method == "GET":
        request_path = f"GET {url.path} HTTP/1.0\r\n"
        request_host = f"Host: {url.host}\r\n\r\n"
        # print(f"{request_path}{request_host}")
        s.send(f"{request_path}{request_host}".encode("utf8"))
    else:
        body = "{} {} HTTP/1.0\r\n".format(method, url.path)
        body += "Host: {}\r\n".format(url.host)
        content_length = len(payload.encode("utf8"))
        body += "Content-Length: {}\r\n".format(content_length)
        body += "\r\n" + payload
        s.send(body.encode("utf8"))

    # Parse Version / Status / Explanation
    response = s.makefile("r", encoding="utf8", newline="\r\n")
    statusline = response.readline()
    version, status, explanation = statusline.split(" ", 2)
    status = int(status)

    # Parse Headers
    headers = {}
    while True:
        line = response.readline()
        if line == "\r\n": break
        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()

    # Parse Body
    body = response.read()
    s.close()

    return Response(version, status, explanation, headers, body)


def main():
    # Download a web page
    request_url = sys.argv[1]
    print("Provided URL: %s" %request_url)

    request_url = stripoutUrl(request_url)
    print("Parsed URL:")
    print(request_url)
    print("-"*30)

    response = request(request_url)
    if 300<= response.status < 400:
        for i in range(3):
            print("Redirect URL:\n" + response.headers["location"])
            redirectUrl = stripoutUrl(response.headers["location"])
            redirectResponse = request(redirectUrl)
            if redirectResponse.status == 200:
                response = redirectResponse
                break   
    print(response)
    print("-"*30)

    # Draw into window
    mybrowser = browser.Browser()
    mybrowser.load(request_url)
    tkinter.mainloop()

if __name__ == "__main__":
    main()
    # cProfile.run("main()", sort=SortKey.CUMULATIVE)
    

