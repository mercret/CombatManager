from tkinter import *  # from x import * is bad practice


# http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """

    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = canvas = Canvas(self, bd=0, highlightthickness=0,
                                      yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        self.interior_id = canvas.create_window(0, 0, window=interior,anchor=NW)

        self.configure_mousewheel()
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar


        interior.bind('<Configure>', self.configure_interior)

        canvas.bind('<Configure>', self.configure_canvas)

    def configure_interior(self,event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            #5 pixels hack i'm so sorry
            self.canvas.config(width=self.interior.winfo_reqwidth()+5)

    def configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def configure_mousewheel(self):
        # mousewheel events
        # windows
        self.interior.bind("<MouseWheel>",
                           lambda event: self.canvas.yview('scroll', int(-1 * (event.delta / 120)), 'units'))
        # unix
        self.interior.bind("<Button-4>", lambda event: self.canvas.yview('scroll', -1, 'units'))
        self.interior.bind("<Button-5>", lambda event: self.canvas.yview('scroll', 1, 'units'))

    def clear(self):
        self.interior.destroy()
        self.interior = Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior,anchor=NW)
        self.interior.bind('<Configure>', self.configure_interior)
        self.configure_mousewheel()
