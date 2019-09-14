from PyQt5.QtWidgets import QApplication, QLabel, QPushButton

app = QApplication([])
app.setStyle('Fusion')
label = QLabel('Hello World!')
label.show()
button = QPushButton('Button')

def on_button_click():
    print('Detecting model')
    
button.clicked.connect(on_button_click)
button.show()

app.exec_()