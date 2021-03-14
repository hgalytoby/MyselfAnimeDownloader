import json
import sys

from UI.myself_close_ui import Ui_MyselfClose

from PyQt5 import QtWidgets, QtGui, Qt

from myself_thread import ProcessExit


class MyselfClose(QtWidgets.QWidget, Ui_MyselfClose):
    def __init__(self, anime):
        super(MyselfClose, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.Qt.CustomizeWindowHint)
        self.setFixedSize(self.width(), self.height())
        self.pixmap = QtGui.QPixmap("./image/logo.png")
        self.logo_label.setPixmap(self.pixmap)
        self.logo_label.setScaledContents(True)
        self.anime = anime
        self.process_exit = ProcessExit(anime=self.anime)
        self.process_exit.process_exit_signal.connect(self.process_exit_task)
        self.process_exit.start()

    def process_exit_task(self, signal):
        QtWidgets.QApplication.closeAllWindows()
