import parse
import tkinter
from parse import TextNode, ElementNode

from globalDeclare import Variables
class DrawText:
    def __init__(self, x1, y1, text, font):
        self.x1 = x1
        self.y1 = y1
        self.text = text
        self.font = font
        self.y2 = y1 + font.metrics("linespace")

    def draw(self, scroll, canvas):
        canvas.create_text(
            self.x1, self.y1 - scroll,
            text=self.text,
            font=self.font,
            anchor='nw',
        )
    
class DrawRect:
    def __init__(self, x1, y1, x2, y2, color):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color

    def draw(self, scroll, canvas):
        canvas.create_rectangle(
            self.x1, self.y1 - scroll,
            self.x2, self.y2 - scroll,
            width=0,
            fill=self.color,
        )

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

        self.mt = self.mr = self.mb = self.ml = -1
        self.bt = self.br = self.bb = self.bl = -1
        self.pt = self.pr = self.pb = self.pl = -1

    def layout(self):
        self.mt = px(self.node.style.get("margin-top", "0px"))
        self.bt = px(self.node.style.get("border-top-width", "0px"))
        self.pt = px(self.node.style.get("padding-top", "0px"))

        self.mr = px(self.node.style.get("margin-right", "0px"))
        self.br = px(self.node.style.get("border-right-width", "0px"))
        self.pr = px(self.node.style.get("padding-right", "0px"))

        self.mb = px(self.node.style.get("margin-bottom", "0px"))
        self.bb = px(self.node.style.get("border-bottom-width", "0px"))
        self.pb = px(self.node.style.get("padding-bottom", "0px"))

        self.ml = px(self.node.style.get("margin-left", "0px"))
        self.bl = px(self.node.style.get("border-left-width", "0px"))
        self.pl = px(self.node.style.get("padding-left", "0px"))


        self.w = Variables.WIDTH

        child = BlockLayout(self.node, self)
        child.x = self.x = 10
        child.y = self.y = 10
        self.children.append(child)
        child.layout()

        self.h = child.h

    def draw(self, to):
        self.children[0].draw(to)




class BlockLayout:
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent
        self.children = []

        self.w = -1
        self.h = -1

        # margin, border, padding
        self.mt = self.mr = self.mb = self.ml = -1
        self.bt = self.br = self.bb = self.bl = -1
        self.pt = self.pr = self.pb = self.pl = -1

    def layout(self):
        self.mt = px(self.node.style.get("margin-top", "0px"))
        self.bt = px(self.node.style.get("border-top-width", "0px"))
        self.pt = px(self.node.style.get("padding-top", "0px"))

        self.mr = px(self.node.style.get("margin-right", "0px"))
        self.br = px(self.node.style.get("border-right-width", "0px"))
        self.pr = px(self.node.style.get("padding-right", "0px"))

        self.mb = px(self.node.style.get("margin-bottom", "0px"))
        self.bb = px(self.node.style.get("border-bottom-width", "0px"))
        self.pb = px(self.node.style.get("padding-bottom", "0px"))

        self.ml = px(self.node.style.get("margin-left", "0px"))
        self.bl = px(self.node.style.get("border-left-width", "0px"))
        self.pl = px(self.node.style.get("padding-left", "0px"))


        if self.has_block_children():
            for child in self.node.children:
                if isinstance(child, TextNode): continue
                self.children.append(BlockLayout(child, self))
        else:
            self.children.append(InlineLayout(self.node, self))

        self.w = self.parent.w - self.parent.pl - self.parent.pr \
        - self.parent.bl - self.parent.br \
        - self.ml - self.mr

        self.y += self.mt
        self.x += self.ml
        y = self.y
        for child in self.children:
            child.x = self.x + self.pl + self.pr + self.bl + self.br
            child.y = y
            child.layout()
            y += child.h + child.mt + child.mb
        self.h = y - self.y

    def has_block_children(self):
        for child in self.node.children:
            if isinstance(child, TextNode):
                if not child.text.isspace():
                    return False
            elif child.style.get("display", "block") == "inline":
                return False
        return True

    def draw(self, to):
        if self.node.tag == "pre":
            x2, y2 = self.x + self.w, self.y + self.h
            to.append(DrawRect(self.x, self.y, x2, y2, "gray"))
        for child in self.children:
            child.draw(to)

