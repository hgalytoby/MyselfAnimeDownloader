import json
import os

from UI.login_ui import Ui_AccountLogin
from PyQt5 import QtWidgets

from myself_thread import LoginInit, MyselfLogin


class AccountLogin(QtWidgets.QMainWindow, Ui_AccountLogin):
    """
    設定視窗。
    """

    def __init__(self, main_label, main_button):
        super(AccountLogin, self).__init__()
        self.setupUi(self)
        self.main_label = main_label
        self.main_button = main_button
        self.login_dict = {}
        self.username = None
        self.load_user()
        self.init()
        self.login_pushButton.clicked.connect(self.login_event)
        self.question_comboBox.currentIndexChanged.connect(self.answer_lineEdit_event)

    def load_user(self):
        if os.path.isfile('user.json'):
            user = json.load(open('user.json', 'r', encoding='utf-8'))
            if user.get('account'):
                self.account_lineEdit.setText(user['account'])
            if user.get('password'):
                self.password_lineEdit.setText(user['password'])
            if user.get('remember'):
                if user['remember']:
                    self.remember_checkBox.setChecked(True)

    def init(self):
        self.login_init = LoginInit()
        self.login_init.login_init_signal.connect(self.login_init_mession)
        self.login_init.start()

    def answer_lineEdit_event(self, index):
        if index == 0:
            self.answer_lineEdit.setEnabled(False)
        else:
            self.answer_lineEdit.setEnabled(True)

    def login_init_mession(self, signal):
        self.login_dict.update(signal)
        for i, m in enumerate(signal['login']):
            self.account_comboBox.addItem(m)
        for i, m in enumerate(signal['question']):
            self.question_comboBox.addItem(m)

    def login_event(self):
        if self.login_dict:
            if not self.account_lineEdit.text():
                QtWidgets.QMessageBox().information(self, "確定", '請輸入帳號', QtWidgets.QMessageBox.Ok)
            elif not self.password_lineEdit.text():
                QtWidgets.QMessageBox().information(self, "確定", '請輸入密碼', QtWidgets.QMessageBox.Ok)
            else:
                self.username = self.account_lineEdit.text()
                login_data = {
                    'loginfield': self.login_dict['login'][self.account_comboBox.currentText()],
                    'username': self.username,
                    'password': self.password_lineEdit.text(),
                    'questionid': self.login_dict['question'][self.question_comboBox.currentText()],
                    'answer': self.answer_lineEdit.text()
                }
                if self.remember_checkBox.isChecked():
                    json.dump({'account': self.account_lineEdit.text(), 'password': self.password_lineEdit.text(),
                               'remember': True}, open('user.json', 'w', encoding='utf-8'), indent=2)
                else:
                    json.dump({'remember': False}, open('user.json', 'w', encoding='utf-8'), indent=2)
                self.login_pushButton.setEnabled(False)
                self.login_pushButton.setText('登入中')
                self.myself_login = MyselfLogin(login_data=login_data)
                self.myself_login.myself_login_signal.connect(self.login_mission)
                self.myself_login.start()
        else:
            QtWidgets.QMessageBox().information(self, "確定", '請在試一次', QtWidgets.QMessageBox.Ok)

    def login_mission(self, signal):
        if signal:
            self.main_label.setText(self.username)
            self.main_button.setText('登出')
            QtWidgets.QMessageBox().information(self, "確定", '登入成功', QtWidgets.QMessageBox.Ok)
            self.close()
        else:
            QtWidgets.QMessageBox().information(self, "確定", '登入失敗', QtWidgets.QMessageBox.Ok)
            self.login_pushButton.setEnabled(True)
            self.login_pushButton.setText('登入')
