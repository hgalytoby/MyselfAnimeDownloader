import os
import sys
import json
import time
import shutil
import random
import datetime
import requests
from concurrent.futures import ThreadPoolExecutor
from UI.main_ui import Ui_Anime
from UI.config_ui import Ui_Config
from bs4 import BeautifulSoup
from PyQt5 import QtCore, QtWidgets, QtGui

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}


class Anime(QtWidgets.QMainWindow, Ui_Anime):
    def __init__(self):
        super(Anime, self).__init__()
        self.setupUi(self)
        self.res = requests.Session()
        self.video_data = dict()
        self.week_data()
        self.mouseHoverOnTabBar()
        self.anime_page_Visible()
        self.setFixedSize(self.width(), self.height())
        self.story_checkbox_dict = dict()
        self.menu.actions()[0].triggered.connect(self.config)
        self.story_list_all_pushButton.clicked.connect(self.check_checkbox)
        self.download_pushbutton.clicked.connect(self.download_anime)
        self.download_anime_Thread = dict()

    def download_anime(self):
        for i in self.story_checkbox_dict:
            if self.story_checkbox_dict[i].isChecked():
                data = json.loads(self.story_checkbox_dict[i].objectName())
                anime = data['data']['name'] + data['data']['num']
                if anime not in self.download_anime_Thread:
                    print('in')
                    self.download_anime_Thread[anime] = Download_Video(data=data)
                    self.download_anime_Thread[anime].download_video.connect(self.download_anime_task)
                    self.download_anime_Thread[anime].start()

    def download_anime_task(self, signal):
        print('完成度', '%.2f' % signal["success"], '%')
        if signal['success'] == 100 and self.download_anime_Thread[signal['td']].ok is True:
            # del self.download_anime_Thread[signal['td']]
            self.download_anime_Thread[signal['td']].terminate()

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
                anime_name.clicked.connect(self.week_button_event)
                update_num = QtWidgets.QLabel(f'<span style=\"{signal[i][m]["color"]}\">{signal[i][m]["update"]}')
                update_num.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
                form_layout.addRow(anime_name, update_num)
            week[i].setLayout(form_layout)

    def week_button_event(self):
        sender = self.sender()
        pushButton = self.findChild(QtWidgets.QPushButton, sender.objectName())
        url = pushButton.objectName()
        self.anime_info = Anime_info(url=url)
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

    def get_m3u8(self):
        pass

    # def get_video_url(self):
    #     # url = 'https://myself-bbs.com/thread-45388-1-1.html'
    #     res = 'https://v.myself-bbs.com/vpx/45388/001/'
    #     m3u8_url = 'https://vpx57.myself-bbs.com/45388/001/720p.m3u8'
    #     res = self.res.get(url=res, headers=self.headers).json()
    #     host = sorted(res['host'], key=lambda i: i.get('weight'), reverse=True)
    #     m3u8_data = self.res.get(url=host[0]['host'] + res['video']['720p'], headers=self.headers).text
    #     m3u8_count = m3u8_data.count('EXTINF')
    #     'https://vpx57.myself-bbs.com/45388/001/720p_003.ts'
    #     task = list()
    #     print(m3u8_count)
    #     for i in range(m3u8_count):
    #         video = f"{host[0]['host']}{res['video']['720p'].split('.')[0]}_{i:03d}.ts"
    #         threading.Thread(target=self.download_video, args=(i, video)).start()
    #     while True:
    #         if len(self.video_data) == m3u8_count:
    #             break
    #         time.sleep(1)
    #         print(len(self.video_data))
    #     for i in range(m3u8_count):
    #         with open('test.mp4', 'ab') as v:
    #             v.write(self.video_data[i])

        # v.write(data)

    # print(self.video_data)
    # data = self.res.get(url=video, headers=self.headers).content
    # print(data)
    # with open('test.mp4', 'ab') as v:
    #     v.write(data)
    # task.append(f"{host[0]['host']}{res['video']['720p'].split('.')[0]}{i:03d}.ts")

    # print(res, res.count('EXTINF'))

    # html = BeautifulSoup(res, features='lxml')
    # for i in html.find_all('ul', class_='main_list'):
    #     print(i)

    # print(url)
    # with open('test.mp4', 'ab') as v:
    #     v.write(data)


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

    def __init__(self, url):
        super(Anime_info, self).__init__()
        self.url = url

    def run(self):
        res = requests.get(url=self.url, headers=headers).text
        html = BeautifulSoup(res, features='lxml')
        data = dict()
        for i in html.find_all('ul', class_='main_list'):
            total = dict()
            for j, m in enumerate(i.find_all('a')):
                if j % 2 == 0:
                    title = m.text
                else:
                    url = str(m.attrs['data-href']).replace('player/play', 'vpx').replace('\r', '')
                    total.update({title: url})
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
                    data.update({'name': m.text})
        self.anime_info_signal.emit(data)


class Download_Video(QtCore.QThread):
    download_video = QtCore.pyqtSignal(dict)

    def __init__(self, data):
        super(Download_Video, self).__init__()
        self.data = data
        self.video_data = dict()
        self.ban = '//:*?"<>|.'
        self.td = dict()
        self.ok = False

    def badname(self, name):
        for i in self.ban:
            name = str(name).replace(i, ' ')
        return name.strip()

    def run(self):
        res = requests.get(url=self.data['data']['url'], headers=headers)
        print(res.json())
        while True:
            if res:
                break
            time.sleep(5)
        res = res.json()
        # print(res)
        # host = sorted(res['host'], key=lambda i: i.get('weight'), reverse=True)
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
            time.sleep(5)
            result = {'success': (len(self.video_data) / m3u8_count * 100),
                      'td': self.data["data"]["name"] + self.data["data"]["num"]}
            self.download_video.emit(result)
            print(f'{self.data["data"]["name"] + self.data["data"]["num"]} 目標:{m3u8_count} 當前:{len(self.video_data)}')
        self.write_video(m3u8_count)
        del self.video_data
        self.ok = True

    def write_video(self, m3u8_count):
        folder_name = self.badname(self.data['data']['name'])
        file_name = self.badname(self.data['data']['num'])
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        for i in range(m3u8_count):
            with open(f'{folder_name}/{file_name}.mp4', 'ab') as v:
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
        self.setFixedSize(self.width(), self.height())

    def config(self):
        if not os.path.isfile('config.json'):
            json.dump({'path': ''}, open('config.json', 'w', encoding='utf-8'))
        else:
            config = json.load(open('config.json', 'r', encoding='utf-8'))
            self.download_path_lineEdit.setText(config['path'])

    def save_config(self):
        path = self.download_path_lineEdit.text()
        json.dump({'path': path}, open('config.json', 'w', encoding='utf-8'))

    def download_path(self):
        download_path = QtWidgets.QFileDialog.getExistingDirectory(self, "選取資料夾")
        self.download_path_lineEdit.setText(download_path)

    def exit(self):
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    anime = Anime()
    anime.show()
    app.exec_()
