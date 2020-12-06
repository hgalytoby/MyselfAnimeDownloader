from PyQt5 import QtWidgets


def check_version_task(self, signal):
    if signal:
        text = f"<br><br><font size=4  color=#000000>作者更新了！ <a href=https://github.com/hgalytoby/MyselfAnimeDownloader>GitHub</a>"
        QtWidgets.QMessageBox().about(self, '發現新版本', text)
    else:
        if self.check_version_result:
            text = f"<br><br>已經是最新版本了"
            QtWidgets.QMessageBox().about(self, '發現新版本', text)
    self.check_version_result = True
