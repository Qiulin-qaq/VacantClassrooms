import sys
import qrc
import logInWidget
from PyQt5.QtWidgets import QApplication

# 连接数据库
if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = logInWidget.logInWidget()
    w.show()

    app.exec_()
