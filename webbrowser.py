import sys
import ssl
import socket
import tkinter
import tkinter.font

HSTEP, VSTEP = 13, 18
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
        self.display_list = []
        self.text = ""

        self.window = tkinter.Tk()
        
        self.window.title("Yu-Ching Hsu's Browser")
        self.canvas = tkinter.Canvas(
            self.window, 
            width=self.WIDTH,
            height=self.HEIGHT
        )
        self.canvas.pack(expand=True, fill="both")
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Configure>", self.windowresize)
        self.window.bind("+", self.zoomin)
        self.window.bind("-", self.zoomout)

        self.gif_grinFace = tkinter.PhotoImage(file='resize_griningFace.gif')

    def scrolldown(self, e):
        self.scroll += self.SCROLL_STEP
        self.render()

    def scrollup(self, e):
        self.scroll -= self.SCROLL_STEP
        self.render()

    def windowresize(self, e):
        self.WIDTH = e.width
        self.HEIGHT = e.height
        self.layout(self.text)
    
    def zoomin(self, e):
        # self.font.size += 2
        self.layout(self.text)

    def zoomout(self, e):
        # self.font.size -= 2
        self.layout(self.text)

    def render(self):
        self.canvas.delete("all")
        for self.x, self.y, c in self.display_list:
            if self.y > self.scroll + self.HEIGHT: continue
            if self.y + VSTEP < self.scroll: continue
            if c == ':)':
                self.canvas.create_image(self.x, self.y-self.scroll, image=self.gif_grinFace)
                continue
            self.canvas.create_text(self.x, self.y-self.scroll, text=c, font=self.font, anchor='nw')
            self.x += self.font.measure(c)
    
    def layout(self, tokens):
        self.display_list = Layout(tokens).display_list

class Layout:
    def __init__(self, tokens):
        self.display_list = []
        self.x, self.y = HSTEP, VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16
        for tok in tokens:
            self.token(tok)

    def text(self, text):
        self.font = tkinter.font.Font(
            family="Times",
            size=16,
            weight = self.weight,
            slant = self.style
        )
        for word in text.split():
            w = self.font.measure(word)
            if self.x + w >= self.WIDTH - HSTEP:
                self.y += self.font.metrics("linespace") * 1.2
                self.x = HSTEP
            self.display_list.append((self.x, self.y, word, self.font))
            self.x += w + self.font.measure(" ")

    def token(self, tok):
        if isinstance(tok, Text):
            self.text(tok)
        elif tok.tag == "i": self.style = "italic"
        elif tok.tag == "/i": self.style = "roman"
        elif tok.tag == "b": self.weight = "bold"
        elif tok.tag == "/b": self.weight = "normal"
        self.render()

class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag

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

def getDivident(body):
    tag = "DIVIDEND_AND_YIELD-value"
    start_idx = body.find(tag) + len(tag)
    in_angle = False
    for c in body[start_idx:start_idx+100]:
        if c == ">":
            in_angle = True
        elif c == "<":
            in_angle = False
        elif in_angle:
            print(c, end="")

def lex(body):
    out = []
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
            if text: out.append(Text(text))
            text = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(text))
            text = ""
        else:
            text += c
    if not in_tag and text:
        out.append(Text(text))
    return out


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
                response = redirectResponse
                break   
    print(response)
    print("-"*30)
    # getDivident(response.body)
    # # Draw into window
    browser = Browser()
    content = lex(response.body)
    
    browser.layout(content)
    tkinter.mainloop()
