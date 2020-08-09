import os
import sys
import json
import time
import random
import datetime
import requests
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from UI.main_ui import Ui_Anime
from UI.config_ui import Ui_Config
from UI.save_ui import Ui_Save
from UI.note_ui import Ui_Note
from bs4 import BeautifulSoup
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}


class Anime(QtWidgets.QMainWindow, Ui_Anime):
    def __init__(self):
        super(Anime, self).__init__()
        self.setupUi(self)
        self.week_data()
        self.mouseHoverOnTabBar()
        self.anime_page_Visible()
        self.pushbutton_hand()
        self.setFixedSize(self.width(), self.height())
        self.menu.actions()[0].triggered.connect(self.config)
        self.story_list_all_pushButton.clicked.connect(self.check_checkbox)
        self.download_pushbutton.clicked.connect(self.download_anime)
        self.video_data = dict()
        self.story_checkbox_dict = dict()
        self.download_anime_Thread = dict()
        self.download_progressBar_dict = dict()
        self.download_status_label_dict = dict()
        self.download_count = 0
        self.get_html_queue = multiprocessing.Manager().Queue()
        self.result_html_queue = multiprocessing.Manager().Queue()
        self.download_tableWidget.setColumnWidth(0, 400)
        self.download_tableWidget.setColumnWidth(1, 150)
        # self.download_tableWidget.setColumnWidth(2, 431)
        self.download_tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

    def pushbutton_hand(self):
        self.story_list_all_pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.download_pushbutton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def download_anime(self):
        for i in self.story_checkbox_dict:
            if self.story_checkbox_dict[i].isChecked():
                data = json.loads(self.story_checkbox_dict[i].objectName())
                anime = data['data']['name'] + data['data']['num']
                if anime not in self.download_anime_Thread:
                    self.download_tableWidget.setRowCount(self.download_count + 1)
                    name = QtWidgets.QTableWidgetItem(f"{data['data']['name']}　　{data['data']['num']}")
                    status = QtWidgets.QTableWidgetItem('準備中')
                    self.download_progressBar_dict.update({anime: QtWidgets.QProgressBar()})
                    self.download_progressBar_dict[anime].setValue(0)
                    self.download_progressBar_dict[anime].setAlignment(QtCore.Qt.AlignCenter)
                    self.download_status_label_dict.update({anime: status})
                    self.download_status_label_dict[anime].setTextAlignment(QtCore.Qt.AlignCenter)
                    self.download_tableWidget.setItem(self.download_count, 0, name)
                    self.download_tableWidget.setItem(self.download_count, 1, status)
                    self.download_tableWidget.setCellWidget(self.download_count, 2,
                                                            self.download_progressBar_dict[anime])
                    self.download_count += 1
                    self.download_anime_Thread[anime] = Download_Video(data=data)
                    self.download_anime_Thread[anime].download_video.connect(self.download_anime_task)
                    self.download_anime_Thread[anime].start()

    def download_anime_task(self, signal):
        if int(signal['success']) == 100 and signal['status']:
            self.download_status_label_dict[signal['name']].setText('已完成')
            self.download_progressBar_dict[signal['name']].setValue(100)
            self.download_anime_Thread[signal['name']].terminate()
        else:
            self.download_status_label_dict[signal['name']].setText('下載中')
            self.download_progressBar_dict[signal['name']].setValue(signal["success"] - 1)

    def config(self):
        self.config_windows = Config()
        self.config_windows.show()

    def check_checkbox(self):
        if self.story_list_all_pushButton.text() == '全選':
            for i in self.story_checkbox_dict:
                self.story_checkbox_dict[i].setChecked(True)
            self.story_list_all_pushButton.setText('取消全選')
        else:
            for i in self.story_checkbox_dict:
                self.story_checkbox_dict[i].setChecked(False)
            self.story_list_all_pushButton.setText('全選')

    def anime_page_Visible(self, status=False):
        if status:
            self.image_label.setVisible(True)
            self.type_label.setVisible(True)
            self.premiere_label.setVisible(True)
            self.total_set_label.setVisible(True)
            self.author_label.setVisible(True)
            self.web_label.setVisible(True)
            self.remarks_label.setVisible(True)
            self.introduction_textBrowser.setVisible(True)
            self.story_list_label.setVisible(True)
            self.story_list_all_pushButton.setVisible(True)
            self.story_list_scrollArea.setVisible(True)
            self.download_pushbutton.setVisible(True)
        else:
            self.image_label.setVisible(False)
            self.type_label.setVisible(False)
            self.premiere_label.setVisible(False)
            self.total_set_label.setVisible(False)
            self.author_label.setVisible(False)
            self.web_label.setVisible(False)
            self.remarks_label.setVisible(False)
            self.introduction_textBrowser.setVisible(False)
            self.story_list_label.setVisible(False)
            self.story_list_all_pushButton.setVisible(False)
            self.story_list_scrollArea.setVisible(False)
            self.download_pushbutton.setVisible(False)

    def week_data(self):
        self._week_data = Week_data_signal()
        self._week_data.week_data_signal.connect(self.week_data_task)
        self._week_data.start()

    def week_data_task(self, signal):
        week = {0: self.Monday_scrollAreaWidgetContents, 1: self.Tuesday_scrollAreaWidgetContents,
                2: self.Wednesday_scrollAreaWidgetContents, 3: self.Thursday_scrollAreaWidgetContents,
                4: self.Friday_scrollAreaWidgetContents, 5: self.Staurday_scrollAreaWidgetContents,
                6: self.Sunday_scrollAreaWidgetContents}
        for i in signal:
            form_layout = QtWidgets.QFormLayout()
            for j, m in enumerate(signal[i]):
                anime_name = QtWidgets.QPushButton('．' + m)
                anime_name.setObjectName(signal[i][m]['url'])
                anime_name.setStyleSheet("QPushButton {\n"
                                         "background-color:transparent;\n"
                                         "color: #339900;\n"
                                         "font-size:22px;\n"
                                         "}"
                                         "QPushButton:hover{background-color:transparent; color: black;}\n"
                                         "QPushButton:pressed{\n"
                                         "background-color: #ffffff;\n"
                                         "border-style: inset;\n"
                                         "color: black;\n"
                                         " }\n"
                                         )
                anime_name.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                anime_name.clicked.connect(self.week_button_event)
                update_num = QtWidgets.QLabel(
                    f'<span style=\" font-size:16pt; {signal[i][m]["color"]}\">{signal[i][m]["update"]}')
                update_num.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
                form_layout.addRow(anime_name, update_num)
            week[i].setLayout(form_layout)

    def week_button_event(self):
        sender = self.sender()
        pushButton = self.findChild(QtWidgets.QPushButton, sender.objectName())
        url = pushButton.objectName()
        executor = ProcessPoolExecutor(max_workers=1)
        executor.submit(html, self.get_html_queue, self.result_html_queue, 'one')
        self.anime_info = Anime_info(url=url, get_html_queue=self.get_html_queue,
                                     result_html_queue=self.result_html_queue)
        self.anime_info.anime_info_signal.connect(self.anime_info_data)
        self.anime_info.start()
        self.anime_info_tabWidget.setCurrentIndex(1)
        self.anime_page_Visible()

    def anime_info_data(self, signal):
        self.story_list_all_pushButton.setText('全選')
        self.introduction_textBrowser.clear()
        self.story_checkbox_dict.clear()
        pix = QtGui.QPixmap()
        pix.loadFromData(signal['image'])
        self.image_label.clear()
        self.image_label.setPixmap(pix)
        self.type_label.setText(signal[0])
        self.premiere_label.setText(signal[1])
        self.total_set_label.setText(signal[2])
        self.author_label.setText(signal[3])
        self.web_label.setText(signal[4])
        self.remarks_label.setText(signal[5])
        self.introduction_textBrowser.setHtml(
            '<p style=\" color: #000000;\"font-size:16pt;>劇情介紹</p>\n' + signal['info'])
        for i in range(self.story_list_scrollAreaWidgetContents_Layout.count()):
            self.story_list_scrollAreaWidgetContents_Layout.itemAt(i).widget().deleteLater()
        if 60 + len(signal['total']) * 20 > 200:
            self.story_list_scrollArea.setGeometry(QtCore.QRect(10, 100, 211, 211))
        else:
            self.story_list_scrollArea.setGeometry(QtCore.QRect(10, 100, 211, 60 + len(signal['total']) * 20))
        for i, m in enumerate(signal['total']):
            checkbox = QtWidgets.QCheckBox(m)
            data = json.dumps({'data': {'name': signal['name'], 'num': m, 'url': signal['total'][m]}})
            checkbox.setObjectName(data)
            self.story_checkbox_dict.update({i: checkbox})
            self.story_list_scrollAreaWidgetContents_Layout.addWidget(checkbox)
        self.anime_page_Visible(status=True)
        self.anime_info.terminate()

    def mouseHoverOnTabBar(self):
        self.tabBar = self.week_tabWidget.tabBar()
        self.tabBar.setMouseTracking(True)
        self.tabBar.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.tabBar:
            if event.type() == QtCore.QEvent.MouseMove:
                index = self.tabBar.tabAt(event.pos())
                self.tabBar.setCurrentIndex(index)
                return True
        return super().eventFilter(obj, event)


