import os
import sys
import json
import time
import random
import gc
import re
import shutil
import psutil
import datetime
import requests
# import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from UI.main_ui import Ui_Anime
from UI.config_ui import Ui_Config
from UI.save_ui import Ui_Save
from UI.note_ui import Ui_Note
from UI.url_ui import Ui_Url
from bs4 import BeautifulSoup
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}


class MyProxyStyle(QtWidgets.QProxyStyle):
    pass

    def pixelMetric(self, QStyle_PixelMetric, option=None, widget=None):

        if QStyle_PixelMetric == QtWidgets.QStyle.PM_SmallIconSize:
            return 40
        else:
            return QtWidgets.QProxyStyle.pixelMetric(self, QStyle_PixelMetric, option, widget)


class Anime(QtWidgets.QMainWindow, Ui_Anime):
    def __init__(self):
        super(Anime, self).__init__()
        self.setupUi(self)
        self.pid = os.getpid()
        self.setWindowIcon(QtGui.QIcon('image/logo.ico'))
        self.download_tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.write_config()
        self.load_week_data()
        self.anime_page_Visible()
        self.load_anime_label.setVisible(False)
        self.mouseHoverOnTabBar()
        self.loading_config_status()
        self.setFixedSize(self.width(), self.height())
        self.week = {0: self.Monday_scrollAreaWidgetContents, 1: self.Tuesday_scrollAreaWidgetContents,
                     2: self.Wednesday_scrollAreaWidgetContents, 3: self.Thursday_scrollAreaWidgetContents,
                     4: self.Friday_scrollAreaWidgetContents, 5: self.Staurday_scrollAreaWidgetContents,
                     6: self.Sunday_scrollAreaWidgetContents}
        # self.menu.actions()[0].triggered.connect(config.show)
        self.menu.actions()[2].triggered.connect(self.closeEvent)
        self.story_list_all_pushButton.clicked.connect(self.check_checkbox)
        self.download_pushbutton.clicked.connect(self.download_anime)
        self.customize_pushButton.clicked.connect(self.anime_info_event)
        self.now_download_value = 1
        self.download_tableWidget_rowcount = 0
        self.download_video_mission_list = list()
        self.week_dict = dict()
        self.week_layout = dict()
        self.story_checkbox_dict = dict()
        self.download_anime_Thread = dict()
        self.download_progressBar_dict = dict()
        self.download_status_label_dict = dict()
        self.tableWidgetItem_download_dict = dict()
        self.download_tableWidget.setColumnWidth(0, 400)
        self.download_tableWidget.setColumnWidth(1, 150)
        # self.download_tableWidget.setColumnWidth(2, 431)
        self.download_tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.download_tableWidget.cellClicked.connect(self.print_row)
        self.load_week_label_status = False
        self.load_anime_label_status = False
        self.download_tableWidget.verticalHeader().setVisible(False)
        self.download_tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.anime_info_tabWidget.currentChanged.connect(self.doubleClicked_table)
        self.download_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.download_tableWidget.customContextMenuRequested.connect(self.on_customContextMenuRequested)
        self.download_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.pushButton.clicked.connect(self.del_ob)

    def del_ob(self):
        gc.collect()

    def on_customContextMenuRequested(self, pos):
        # print(pos)
        # it = self.download_tableWidget.itemAt(pos)
        select = list()
        # for i in self.download_tableWidget.selectedItems()[::2]:
        #     select.append(i.row())
        for i in self.download_tableWidget.selectedIndexes()[::3]:
            select.append(i.row())
        select.sort(reverse=True)

        # select.sort(reverse=True)
        # print(self.download_tableWidget.selectionModel().selection().indexes())
        # if it is None:
        #     return
        # row = it.row()
        # column = it.column()
        # item_range = QtWidgets.QTableWidgetSelectionRange(0, c, self.download_tableWidget.rowCount() - 1, c)
        # self.download_tableWidget.setRangeSelected(item_range, True)
        # if len(select) == 0:
        #     return None
        # menu = QtWidgets.QMenu()
        # if len(select) > 1:
        #     delete_row_action = menu.addAction("刪除所有選取項目")
        # else:
        #     delete_row_action = menu.addAction("刪除選取項目")
        # all_delete_row_action = menu.addAction("清除已完成")
        # action = menu.exec_(self.download_tableWidget.viewport().mapToGlobal(pos))
        # if action == delete_row_action:
        #     for i in select:
        #         download_anime_Thread_name = self.download_tableWidget.item(i, 0).text()
        #         download_anime_Thread_name = ''.join(download_anime_Thread_name.split('　　'))
        #         # self.download_anime_Thread[download_anime_Thread_name].terminate()
        #         del self.download_anime_Thread[download_anime_Thread_name]
        #         # self.download_anime_Thread[download_anime_Thread_name].wait()
        #         self.download_tableWidget.removeRow(i)
        # elif action == all_delete_row_action:
        #     pass

    def doubleClicked_table(self, index):
        if index != 0 and not self.load_week_label_status:
            self.load_week_label.setVisible(False)
        elif index == 0 and not self.load_week_label_status:
            self.load_week_label.setVisible(True)
        if index != 1 and self.load_anime_label_status:
            self.load_anime_label.setVisible(False)
        elif index == 1 and self.load_anime_label_status:
            self.load_anime_label.setVisible(True)

    def print_row(self, r, c):
        print(r, c)

    def status(self):
        pass

    def closeEvent(self, event):
        QtWidgets.QApplication.closeAllWindows()

    def write_config(self):
        config = {'path': os.getcwd(), 'speed': {'type': 'slow', 'value': 1}, 'simultaneous': 5}
        if not os.path.isfile('config.json'):
            json.dump(config, open('config.json', 'w', encoding='utf-8'), indent=2)
        else:
            data = json.load(open('config.json', 'r', encoding='utf-8'))
            for i in config:
                if i not in data:
                    data[i] = config[i]
            json.dump(data, open('config.json', 'w', encoding='utf-8'), indent=2)

    def loading_config_status(self):
        self.config_status = Loading_config_status(pid=os.getpid())
        self.config_status.loading_config_status_signal.connect(self.loading_config_status_mission)
        self.config_status.start()

    def loading_config_status_mission(self, signal):
        self.simultaneously_value = signal['simultaneous']
        self.speed_value = signal['speed']['value']
        self.left_status_label.setText(
            f'狀態: {self.now_download_value - 1} 個下載中　　連接設定: {self.speed_value} / {self.simultaneously_value}')
        self.right_ststus_label.setText(f'記憶體: {signal["memory"]}MB / 程序: {signal["cpu"]}%')
        # gc.collect()

    def download_anime(self):
        for i in self.story_checkbox_dict:
            if self.story_checkbox_dict[i].isChecked():
                data = json.loads(self.story_checkbox_dict[i].objectName())
                anime = data['data']['name'] + data['data']['num']
                if anime not in self.download_anime_Thread:
                    self.download_tableWidget.setRowCount(self.download_tableWidget_rowcount + 1)
                    self.tableWidgetItem_download_dict.update(
                        {anime: {'name': QtWidgets.QTableWidgetItem(f"{data['data']['name']}　　{data['data']['num']}"),
                                 'status': QtWidgets.QTableWidgetItem('準備中'),
                                 'schedule': QtWidgets.QProgressBar()}})
                    self.tableWidgetItem_download_dict[anime]['status'].setTextAlignment(QtCore.Qt.AlignCenter)
                    self.tableWidgetItem_download_dict[anime]['schedule'].setValue(0)
                    self.tableWidgetItem_download_dict[anime]['schedule'].setAlignment(QtCore.Qt.AlignCenter)
                    self.download_tableWidget.setItem(self.download_tableWidget_rowcount, 0,
                                                      self.tableWidgetItem_download_dict[anime]['name'])
                    self.download_tableWidget.setItem(self.download_tableWidget_rowcount, 1,
                                                      self.tableWidgetItem_download_dict[anime]['status'])
                    self.download_tableWidget.setCellWidget(self.download_tableWidget_rowcount, 2,
                                                            self.tableWidgetItem_download_dict[anime]['schedule'])
                    self.download_tableWidget_rowcount += 1
                    self.download_video_mission_list.append(anime)
                    self.download_anime_Thread[anime] = Download_Video(data=data)
                    self.download_anime_Thread[anime].download_video.connect(self.download_anime_task)
                    self.download_anime_Thread[anime].start()

    def download_anime_task(self, signal):
        if int(signal['success']) == 100:
            self.tableWidgetItem_download_dict[signal['name']]['status'].setText('已完成')
            self.tableWidgetItem_download_dict[signal['name']]['schedule'].setValue(signal["success"])
            # self.download_anime_Thread[signal['name']].terminate()
            # self.download_anime_Thread[signal['name']].quit()
            # self.download_anime_Thread[signal['name']].wait()
            del self.download_anime_Thread[signal['name']]
        else:
            self.tableWidgetItem_download_dict[signal['name']]['status'].setText('下載中')
            self.tableWidgetItem_download_dict[signal['name']]['schedule'].setValue(signal["success"])

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
            self.load_anime_label.setVisible(False)
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
            self.load_anime_label.setVisible(True)
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

    def load_week_data(self):
        self.week_data = Week_data_signal()
        self.week_data.week_data_signal.connect(self.week_data_task)
        self.week_data.start()

    def week_data_task(self, signal):
        for i in signal:
            self.week_layout.update({i: QtWidgets.QFormLayout()})
            for j, m in enumerate(signal[i]):
                self.week_dict.update({m: {'pushbutton': QtWidgets.QPushButton('．' + m),
                                           'update': QtWidgets.QLabel(
                                               f'<span style=\" font-size:16pt; {signal[i][m]["color"]}\">{signal[i][m]["update"]}')}})
                self.week_dict[m]['pushbutton'].setObjectName(signal[i][m]['url'])
                self.week_dict[m]['pushbutton'].setStyleSheet("QPushButton {\n"
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
                self.week_dict[m]['pushbutton'].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.week_dict[m]['pushbutton'].clicked.connect(self.anime_info_event)
                self.week_dict[m]['update'].setAlignment(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
                self.week_layout[i].addRow(self.week_dict[m]['pushbutton'], self.week_dict[m]['update'])
            self.week[i].setLayout(self.week_layout[i])
        self.load_week_label.setVisible(False)
        self.load_week_label_status = True
        # self.week_data.quit()
        # self.week_data.wait()
        del self.week_data

    def anime_info_event(self):
        sender = self.sender()
        pushButton = self.findChild(QtWidgets.QPushButton, sender.objectName())
        ok = True
        if pushButton.objectName() == 'customize_pushButton':
            if re.match('^https://myself-bbs.com/thread-[0-9]{4,6}-\d-\d.html$',
                        self.customize_lineEdit.text().strip()):
                url = self.customize_lineEdit.text().strip()
            else:
                url = self.customize_lineEdit.text().strip()
                self.url_error = QtWidgets.QMessageBox.information(self, '錯誤',
                                                                   f"<font size=5  color=#000000>網址有誤！</font> <br/><font size=4  color=#000000>確認輸入的 <a href={url}>網址 </a><font size=4  color=#000000>是否正確！<",
                                                                   QtWidgets.QMessageBox.Ok)
                # QMessageBox {
                #     background-color: #333333;
                # }
                #
                # QMessageBox QLabel {
                #     color: #aaa;
                # }
                ok = False
        else:
            url = pushButton.objectName()
        if ok:
            self.load_anime_label.setVisible(True)
            self.load_anime_label_status = True
            self.anime_info = Anime_info(url=url)
            self.anime_info.anime_info_signal.connect(self.anime_info_data)
            self.anime_info.start()
            self.anime_info_tabWidget.setCurrentIndex(1)
            self.anime_page_Visible()

    def anime_info_data(self, signal):
        self.customize_lineEdit.clear()
        self.story_list_all_pushButton.setText('全選')
        self.introduction_textBrowser.clear()
        self.story_checkbox_dict.clear()
        self.pix = QtGui.QPixmap()
        self.pix.loadFromData(signal['image'])
        self.image_label.clear()
        self.image_label.setPixmap(self.pix)
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
            data = json.dumps({'data': {'name': signal['name'], 'num': m, 'url': signal['total'][m]}})
            self.story_checkbox_dict.update({i: QtWidgets.QCheckBox(m)})
            self.story_checkbox_dict[i].setObjectName(data)
            self.story_list_scrollAreaWidgetContents_Layout.addWidget(self.story_checkbox_dict[i])
        self.anime_page_Visible(status=True)
        self.load_anime_label_status = False
        # self.anime_info.terminate()
        # self.anime_info.wait()
        # self.anime_info.quit()
        # del self.anime_info

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
        del res, html
        self.week_data_signal.emit(week_dict)


class Anime_info(QtCore.QThread):
    anime_info_signal = QtCore.pyqtSignal(dict)

    def __init__(self, url):
        super(Anime_info, self).__init__()
        self.url = url

    def get_anime_data(self):
        res = requests.get(url=self.url, headers=headers).text
        html = BeautifulSoup(res, features='lxml')
        data = dict()
        total = dict()
        for i in html.select('ul.main_list'):
            for j in i.find_all('a', href='javascript:;'):
                title = j.text
                for k in j.parent.select("ul.display_none li"):
                    a = k.select_one("a[data-href*='v.myself-bbs.com']")
                    if k.select_one("a").text == '站內':
                        url = a["data-href"].replace('player/play', 'vpx').replace("\r", "").replace("\n", "")
                        total.update({title: url})
        data.update({'total': total})
        for i in html.find_all('div', class_='info_info'):
            for j, m in enumerate(i.find_all('li')):
                data.update({j: m.text})
        for i in html.find_all('div', class_='info_introduction'):
            for j in i.find_all('p'):
                data.update({'info': j.text})
        for i in html.find_all('div', class_='info_img_box fl'):
            for j in i.find_all('img'):
                image = requests.get(url=j['src'], headers=headers).content
                data.update({'image': image})
                del image
        for i in html.find_all('div', class_='z'):
            for j, m in enumerate(i.find_all('a')):
                if j == 4:
                    data.update({'name': m.text.split('【')[0]})
        del res, html
        return data

    def run(self):
        data = self.get_anime_data()
        self.anime_info_signal.emit(data)


class Download_Video(QtCore.QThread):
    download_video = QtCore.pyqtSignal(dict)

    def __init__(self, data):
        super(Download_Video, self).__init__()
        self.data = data
        self.video_data = 0
        self.ban = '//:*?"<>|.'
        self.result = dict()
        self.stop = False
        self.folder_name = self.badname(self.data['data']['name'])
        self.file_name = self.badname(self.data['data']['num'])
        self.path = json.load(open('config.json', 'r', encoding='utf-8'))

    def badname(self, name):
        for i in self.ban:
            name = str(name).replace(i, ' ')
        return name.strip()

    def get_host_video_data(self):
        while True:
            try:
                res = requests.get(url=self.data['data']['url'], headers=headers, timeout=5)
                if res:
                    return res.json()
            except:
                time.sleep(5)

    def get_m3u8_data(self, res):
        while True:
            try:
                m3u8_data = requests.get(url=res['host'][0]['host'] + res['video']['720p'], headers=headers, timeout=5)
                if m3u8_data:
                    return m3u8_data.text
            except:
                time.sleep(5)

    def video(self, i, res, host):
        host_value = 0
        url = f"{host[host_value]['host']}{res['video']['720p'].split('.')[0]}_{i:03d}.ts"
        while True:
            try:
                data = requests.get(url=url, headers=headers, stream=True, timeout=3)
                # data = requests.get(url=url, headers=headers, timeout=3)
                if data:
                    while True:
                        if self.video_data == i:
                            with open(f'{self.path["path"]}/{self.folder_name}/{self.file_name}.mp4', 'ab') as v:
                                shutil.copyfileobj(data.raw, v)
                                # v.write(data.content)
                            del data
                            self.video_data += 1
                            break
                        time.sleep(1)
                    break
            except:
                host_value += 1
                url = f"{host[host_value]['host']}{res['video']['720p'].split('.')[0]}_{i:03d}.ts"
                time.sleep(1)

    def turn_me(self):
        while True:
            if anime.download_video_mission_list[0] == self.data["data"]["name"] + self.data["data"]["num"] \
                    and anime.simultaneously_value >= anime.now_download_value:
                anime.now_download_value += 1
                del anime.download_video_mission_list[0]
                break
            time.sleep(3)

    def run(self):
        if not os.path.isdir(f'{self.path["path"]}/{self.folder_name}'):
            os.mkdir(f'{self.path["path"]}/{self.folder_name}')
        self.turn_me()
        res = self.get_host_video_data()
        m3u8_data = self.get_m3u8_data(res)
        m3u8_count = m3u8_data.count('EXTINF')
        executor = ThreadPoolExecutor(max_workers=anime.speed_value)
        host = sorted(res['host'], key=lambda i: i.get('weight'), reverse=True)
        # if os.path.isfile(f'{self.path["path"]}/{self.folder_name}/{self.file_name}.tmp'):
        #     os.remove(f'{self.path["path"]}/{self.folder_name}/{self.file_name}.tmp')
        for i in range(m3u8_count):
            executor.submit(self.video, i, res, host)
        while True:
            self.result.update({'success': int(self.video_data / m3u8_count * 100),
                                'name': self.data["data"]["name"] + self.data["data"]["num"],
                                })
            if self.video_data == m3u8_count:
                self.download_video.emit(self.result)
                anime.now_download_value -= 1
                break
            self.download_video.emit(self.result)
            time.sleep(1)
        self.quit()
        self.wait()


class Loading_config_status(QtCore.QThread):
    loading_config_status_signal = QtCore.pyqtSignal(dict)

    def __init__(self, pid):
        super(Loading_config_status, self).__init__()
        self.info = psutil.Process(pid)

    def run(self):
        while True:
            config = json.load(open('config.json', 'r', encoding='utf-8'))
            cpu = '%.2f' % (self.info.cpu_percent() / psutil.cpu_count())
            memory = '%.2f' % (self.info.memory_full_info().uss / 1024 / 1024)
            config.update({'cpu': cpu, 'memory': memory})
            # self.info.memory_full_info().rss / 1024 / 1024
            # self.info.cpu_percent(interval=1), self.info.memory_info()[0] / float(2 ** 20)
            self.loading_config_status_signal.emit(config)
            time.sleep(1)


class Config(QtWidgets.QMainWindow, Ui_Config):
    def __init__(self):
        super(Config, self).__init__()
        self.setupUi(self)
        self.config()
        self.setFixedSize(self.width(), self.height())
        self.browse_pushButton.clicked.connect(self.download_path)
        self.save_pushButton.clicked.connect(self.save_config)
        self.cancel_pushButton.clicked.connect(self.close)
        self.simultaneous_download_lineEdit.setValidator(QtGui.QIntValidator())
        self.note_pushButton.clicked.connect(self.note_message_box)
        self.speed_radioButton_dict = {self.slow_radioButton: {'type': 'slow', 'value': 1},
                                       self.genera_radioButton: {'type': 'genera', 'value': 3},
                                       self.high_radioButton: {'type': 'high', 'value': 8},
                                       self.starburst_radioButton: {'type': 'starburst', 'value': 16}}

    def note_message_box(self):
        QtWidgets.QMessageBox().information(self, "注意事項",
                                            '慢速: 1 次 1 個連接<br/>一般: 1 次 3 個連接<br/>高速: 1 次 8 個連接<br/>星爆: 1 次 16 個連接<br/><br/>連接值:1次取得多少影片來源。<br/>連接值越高吃的網速就越多。<br/>同時下載數量越高，記憶體與網速就吃越多。',
                                            QtWidgets.QMessageBox.Yes)

    def config(self):
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

    def save_config(self):
        path = self.download_path_lineEdit.text()
        simultaneous = self.simultaneous_download_lineEdit.text()
        for i in self.speed_radioButton_dict:
            if i.isChecked():
                speed = self.speed_radioButton_dict[i]
                break
        data = {'path': path, 'speed': speed, 'simultaneous': int(simultaneous)}
        json.dump(data, open('config.json', 'w', encoding='utf-8'), indent=2)
        save.config = self
        save.show()

    def download_path(self):
        download_path = QtWidgets.QFileDialog.getExistingDirectory(self, "選取資料夾", self.download_path_lineEdit.text())
        self.download_path_lineEdit.setText(download_path)


class Save(QtWidgets.QMainWindow, Ui_Save):
    def __init__(self, config=None):
        super(Save, self, ).__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.confirm_pushButton.clicked.connect(self.confirm)
        self.config = config

    def confirm(self):
        self.close()
        self.config.close()


# def html(get_html=None, result_html=None, choose='one'):
#     """
#     兩種用法，結果都是一樣的。
#     1.
#     app = QtWidgets.QApplication(sys.argv)
#     browser = QtWebEngineWidgets.QWebEngineView()
#     browser.load(QtCore.QUrl(url))
#     browser.loadFinished.connect(on_load_finished)
#     app.exec_()
#     2.
#     r = render(url)
#     result_html.put(r)
#     """
#
#     def render(url):
#
#         class Render(QtWebEngineWidgets.QWebEngineView):
#             def __init__(self, url):
#                 self.html = None
#                 self.app = QtWidgets.QApplication(sys.argv)
#                 QtWebEngineWidgets.QWebEngineView.__init__(self)
#                 self.loadFinished.connect(self._loadFinished)
#                 self.load(QtCore.QUrl(url))
#                 while self.html is None:
#                     self.app.processEvents(
#                         QtCore.QEventLoop.ExcludeUserInputEvents | QtCore.QEventLoop.ExcludeSocketNotifiers | QtCore.QEventLoop.WaitForMoreEvents)
#                 self.app.quit()
#
#             def _callable(self, data):
#                 self.html = data
#
#             def _loadFinished(self, result):
#                 self.page().toHtml(self._callable)
#
#         return Render(url).html
#
#     def callback_function(html):
#         result_html.put(html)
#         browser.close()
#
#     def on_load_finished():
#         browser.page().runJavaScript("document.getElementsByTagName('html')[0].innerHTML", callback_function)
#
#     while True:
#         if get_html.qsize() > 0:
#             url = get_html.get()
#             if choose == 'one':
#                 r = render(url)
#                 result_html.put(r)
#             else:
#                 app = QtWidgets.QApplication(sys.argv)
#                 browser = QtWebEngineWidgets.QWebEngineView()
#                 browser.load(QtCore.QUrl(url))
#                 browser.loadFinished.connect(on_load_finished)
#                 app.exec_()
#             break
#         time.sleep(1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # myStyle = MyProxyStyle()
    # app.setStyle(myStyle)
    anime = Anime()
    config = Config()
    save = Save()
    anime.menu.actions()[0].triggered.connect(config.show)
    # note = QMessageBox.information(self,  # 使用infomation信息框
    #                                "标题",
    #                                "消息" * 10,
    #                                )
    # config.note_pushButton.clicked.connect(lambda: emsg.showMessage('Message: ' + lineedit.text()))

    anime.show()
    app.exec_()

    # print(os.getpid())
    # print(psutil.virtual_memory())
    # process = psutil.Process(os.getpid())
    # while True:
    #     # for i in range(10):
    #
    #     print(process.cpu_percent(),'|' , psutil.Process(os.getpid()).memory_info().rss)
    #     time.sleep(10)
    # # print(info)
    # url = 'https://myself-bbs.com/thread-45043-1-1.html'
    #
    # print(re.match('^https://myself-bbs.com/thread-[0-9]{4,6}-\d-\d.html$', url))
    # # # print(psutil.Process(os.getpid()).memory_info().rss)
    # # while True:
    # #     info = psutil.Process(os.getpid())
    # #     print(info.cpu_percent(), '...',info.memory_percent())
    # #     time.sleep(0.2)
    # pass
