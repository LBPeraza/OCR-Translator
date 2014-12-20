# Animation.py
# Lukas Peraza
# lbp
# Section A
# 15-112 Fall 2013

import random
from Tkinter import *

###########################################
# Animation class
# Slightly modified from class
# to include mouse motion and
# mouse released events
#
# for use in OCR Translator
###########################################

class Animation(object):
    # Override these methods when creating your own animation
    def mousePressed(self, event): pass
    def mouseReleased(self, event): pass
    def keyPressed(self, event): pass
    def mouseMotion(self, event): pass
    def leftMouseMotion(self, event): pass
    def timerFired(self): pass
    def init(self): pass
    def redrawAll(self): pass
    def __init__(self): pass
    
    # Call app.run(width,height) to get your app started
    def run(self, title, width=300, height=300):
        # create the root and the canvas
        root = Tk()
        root.title(title)
        self.width = width
        self.height = height
        self.canvas = Canvas(root, width=width, height=height)
        self.canvas.pack()
        # set up events
        def redrawAllWrapper():
            self.canvas.delete(ALL)
            self.redrawAll()
        def mousePressedWrapper(event):
            self.mousePressed(event)
            redrawAllWrapper()
        def mouseReleasedWrapper(event):
            self.mouseReleased(event)
            redrawAllWrapper()
        def keyPressedWrapper(event):
            self.keyPressed(event)
            redrawAllWrapper()
        def mouseMotionWrapper(event):
            self.mouseMotion(event)
            redrawAllWrapper()
        def leftMouseMotionWrapper(event):
            self.leftMouseMotion(event)
            redrawAllWrapper()
        root.bind("<Button-1>", mousePressedWrapper)
        root.bind("<B1-ButtonRelease>", mouseReleasedWrapper)
        root.bind("<Key>", keyPressedWrapper)
        root.bind("<Motion>", mouseMotionWrapper)
        root.bind("<B1-Motion>", leftMouseMotionWrapper)
        # set up timerFired events
        self.timerFiredDelay = 250 # milliseconds
        def timerFiredWrapper():
            self.timerFired()
            redrawAllWrapper()
            # pause, then call timerFired again
            self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
        # init and get timerFired running
        self.init()
        timerFiredWrapper()
        # and launch the app
        root.mainloop()  # This call BLOCKS (so your program waits until you close the window!)
        root.quit()
