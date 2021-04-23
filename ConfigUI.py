import json

from UI.config_ui import Ui_Config
from PyQt5 import QtWidgets, QtGui


class Config(QtWidgets.QMainWindow, Ui_Config):
    """
    設定視窗。
    """

    def __init__(self, anime):
        super(Config, self).__init__()
        self.setupUi(self)
        self.anime = anime
        self.config()
        self.setWindowIcon(QtGui.QIcon('image/logo.ico'))
        self.setFixedSize(self.width(), self.height())
        self.browse_pushButton.clicked.connect(self.download_path)
        self.save_pushButton.clicked.connect(self.save_config)
        self.cancel_pushButton.clicked.connect(self.close)
        self.simultaneous_download_lineEdit.setValidator(QtGui.QIntValidator())
        self.re_download_lineEdit.setValidator(QtGui.QIntValidator())
        self.note_pushButton.clicked.connect(self.note_message_box)
        self.speed_radioButton_dict = {self.slow_radioButton: {'type': 'slow', 'value': 1},
                                       self.genera_radioButton: {'type': 'genera', 'value': 3},
                                       self.high_radioButton: {'type': 'high', 'value': 6},
                                       self.starburst_radioButton: {'type': 'starburst', 'value': 10}}

    def note_message_box(self):
        """
        注意事項視窗。
        """
        QtWidgets.QMessageBox().information(self, "注意事項",
                                            '慢速: 1 次 1 個連接<br/>一般: 1 次 3 個連接<br/>高速: 1 次 6 個連接<br/>星爆: 1 次 10 個連接<br/><br/>連接值:1次取得多少影片來源。<br/>連接值越高吃的網速就越多。<br/>同時下載數量越高，記憶體與網速就吃越多。',
                                            QtWidgets.QMessageBox.Ok)

    def config(self):
        """
        設定視窗介面讀取個個物件設定值。
        """
        config = json.load(open('config.json', 'r', encoding='utf-8'))
        self.download_path_lineEdit.setText(config['path'])
        if config['speed']['type'] == 'genera':
            self.genera_radioButton.setChecked(True)
        elif config['speed']['type'] == 'high':
            self.high_radioButton.setChecked(True)
        elif config['speed']['type'] == 'starburst':
            self.starburst_radioButton.setChecked(True)
        else:
            self.slow_radioButton.setChecked(True)
        self.simultaneous_download_lineEdit.setText(str(config['simultaneous']))
        self.re_download_lineEdit.setText(str(config['re_download']['min']))
        if not config['re_download']['status']:
            self.re_download_Checkbox.setChecked(False)

    def save_config(self):
        """
        儲存按鈕事件。
        """
        path = self.download_path_lineEdit.text()
        simultaneous = int(self.simultaneous_download_lineEdit.text())
        re_time = int(self.re_download_lineEdit.text())
        if 0 > simultaneous:
            QtWidgets.QMessageBox().warning(self, '愛調皮', '調皮!輸入正整數哦!', QtWidgets.QMessageBox.Ok)
            self.simultaneous_download_lineEdit.setText('5')
        elif 0 > re_time:
            QtWidgets.QMessageBox().warning(self, '愛調皮', '調皮!輸入正整數哦!', QtWidgets.QMessageBox.Ok)
            self.re_download_lineEdit.setText('2')
        else:
            for i in self.speed_radioButton_dict:
                if i.isChecked():
                    speed = self.speed_radioButton_dict[i]
                    break
            data = {'path': path, 'speed': speed, 'simultaneous': simultaneous,
                    're_download': {'status': True, 'min': re_time}}
            if not self.re_download_Checkbox.isChecked():
                data['re_download']['status'] = False
            json.dump(data, open('config.json', 'w', encoding='utf-8'), indent=2)
            self.anime.save_path = data['path']
            self.anime.simultaneously_value = data['simultaneous']
            self.anime.speed_value = data['speed']['value']
            self.anime.re_download_status = data['re_download']['status']
            self.anime.re_download_min = data['re_download']['min']
            QtWidgets.QMessageBox().information(self, '儲存', "<font size='6'>資料已成功地儲存。</font>", QtWidgets.QMessageBox.Ok)
            self.close()

    def download_path(self):
        """
        瀏覽資料夾按鈕。
        """
        download_path = QtWidgets.QFileDialog.getExistingDirectory(self, "選取資料夾", self.download_path_lineEdit.text())
        self.download_path_lineEdit.setText(download_path)
