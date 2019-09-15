# import tkinter as tk
import cv2, math, sys
from imutils.video import WebcamVideoStream
from tkinter import *
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk


class Paint(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'

    def __init__(self):
        self.root = Tk()
        self.sidePanel = Frame(self.root, bg='white', width=600, height=600)
        self.sidePanel.grid(row=1,columnspan=5)

        self.vs = WebcamVideoStream(src=0)
        self.vidArea = Canvas(self.sidePanel)
        self.vidArea.grid(row=1, columnspan=5)

        self.settingsPanel = Canvas(self.sidePanel)
        self.settingsPanel.grid(row=1, columnspan=5)

        self.drawArea = Canvas(self.root, bg='white', width=600, height=600)
        self.drawArea.grid(row=1, columnspan=5)

        self.sidePanel.pack(side="left", expand=True, fill="both")
        self.vidArea.pack(fill='x')
        self.settingsPanel.pack(fill='x')

        self.drawArea.pack(side="right", expand=True, fill="both")

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = 1
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.drawArea.bind('<B1-Motion>', self.paint)
        self.drawArea.bind('<ButtonRelease-1>', self.reset)
        self.vs.start()

    def paint(self, event):
        print("hey")
        frame = self.vs.read()
        image = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=image)
        Label(self.vidArea, image=imgtk).pack()
        self.line_width = 1
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.drawArea.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None


if __name__ == '__main__':
    Paint()