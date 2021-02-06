import re

from PyQt5 import QtWidgets


def check_url(self):
    """
    判斷 Myself 網的的指定動漫頁面。
    """
    url = self.customize_lineEdit.text().strip()
    if re.match(r'^https://myself-bbs.com/thread-[0-9]{5,5}-1-1.html$', url) or re.match(
            r'^https://myself-bbs.com/forum.php\Wmod=viewthread&tid=[0-9]{5,5}&.', url) or re.match(
        r'^https://www.myself-bbs.com/thread-[0-9]{5,5}-1-1.html$', url) or re.match(
        r'^https://www.myself-bbs.com/forum.php\Wmod=viewthread&tid=[0-9]{5,5}&.', url):
        self.loading_anime(url=url)
    else:
        if url[-1] == '/':
            url = url[:-1]
        self.url_error = QtWidgets.QMessageBox.information(self, '錯誤',
                                                           f"<font size=5  color=#000000>網址有誤！</font> <br/><font size=4  color=#000000>確認輸入的 <a href={url}>網址 </a><font size=4  color=#000000>是否正確！<",
                                                           QtWidgets.QMessageBox.Ok)
