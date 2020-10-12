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

    def layout(self):
        self.w = Variables.WIDTH

        child = BlockLayout(self.node, self)
        child.x = self.x = 0
        child.y = self.y = 0
        self.children.append(child)
        child.layout()

        # child.layout()
        self.h = child.h

    def draw(self, to):
        self.children[0].draw(to)

class BlockLayout:
    def __init__(self, node, parent):
        self.node = node
        self.parent = parent
        self.children = []

        # self.x = -1
        # self.y = -1
        self.w = -1
        self.h = -1
    
    def layout(self):

        if self.has_block_children():
            for child in self.node.children:
                if isinstance(child, TextNode): continue
                self.children.append(BlockLayout(child, self))
        else:
            self.children.append(InlineLayout(self.node, self))

        self.w = self.parent.w
        y = self.y
        for child in self.children:
            child.x = self.x
            child.y = y
            child.layout()
            y += child.h
        self.h = y - self.y

    def has_block_children(self):
        for child in self.node.children:
            if isinstance(child, TextNode):
                if not child.text.isspace():
                    return False
            elif child.tag in Variables.INLINE_ELEMENTS:
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

        # self.x = -1
        # self.y = -1
        self.w = -1
        self.h = -1

    def layout(self):
        
        self.display_list = []

        self.cx = self.x
        self.cy = self.y

        self.w = self.parent.w

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

    def draw(self, to):
        # to.extend(self.display_list)
        for x, y, word, font in self.display_list:
            to.append(DrawText(x, y, word, font))
    
    def recurse(self, tree):
        if isinstance(tree, TextNode):
            self.text(tree.text)
        else:
            self.handle_open_tag(tree.tag, tree.attributes)
            for child in tree.children:
                self.recurse(child)
            self.handle_close_tag(tree.tag)
            
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
