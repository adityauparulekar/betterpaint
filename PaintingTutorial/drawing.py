import sys
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QDialog, QPushButton
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import pyqtSlot


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        left = 0
        top = 30
        width = 1600
        height = 1000

        # self.setGeometry(left, top, width, height)
        layout = QGridLayout()

        def vidButton():
            print('V i d e o')

        def setButton():
            print('S e t t i n g')

        # Temp set 0,0 Slot as Button instead of Video
        vButton = QPushButton('video here')
        vButton.clicked.connect(vidButton)
        layout.addWidget(vButton, 0, 0)

        # Temp set 0,1 Slot as Button instead of Full Settings
        sButton = QPushButton('settings here')
        sButton.clicked.connect(setButton)
        layout.addWidget(sButton, 1, 0)

        cv = Canvas()
        cButton = QPushButton('canvas here')
        layout.addWidget(cButton, 0, 1, -1, 1)
        self.setWindowTitle('FingerPaint')
        self.setLayout(layout)
        self.show()


class Canvas(QWidget):
    def __init__(self):
        super().__init__()


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.text = "Woah I can display text on a Canvas"
        self.setGeometry(0, 30, 1000, 1000)
        self.setWindowTitle('Drawing text')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        # RGB for QColor
        qp.setPen(QColor(168, 34, 200))
        # Second Argument Font Size
        qp.setFont(QFont('Decorative', 20))
        qp.drawText(event.rect(), Qt.AlignCenter, self.text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
