from PyQt5 import QtCore, QtWidgets, QtGui


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, MainWindow, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.ui = MainWindow
        self.menu = QtWidgets.QMenu()
        self.show_window_action = QtWidgets.QAction("啟動", self, triggered=self.show_window)
        self.show_msg_action = QtWidgets.QAction("顯示通知", self, triggered=self.showMsg)
        self.quit_action = QtWidgets.QAction("退出", self, triggered=self.quit)
        self.menu.addAction(self.show_window_action)
        self.menu.addAction(self.show_msg_action)
        self.menu.addAction(self.quit_action)
        self.setContextMenu(self.menu)
        self.setIcon(QtGui.QIcon('./image/logo.ico'))
        self.icon = QtGui.QIcon('./image/logo.ico')
        self.activated.connect(self.onIconClicked)

    def showMsg(self):
        self.showMessage("Message", "幫我此專案 GitHub 按星星~ 謝謝您!", self.icon)

    def show_window(self):
        self.ui.showNormal()
        self.ui.activateWindow()

    def quit(self):
        QtWidgets.qApp.quit()

    # 點擊 icon 傳送的信號會有一個整數值，1=右键，2=連續兩下左鍵，3=單點左鍵，4=滾輪點擊
    def onIconClicked(self, reason):
        if reason == 2 or reason == 3:
            if self.ui.isMinimized() or not self.ui.isVisible():
                self.ui.showNormal()
                self.ui.activateWindow()
                self.ui.setWindowFlags(QtCore.Qt.Window)
                self.ui.show()
            else:
                self.ui.showMinimized()
                self.ui.setWindowFlags(QtCore.Qt.SplashScreen)
                self.ui.show()
