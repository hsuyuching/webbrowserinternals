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
    ADDR_START = 85 # x