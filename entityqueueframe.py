from tkinter import *

class EntityQueueFrame(Frame):

    def __init__(self,master):
        Frame.__init__(self,master)
        self.master=master

    def refresh(self,entityqueue):
        for i,e in zip(range(1,entityqueue.length+1),entityqueue):
            self.add(i,e)


    def add(self,index,entity):
