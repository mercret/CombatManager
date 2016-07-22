from tkinter import *
from verticalscrolledframe import VerticalScrolledFrame
from entityqueue import *


class EntityQueueFrame(VerticalScrolledFrame):
    def __init__(self, master):
        VerticalScrolledFrame.__init__(self, master)

    def refresh(self, entityqueue):
        self.clear()
        for entity in entityqueue:
            Label(self.interior, text="-->" if entityqueue.position == entityqueue.index else "   ").grid(row=entityqueue.index,
                                                                                              column=0)
            Label(self.interior, text=str(entityqueue.index + 1)).grid(row=entityqueue.index, column=1)
            Label(self.interior, text=entity.name).grid(row=entityqueue.index, column=2)
            Label(self.interior, text=str(entity.initiative)).grid(row=entityqueue.index, column=3)
            Label(self.interior, text='{}/{}'.format(entity.health, entity.maxHealth)).grid(row=entityqueue.index,
                                                                                            column=4)
