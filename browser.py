import tkinter
import layout
import parse
import dukpy

import traceback
from connect import request, stripoutUrl
from globalDeclare import Variables, Timer
from layout import CSSParser, InputLayout
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
        # self.window.bind("<Configure>", self.windowresize)
        self.window.bind("<Button-1>", self.handle_click)
        self.window.bind("<Key>", self.keypress)
        self.window.bind("<Return>", self.pressenter)
        self.window.bind("<BackSpace>", self.backspace)
        self.history = []
        self.future = []
        self.curridx = 0
        self.focus = None
        self.address_bar = ""
        self.timer = Timer()

    def backspace(self, e):
        if self.focus == "address bar":
            if self.address_bar:
                self.address_bar = self.address_bar[:-1]
                self.render()
        elif self.focus:
            text = self.focus.node.attributes.get("value", "")
            if text != "":
                self.focus.node.attributes["value"] = text[:-1]
                self.dispatch_event("change", self.focus.node)
                self.layout(self.document.node)
                self.render()
    
    def pressenter(self, e):
        if self.focus == "address bar":
            self.focus = None
            self.future = []
            self.load(self.address_bar)
        elif self.focus: # is an obj (form)
            self.submit_form(self.focus.node)
            self.focus = None
            self.render()


    def keypress(self, e):
        if len(e.char) != 1 or ord(e.char) < 0x20 or 0x7f <= ord(e.char):
            return
        if not self.focus: return
        if self.focus == "address bar":
            if len(e.char) == 1 and 0x20 <= ord(e.char) < 0x7f:
                self.address_bar += e.char
                self.render()
        elif isinstance(self.focus, InputLayout):
            self.focus.node.attributes["value"] += e.char
            self.dispatch_event("change", self.focus.node)
            # self.layout(self.document.node)
            self.reflow(self.focus)

    def handle_click(self, e):
        if e.y < 60: # Browser chrome
            # click "back" button
            if 10 <= e.x < 35 and 10 <= e.y < 50:
                self.go_back()
            # click "refresh" button
            elif 45 <= e.x < 70 and 10 <= e.y < 50:
                self.refresh()
            #click "forward" button
            elif 80 <= e.x < 105 and 10 <= e.y < 50:
                self.go_forward()
            # click address bar
            elif Variables.ADDR_START-5 <= e.x < 800 and 10 <= e.y < 50:
                self.focus = "address bar"
                self.address_bar = ""
                self.render()

        else: # page content
            x, y = e.x, e.y - 60 + self.scroll
            obj = find_layout(x, y, self.document)
            if not obj: return
            elt = obj.node
            if elt and self.dispatch_event('click', elt): return
            
            # press on <input>
            # if is_input(elt): 
            #     self.click_input(elt)
            #     self.focus = obj
            #     self.layout(self.document.node)

            while elt and (isinstance(elt, TextNode) or (not is_link(elt) and elt.tag != "button" and elt.tag != "input")):
                elt = elt.parent
            if not elt:
                pass
            elif is_link(elt):
                temp = self.url
                if isinstance(self.url, str):
                    temp = stripoutUrl(self.url)
                url = relative_url(elt.attributes["href"], temp)
                self.future = []
                self.load(url)

            elif elt.tag == "input":
                elt.attributes["value"] = ""
                self.focus = obj
                return self.reflow(self.focus)

            elif elt.tag == "button":
                self.focus = None
                self.submit_form(elt)

    def submit_form(self, elt):
        while elt and elt.tag != 'form':
            elt = elt.parent
        if not elt: return
        self.dispatch_event("submit", elt)
        inputs = find_inputs(elt, [])
        body = ""
        for input in inputs:
            name = input.attributes['name']
            value = input.attributes.get('value', '')
            body += "&" + name + "="
            body += value.replace(" ", "%20")
        body = body[1:]
     
        if isinstance(self.url, str):
            self.url = stripoutUrl(self.url)
        url = relative_url(elt.attributes['action'], self.url)
        
        if self.dispatch_event("submit", elt): return
        self.load(url, body)

    def click_input(self, elt):
        elt.attributes["value"] = ""

    def go_back(self):
        if len(self.history) > 1: # if no previous page, then not enter
            self.future.append(self.history.pop())
            back = self.history.pop()
            self.load(back)

    def refresh(self):
        self.load(self.url)

    def go_forward(self):
        if self.future:
            self.load(self.future.pop())

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
        self.layout(self.nodes)
    
    def layout(self, tree):
        self.timer.start("Style")
        style(tree, self.rules, None)
        self.timer.start("Layout (phase 1)")
        self.document = layout.DocumentLayout(tree)
        self.reflow(self.document)

    def reflow(self, obj):
        self.timer.start("Style")
        style(obj.node, self.rules, None)
        self.timer.start("Layout (phase 1)")
        obj.size()
        self.timer.start("Layout (phase 2)")
        self.document.position()

        self.timer.start("Display list")
        self.display_list = []
        self.document.draw(self.display_list)
        self.render()
        self.max_y = self.document.h


    def render(self):
        self.timer.start("Rendering")
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.y1 > self.scroll + Variables.HEIGHT: continue
            if cmd.y2 < self.scroll: continue
            cmd.draw(self.scroll - 60, self.canvas)

        self.timer.start("Chrome")
        # address bar
        self.canvas.create_rectangle(Variables.ADDR_START-5, 0, 800, 60, width=0, fill='light gray')
        self.canvas.create_rectangle(Variables.ADDR_START, 10, 790, 50)
        
        font = tkinter.font.Font(family="Courier", size=20)
        url = self.url
        if not isinstance(url, str):
            url = self.url.scheme+"://"+self.url.host+self.url.path
        self.canvas.create_text(Variables.ADDR_START+5, 15, anchor='nw', text=self.address_bar, font=font)
    
        # back button
        if len(self.history)>1: button_color = "black"
        else: button_color = "gray"
        self.canvas.create_rectangle(10, 10, 35, 50)
        self.canvas.create_polygon(15, 30, 30, 20, 30, 40, fill=button_color)

        # refresh button
        self.canvas.create_rectangle(45, 10, 70, 50)
        refreshpath = [
            12,3,9,0,9,2,0,2,0,16,14,16,14,8,12,8,12,14,2,14,2,4,9,4,9,6,12,3
        ]
        scale = 1.2
        for i in range(0,len(refreshpath),2):
            refreshpath[i] = int(refreshpath[i]*scale) + Variables.RESET_ICON[0]
            refreshpath[i+1] = int(refreshpath[i+1]*scale) + Variables.RESET_ICON[1]
        self.canvas.create_polygon(refreshpath, fill="black")

        # forward button x1,y1,x2,y2
        if self.future: button_color = "black"
        else: button_color = "gray"
        self.canvas.create_rectangle(80, 10, 105, 50)
        self.canvas.create_polygon(85, 20, 100, 30, 85, 40, fill=button_color)
        
        if self.focus == "address bar":
            w = font.measure(self.address_bar)
            self.canvas.create_line(Variables.ADDR_START+5 + w, 15, Variables.ADDR_START+5 + w, 45)

        # <input> cursor
        if isinstance(self.focus, InputLayout):
            text = self.focus.node.attributes.get("value", "")
            x = self.focus.x + self.focus.font.measure(text)
            y = self.focus.y
            # add 60px to make up the address bar
            self.canvas.create_line(x, y+60, x, y + self.focus.h + 60)
        
        self.timer.stop()


    def load(self, url, body=None): # body: encode form for params
        self.url = url
        self.timer.start("Downloading")
        if isinstance(url, str):
            self.address_bar = url
            url = stripoutUrl(url)
        else: 
            self.address_bar = url.scheme+"://"+url.host+url.path
        
        if not (self.history and self.history[-1] == url):
            self.history.append(url)

        response = request(url, body)
        header, body = response.headers, response.body
        tokens = parse.lex(body)
        self.timer.start("Parsing HTML")
        nodes = parse.ParseTree().parse(tokens)
        self.nodes = nodes
        
        self.timer.start("Parsing CSS")
        with open("browser.css") as f:
            browser_style = f.read()
            rules = CSSParser(browser_style).parse()

        for link in find_links(nodes, []):
            cssurl = relative_url(link, url)
            cssurl = stripoutUrl(cssurl)
            response = request(cssurl)
            header, body = response.headers, response.body
            rules.extend(CSSParser(body).parse())

        rules.sort(key=lambda t:t[0].priority(), reverse=True)
        style(nodes, rules, None)
        self.rules = rules

        self.timer.start("Running JS")
        self.setup_js()
        for script in find_scripts(nodes, []):
            jsurl = relative_url(script, self.history[-1])
            jsurl = stripoutUrl(jsurl)
            res = request(jsurl)
            header, body = res.headers, res.body
            try:
                print("Script returned: ", self.js_environment.evaljs(body))
            except:
                print("Script", script, "crashed")
                # traceback.print_exc()
                # raise
        
        self.layout(nodes)
        # self.size(node)

    def js_querySelectorAll(self, sel):
        try:
            # parse the selector then find and return the matching eles.
            selector, _ = CSSParser(sel + "{").selector(0)
            elts = find_selected(self.nodes, selector, [])
            return [self.make_handle(elt) for elt in elts]
        except:
            traceback.print_exc()
            raise
    
    def js_getAttribute(self, handle, attr):
        try:
            elt = self.handle_to_node[handle]
            return elt.attributes.get(attr, None)
        except:
            print("js_getAttribute error")
            traceback.print_exc()
            raise
    
    def js_innerHTML(self, handle, s):
        try:
            doc = parse.ParseTree().parse(parse.lex("<html><body>" + s + "</body></html>"))
            new_nodes = doc.children[0].children
            
            elt = self.handle_to_node[handle]
            elt.children = new_nodes
            for child in elt.children:
                child.parent = elt
            self.timer.start("Style")
            style(self.nodes, self.rules, None)
            # self.layout(self.nodes)
            self.timer.start("Layout (phase 2)")
            self.reflow(layout_for_node(self.document, elt))
            # self.render()
        except:
            print("js_innerHTML error")
            traceback.print_exc()
            raise

    def setup_js(self):
        self.node_to_handle = {}
        self.handle_to_node = {}
        self.js_environment = dukpy.JSInterpreter()
        self.js_environment.export_function(
            "log", print)
        self.js_environment.export_function(
            "querySelectorAll",
            self.js_querySelectorAll
        )
        self.js_environment.export_function(
            "getAttribute",
            self.js_getAttribute
        )
        self.js_environment.export_function(
            "innerHTML",
            self.js_innerHTML
        )
        with open("runtime.js") as f:
            self.js_environment.evaljs(f.read())
    
    def make_handle(self, elt):
        if id(elt) not in self.node_to_handle:
            handle = len(self.node_to_handle)
            self.node_to_handle[id(elt)] = handle
            self.handle_to_node[handle] = elt
        else:
            handle = self.node_to_handle[id(elt)]
        return handle

    def dispatch_event(self, type, elt):
        # print("type: ", type, "elt:", elt)
        handle = self.make_handle(elt)
        code = "__runHandlers({}, \"{}\")".format(handle, type)

        self.js_environment.evaljs(code)
        do_default = self.js_environment.evaljs(code)
        return not do_default

