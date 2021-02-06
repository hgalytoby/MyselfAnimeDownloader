from PyQt5 import QtWidgets

from LoginUI import AccountLogin
from myself_tools import myself_logout


def login_event(self):
    if self.login_pushButton.text() == '登入':
        self.account_login = AccountLogin(main_label=self.username_label, main_button=self.login_pushButton)
        self.account_login.show()
    else:
        myself_logout()
        QtWidgets.QMessageBox().information(self, "確定", '已登出', QtWidgets.QMessageBox.Ok)
        self.login_pushButton.setText('登入')
        self.username_label.setText('尚未登入')
