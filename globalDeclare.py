class Variables:
    SELF_CLOSING_TAGS = [
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ]
    HEAD_TAGS = [
        "base", "basefont", "bgsound", "noscript",
        "link", "meta", "title", "style", "script",
    ]

    ENTITIES = {
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&amp;": "&"
    }
    
    WIDTH, HEIGHT = 800, 600
    HSTEP, VSTEP = 13, 18
    SCROLL_STEP = 100

    INHERITED_PROPERTIES = {
    "font-style": "normal",
    "font-weight": "normal",
    "font-size": "16px",
    "color": "black"
    }
    ADDR_START = 115 # x
    RESET_ICON = (50, 20) # x, y

import time
class Timer:
    def __init__(self):
        self.phase = None
        self.time = None

    def start(self, name):
        if self.phase: self.stop()
        self.phase = name
        self.time = time.time()
        
    def stop(self):
        dt = time.time() - self.time
        print("[{:>10.6f}] {}".format(dt, self.phase))
        self.phase = None