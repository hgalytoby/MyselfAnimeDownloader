from PyQt5 import QtWidgets, QtGui

from UI.about_ui import Ui_About


class About(QtWidgets.QMainWindow, Ui_About):
    """
    關於視窗。
    """

    def __init__(self):
        super(About, self, ).__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('image/logo.ico'))
        self.setFixedSize(self.width(), self.height())
        self.pixmap = QtGui.QPixmap("./image/logo.ico")
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setScaledContents(True)
        self.close_pushButton.clicked.connect(self.close)
