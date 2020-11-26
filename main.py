import os
import re
import sys
import json
import time
# import gc
import shutil
import psutil
import datetime
import requests
import webbrowser
# from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from UI.main_ui import Ui_Anime
from UI.config_ui import Ui_Config
from UI.about_ui import Ui_About
from bs4 import BeautifulSoup
from PyQt5 import QtCore, QtWidgets, QtGui

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
        self.ban = '//:*?"<>|.'
        self.now_download_value = 0
        self.load_week_label_status = False
        self.load_anime_label_status = False
        self.load_end_anime_status = False
        self.thread_write_download_order_status = False
        self.week_dict = dict()
        self.end_tab = dict()
        self.end_qt_object = dict()
        self.week_layout_dict = dict()
        self.story_checkbox_dict = dict()
        self.download_anime_Thread = dict()
        self.history_tableWidget_dict = dict()
        self.download_progressBar_dict = dict()
        self.download_status_label_dict = dict()
        self.tableWidgetItem_download_dict = dict()
        self.pid = os.getpid()
        self.setWindowIcon(QtGui.QIcon('image/logo.ico'))
        self.download_tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.save_path, self.simultaneously_value, self.speed_value, self.wait_download_video_mission_list, self.now_download_video_mission_list = self.basic_config()
        self.load_week_data()
        self.anime_page_Visible()
        self.load_anime_label.setVisible(False)
        self.load_end_anime_label.setVisible(False)
        self.tabBar = self.mouseHoverOnTabBar()
        self.loading_config_status()
        self.load_download_menu()
        self.load_history()
        self.loading_end_anime()
        self.setFixedSize(self.width(), self.height())
        self.week = {0: self.Monday_scrollAreaWidgetContents, 1: self.Tuesday_scrollAreaWidgetContents,
                     2: self.Wednesday_scrollAreaWidgetContents, 3: self.Thursday_scrollAreaWidgetContents,
                     4: self.Friday_scrollAreaWidgetContents, 5: self.Staurday_scrollAreaWidgetContents,
                     6: self.Sunday_scrollAreaWidgetContents}
        self.download_tableWidget.setColumnWidth(0, 400)
        self.download_tableWidget.setColumnWidth(1, 150)
        # self.download_tableWidget.setColumnWidth(2, 431)
        self.download_tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.download_tableWidget.cellClicked.connect(self.print_row)
        self.download_tableWidget.verticalHeader().setVisible(False)
        self.download_tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.download_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.download_tableWidget.customContextMenuRequested.connect(
            self.download_tableWidget_on_custom_context_menu_requested)
        self.download_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.history_tableWidget.setColumnWidth(1, 150)
        self.history_tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.history_tableWidget.verticalHeader().setVisible(False)
        self.history_tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.history_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.history_tableWidget.customContextMenuRequested.connect(
            self.history_tableWidget_on_custom_context_menu_requested)
        self.history_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # self.menu.actions()[0].triggered.connect(config.show)
        self.menu.actions()[2].triggered.connect(self.closeEvent)
        self.story_list_all_pushButton.clicked.connect(self.check_checkbox)
        self.download_pushbutton.clicked.connect(self.download_anime)
        self.customize_pushButton.clicked.connect(self.check_url)
        self.anime_info_tabWidget.currentChanged.connect(self.click_on_tablewidget)

    def badname(self, name):
        """
        避免不正當名字出現導致資料夾或檔案無法創建。
        """
        for i in self.ban:
            name = str(name).replace(i, ' ')
        return name.strip()

    def history_tableWidget_on_custom_context_menu_requested(self, pos):
        item = self.history_tableWidget.itemAt(pos)
        menu = QtWidgets.QMenu()
        go_home_action = menu.addAction('前往官網')
        load_anime_action = menu.addAction('讀取動漫資訊')
        delete_select_history_action = menu.addAction('清除選取的歷史紀錄')
        delete_all_history_action = menu.addAction('清除所有歷史紀錄')
        select = dict()
        for i in self.history_tableWidget.selectedIndexes()[::1]:
            tableWidget_item_name = self.history_tableWidget.item(i.row(), 0).text()
            tableWidget_item_name = ''.join(tableWidget_item_name.split('　　'))
            select.update({i.row(): tableWidget_item_name})
        if item is None:
            go_home_action.setVisible(False)
            delete_all_history_action.setVisible(True)
            load_anime_action.setVisible(False)
            delete_select_history_action.setVisible(False)
        else:
            go_home_action.setVisible(True)
            delete_all_history_action.setVisible(True)
            load_anime_action.setVisible(True)
            delete_select_history_action.setVisible(True)
        action = menu.exec_(self.history_tableWidget.viewport().mapToGlobal(pos))
        if action == go_home_action:
            webbrowser.open(self.history_tableWidget_dict[select[list(select.keys())[0]]]['home'])
        elif action == load_anime_action:
            self.loading_anime(url=self.history_tableWidget_dict[select[list(select.keys())[0]]]['home'])
        elif action == delete_select_history_action:
            self.history_delete_list(data=select, mode='select')
        elif action == delete_all_history_action:
            self.history_delete_list(data=select, mode='all')

    def history_delete_list(self, data=None, mode=None):
        data = dict(sorted(data.items(), reverse=True))
        if mode == 'all':
            text = '確定刪除所有歷史紀錄？'
        else:
            text = '確定刪除所選取的歷史紀錄？'
        msg = QtWidgets.QMessageBox().information(self, '確認', text, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No,
                                                  QtWidgets.QMessageBox.No)
        if msg == QtWidgets.QMessageBox.Ok:
            if mode == 'all':
                for i in os.listdir('./Log/history/'):
                    os.remove(f'./Log/history/{i}')
                self.history_tableWidget_dict.clear()
            else:
                for i in data:
                    os.remove(f'./Log/history/{data[i]}.json')
                    del self.history_tableWidget_dict[data[i]]

    def download_tableWidget_on_custom_context_menu_requested(self, pos):
        """
        下載清單頁面，右鍵選單功能。
        """
        item = self.download_tableWidget.itemAt(pos)
        # row = item.row()
        # column = item.column()
        # item_range = QtWidgets.QTableWidgetSelectionRange(0, c, self.download_tableWidget.rowCount() - 1, c)
        # self.download_tableWidget.setRangeSelected(item_range, True)
        # # print(self.download_tableWidget.selectionModel().selection().indexes())
        # if it is None:
        # else:
        menu = QtWidgets.QMenu()
        select = dict()
        for i in self.download_tableWidget.selectedIndexes()[::3]:
            tableWidget_item_name = self.download_tableWidget.item(i.row(), 0).text()
            directory_name = tableWidget_item_name.split("　　")[0]
            file_name = tableWidget_item_name.split("　　")[1]
            download_anime_Thread_name = directory_name + file_name
            select.update({i.row(): {'directory': directory_name,
                                     'file_name': file_name,
                                     'thread': download_anime_Thread_name,
                                     'name': tableWidget_item_name}})
        open_directory = menu.addAction('打開目錄')
        completed_delete_action = menu.addAction('已完成清除')
        raise_priority_action = menu.addAction('提高優先權')
        lower_priority_action = menu.addAction('降低優先權')
        list_delete_action = menu.addAction('從清單刪除')
        list_drive_delete_action = menu.addAction('從清單和硬碟刪除')
        if item is None:
            open_directory.setVisible(False)
            completed_delete_action.setVisible(True)
            raise_priority_action.setVisible(False)
            lower_priority_action.setVisible(False)
            list_delete_action.setVisible(False)
            list_drive_delete_action.setVisible(False)
        else:
            open_directory.setVisible(True)
            completed_delete_action.setVisible(False)
            raise_priority_action.setVisible(True)
            lower_priority_action.setVisible(True)
            list_delete_action.setVisible(True)
            list_drive_delete_action.setVisible(True)
        action = menu.exec_(self.download_tableWidget.viewport().mapToGlobal(pos))
        if action == completed_delete_action:
            for i in range(self.download_tableWidget.rowCount(), 0, -1):
                download_anime_Thread_name = self.download_tableWidget.item(i - 1, 0).text()
                download_anime_Thread_name = ''.join(download_anime_Thread_name.split('　　'))
                status = self.download_tableWidget.item(i - 1, 1).text()
                if status == '已完成':
                    if os.path.isfile(f'./Log/undone/{download_anime_Thread_name}.json'):
                        os.remove(f'./Log/undone/{download_anime_Thread_name}.json')
                    self.download_tableWidget.removeRow(i - 1)
                    del self.download_anime_Thread[download_anime_Thread_name]
                    del self.tableWidgetItem_download_dict[download_anime_Thread_name]
        else:
            if action == open_directory:
                os.startfile(f'{self.save_path}/{select[list(select.keys())[0]]["directory"]}')
            elif action == raise_priority_action:
                self.control_download_tablewidget(data=select, status=True)

            elif action == lower_priority_action:
                self.control_download_tablewidget(data=select, status=False)
            elif action == list_delete_action:
                self.download_menu_delete_list(data=select, remove_file=False)
            elif action == list_drive_delete_action:
                self.download_menu_delete_list(data=select, remove_file=True)

    def control_download_tablewidget(self, data=None, status=True):
        def move_item(mode):
            for i in data:
                move_name = self.download_tableWidget.item(i - mode, 0).text()
                move_name_item = QtWidgets.QTableWidgetItem(move_name)
                move_status = self.download_tableWidget.item(i - mode, 1).text()
                move_status_item = QtWidgets.QTableWidgetItem(move_status)
                move_status_item.setTextAlignment(QtCore.Qt.AlignCenter)
                move_schedule = QtWidgets.QProgressBar()
                move_schedule_value = self.download_tableWidget.cellWidget(i - mode, 2).value()
                move_schedule.setValue(move_schedule_value)
                move_schedule.setAlignment(QtCore.Qt.AlignCenter)
                move_item = ''.join(move_name.split('　　'))
                select_name = self.download_tableWidget.item(i, 0).text()
                select_name_item = QtWidgets.QTableWidgetItem(select_name)
                select_status = self.download_tableWidget.item(i, 1).text()
                select_status_item = QtWidgets.QTableWidgetItem(select_status)
                select_status_item.setTextAlignment(QtCore.Qt.AlignCenter)
                select_schedule = QtWidgets.QProgressBar()
                select_schedule_value = self.download_tableWidget.cellWidget(i, 2).value()
                select_schedule.setValue(select_schedule_value)
                select_schedule.setAlignment(QtCore.Qt.AlignCenter)
                select_item = ''.join(select_name.split('　　'))
                self.tableWidgetItem_download_dict.update(
                    {select_item: {'name': select_name_item,
                                   'status': select_status_item,
                                   'schedule': select_schedule}})
                self.tableWidgetItem_download_dict.update(
                    {move_item: {'name': move_name_item,
                                 'status': move_status_item,
                                 'schedule': move_schedule}})
                if move_item in self.wait_download_video_mission_list and select_item in self.wait_download_video_mission_list:
                    move_index = self.wait_download_video_mission_list.index(move_item)
                    select_index = self.wait_download_video_mission_list.index(select_item)
                    self.wait_download_video_mission_list[select_index], self.wait_download_video_mission_list[
                        move_index] = \
                        self.wait_download_video_mission_list[move_index], self.wait_download_video_mission_list[
                            select_index]
                elif select_item in self.now_download_video_mission_list and move_item in self.now_download_video_mission_list:
                    move_index = self.now_download_video_mission_list.index(move_item)
                    select_index = self.now_download_video_mission_list.index(select_item)
                    self.now_download_video_mission_list[select_index], self.now_download_video_mission_list[
                        move_index] = \
                        self.now_download_video_mission_list[move_index], self.now_download_video_mission_list[
                            select_index]
                self.download_tableWidget.takeItem(i - mode, 0)
                self.download_tableWidget.setItem(i - mode, 0, select_name_item)
                self.download_tableWidget.takeItem(i - mode, 1)
                self.download_tableWidget.setItem(i - mode, 1, select_status_item)
                self.download_tableWidget.removeCellWidget(i - mode, 2)
                self.download_tableWidget.setCellWidget(i - mode, 2, select_schedule)
                self.download_tableWidget.takeItem(i, 0)
                self.download_tableWidget.setItem(i, 0, move_name_item)
                self.download_tableWidget.takeItem(i, 1)
                self.download_tableWidget.setItem(i, 1, move_status_item)
                self.download_tableWidget.removeCellWidget(i, 2)
                self.download_tableWidget.setCellWidget(i, 2, move_schedule)

        if status:
            if 0 in data:
                del data[0]
            move_item(mode=1)
        else:
            if self.download_tableWidget.rowCount() - 1 in data:
                del data[self.download_tableWidget.rowCount() - 1]
            move_item(mode=-1)
        json.dump({'wait': self.wait_download_video_mission_list,
                   'now': self.now_download_video_mission_list},
                  open('./Log/download_order.json', 'w', encoding='utf-8'), indent=2)

    def download_menu_delete_list(self, data=None, remove_file=False):
        """
        下載清單，判斷是否要刪除檔案與 Thread 是否存在。
        """
        data = dict(sorted(data.items(), reverse=True))
        if remove_file:
            text = '你想要刪除這些影片嗎?\n註解: 檔案將被「刪除」。'
        else:
            text = '你想要刪除這些影片嗎?\n註解: 檔案將「不被刪除」。'
        msg = QtWidgets.QMessageBox().information(self, '確認', text, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No,
                                                  QtWidgets.QMessageBox.No)
        if msg == QtWidgets.QMessageBox.Ok:
            for i in data:
                # if data[i]["thread"] in self.download_anime_Thread:
                if data[i]["thread"] in self.now_download_video_mission_list:
                    self.now_download_video_mission_list.remove(data[i]["thread"])
                    self.now_download_value -= 1
                if data[i]["thread"] in self.wait_download_video_mission_list:
                    self.wait_download_video_mission_list.remove(data[i]["thread"])
                if os.path.isfile(f'./Log/undone/{data[i]["thread"]}.json'):
                    os.remove(f'./Log/undone/{data[i]["thread"]}.json')
                if remove_file:
                    if not self.download_anime_Thread[data[i]["thread"]]['over']:
                        self.download_anime_Thread[data[i]["thread"]]['thread'].remove_file = True
                        self.download_anime_Thread[data[i]["thread"]]['thread'].exit = True
                    try:
                        if os.path.isfile(f'{self.save_path}/{data[i]["directory"]}/{data[i]["file_name"]}.mp4'):
                            os.remove(f'{self.save_path}/{data[i]["directory"]}/{data[i]["file_name"]}.mp4')
                    except PermissionError:
                        pass
                del self.download_anime_Thread[data[i]["thread"]]
                del self.tableWidgetItem_download_dict[data[i]["thread"]]
                self.download_tableWidget.removeRow(i)

    def click_on_tablewidget(self, index):
        """
        TabWidget切換時，判斷讀取動漫資訊是否顯示。
        """
        if index != 0 and not self.load_week_label_status:
            self.load_week_label.setVisible(False)
        elif index == 0 and not self.load_week_label_status:
            self.load_week_label.setVisible(True)
        if index != 1 and not self.load_end_anime_status:
            self.load_end_anime_label.setVisible(False)
        elif index == 1 and not self.load_end_anime_status:
            self.load_end_anime_label.setVisible(True)
        if index != 2 and self.load_anime_label_status:
            self.load_anime_label.setVisible(False)
        elif index == 2 and self.load_anime_label_status:
            self.load_anime_label.setVisible(True)

    def print_row(self, r, c):
        # print(r, c)
        pass

    def closeEvent(self, event):
        """
        關閉主視窗其餘子視窗也會關閉。
        """
        QtWidgets.QApplication.closeAllWindows()

    def basic_config(self):
        """
        每次打開會判斷有沒有 config.json。
        """
        config = {'path': os.getcwd(), 'speed': {'type': 'slow', 'value': 1}, 'simultaneous': 5}
        if not os.path.isfile('config.json'):
            data = config
            json.dump(data, open('config.json', 'w', encoding='utf-8'), indent=2)
        else:
            data = json.load(open('config.json', 'r', encoding='utf-8'))
            for i in config:
                if i not in data:
                    data[i] = config[i]
            json.dump(data, open('config.json', 'w', encoding='utf-8'), indent=2)

        if not os.path.isdir('Log'):
            os.mkdir('Log')
        if not os.path.isdir('./Log/undone'):
            os.mkdir('./Log/undone')
        if not os.path.isdir('./Log/history'):
            os.mkdir('./Log/history')
        if os.path.isfile('./Log/download_order.json'):
            download_order = json.load(open('./Log/download_order.json', 'r', encoding='utf-8'))
            wait = download_order['wait']
            now = download_order['now']
        else:
            wait = list()
            now = list()
        return data['path'], data['simultaneous'], data['speed']['value'], wait, now

    def load_download_menu(self):
        menu = self.now_download_video_mission_list + self.wait_download_video_mission_list
        for i in self.now_download_video_mission_list:
            data = json.load(open(f'./Log/undone/{i}.json', 'r', encoding='utf-8'))
            self.create_tablewidgetitem(data=data, now=True, init=True)
        wait_list = self.wait_download_video_mission_list[:]
        for i in wait_list:
            data = json.load(open(f'./Log/undone/{i}.json', 'r', encoding='utf-8'))
            self.create_tablewidgetitem(data=data, init=True)
        for i in os.listdir('./Log/undone/'):
            if i.endswith('.json') and i[:-5] not in menu:
                data = json.load(open(f'./Log/undone/{i}', 'r', encoding='utf-8'))
                self.create_tablewidgetitem(data=data, init=True)

    def loading_config_status(self):
        """
        創讀取狀態列的 Thread。
        """
        self.config_status = Loading_config_status(pid=os.getpid())
        self.config_status.loading_config_status_signal.connect(self.loading_config_status_mission)
        self.config_status.start()

    def loading_config_status_mission(self, signal):
        """
        接收狀態列 Thread 信號。
        """
        self.left_status_label.setText(
            f'狀態: {self.now_download_value} 個下載中　　連接設定: {self.speed_value} / {self.simultaneously_value}')
        self.right_ststus_label.setText(f'記憶體: {signal["memory"]}MB / 程序: {signal["cpu"]}%')

    def download_anime(self):
        """
        檢查 checkbox 是否被選取，並創建 tablewidgetitem。
        """
        for i in self.story_checkbox_dict:
            if self.story_checkbox_dict[i].isChecked():
                data = json.loads(self.story_checkbox_dict[i].objectName())
                if data['total_name'] in self.download_anime_Thread and self.download_anime_Thread[data['total_name']][
                    'over']:
                    msg = QtWidgets.QMessageBox().information(self, '確認', '確認重新下鮺',
                                                              QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No,
                                                              QtWidgets.QMessageBox.No)
                    if msg == QtWidgets.QMessageBox.Ok:
                        self.create_tablewidgetitem(data=data)
                elif data['total_name'] not in self.download_anime_Thread:
                    self.create_tablewidgetitem(data=data)

    def create_tablewidgetitem(self, data=None, now=False, init=False):
        if not now:
            self.wait_download_video_mission_list.append(data['total_name'])
        rowcount = self.download_tableWidget.rowCount()
        self.download_tableWidget.setRowCount(rowcount + 1)
        self.tableWidgetItem_download_dict.update(
            {data['total_name']: {'name': QtWidgets.QTableWidgetItem(data['name_num']),
                                  'status': QtWidgets.QTableWidgetItem(data['status']),
                                  'schedule': QtWidgets.QProgressBar()}})
        self.tableWidgetItem_download_dict[data['total_name']]['status'].setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetItem_download_dict[data['total_name']]['schedule'].setValue(data['schedule'])
        self.tableWidgetItem_download_dict[data['total_name']]['schedule'].setAlignment(QtCore.Qt.AlignCenter)
        self.download_tableWidget.setItem(rowcount, 0,
                                          self.tableWidgetItem_download_dict[data['total_name']]['name'])
        self.download_tableWidget.setItem(rowcount, 1,
                                          self.tableWidgetItem_download_dict[data['total_name']]['status'])
        self.download_tableWidget.setCellWidget(rowcount, 2,
                                                self.tableWidgetItem_download_dict[data['total_name']]['schedule'])
        data.update({'time': datetime.datetime.strftime(datetime.datetime.today(), '%Y/%m/%d %H:%M:%S')})
        if data['schedule'] == 100:
            self.download_anime_Thread.update({data['total_name']: {'thread': None,
                                                                    'over': True}})
        else:
            self.download_anime_Thread.update({data['total_name']: {'thread': Download_Video(data=data, init=init),
                                                                    'over': False}})
            self.download_anime_Thread[data['total_name']]['thread'].download_video.connect(self.download_anime_task)
            self.download_anime_Thread[data['total_name']]['thread'].start()

    def download_anime_task(self, signal):
        """
        接收下載動漫 Thread。
        """
        if int(signal['schedule']) == 100:
            self.download_anime_Thread[signal['total_name']]['over'] = True
            self.tableWidgetItem_download_dict[signal['total_name']]['status'].setText(signal["status"])
            self.tableWidgetItem_download_dict[signal['total_name']]['schedule'].setValue(signal["schedule"])
        else:
            try:
                if self.download_anime_Thread[signal['total_name']]['thread'].stop:
                    self.tableWidgetItem_download_dict[signal['total_name']]['status'].setText('暫停')
                else:
                    self.tableWidgetItem_download_dict[signal['total_name']]['status'].setText(signal["status"])
                self.tableWidgetItem_download_dict[signal['total_name']]['schedule'].setValue(signal["schedule"])
            except KeyError:
                print('應該是 Thread 被刪除，剛好 emit。')

    def config(self):
        """
        開啟設定介面。
        """
        self.config_windows = Config()
        self.config_windows.show()

    def check_checkbox(self):
        """
        動漫資訊的 checkbox 判斷。
        """
        if self.story_list_all_pushButton.text() == '全選':
            for i in self.story_checkbox_dict:
                self.story_checkbox_dict[i].setChecked(True)
            self.story_list_all_pushButton.setText('取消全選')
        else:
            for i in self.story_checkbox_dict:
                self.story_checkbox_dict[i].setChecked(False)
            self.story_list_all_pushButton.setText('全選')

    def anime_page_Visible(self, status=False):
        """
        動漫資訊裡的各個物件顯示與隱藏。
        """
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
        """
        創每周動漫更新表 Thread。
        """
        self.week_data = Week_data()
        self.week_data.week_data_signal.connect(self.week_data_task)
        self.week_data.start()

    def week_data_task(self, signal):
        """
        接收每周動漫更新表 Thread。
        """
        for i in signal:
            self.week_layout_dict.update({i: QtWidgets.QFormLayout()})
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
                                                              "QPushButton:hover{background-color:transparent; color: #000000;}\n"
                                                              "QPushButton:pressed{\n"
                                                              "background-color: transparent;\n"
                                                              "border-style: inset;\n"
                                                              "color: #339900;\n"
                                                              " }\n"
                                                              )
                self.week_dict[m]['pushbutton'].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.week_dict[m]['pushbutton'].clicked.connect(self.anime_info_event)
                self.week_dict[m]['update'].setAlignment(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
                self.week_layout_dict[i].addRow(self.week_dict[m]['pushbutton'], self.week_dict[m]['update'])
            self.week[i].setLayout(self.week_layout_dict[i])
        self.load_week_label.setVisible(False)
        self.load_week_label_status = True
        # self.week_data.quit()
        # self.week_data.wait()
        del self.week_data

    def anime_info_event(self):
        """
        每周動漫表的動漫按鈕事件，並創動漫資訊 Thread。
        """
        sender = self.sender()
        pushButton = self.findChild(QtWidgets.QPushButton, sender.objectName())
        url = pushButton.objectName()
        self.loading_anime(url=url)

    def loading_anime(self, url):
        self.load_anime_label.setVisible(True)
        self.load_anime_label_status = True
        self.anime_info = Anime_info(url=url)
        self.anime_info.anime_info_signal.connect(self.anime_info_data)
        self.anime_info.start()
        self.anime_info_tabWidget.setCurrentIndex(2)
        self.anime_page_Visible()

    def anime_info_data(self, signal):
        """
        接收動漫資訊 Thread。
        """
        if len(signal['total']) == 0:
            self.load_anime_label.setVisible(False)
            self.load_anime_label_status = False
            QtWidgets.QMessageBox().information(self, "確定",
                                                f"<font size=5  color=#000000>網址有誤！</font> <br/><font size=4  color=#000000>請確認輸入的 <a href={signal['home']}>網址 </a>",
                                                QtWidgets.QMessageBox.Ok)
        else:
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
            if 60 + len(signal['total']) * 20 > 240:
                self.story_list_scrollArea.setGeometry(QtCore.QRect(10, 60, 211, 251))
            else:
                self.story_list_scrollArea.setGeometry(QtCore.QRect(10, 60, 211, 40 + len(signal['total']) * 20))
            for i, m in enumerate(signal['total']):
                data = json.dumps(
                    {'name': self.badname(signal['name']), 'num': self.badname(m), 'url': signal['total'][m],
                     'name_num': f"{self.badname(signal['name'])}　　{self.badname(m)}", 'schedule': 0,
                     'status': '準備中', 'total_name': self.badname(signal['name']) + self.badname(m),
                     'video_ts': 0, 'time': None, 'home': signal['home']})
                self.story_checkbox_dict.update({i: QtWidgets.QCheckBox(m)})
                self.story_checkbox_dict[i].setObjectName(data)
                self.story_list_scrollAreaWidgetContents_Layout.addWidget(self.story_checkbox_dict[i])
            self.anime_page_Visible(status=True)
            self.load_anime_label_status = False
            # self.anime_info.terminate()
            # self.anime_info.wait()
            # self.anime_info.quit()
            del self.anime_info

    def loading_end_anime(self):
        self.end_anime = End_anime()
        self.end_anime.end_anime_signal.connect(self.end_anime_data)
        self.end_anime.start()

    def end_anime_data(self, signal):
        for i in signal:
            self.end_tab.update({i: QtWidgets.QTabWidget()})
            month_dict = dict()
            for month, j in enumerate(signal[i]):
                content_len = len(signal[i][j])
                if content_len % 3 == 0:
                    high = content_len // 3
                else:
                    high = content_len // 3 + 1
                if month == 0:
                    size = high
                self.end_qt_object.update({j: {'widget': QtWidgets.QWidget(),
                                               'GridLayout': QtWidgets.QGridLayout(),
                                               'size': high,
                                               'index': i}})
                for index, k in enumerate(signal[i][j]):
                    r, c = divmod(index, 3)
                    self.end_qt_object[j].update({k: QtWidgets.QPushButton(k)})
                    self.end_qt_object[j][k].setObjectName(signal[i][j][k])
                    self.end_qt_object[j][k].setStyleSheet("QPushButton {\n"
                                                           "background-color:transparent;\n"
                                                           "color: #000000;\n"
                                                           "font-size:12px;\n"
                                                           "}"
                                                           "QPushButton:hover{background-color:transparent; color: #00aaff;}\n"
                                                           "QPushButton:pressed{\n"
                                                           "background-color: transparent;\n"
                                                           "border-style: inset;\n"
                                                           "color: black;\n"
                                                           " }\n"
                                                           )
                    self.end_qt_object[j][k].clicked.connect(self.anime_info_event)
                    self.end_qt_object[j][k].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                    self.end_qt_object[j]['GridLayout'].addWidget(self.end_qt_object[j][k], r, c,
                                                                  QtCore.Qt.AlignHCenter)

                self.end_qt_object[j]['widget'].setLayout(self.end_qt_object[j]['GridLayout'])
                month_dict.update({month: j})
                self.end_tab[i].addTab(self.end_qt_object[j]['widget'], j)
            month_json = json.dumps(month_dict)
            self.end_tab[i].setObjectName(month_json)
            if size > 3:
                self.end_tab[i].setMinimumSize(878, size * 30)
            else:
                self.end_tab[i].setMinimumSize(878, size * 40)
            self.end_tab[i].setCurrentIndex(0)
            self.end_tab[i].tabBar().setMouseTracking(True)
            self.end_tab[i].tabBar().installEventFilter(self)
            self.tabBar.append(self.end_tab[i])
            self.end_tab[i].currentChanged.connect(self.end_tabwidget_index)
            self.end_scrollAreaWidgetContents_Layout.addWidget(self.end_tab[i])
            self.load_end_anime_label.setVisible(False)
            self.load_end_anime_status = True

    def end_tabwidget_index(self, index):
        sender = self.sender()
        pushButton = self.findChild(QtWidgets.QTabWidget, sender.objectName())
        p = json.loads(pushButton.objectName())
        size = self.end_qt_object[p[str(index)]]['size']
        tab_index = self.end_qt_object[p[str(index)]]['index']
        if size > 3:
            self.end_tab[tab_index].setMinimumHeight(size * 30)
        else:
            self.end_tab[tab_index].setMinimumHeight(size * 40)

    def check_url(self):
        url = self.customize_lineEdit.text().strip()
        if re.match(r'^https://myself-bbs.com/thread-[0-9]{5,5}-1-1.html$', url) \
                or re.match(r'^https://myself-bbs.com/forum.php\Wmod=viewthread&tid=[0-9]{5,5}&.', url):
            self.loading_anime(url=url)
        else:
            if url[-1] == '/':
                url = url[:-1]
            self.url_error = QtWidgets.QMessageBox.information(self, '錯誤',
                                                               f"<font size=5  color=#000000>網址有誤！</font> <br/><font size=4  color=#000000>確認輸入的 <a href={url}>網址 </a><font size=4  color=#000000>是否正確！<",
                                                               QtWidgets.QMessageBox.Ok)

    def load_history(self):
        self.history_thread = History()
        self.history_thread.history_signal.connect(self.create_history_tablewidteritem)
        self.history_thread.start()

    def create_history_tablewidteritem(self, signal):
        rowcount = self.history_tableWidget.rowCount()
        self.history_tableWidget.setRowCount(rowcount + 1)
        self.history_tableWidget_dict.update(
            {signal['total_name']: {'name': QtWidgets.QTableWidgetItem(signal['name_num']),
                                    'time': QtWidgets.QTableWidgetItem(signal['time']),
                                    'home': signal['home']
                                    }})
        self.history_tableWidget_dict[signal['total_name']]['time'].setTextAlignment(QtCore.Qt.AlignCenter)
        self.history_tableWidget_dict[signal['total_name']]['name'].setTextAlignment(QtCore.Qt.AlignCenter)
        self.history_tableWidget.setItem(rowcount, 0,
                                         self.history_tableWidget_dict[signal['total_name']]['name'])
        self.history_tableWidget.setItem(rowcount, 1,
                                         self.history_tableWidget_dict[signal['total_name']]['time'])

    def mouseHoverOnTabBar(self):
        """
        滑鼠移動。
        """
        # self.tabBar = self.week_tabWidget.tabBar().setMouseTracking(True)
        # self.tabBar.setMouseTracking(True)
        # self.tabBar.installEventFilter(self)
        self.week_tabWidget.tabBar().setMouseTracking(True)
        self.week_tabWidget.tabBar().installEventFilter(self)
        return [self.week_tabWidget]

    def eventFilter(self, obj, event):
        """
        滑鼠移動到 TabWidget 不用點擊就會自動切換頁面。
        """
        for i in self.tabBar:
            if obj == i.tabBar():
                if event.type() == QtCore.QEvent.MouseMove:
                    index = i.tabBar().tabAt(event.pos())
                    i.tabBar().setCurrentIndex(index)
                    return True
        return super().eventFilter(obj, event)


class Week_data(QtCore.QThread):
    """
    爬每周動漫資訊。
    """
    week_data_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(Week_data, self).__init__()

    def run(self):
        res = requests.get(url='https://myself-bbs.com/portal.php', headers=headers)
        html = BeautifulSoup(res.text, features='lxml')
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
        res.close()
        res, html = None, None
        del res, html
        self.week_data_signal.emit(week_dict)


class End_anime(QtCore.QThread):
    end_anime_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(End_anime, self).__init__()

    def run(self):
        url = 'https://myself-bbs.com/portal.php?mod=topic&topicid=8'
        res = requests.get(url=url, headers=headers)
        html = BeautifulSoup(res.text, features='lxml')
        data = dict()
        for index, i in enumerate(html.find_all('div', {'class': 'tab-title title column cl'})):
            month = dict()
            for j, m in enumerate(i.find_all('div', {'class': 'block move-span'})):
                anime = dict()
                for k in m.find('span', {'class': 'titletext'}):
                    year = k
                for k in m.find_all('a'):
                    anime.update({k['title']: f"https://myself-bbs.com/{k['href']}"})
                month.update({year: anime})
            data.update({index: month})
        res.close()
        self.end_anime_signal.emit(data)


class Anime_info(QtCore.QThread):
    """
    爬動漫資訊。
    """
    anime_info_signal = QtCore.pyqtSignal(dict)

    def __init__(self, url):
        super(Anime_info, self).__init__()
        self.url = url

    def get_anime_data(self):
        res = requests.get(url=self.url, headers=headers)
        html = BeautifulSoup(res.text, features='lxml')
        data = {'home': self.url}
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
                image = None
                del image
        for i in html.find_all('div', class_='z'):
            for j, m in enumerate(i.find_all('a')):
                if j == 4:
                    data.update({'name': m.text.split('【')[0]})
        res.close()
        res, html = None, None
        del res, html
        return data

    def run(self):
        data = self.get_anime_data()
        self.anime_info_signal.emit(data)


class History(QtCore.QThread):
    history_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(History, self).__init__()
        self.data = list()

    def run(self):
        while True:
            try:
                result = list()
                for i in os.listdir('./Log/history/'):
                    result.append(i)
                if self.data != result:
                    anime.history_tableWidget.clearContents()
                    anime.history_tableWidget.setRowCount(0)
                    self.data = result
                    for i in self.data:
                        if i.endswith('.json'):
                            data = json.load(open(f'./Log/history/{i}', 'r', encoding='utf-8'))
                            self.history_signal.emit(data)
            except NameError:
                pass
            time.sleep(1)


class Download_Video(QtCore.QThread):
    """
    下載動漫。
    """
    download_video = QtCore.pyqtSignal(dict)

    def __init__(self, data, init):
        super(Download_Video, self).__init__()
        self.data = data
        self.path = json.load(open('config.json', 'r', encoding='utf-8'))
        self.folder_name = self.data['name']
        self.file_name = self.data['num']
        if not os.path.isdir(f'{self.path["path"]}/{self.folder_name}'):
            os.mkdir(f'{self.path["path"]}/{self.folder_name}')
        if self.data['video_ts'] == 0 and os.path.isfile(
                f'{self.path["path"]}/{self.folder_name}/{self.file_name}.mp4'):
            os.remove(f'{self.path["path"]}/{self.folder_name}/{self.file_name}.mp4')
        json.dump(self.data, open(f'./Log/undone/{self.data["total_name"]}.json', 'w', encoding='utf-8'), indent=2)
        json.dump(self.data, open(f'./Log/history/{self.data["total_name"]}.json', 'w', encoding='utf-8'), indent=2)
        self.stop = False
        self.exit = False
        self.remove_file = False
        self.del_download_order = False
        # self.write_undone_status = False
        # self.write_download_order_status = False
        if not init:
            self.write_download_order()


    def write_download_order(self):
        while True:
            try:
                if not anime.thread_write_download_order_status:
                    anime.thread_write_download_order_status = True
                    download = {'wait': anime.wait_download_video_mission_list,
                                'now': anime.now_download_video_mission_list}
                    json.dump(download, open('./Log/download_order.json', 'w', encoding='utf-8'), indent=2)
                    anime.thread_write_download_order_status = False
                    break
                time.sleep(0.2)
            except NameError:
                time.sleep(0.5)

    def write_undone(self, index, m3u8_count):
        if self.data['video_ts'] == m3u8_count - 1 or self.data['video_ts'] == m3u8_count:
            status = '已完成'
            schedule = 100
        else:
            status = '下載中'
            schedule = int(self.data['video_ts'] / (m3u8_count - 1) * 100)
        self.data.update({'video_ts': index,
                          'schedule': schedule,
                          'status': status})
        json.dump(self.data, open(f'./Log/undone/{self.data["total_name"]}.json', 'w', encoding='utf-8'),
                  indent=2)

    def del_file_and_json(self):
        try:
            if os.path.isfile(f'./Log/undone/{self.data["total_name"]}.json'):
                os.remove(f'./Log/undone/{self.data["total_name"]}.json')
        except (PermissionError, FileNotFoundError):
            pass
        except BaseException as error:
            print(f'del_file_and_json error: {error}')
        try:
            os.remove(f'{self.path["path"]}/{self.folder_name}/{self.file_name}.mp4')
        except (PermissionError, FileNotFoundError):
            pass
        except BaseException as error:
            print(f'del_file_and_json error: {error}')

    def turn_me(self):
        """
        判斷下載列表順序使否輪到自己。
        """
        while True:
            try:
                if self.exit:
                    break
                elif self.data["name"] + self.data["num"] in anime.now_download_video_mission_list:
                    anime.now_download_value += 1
                    break
                elif len(anime.wait_download_video_mission_list) > 0 and anime.wait_download_video_mission_list[0] == \
                        self.data["name"] + self.data["num"] and anime.simultaneously_value > anime.now_download_value:
                    anime.now_download_value += 1
                    anime.now_download_video_mission_list.append(anime.wait_download_video_mission_list.pop(0))
                    self.write_download_order()
                    break
                time.sleep(3)
            except NameError:
                time.sleep(0.5)

    def get_host_video_data(self):
        """
        取得 Host資料。
        """
        while True:
            try:
                if not self.stop and not self.exit:
                    res = requests.get(url=self.data['url'], headers=headers, timeout=5)
                    if res:
                        data = res.json()
                        res.close()
                        return data
                elif self.exit:
                    if not self.del_download_order:
                        self.del_download_order = True
                        self.write_download_order()
                        self.del_file_and_json()
                    break
            except BaseException as error:
                time.sleep(5)

    def get_m3u8_data(self, res):
        """
        取得 m3u8 資料。
        """
        if self.exit:
            return None
        index = 0
        url = res['host'][index]['host'] + res['video']['720p']
        while True:
            try:
                if not self.stop and not self.exit:
                    m3u8_data = requests.get(url=url, headers=headers, timeout=5)
                    if m3u8_data:
                        data = m3u8_data.text
                        m3u8_data.close()
                        return data
                elif self.exit:
                    if not self.del_download_order:
                        self.del_download_order = True
                        self.write_download_order()
                        self.del_file_and_json()
                    break
            except:
                index += 1
                url = res['host'][index]['host'] + res['video']['720p']
                time.sleep(5)

    def run(self):
        self.turn_me()

        res = self.get_host_video_data()
        m3u8_data = self.get_m3u8_data(res)
        if self.exit:
            self.quit()
            self.wait()
        else:
            m3u8_count = m3u8_data.count('EXTINF')
            host = sorted(res['host'], key=lambda i: i.get('weight'), reverse=True)
            executor = ThreadPoolExecutor(max_workers=anime.speed_value)
            for i in range(self.data['video_ts'], m3u8_count):
                executor.submit(self.video, i, res, host, m3u8_count)
            while True:
                if self.data['video_ts'] == m3u8_count:
                    # self.data.update({'status': '已完成'})
                    anime.now_download_video_mission_list.remove(self.data['total_name'])
                    self.write_download_order()
                    anime.now_download_value -= 1
                    break
                if self.exit:
                    break
                self.data.update({'schedule': int(self.data['video_ts'] / (m3u8_count - 1) * 100),
                                  'status': '下載中',
                                  })
                self.download_video.emit(self.data)
                time.sleep(1)
            self.download_video.emit(self.data)
            self.quit()
            self.wait()

    def video(self, i, res, host, m3u8_count):
        """
        請求 URL 下載影片。
        """
        host_value = 0
        url = f"{host[host_value]['host']}{res['video']['720p'].split('.')[0]}_{i:03d}.ts"
        ok = False
        while True:
            # self.data['video_ts'] += 1
            # break
            try:
                if not self.stop and not self.exit:
                    data = requests.get(url=url, headers=headers, stream=True, timeout=3)
                    if data:
                        while True:
                            if self.data['video_ts'] == i:
                                with open(f'{self.path["path"]}/{self.folder_name}/{self.file_name}.mp4', 'ab') as v:
                                    self.write_undone(index=i, m3u8_count=m3u8_count)
                                    shutil.copyfileobj(data.raw, v)
                                self.data['video_ts'] += 1
                                self.write_undone(index=self.data['video_ts'], m3u8_count=m3u8_count)
                                if self.remove_file:
                                    self.del_download_order = True
                                    self.write_download_order()
                                    self.del_file_and_json()
                                ok = True
                                data.close()
                                data = None
                                del data
                                break
                            elif self.stop or self.exit:
                                data.close()
                                data = None
                                del data
                                break
                            time.sleep(1)
                    if ok:
                        break
                if self.exit:
                    if not self.del_download_order:
                        self.del_download_order = True
                        self.write_download_order()
                        self.del_file_and_json()
                    break
                time.sleep(5)
            except (requests.exceptions.RequestException, requests.ConnectionError,
                    requests.exceptions.ChunkedEncodingError, ConnectionResetError):
                if host_value - 1 > len(host):
                    host_value = 0
                else:
                    host_value += 1
                url = f"{host[host_value]['host']}{res['video']['720p'].split('.')[0]}_{i:03d}.ts"
                print(url)
                time.sleep(1)
            except BaseException as error:
                print('基礎錯誤', error)


class Loading_config_status(QtCore.QThread):
    """
    抓記憶體與CPU。
    """
    loading_config_status_signal = QtCore.pyqtSignal(dict)

    def __init__(self, pid):
        super(Loading_config_status, self).__init__()
        self.info = psutil.Process(pid)
        self.config = dict()

    def run(self):
        while True:
            cpu = '%.2f' % (self.info.cpu_percent() / psutil.cpu_count())
            memory = '%.2f' % (self.info.memory_full_info().rss / 1024 / 1024)
            # memory = '%.2f' % (psutil.virtual_memory().percent)
            # memory = '%.2f' % (self.info.memory_full_info().uss / 1024 / 1024)
            self.config.update({'cpu': cpu, 'memory': memory})
            self.loading_config_status_signal.emit(self.config)
            time.sleep(1)


class Config(QtWidgets.QMainWindow, Ui_Config):
    """
    設定視窗。
    """

    def __init__(self):
        super(Config, self).__init__()
        self.setupUi(self)
        self.config()
        self.setWindowIcon(QtGui.QIcon('image/logo.ico'))
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
        """
        注意事項視窗。
        """
        QtWidgets.QMessageBox().information(self, "注意事項",
                                            '慢速: 1 次 1 個連接<br/>一般: 1 次 3 個連接<br/>高速: 1 次 8 個連接<br/>星爆: 1 次 16 個連接<br/><br/>連接值:1次取得多少影片來源。<br/>連接值越高吃的網速就越多。<br/>同時下載數量越高，記憶體與網速就吃越多。',
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

    def save_config(self):
        """
        儲存按鈕事件。
        """
        path = self.download_path_lineEdit.text()
        simultaneous = self.simultaneous_download_lineEdit.text()
        for i in self.speed_radioButton_dict:
            if i.isChecked():
                speed = self.speed_radioButton_dict[i]
                break
        data = {'path': path, 'speed': speed, 'simultaneous': int(simultaneous)}
        json.dump(data, open('config.json', 'w', encoding='utf-8'), indent=2)
        anime.save_path = data['path']
        anime.simultaneously_value = data['simultaneous']
        anime.speed_value = data['speed']['value']
        QtWidgets.QMessageBox().information(self, '儲存', "<font size='6'>資料已成功地儲存。</font>", QtWidgets.QMessageBox.Ok)
        self.close()

    def download_path(self):
        """
        瀏覽資料夾按鈕。
        """
        download_path = QtWidgets.QFileDialog.getExistingDirectory(self, "選取資料夾", self.download_path_lineEdit.text())
        self.download_path_lineEdit.setText(download_path)


class About(QtWidgets.QMainWindow, Ui_About):
    """
    關於視窗。
    """

    def __init__(self):
        super(About, self, ).__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('image/logo.ico'))
        self.setFixedSize(self.width(), self.height())
        self.pixmap = QtGui.QPixmap("./image/logo.ico")
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setScaledContents(True)
        self.close_pushButton.clicked.connect(self.close)


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
    about = About()
    anime.menu.actions()[0].triggered.connect(config.show)
    anime.menu.actions()[1].triggered.connect(about.show)
    anime.show()
    app.exec_()
