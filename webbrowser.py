import sys
import ssl
import socket
import tkinter

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

class Browser:
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.SCROLL_STEP = 100
        self.scroll = 0
        self.HSTEP = 13
        self.VSTEP = 18
        
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=self.WIDTH,
            height=self.HEIGHT
        )
        self.canvas.pack()
        self.window.bind("<Down>", self.scrolldown)

    def scrolldown(self, e):
        self.scroll += self.SCROLL_STEP
        self.render()

    def render(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + self.HEIGHT: continue
            if y + self.VSTEP < self.scroll: continue
            self.canvas.create_text(x, y-self.scroll, text=c)
        
    def layout(self, text):
        
        x, y = self.HSTEP, self.VSTEP
        self.display_list = []
        for c in text:
            self.display_list.append((x,y,c))
            x += self.HSTEP  # keep move right
            if x >= self.WIDTH - self.HSTEP:
                y += self.VSTEP  # next line (move down)
                x = self.HSTEP   # reset to left
        self.render()

def stripoutUrl(url: str) -> Url:
    assert url.find("://")!=-1, "URL should include ://"
    scheme, url = url.split("://", 1)
    assert scheme in ["http", "https"], "Unknown scheme {}".format(scheme)

    port = 80 if scheme == "http" else 443
    host, path = url.split("/", 1)
    path = "/" + path
    
    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)
    return Url(scheme, host, port, path)
    
def request(url: Url):
    # Connect
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    s.connect((url.host, url.port))
    if url.scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=url.host)

    # Request
    request_path = f"GET {url.path} HTTP/1.0\r\n"
    request_host = f"Host: {url.host}\r\n\r\n"
    print(f"{request_path}{request_host}")
    s.send(f"{request_path}{request_host}".encode("utf8"))

    # Parse Version / Status / Explanation
    response = s.makefile("r", encoding="latin1", newline="\r\n")
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

def show(body):
    start_idx = body.find("<body")
    end_idx = body.find("/body>")
    in_angle = False
    for c in body[start_idx:end_idx]:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            print(c, end="")

def lex(body):
    text = ""
    in_angle = False
    for c in body:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            text += c
    return text


if __name__ == "__main__":

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
                print(redirectResponse)
                break
    else:        
        print(response)
    
    # Draw into window
    browser = Browser()
    content = lex(response.body)
    browser.layout(content)
    tkinter.mainloop()
