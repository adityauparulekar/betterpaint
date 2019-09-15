import sys
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QDialog, QPushButton, QLabel, QMainWindow
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QImage, QPixmap
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QPoint, QThread
import cv2

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, parent=None, szImage=None):
        super().__init__(parent=parent)
        self.sz = szImage


    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret: 
                frame = cv2.flip(frame, 1)
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(self.sz.width() + 100, self.sz.height(), Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

class VideoComponent(QWidget):
    def __init__(self, sz):
        super().__init__()

        self.label = QLabel(self)
        print(f'{sz.width()} {sz.height()}')
        self.label.resize(sz.width(), sz.height())

        th = Thread(self, sz)
        th.changePixmap.connect(self.setImage)
        th.start()
    
    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

class Canvas(QWidget):
    def __init__(self):
        super().__init__()

        self.drawing = False
        self.brushSize = 2
        self.brushColor = Qt.black

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.lastPoint = QPoint()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
    
    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.drawing = False
    
    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

                
class Content(QWidget):
    def __init__(self, sz):
        super().__init__()
        self.initUI(sz)

    def initUI(self, sz):
        layout = QGridLayout()

        def vidButton():
            print('V i d e o')

        def setButton():
            print('S e t t i n g')

        # Temp set 0,0 Slot as Button instead of Video
        vc = VideoComponent(sz / 2)
        vButton = QPushButton('video here')
        vButton.clicked.connect(vidButton)
        layout.addWidget(vc, 0, 0)

        # Temp set 0,1 Slot as Button instead of Full Settings
        sButton = QPushButton('settings here')
        sButton.clicked.connect(setButton)
        layout.addWidget(sButton, 1, 0)

        self.canvas = Canvas()
        layout.addWidget(self.canvas, 0, 1, -1, 1)
        self.setLayout(layout)

class App(QMainWindow):
    def __init__(self, sz):
        super().__init__()
        con = Content(sz)
        self.setCentralWidget(con)

        self.setWindowTitle('FingerPaint')
        self.setFixedSize(sz)
        self.showMaximized()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    screen = app.primaryScreen()
    ex = App(screen.size())

    sys.exit(app.exec_())
