import sys
import ssl
import socket
import tkinter
import tkinter.font
import re

HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100

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
        self.scroll = 0
        self.text = ""

        self.window = tkinter.Tk()
        
        self.window.title("Yu-Ching Hsu's Browser")
        self.canvas = tkinter.Canvas(
            self.window, 
            width = WIDTH,
            height = HEIGHT
        )
        self.canvas.pack(expand=True, fill="both")
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Configure>", self.windowresize)
        self.window.bind("+", self.zoomin)
        self.window.bind("-", self.zoomout)

        self.gif_grinFace = tkinter.PhotoImage(file='resize_griningFace.gif')

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.render()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        self.render()

    def windowresize(self, e):
        global WIDTH
        global HEIGHT
        WIDTH = e.width
        HEIGHT = e.height
        self.layout(self.text)
    
    def zoomin(self, e):
        self.font.size += 2
        self.layout(self.text)

    def zoomout(self, e):
        self.font.size -= 2
        self.layout(self.text)

    def render(self):
        self.canvas.delete("all")
        for x, y, w, font in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            if w == ':)':
                self.canvas.create_image(x, y-self.scroll, image=self.gif_grinFace)
                continue
            self.canvas.create_text(x, y-self.scroll, text=w, font=font, anchor='nw')
            x += font.measure(w)
    
    def layout(self, tokens):
        # prepare the display_list
        self.display_list = Layout(tokens).display_list
        self.text = tokens
        assert len(self.display_list)>0 

        # render
        self.render()

class Layout:
    def __init__(self, tokens):
        self.display_list = []
        self.x, self.y = HSTEP, VSTEP
        self.line = []
        self.weight = "normal"
        self.style = "roman"
        self.size = 16
        self.title = False
        self.supFlag = False
        self.sourceCode = False
        for tok in tokens:
            # call token() function
            self.token(tok)

    def text(self, text):
        font = tkinter.font.Font(
            family="Times",
            size=self.size,
            weight = self.weight,
            slant = self.style
        )
        text = text.replace("&quot;", '"')
        for word in text.split():
            w = font.measure(word)
            if self.x + w >= WIDTH - HSTEP:
                # prepare newline, ans reset self.x ans self.line
                self.flush()
            self.line.append((self.x, word, font))
            self.x += w + font.measure(" ")

    def flush(self):
        if not self.line: return

        # align the words along the line
        metrics = [font.metrics() for _,_,font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        max_descent = max([metric["descent"] for metric in metrics])
        baseline = self.y + 1.2 * max_ascent
        self.y = baseline + 1.2 * max_descent

        # add all words to self.display_list with x, y, word, font
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            if self.supFlag:
                y -= 5
            self.display_list.append((x, y, word, font))
        
        # reset the self.x and self.line
        self.x = HSTEP
        self.line = []

    def token(self, tok):
        if isinstance(tok, Text):
            # call text() method
            self.text(tok.text)
        elif tok.tag == "i": 
            self.style = "italic"
        elif tok.tag == "/i": 
            self.style = "roman"
        elif tok.tag == "b": 
            self.weight = "bold"
        elif tok.tag == "/b": 
            self.weight = "normal"
        # elif tok.tag == "small": 
        #     self.size -= 2
        # elif tok.tag == "/small": 
        #     self.size += 2
        # elif tok.tag == "big": 
        #     self.size += 4
        # elif tok.tag == "/big": 
        #     self.size -= 4
        elif tok.tag == "br": 
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.y += VSTEP
        elif tok.tag == 'h1 class="title"':
            self.size += 10
            self.weight = "bold"
            self.title = True
            self.centerline()
            self.flush()
        elif tok.tag.startswith("h1 id="):
            self.size += 4
            self.weight = "bold"
            self.flush()
        elif tok.tag == '/h1' and self.title:
            self.size -= 10
            self.weight = "normal"
            self.centerline()
            self.flush()
            self.title = False
        elif tok.tag == "/h1":
            self.size -= 4
            self.weight = "normal"
            self.centerline()
            self.flush()
        elif tok.tag == "sup":
            self.size -= 4
            self.supFlag = True
        elif tok.tag == "/sup" and self.supFlag:
            self.size += 4
            self.supFlag = False
        elif tok.tag.startswith('div class="sourceCode"'):
            self.sourceCode = True
        elif self.sourceCode and tok.tag.startswith("span id="):
            self.tabSourceCode()
            self.flush()
        elif self.sourceCode and tok.tag == "/div":
            self.sourceCode = False
            self.flush()


    def centerline(self):
        # [ |what |is |a |font?  ]
        global WIDTH
        freespace = 0
        if self.line != []:
            x, word, font = self.line[-1]
            freespace = (WIDTH - x - font.measure(word))//2
        for i in range(len(self.line)):
            self.line[i] = (self.line[i][0]+freespace, \
                            self.line[i][1],\
                            self.line[i][2])
    def tabSourceCode(self):
        for i in range(len(self.line)):
            self.line[i] = (self.line[i][0]+ 4 * self.line[i][2].measure(" "), \
                            self.line[i][1],\
                            self.line[i][2])

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

    # Draw into window
    browser = Browser()
    content = lex(response.body)
    # call layout function in Browser,
    # and layout function construct Layout(content)
    browser.layout(content)
    tkinter.mainloop()
