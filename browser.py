import tkinter
import layout
import parse

from globalDeclare import Variables

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
        self.gif_grinFace = tkinter.PhotoImage(file='resize_griningFace.gif')

    def scrolldown(self, e):
        # self.scroll += Variables.SCROLL_STEP
        # self.render()
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
        document = layout.DocumentLayout(tree)
        document.layout()
        self.display_list = []
        document.draw(self.display_list)
        self.render()
        self.max_y = document.h

        # _print_tree(self.tree, "  ")

    
    # def render(self):
    #     self.canvas.delete("all")
    #     for x, y, w, font in self.display_list:
    #         if y > self.scroll + Variables.HEIGHT: continue
    #         if y + Variables.VSTEP < self.scroll: continue
    #         if w == ':)':
    #             self.canvas.create_image(x, y-self.scroll, image=self.gif_grinFace)
    #             continue
    #         self.canvas.create_text(x, y-self.scroll, text=w, font=font, anchor='nw')
    #         x += font.measure(w)
    def render(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.y1 > self.scroll + Variables.HEIGHT: continue
            if cmd.y2 < self.scroll: continue
            cmd.draw(self.scroll, self.canvas)

def _print_tree(tree, indent_space):
        print(f'{indent_space} {tree}')
        if isinstance(tree, parse.ElementNode):   
            for child in tree.children:    
                _print_tree(child, indent_space + '  ')