class InlineLayout:
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent
        self.children = []

        self.w = -1
        self.h = -1

        self.mt = self.mr = self.mb = self.ml = -1
        self.bt = self.br = self.bb = self.bl = -1
        self.pt = self.pr = self.pb = self.pl = -1

    def layout(self):
        self.mt = px(self.node.style.get("margin-top", "0px"))
        self.bt = px(self.node.style.get("border-top-width", "0px"))
        self.pt = px(self.node.style.get("padding-top", "0px"))

        self.mr = px(self.node.style.get("margin-right", "0px"))
        self.br = px(self.node.style.get("border-right-width", "0px"))
        self.pr = px(self.node.style.get("padding-right", "0px"))

        self.mb = px(self.node.style.get("margin-bottom", "0px"))
        self.bb = px(self.node.style.get("border-bottom-width", "0px"))
        self.pb = px(self.node.style.get("padding-bottom", "0px"))

        self.ml = px(self.node.style.get("margin-left", "0px"))
        self.bl = px(self.node.style.get("border-left-width", "0px"))
        self.pl = px(self.node.style.get("padding-left", "0px"))

        self.display_list = []

        self.cx = self.x
        self.cy = self.y

        self.w = self.parent.w - self.parent.pl - self.parent.pr \
            - self.parent.bl - self.parent.br

        self.weight = "normal"
        self.style = "roman"
        self.size = 16

        self.title = False
        self.supFlag = False
        self.sourceCode = False

        self.line = []
        self.recurse(self.node)
        self.flush()
    
        self.h = self.cy - self.y

    def font(self, node):
        bold = node.style["font-weight"]
        italic = node.style["font-style"]
        if italic == "normal": italic = "roman"
        size = int(px(node.style.get("font-size")) * .75)
        return tkinter.font.Font(size=size, weight=bold, slant=italic)

    def draw(self, to):
        for x, y, word, font in self.display_list:
            to.append(DrawText(x, y, word, font))
    
    def recurse(self, node):
        if isinstance(node, TextNode):
            self.text(node)
        else:
            for child in node.children:
                self.recurse(child)
            
    def text(self, node):
        font = self.font(node)
        for word in node.text.split():
            w = font.measure(word)
            if self.cx + w >= Variables.WIDTH - Variables.HSTEP:
                # prepare newline, ans reset self.cx ans self.line
                self.flush()
            self.line.append((self.cx, word, font))
            self.cx += w + font.measure(" ")

    def flush(self):
        if not self.line: return

        # align the words along the line
        metrics = [font.metrics() for _,_,font in self.line]
        max_ascent = abs(max([metric["ascent"] for metric in metrics]))
        max_descent = abs(max([metric["descent"] for metric in metrics]))
        baseline = self.cy + 1.2 * max_ascent

        # add all words to self.display_list with x, y, word, font
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            if self.supFlag:
                y -= 5
            self.display_list.append((x, y, word, font))
        
        # reset the self.cx and self.line
        self.cy = baseline + abs(1.2 * max_descent)
        self.cx = Variables.HSTEP
        self.line = []

    def handle_open_tag(self, tag, attributes):
            if tag == "i":
                self.style = "italic"
            elif tag == "b": 
                self.weight = "bold"
            elif tag == "br": 
                self.flush()
            elif tag == 'h1' and attributes.get('class') == "\"title\"":
                self.size += 10
                self.weight = "bold"
                self.title = True
                self.centerline()
                self.flush()
            elif tag == 'h1' and 'id' in attributes:
                self.size += 4
                self.weight = "bold"
                self.flush()
            elif tag == "sup":
                self.size -= 4
                self.supFlag = True
            elif tag == 'div' and attributes.get('class') == "sourceCode":
                self.sourceCode = True
            elif self.sourceCode and tag == 'span' and 'id' in attributes:
                self.tabSourceCode()
                self.flush()
        
    def handle_close_tag(self, tag):
        if tag == "i":
            self.style = "roman"
        elif tag == "b": 
            self.weight = "normal"
        elif tag == "p":
            self.flush()
            self.cy += Variables.VSTEP
        elif tag == 'h1' and self.title:
            self.size -= 10
            self.weight = "normal"
            self.centerline()
            self.flush()
            self.title = False
        elif tag == "h1":
            self.size -= 4
            self.weight = "normal"
            self.centerline()
            self.flush()
        elif tag == "sup" and self.supFlag:
            self.size += 4
            self.supFlag = False
        elif self.sourceCode and tag == "div":
            self.sourceCode = False
            self.flush()

    def centerline(self):
        # [ |what |is |a |font?  ]
        freespace = 0
        if self.line != []:
            x, word, font = self.line[-1]
            freespace = (Variables.WIDTH - x - font.measure(word))//2
        for i in range(len(self.line)):
            self.line[i] = (self.line[i][0]+freespace, \
                            self.line[i][1],\
                            self.line[i][2])
    
    def tabSourceCode(self):
        for i in range(len(self.line)):
            self.line[i] = (self.line[i][0]+ 4 * self.line[i][2].measure(" "), \
                            self.line[i][1],\
                            self.line[i][2])