def find_links(node, lst):
    if not isinstance(node, ElementNode): return
    if node.tag == "link" and \
       node.attributes.get("rel", "") == "stylesheet" and \
       "href" in node.attributes:
        lst.append(node.attributes["href"])
    for child in node.children:
        find_links(child, lst)
    return lst

def find_selected(node, sel, out):
    if not isinstance(node, ElementNode): return
    if sel.matches(node):
        out.append(node)
    for child in node.children:
        find_selected(child, sel, out)
    return out

def find_scripts(node, out):
    if not isinstance(node, ElementNode): return
    if node.tag == "script" and \
       "src" in node.attributes:
        out.append(node.attributes["src"])
    for child in node.children:
        find_scripts(child, out)
    return out

def find_layout(x, y, tree):
    for child in reversed(tree.children):
        result = find_layout(x, y, child)
        if result: return result
    if tree.x <= x < tree.x + tree.w and \
       tree.y <= y < tree.y + tree.h:
        return tree

def relative_url(url, current) -> str: #current: Url
    current = current.scheme+"://"+current.host+":"+str(current.port)+current.path
    if "://" in url:
        return url
    elif url.startswith("/"):
        return "/".join(current.split("/")[:3]) + url
    else:
        return current.rsplit("/", 1)[0] + "/" + url

def is_input(elt):
    if isinstance(elt, ElementNode) and \
        elt.tag == "input":
        return True
    return False

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

def find_inputs(elt, out):
    if not isinstance(elt, ElementNode): return
    if elt.tag == 'input' and 'name' in elt.attributes:
        out.append(elt)
    for child in elt.children:
        find_inputs(child, out)
    return out

def _print_tree(tree, indent_space):
        print(f'{indent_space} {tree}')
        if isinstance(tree, parse.ElementNode):   
            for child in tree.children:    
                _print_tree(child, indent_space + '  ')

def layout_for_node(tree, node):
    if tree.node == node:
        return tree
    for child in tree.children:
        out = layout_for_node(child, node)
        if out: return out