import tkinter
from tkinter import *
import cv2
import PIL.Image
import PIL.ImageTk
import time
from tkinter.colorchooser import askcolor
from tkinter.ttk import *
import numpy as np
import math
import json

hand_hist = None
traverse_point = []
total_rectangle = 9
hand_rect_one_x = None
hand_rect_one_y = None

hand_rect_two_x = None
hand_rect_two_y = None


def rescale_frame(frame, wpercent=80, hpercent=80):
    width = int(frame.shape[1] * wpercent / 100)
    height = int(frame.shape[0] * hpercent / 100)
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)


def contours(hist_mask_image):
    gray_hist_mask_image = cv2.cvtColor(hist_mask_image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_hist_mask_image, 0, 255, 0)
    cont, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return cont


def max_contour(contour_list):
    max_i = 0
    max_area = 0

    for i in range(len(contour_list)):
        cnt = contour_list[i]

        area_cnt = cv2.contourArea(cnt)

        if area_cnt > max_area:
            max_area = area_cnt
            max_i = i

        return contour_list[max_i]


def draw_rect(frame):
    rows, cols, _ = frame.shape
    global total_rectangle, hand_rect_one_x, hand_rect_one_y, hand_rect_two_x, hand_rect_two_y

    hand_rect_one_x = np.array(
        [6 * rows / 20, 6 * rows / 20, 6 * rows / 20, 9 * rows / 20, 9 * rows / 20, 9 * rows / 20, 12 * rows / 20,
         12 * rows / 20, 12 * rows / 20], dtype=np.uint32)

    hand_rect_one_y = np.array(
        [9 * cols / 20, 10 * cols / 20, 11 * cols / 20, 9 * cols / 20, 10 * cols / 20, 11 * cols / 20, 9 * cols / 20,
         10 * cols / 20, 11 * cols / 20], dtype=np.uint32)

    hand_rect_two_x = hand_rect_one_x + 10
    hand_rect_two_y = hand_rect_one_y + 10

    for i in range(total_rectangle):
        cv2.rectangle(frame, (hand_rect_one_y[i], hand_rect_one_x[i]),
                      (hand_rect_two_y[i], hand_rect_two_x[i]),
                      (0, 255, 0), 1)

    return frame


def hand_histogram(frame, roiAlt, use):
    global hand_rect_one_x, hand_rect_one_y

    if use == True:
        hand_hist = cv2.calcHist([roiAlt], [0, 1], None, [180, 256], [0, 180, 0, 256])
    else:
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        roi = np.zeros([90, 10, 3], dtype=hsv_frame.dtype)

        for i in range(total_rectangle):
            roi[i * 10: i * 10 + 10, 0: 10] = hsv_frame[hand_rect_one_x[i]:hand_rect_one_x[i] + 10, hand_rect_one_y[i]:hand_rect_one_y[i] + 10]

        hand_hist = cv2.calcHist([roi], [0, 1], None, [180, 256], [0, 180, 0, 256])
        
    return cv2.normalize(hand_hist, hand_hist, 0, 255, cv2.NORM_MINMAX)


def hist_masking(frame, hist):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0, 1], hist, [0, 180, 0, 256], 1)

        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
        cv2.filter2D(dst, -1, disc, dst)

        ret, thresh = cv2.threshold(dst, 150, 255, cv2.THRESH_BINARY)
        # thresh = cv2.dilate(thresh, None, iterations=5)

        thresh = cv2.merge((thresh, thresh, thresh))

        # cv2.imshow("image", cv2.bitwise_and(frame, thresh))
        return cv2.bitwise_and(frame, thresh)


def centroid(max_contour):
    moment = cv2.moments(max_contour)
    if moment['m00'] != 0:
        cx = int(moment['m10'] / moment['m00'])
        cy = int(moment['m01'] / moment['m00'])
        return cx, cy
    else:
        return None

def closestTo(centroidList, lastPoint):
    min_index = 0
    minVal = 1000000000
    lastx = 0
    lasty = 0
    if lastPoint is not None:
        lastx = lastPoint[0]
        lasty = lastPoint[1]
    for i in range(len(centroidList)):
        if centroidList[i] is not None:
            x = centroidList[i][0]
            y = centroidList[i][1]
            xp = pow(x-lastx, 2)
            yp = pow(y-lasty, 2)
            sum = xp + yp
            dist = math.sqrt(sum)
            if dist < minVal:
                min_index = i
                minVal = dist
    return centroidList[min_index]

def draw_circles(frame, traverse_point):
    if traverse_point is not None:
        for i in range(len(traverse_point)):
            cv2.circle(frame, traverse_point[i], int(5 - (5 * i * 3) / 100), [0, 255, 255], -1)

