import parse
import tkinter
from parse import TextNode, ElementNode

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18

class Layout:
    def __init__(self, tree):
        self.display_list = []
        self.x, self.y = HSTEP, VSTEP
        self.line = []
        self.weight = "normal"
        self.style = "roman"
        self.size = 16
        self.title = False
        self.supFlag = False
        self.sourceCode = False
        # tree = self.parse(tokens)
        self.recurse(tree)
        self.flush()
    
    def recurse(self, tree):
        if isinstance(tree, TextNode):
            self.text(tree.text)
        else:
            self.handle_open_tag(tree.tag, tree.attributes)
            for child in tree.children:
                self.recurse(child)
            self.handle_close_tag(tree.tag)

    def _print_tree(self, tree, indent_space):
        print(f'{indent_space} {tree}')
        if isinstance(tree, ElementNode):   
            for child in tree.children:    
                self._print_tree(child, indent_space + '  ')
            
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
            self.y += VSTEP
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
