import tkinter
import layout

from globalDeclare import Variables

class Browser:
    def __init__(self):
        self.scroll = 0
        self.text = ""
        self.window = tkinter.Tk()
        self.window.title("Yu-Ching Hsu's Browser")
        self.canvas = tkinter.Canvas( self.window, width = Variables.WIDTH, height = Variables.HEIGHT)
        self.canvas.pack(expand=True, fill="both")
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Configure>", self.windowresize)
        self.gif_grinFace = tkinter.PhotoImage(file='resize_griningFace.gif')

    def scrolldown(self, e):
        self.scroll += Variables.SCROLL_STEP
        self.render()

    def scrollup(self, e):
        self.scroll -= Variables.SCROLL_STEP
        self.render()

    def windowresize(self, e):
        Variables.WIDTH = e.width
        Variables.HEIGHT = e.height
        self.layout(self.text)
    
    def layout(self, nodes):
        self.display_list = layout.Layout(nodes).display_list
        self.text = nodes
        self.render()

    def render(self):
        self.canvas.delete("all")
        for x, y, w, font in self.display_list:
            if y > self.scroll + Variables.HEIGHT: continue
            if y + Variables.VSTEP < self.scroll: continue
            if w == ':)':
                self.canvas.create_image(x, y-self.scroll, image=self.gif_grinFace)
                continue
            self.canvas.create_text(x, y-self.scroll, text=w, font=font, anchor='nw')
            x += font.measure(w)