def manage_image_opr(frame, hand_hist):
    hist_mask_image = hist_masking(frame, hand_hist)
    contour_list = contours(hist_mask_image)

    max_cont = max_contour(contour_list)
    cnt_max = centroid(max_cont)

    centroids = []
    for i in range(0,len(contour_list)):
        centroids.append(centroid(contour_list[i]))
    
    cv2.circle(frame, cnt_max, 5, [255, 0, 255], -1)

    if max_cont is not None:
        hull = cv2.convexHull(max_cont, returnPoints=False)
        defects = cv2.convexityDefects(max_cont, hull)
        far_point = (0,0)
        #if len(traverse_point) >= 2:
        #    far_point = minCost(contour_list[i], traverse_point[len(traverse_point - 2)], traverse_point[len(traverse_point - 1)])
        if len(traverse_point) >= 1:
            far_point = closestTo(centroids, traverse_point[len(traverse_point) - 1])
        else:
            far_point = cnt_max
            
        cv2.circle(frame, far_point, 5, [0, 0, 255], -1)

        if len(traverse_point) < 20:
            traverse_point.append(far_point)
        else:
            traverse_point.pop(0)
            traverse_point.append(far_point)

        draw_circles(frame, traverse_point)


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

        self.drawArea = tkinter.Canvas(
            window, bg='white', width=640, height=800)
        self.drawArea.grid(row=0, column=1, rowspan=6)

        self.clearButton = Button(window, text="clear", command=self.clear)
        self.clearButton.grid(row=5, column=0)
        self.sizeSlider = Scale(window, from_=1, to=10,
                                orient=HORIZONTAL, length=500)
        self.sizeSlider.grid(row=4, column=0)
        self.colorButton = Button(window, text="color", command=self.getColor)
        self.colorButton.grid(row=3, column=0)
        self.old_x = None
        self.old_y = None
        self.color = 'black'
        self.line_width = 1
        self.cursor_x = 100
        self.cursor_y = 100
        self.cursor = None
        self.drawEnable = False
        self.points = [None] * 5
        # self.drawArea.grid(row=1, columnspan=5)
        # self.drawArea.pack(side="right")
        self.setup()
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 50
        self.update()
        self.window.mainloop()

    def getColor(self):
        self.color = askcolor()[1]
        if self.cursor:
            self.drawArea.delete(self.cursor)
        radius = 15
        self.cursor = self.drawArea.create_oval(self.cursor_x - radius / 2, self.cursor_y - radius / 2, self.cursor_x + radius / 2, self.cursor_y + radius / 2, outline=self.color)
    def reset(self, event):
        self.old_x, self.old_y = None, None
    def setup(self):
        self.drawArea.bind('<B1-Motion>', self.paint)
        self.drawArea.bind('<ButtonRelease-1>', self.reset)
        self.window.bind('<KeyPress-a>', self.push)
        self.window.bind('<KeyRelease-a>', self.release)
        # self.drawArea.bind('<B1-Motion>', self.push)
        # self.drawArea.bind('<ButtonRelease-1>', self.release)
    def paint(self, event):
        self.line_width = self.sizeSlider.get()
        if self.cursor:
            self.drawArea.delete(self.cursor)
        
        radius = 15
        self.cursor = self.drawArea.create_oval(self.cursor_x - radius / 2, self.cursor_y - radius / 2, self.cursor_x + radius / 2, self.cursor_y + radius / 2, outline=self.color)

        paint_color = self.color
        if self.old_x and self.old_y:
            self.drawArea.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y
        self.cursor_x = event.x
        self.cursor_y = event.y

    def rotate(self, point):
        self.points = self.points[1:] + [point]
    # method for drawing a point
    def draw(self, x, y):
        self.rotate([x, y])
        numValid = 0
        netPoint = [0, 0]
        for i in range(len(self.points)):
            if self.points[i]:
                netPoint[0] += self.points[i][0]
                netPoint[1] += self.points[i][1]
                numValid+=1
        netPoint = [netPoint[0] / numValid, netPoint[1] * 2 / numValid]
        self.line_width = self.sizeSlider.get()
        if self.cursor:
            self.drawArea.delete(self.cursor)
        
        radius = 15

        if self.old_x and self.old_y:
            if self.drawEnable:
                self.drawArea.create_line(self.old_x, self.old_y, netPoint[0], netPoint[1],
                                width=self.line_width, fill=self.color,
                                capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = netPoint[0]
        self.old_y = netPoint[1]
        self.cursor_x = netPoint[0]
        self.cursor_y = netPoint[1]
        self.cursor = self.drawArea.create_oval(self.cursor_x - radius / 2, self.cursor_y - radius / 2, self.cursor_x + radius / 2, self.cursor_y + radius / 2, outline=self.color)

    def push(self, event):
        self.drawEnable = True

    def release(self, event):
        self.drawEnable = False
        

    def clear(self):
        self.drawArea.delete("all")
    def update(self):
        # Get a frame from the video source
        ret, frame, x, y = self.vid.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

        self.draw(640 - x, y)

        self.window.after(self.delay, self.update)

class MyVideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            
            ret, frame = self.vid.read()
            frame = cv2.resize(frame, None, fx=1.0, fy=1.0)
            
            manage_image_opr(frame, hand_hist)

            frame = cv2.flip(frame, 1)
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), traverse_point[-1][0], traverse_point[-1][1])
            else:
                return (ret, None, traverse_point[-1][0], traverse_point[-1][1])
        else:
            return (ret, None, traverse_point[-1][0], traverse_point[-1][1])

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a window and pass it to the Application object

def main():
    global hand_hist
    is_hand_hist_created = False
    capture = cv2.VideoCapture(0)

    while capture.isOpened():
        pressed_key = cv2.waitKey(1)
        _, frame = capture.read()

        if pressed_key & 0xFF == ord('z'):
            is_hand_hist_created = True
            hand_hist = hand_histogram(frame, "lmao", False)

        if is_hand_hist_created:
            break

        else:
            frame = draw_rect(frame)

        cv2.imshow("Calibrating Pointer", cv2.flip(rescale_frame(frame), 1))

        if pressed_key == 27:
            break

    cv2.destroyAllWindows()
    capture.release()

    App(tkinter.Tk(), "fingerpaint")

if __name__ == '__main__':
    main()
