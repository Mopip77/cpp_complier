from PyQt5.QtWidgets import QMainWindow,QApplication
from mainwindow import Ui_MainWindow
import sys

class myWindow(QMainWindow,Ui_MainWindow):

    def __init__(self):
        super(myWindow,self).__init__()
        self.setupUi(self)

if __name__ == "__main__":
    app=QApplication(sys.argv)
    myshow=myWindow()
    myshow.show()
    sys.exit(app.exec_())