class TagSelector:
    def __init__(self, tag):
        self.tag = tag
    
    def matches(self, node):
        return self.tag in node.tag.split()

    def priority(self):
        return 1

class ClassSelector:
    def __init__(self, cls):
        self.cls = cls

    def matches(self, node):
        return self.cls in node.attributes.get("class", "").split()

    def priority(self):
        return 16

class IdSelector:
    def __init__(self, id):
        self.id = id
    def matches(self, node):
        return self.id in node.attributes.get("id", "").split()
    def priority(self):
        return 256

class CSSParser:
    def __init__(self, s):
        self.s = s

    # Call by connect.py, driver of CSSParser
    def parse(self):
        rules, _ = self.file(0)
        return rules

    def value(self, i):
        j = i
        while self.s[j].isalnum() or self.s[j] in "-.":
            j += 1
        return self.s[i:j], j

    def whitespace(self, i):
        j = i
        while j < len(self.s) and self.s[j].isspace():
            j += 1
        return None, j
    
    def pair(self, i):
        prop, i = self.value(i)
        _, i = self.whitespace(i)
        assert self.s[i] == ":"
        _, i = self.whitespace(i + 1)
        val, i = self.value(i)
        _, i = self.whitespace(i + 1)
        return (prop.lower(), val), i
    
    def body(self, i):
        pairs = {}
        assert self.s[i] == "{"
        _, i = self.whitespace(i+1)
        while True:
            if i > len(self.s): break
            if self.s[i] == "}": break

            try:
                (prop, val), i = self.pair(i)
                pairs[prop] = val
                _, i = self.whitespace(i)
                assert self.s[i] == ";"
                _, i = self.whitespace(i+1)
            except AssertionError:
                while self.s[i] not in [";", "}"]:
                    i += 1
                if self.s[i] == ";":
                    _, i = self.whitespace(i + 1)
        assert self.s[i] == "}"
        return pairs, i+1
    
    def selector(self, i):
        if self.s[i] == "#":
            name, i = self.value(i+1)
            return IdSelector(name), i
        elif self.s[i] == ".":
            name, i = self.value(i+1)
            return ClassSelector(name), i
        else:
            name, i = self.value(i)
            return TagSelector(name.lower()), i

    def rule(self, i):
        selector, i = self.selector(i)
        _, i = self.whitespace(i)
        body, i = self.body(i)
        return (selector, body), i

    def file(self, i):
        rules = []
        _, i = self.whitespace(i)
        while i < len(self.s):
            try:
                rule, i = self.rule(i)
            except AssertionError:
                while i < len(self.s) and self.s[i] != "}":
                    i += 1
                i += 1
            else:
                rules.append(rule)
            _, i = self.whitespace(i)
        rules.sort(key=lambda x: x[0].priority(), reverse=True)
        return rules, i
    
    
def px(s):
    if s.endswith("px"):
        return int(s[:-2])
    else:
        return 0

