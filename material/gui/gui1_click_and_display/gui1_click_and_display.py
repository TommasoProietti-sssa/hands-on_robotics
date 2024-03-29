import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

class main_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('gui1_click_and_display.ui', self) # load user interface

        self.counter1 = 0
        self.counter2 = 0
        self.counter3 = 0

        # connect button to function on_click
        self.pushButton1.clicked.connect(self.on_click1)  
        self.pushButton2.clicked.connect(self.on_click2)  
        self.pushButton3.clicked.connect(self.on_click3)     

        # [improvement 1] lambda functions
        # self.pushButton1.clicked.connect(lambda: self.on_click(1))
        # self.pushButton2.clicked.connect(lambda: self.on_click(2))
        # self.pushButton3.clicked.connect(lambda: self.on_click(3))   

    def on_click1(self):
        print('Button 1 clicked')
        self.counter1 += 1
        self.lcdNumber1.display(self.counter1)
    
    def on_click2(self):
        print('Button 2 clicked')
        self.counter2 += 1
        self.lcdNumber2.display(self.counter2)

    def on_click3(self):
        print('Button 3 clicked')
        self.counter3 += 1
        self.lcdNumber3.display(self.counter3)

    # [improvement 1] lambda functions
    # def on_click(self, button):
    #     if button == 1:
    #         print('Button 1 clicked')
    #         self.counter1 += 1
    #         self.lcdNumber1.display(self.counter1)
    #     elif button == 2:
    #         print('Button 2 clicked')
    #         self.counter2 += 1
    #         self.lcdNumber2.display(self.counter2)
    #     elif button == 3:
    #         print('Button 3 clicked')
    #         self.counter3 += 1
    #         self.lcdNumber3.display(self.counter3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = main_window() 
    w.show()
    sys.exit(app.exec_())