class Week_data_signal(QtCore.QThread):
    week_data_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(Week_data_signal, self).__init__()

    def run(self):
        res = requests.get(url='https://myself-bbs.com/portal.php', headers=headers).text
        html = BeautifulSoup(res, features='lxml')
        week_dict = dict()
        for i in html.find_all('div', id='tabSuCvYn'):
            for index, j in enumerate(i.find_all('div', class_='module cl xl xl1')):
                num = j.find_all('a') + j.find_all('span')
                color = list()
                anime_data = dict()
                for k, v in enumerate(j.find_all('font')):
                    if k % 3 == 2:
                        color.append(v.attrs['style'])
                for k in range(len(num) // 2):
                    anime_data.update({num[k]['title']: {'update': num[k + len(num) // 2].text, 'color': color[k],
                                                         'url': f'https://myself-bbs.com/{num[k]["href"]}'}})
                week_dict.update({index: anime_data})
        self.week_data_signal.emit(week_dict)


class Anime_info(QtCore.QThread):
    anime_info_signal = QtCore.pyqtSignal(dict)

    def __init__(self, url, get_html_queue, result_html_queue):
        super(Anime_info, self).__init__()
        self.url = url
        self.get_html_queue = get_html_queue
        self.result_html_queue = result_html_queue

    def getter(self):
        while True:
            if self.result_html_queue.qsize() > 0:
                res = self.result_html_queue.get()
                return res
            time.sleep(1)

    def run(self):
        print('in')
        self.get_html_queue.put(self.url)
        res = self.getter()
        html = BeautifulSoup(res, features='lxml')
        data = dict()
        for i in html.find_all('ul', class_='main_list'):
            total = dict()
            title = list()
            for j in i.find_all('a', href="javascript:;"):
                title.append(j.text)
            for j, m in enumerate(i.find_all('ul', class_="display_none")):
                for k in m.find_all('a'):
                    if k.text == '站內':
                        url = str(k['data-href']).replace('player/play', 'vpx').replace('\n', '').replace('\r', '')
                        total.update({title[j]: url})
            data.update({'total': total})
        for i in html.find_all('div', class_='info_info'):
            for j, m in enumerate(i.find_all('li')):
                data.update({j: m.text})
                # print(j, m.text)
        for i in html.find_all('div', class_='info_introduction'):
            for j in i.find_all('p'):
                data.update({'info': j.text})
                # print(j.text)
        for i in html.find_all('div', class_='info_img_box fl'):
            for j in i.find_all('img'):
                # print(j['src'])
                image = requests.get(url=j['src'], headers=headers).content
                data.update({'image': image})
        for i in html.find_all('div', class_='z'):
            for j, m in enumerate(i.find_all('a')):
                if j == 4:
                    data.update({'name': m.text.split('【')[0]})
        self.anime_info_signal.emit(data)


class Download_Video(QtCore.QThread):
    download_video = QtCore.pyqtSignal(dict)

    def __init__(self, data):
        super(Download_Video, self).__init__()
        self.data = data
        self.video_data = dict()
        self.ban = '//:*?"<>|.'
        self.result = dict()
        self.folder_name = self.badname(self.data['data']['name'])
        self.file_name = self.badname(self.data['data']['num'])
        self.path = json.load(open('config.json', 'r', encoding='utf-8'))

    def badname(self, name):
        for i in self.ban:
            name = str(name).replace(i, ' ')
        return name.strip()

    def run(self):
        if not os.path.isdir(f'{self.path["path"]}/{self.folder_name}'):
            os.mkdir(f'{self.path["path"]}/{self.folder_name}')
        res = requests.get(url=self.data['data']['url'], headers=headers)
        while True:
            if res:
                break
            time.sleep(5)
        res = res.json()
        host = res['host']
        m3u8_data = requests.get(url=host[0]['host'] + res['video']['720p'], headers=headers)
        while True:
            if m3u8_data:
                break
            time.sleep(5)
        m3u8_data = m3u8_data.text
        m3u8_count = m3u8_data.count('EXTINF')
        executor = ThreadPoolExecutor(max_workers=20)
        for i in range(m3u8_count):
            executor.submit(self.video, i, res, host)
        while True:
            if len(self.video_data) == m3u8_count:
                break
            time.sleep(1)
            self.result.update({'success': int((len(self.video_data) / m3u8_count * 100)),
                                'name': self.data["data"]["name"] + self.data["data"]["num"],
                                'status': False})
            self.download_video.emit(self.result)
            print(f'{self.data["data"]["name"] + self.data["data"]["num"]} 目標:{m3u8_count} 當前:{len(self.video_data)}')
        self.write_video(m3u8_count)
        del self.video_data
        self.result['status'] = True
        self.download_video.emit(self.result)

    def write_video(self, m3u8_count):
        for i in range(m3u8_count):
            with open(f'{self.path["path"]}/{self.folder_name}/{self.file_name}.mp4', 'ab') as v:
                v.write(self.video_data[i])

    def video(self, i, res, host):
        url = f"{random.choices(host)[0]['host']}{res['video']['720p'].split('.')[0]}_{i:03d}.ts"
        while True:
            try:
                data = requests.get(url=url, headers=headers, timeout=60)
                if data:
                    self.video_data[i] = data.content
                    break
                else:
                    url = f"{random.choices(host)[0]['host']}{res['video']['720p'].split('.')[0]}_{i:03d}.ts"
                    time.sleep(5)
            except:
                url = f"{random.choices(host)[0]['host']}{res['video']['720p'].split('.')[0]}_{i:03d}.ts"
                time.sleep(5)


class Config(QtWidgets.QMainWindow, Ui_Config):
    def __init__(self):
        super(Config, self).__init__()
        self.setupUi(self)
        self.config()
        self.browse_pushButton.clicked.connect(self.download_path)
        self.save_pushButton.clicked.connect(self.save_config)
        self.cancel_pushButton.clicked.connect(self.exit)
        self.note_pushButton.clicked.connect(self.note_event)

    def config(self):
        self.setFixedSize(self.width(), self.height())
        self.note_pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.cancel_pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.save_pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.browse_pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        if not os.path.isfile('config.json'):
            json.dump({'path': ''}, open('config.json', 'w', encoding='utf-8'), indent=2)
        else:
            config = json.load(open('config.json', 'r', encoding='utf-8'))
            self.download_path_lineEdit.setText(config['path'])

    def save_config(self):
        path = self.download_path_lineEdit.text()
        json.dump({'path': path}, open('config.json', 'w', encoding='utf-8'), indent=2)
        self.save = Save(config=self)
        self.save.show()

    def download_path(self):
        download_path = QtWidgets.QFileDialog.getExistingDirectory(self, "選取資料夾", self.download_path_lineEdit.text())
        self.download_path_lineEdit.setText(download_path)

    def note_event(self):
        self.note_windows = Note()
        self.note_windows.show()

    def exit(self):
        self.close()


class Save(QtWidgets.QMainWindow, Ui_Save):
    def __init__(self, config):
        super(Save, self, ).__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.confirm_pushButton.clicked.connect(self.confirm)
        self.config = config

    def confirm(self):
        self.close()
        self.config.close()


class Note(QtWidgets.QMainWindow, Ui_Note):
    def __init__(self):
        super(Note, self, ).__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.confirm_pushButton.clicked.connect(self.confirm)

    def confirm(self):
        self.close()


def html(get_html=None, result_html=None, choose='one'):
    """
    兩種用法，結果都是一樣的。
    1.
    app = QtWidgets.QApplication(sys.argv)
    browser = QtWebEngineWidgets.QWebEngineView()
    browser.load(QtCore.QUrl(url))
    browser.loadFinished.connect(on_load_finished)
    app.exec_()
    2.
    r = render(url)
    result_html.put(r)
    """

    def render(url):

        class Render(QtWebEngineWidgets.QWebEngineView):
            def __init__(self, url):
                self.html = None
                self.app = QtWidgets.QApplication(sys.argv)
                QtWebEngineWidgets.QWebEngineView.__init__(self)
                self.loadFinished.connect(self._loadFinished)
                self.load(QtCore.QUrl(url))
                while self.html is None:
                    self.app.processEvents(
                        QtCore.QEventLoop.ExcludeUserInputEvents | QtCore.QEventLoop.ExcludeSocketNotifiers | QtCore.QEventLoop.WaitForMoreEvents)
                self.app.quit()

            def _callable(self, data):
                self.html = data

            def _loadFinished(self, result):
                self.page().toHtml(self._callable)

        return Render(url).html

    def callback_function(html):
        result_html.put(html)
        browser.close()

    def on_load_finished():
        browser.page().runJavaScript("document.getElementsByTagName('html')[0].innerHTML", callback_function)

    while True:
        if get_html.qsize() > 0:
            url = get_html.get()
            if choose == 'one':
                r = render(url)
                result_html.put(r)
            else:
                app = QtWidgets.QApplication(sys.argv)
                browser = QtWebEngineWidgets.QWebEngineView()
                browser.load(QtCore.QUrl(url))
                browser.loadFinished.connect(on_load_finished)
                app.exec_()
            break
        time.sleep(1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    anime = Anime()
    anime.show()
    app.exec_()
