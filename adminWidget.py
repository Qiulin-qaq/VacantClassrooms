from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class adminLoginWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.ui = uic.loadUi("./ui/adminWidget.ui")
