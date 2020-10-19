import tkinter
import layout
import parse

from connect import request, stripoutUrl
from globalDeclare import Variables
from layout import CSSParser
from parse import TextNode, ElementNode

class Browser:
    def __init__(self):
        self.scroll = 0
        self.window = tkinter.Tk()
        self.window.title("Yu-Ching Hsu's Browser")
        self.canvas = tkinter.Canvas( self.window, width = Variables.WIDTH, height = Variables.HEIGHT)
        self.canvas.pack(expand=True, fill="both")
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Configure>", self.windowresize)
        self.window.bind("<Button-1>", self.handle_click)
        self.gif_grinFace = tkinter.PhotoImage(file='resize_griningFace.gif')

    def handle_click(self, e):
        x, y = e.x - 60, e.y + self.scroll
        obj = find_layout(x, y, self.document)
        if not obj: return
        elt = obj.node
        while elt and not is_link(elt):
            elt = elt.parent
        if elt:
            temp = self.url
            if isinstance(self.url, str):
                temp = stripoutUrl(self.url)
            url = relative_url(elt.attributes["href"], temp)
            self.load(url)

    def scrolldown(self, e):
        self.scroll = self.scroll + Variables.SCROLL_STEP
        self.scroll = min(self.scroll, self.max_y)
        self.scroll = max(0, self.scroll)
        self.render()

    def scrollup(self, e):
        self.scroll -= Variables.SCROLL_STEP
        self.render()

    def windowresize(self, e):
        Variables.WIDTH = e.width
        Variables.HEIGHT = e.height
        self.layout(self.tree)
    
    def layout(self, tree):
        self.tree = tree
        self.document = layout.DocumentLayout(tree)
        self.document.layout()
        self.display_list = []
        self.document.draw(self.display_list)
        self.render()
        self.max_y = self.document.h

        # _print_tree(self.tree, "  ")

    def render(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.y1 > self.scroll + Variables.HEIGHT: continue
            if cmd.y2 < self.scroll: continue
            cmd.draw(self.scroll - 60, self.canvas)

    def load(self, url):
        self.url = url
        print("new url:", url)
        if isinstance(url, str):
            url = stripoutUrl(url)
        response = request(url)
        header, body = response.headers, response.body
        tokens = parse.lex(body)
        nodes = parse.ParseTree().parse(tokens)

        with open("browser.css") as f:
            browser_style = f.read()
            rules = CSSParser(browser_style).parse()

        for link in find_links(nodes, []):
            cssurl = relative_url(link, url)
            cssurl = stripoutUrl(cssurl)
            response = request(cssurl)
            header, body = response.headers, response.body
            rules.extend(CSSParser(body).parse())

        rules.sort(key=lambda t:t[0].priority(),
            reverse=True)
        style(nodes, rules, None)
        self.layout(nodes)

def _print_tree(tree, indent_space):
        print(f'{indent_space} {tree}')
        if isinstance(tree, parse.ElementNode):   
            for child in tree.children:    
                _print_tree(child, indent_space + '  ')

def find_links(node, lst):
    if not isinstance(node, ElementNode): return
    if node.tag == "link" and \
       node.attributes.get("rel", "") == "stylesheet" and \
       "href" in node.attributes:
        lst.append(node.attributes["href"])
    for child in node.children:
        find_links(child, lst)
    return lst

def find_layout(x, y, tree):
    for child in reversed(tree.children):
        result = find_layout(x, y, child)
        if result: return result
    if tree.x <= x < tree.x + tree.w and \
       tree.y <= y < tree.y + tree.h:
        return tree

def relative_url(url, current) -> str: #current: Url
    # print("***", current)
    current = current.scheme+"://"+current.host+current.path
    if "://" in url:
        return url
    elif url.startswith("/"):
        return "/".join(current.split("/")[:3]) + url
    else:
        return current.rsplit("/", 1)[0] + "/" + url

def is_link(node):
    return isinstance(node, ElementNode) \
        and node.tag == "a" and "href" in node.attributes

def style(node, rules, parent):
    if isinstance(node, TextNode):
        node.style = parent.style
    else:
        for selector, pairs in rules:
            if selector.matches(node):
                for property in pairs:
                    if property not in node.style:
                        node.style[property] = pairs[property]
    
        for property, default in Variables.INHERITED_PROPERTIES.items():
            if property not in node.style:
                if parent:
                    node.style[property] = parent.style[property]
                else:
                    node.style[property] = default
        
        for child in node.children:
            style(child, rules, node)