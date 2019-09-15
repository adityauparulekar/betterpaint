import tkinter
from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
import time
from tkinter.colorchooser import askcolor
from tkinter.ttk import *

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.style = Style()
        self.window.style.theme_use('clam')
        self.window.geometry("1280x800")
        self.window.resizable(False, False)
        self.window.title(window_title)
        self.video_source = video_source
        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)
        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width=640, height=400)
        # self.canvas = tkinter.Canvas(window, width = window.winfo_screenwidth(), height = window.winfo_screenheight())

        self.canvas.grid(row=0, column=0, rowspan=3)
        # self.canvas.pack(side="left")

        self.drawArea = tkinter.Canvas(window, bg='white', width=640, height=800)
        self.drawArea.grid(row=0, column=1, rowspan=6)

        self.clearButton = Button(window, text="clear", command=self.clear)
        self.clearButton.grid(row=5, column=0)
        self.sizeSlider = Scale(window, from_=1, to=10, orient=HORIZONTAL, length=500)
        self.sizeSlider.grid(row=4, column=0)
        self.colorButton = Button(window, text="color", command=self.getColor)
        self.colorButton.grid(row=3, column=0)
        self.old_x = None
        self.old_y = None
        self.color = 'black'
        self.line_width = 1
        # self.drawArea.grid(row=1, columnspan=5)
        # self.drawArea.pack(side="right")
        self.setup()
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 50
        self.update()
        self.window.mainloop()
    def getColor(self):
        self.color = askcolor()[1]
        print(self.color)
    def reset(self, event):
        self.old_x, self.old_y = None, None
    def setup(self):
        self.drawArea.bind('<B1-Motion>', self.paint)
        self.drawArea.bind('<ButtonRelease-1>', self.reset)
    def paint(self, event):
        self.line_width = self.sizeSlider.get()
        paint_color = self.color
        if self.old_x and self.old_y:
            self.drawArea.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y
    def clear(self):
        self.drawArea.delete("all")
    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

        self.window.after(self.delay, self.update)

class MyVideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
            frame = cv2.flip(frame, 1)
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a window and pass it to the Application object
App(tkinter.Tk(), "Tkinter and OpenCV")