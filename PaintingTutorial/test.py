from imutils.video import WebcamVideoStream
from tkinter import *
from PIL import Image, ImageTk

class Trial:
    def __init__(self):
        self.root = Tk()
        self.canvas = Canvas(self.root, width = 600, height = 800)
        self.canvas.pack()
        self.vs = WebcamVideoStream(src=0)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.canvas.bind('<B1-Motion>', self.paint)
        self.vs.start()
    
    def paint(self, event):
        frame = self.vs.read()
        print(frame)
        image = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=image)
        Label(self.canvas, image=imgtk).pack()

if __name__ == '__main__':
    Trial()
