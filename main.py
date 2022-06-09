import os
import sys
import platform
import subprocess
import json
# import gc
import datetime
import webbrowser

from AboutUI import About
from ConfigUI import Config
from MyselfClose import MyselfClose
from TrayIcon import TrayIcon
from UI.main_ui import Ui_Anime
from PyQt5 import QtCore, QtWidgets, QtGui

from event.CheckUrl import check_url
from event.ClickOnMainTableWidget import click_on_tablewidget
from event.EndAnime import search_end_anime, update_end_anime_mission, update_end_anime, create_end_anime_frame, \
    create_end_anime_page
from event.History import create_history_tablewidget_item
from event.InitParameter import init_parameter, init_auto_run
from event.Login import login_event
from event.PushButtonClickedConnect import pushbutton_clicked_connect
from event.Version import check_version_task
from myself_thread import WeeklyUpdate, EndAnime, AnimeData, History, LoadingConfigStatus, DownloadVideo, EndAnimeData, \
    CheckVersion, ReDownload, CheckTsStatus
from myself_tools import badname, kill_pid, load_localhost_end_anime_data, get_all_page, connect_myself_anime

VERSION = '1.1.7'

# if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
#     QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
#
# if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
#     QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# QT_AUTO_SCREEN_SCALE_FACTOR = 2
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)


class Anime(QtWidgets.QMainWindow, Ui_Anime):
    def __init__(self, pid, os_system):
        super(Anime, self).__init__()
        self.setupUi(self)
        self.init_parameter(pid, os_system)
        self.init_auto_run()
        self.setWindowTitle(f'{self.windowTitle()}  ver:{VERSION}')

    def init_parameter(self, pid, os_system):
        """
        宣告物件和一些物件的參數操作。
        :param pid: 程序的 pid。
        """
        init_parameter(self=self, pid=pid, os_system=os_system)

    def init_auto_run(self):
        """
        宣告物件和一些物件的參數操作。
        :param pid: 程序的 pid。
        """
        init_auto_run(self=self)

    def pushbutton_clicked_connect(self):
        """
        所有 pushbutton 連接方法。
        """
        pushbutton_clicked_connect(self=self)

    def load_localhost_end_anime_data(self):
        """
        讀取本地端完結動漫資料。
        """
        data, exist = load_localhost_end_anime_data()
        if exist:
            self.end_anime_lineEdit.setPlaceholderText('搜尋')
            self.end_anime_lineEdit.setEnabled(True)
            self.end_anime_last_update_date.setText(f'最後更新日期: {data["date"]}')
            return data['data_dict'], data['data_list']
        return data['data_dict'], data['data_list']

    def create_end_anime_frame_and_page(self):
        create_end_anime_frame(self=self, search_data=self.localhost_end_anime_list, page=0, limit=8)
        all_page = get_all_page(self.localhost_end_anime_list)
        create_end_anime_page(self=self, page=0, all_page=all_page)

    def check_version(self):
        """
        開 Thread 檢查程式版本。
        """
        self.check_version_thread = CheckVersion(version=VERSION)
        self.check_version_thread.check_version.connect(self.check_version_task)
        self.check_version_thread.start()

    def check_version_task(self, signal):
        """
        接收版本訊息。
        :param signal: 版本訊息。
        """
        check_version_task(self=self, signal=signal)

    def check_re_download(self):
        """
        :return:
        """
        self.check_re_download_thread = ReDownload(anime=self)
        self.check_re_download_thread.re_download.connect(self.check_re_download_task)
        self.check_re_download_thread.start()

    def check_re_download_task(self, signal):
        """
        :return:
        """
        self.download_anime_Thread.update(
            {signal['total_name']: {'thread': DownloadVideo(data=signal, anime=self),
                                    'over': False}})
        self.download_anime_Thread[signal['total_name']]['thread'].download_video.connect(self.download_anime_task)
        self.download_anime_Thread[signal['total_name']]['thread'].start()

    def check_ts_status(self):
        """
        暫時棄用。
        :return:
        """
        self.check_ts_status_thread = CheckTsStatus(anime=self)
        self.check_ts_status_thread.check_ts_status.connect(self.check_ts_status_task)
        self.check_ts_status_thread.start()

    def check_ts_status_task(self, signal):
        """
        暫時棄用。
        :return:
        """
        self.download_anime_Thread.update(
            {signal['total_name']: {'thread': DownloadVideo(data=signal, anime=self),
                                    'over': False}})
        self.download_anime_Thread[signal['total_name']]['thread'].download_video.connect(self.download_anime_task)
        self.download_anime_Thread[signal['total_name']]['thread'].start()

    def history_tableWidget_on_custom_context_menu_requested(self, pos):
        """
        歷史紀錄頁面的右鍵功能。
        """
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
        """
        刪除歷史紀錄
        :param data: 要刪除的資料。
        :param mode: 是刪除單個還是刪除全部。
        """
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
                folder_path = f'{self.save_path}/{select[list(select.keys())[0]]["directory"]}'
                if self.os_system == "Windows":
                    os.startfile(folder_path)
                elif self.os_system == "Darwin":
                    subprocess.Popen(["open", folder_path])
                else:
                    subprocess.Popen(["xdg-open", folder_path])
            elif action == raise_priority_action:
                self.control_download_tablewidget(data=select, status=True)
            elif action == lower_priority_action:
                self.control_download_tablewidget(data=select, status=False)
            elif action == list_delete_action:
                self.download_menu_delete_list(data=select, remove_file=False)
            elif action == list_drive_delete_action:
                self.download_menu_delete_list(data=select, remove_file=True)

    def control_download_tablewidget(self, data=None, status=True):
        """
        控制下載清單的順序。
        :param data: 選取的動漫欄位資料。
        :param status: 用來判斷提高或降低。
        """

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
                move_index = self.download_queue.index(move_item)
                select_index = self.download_queue.index(select_item)
                self.download_queue[select_index], self.download_queue[move_index] = self.download_queue[move_index], \
                                                                                     self.download_queue[select_index]
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
        json.dump({'queue': self.download_queue}, open('./Log/DownloadQueue.json', 'w', encoding='utf-8'), indent=2)

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
                if data[i]["thread"] in self.download_queue:
                    self.download_queue.remove(data[i]["thread"])
                if os.path.isfile(f'./Log/undone/{data[i]["thread"]}.json'):
                    os.remove(f'./Log/undone/{data[i]["thread"]}.json')
                if self.download_anime_Thread[data[i]["thread"]]['thread']:
                    self.download_anime_Thread[data[i]["thread"]]['thread'].exit = True
                if remove_file:
                    if not self.download_anime_Thread[data[i]["thread"]]['over']:
                        self.download_anime_Thread[data[i]["thread"]]['thread'].remove_file = True
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
        click_on_tablewidget(self=self, index=index)

    def print_row(self, r, c):
        """
        當初找 QT 功能時測試用的，目前沒用處了，但不刪除。
        """
        # print(r, c)
        pass

    def closeEvent(self, event):
        """
        關閉主視窗其餘子視窗也會關閉。
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '關閉',
                                               "是否離開程式？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.hide()
            self.myself_close = MyselfClose(anime=self)
            self.myself_close.show()
        else:
            event.ignore()

    def load_download_menu(self):
        """
        讀取下載動漫任務列表並在下載清單創建Item。
        """
        for anime in self.download_end_anime:
            data = json.load(open(f'./Log/undone/{anime}.json', 'r', encoding='utf-8'))
            self.create_tablewidgetitem(data=data, old=True)
        for queue in self.download_queue:
            data = json.load(open(f'./Log/undone/{queue}.json', 'r', encoding='utf-8'))
            self.create_tablewidgetitem(data=data, old=True)

    def loading_config_status(self):
        """
        開讀取狀態列的 Thread。
        """
        self.config_status = LoadingConfigStatus(pid=os.getpid())
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
                    msg = QtWidgets.QMessageBox().information(self, '確認', f'{data["total_name"]} 要重新下載嗎?',
                                                              QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No,
                                                              QtWidgets.QMessageBox.No)
                    if msg == QtWidgets.QMessageBox.Ok:
                        self.create_tablewidgetitem(data=data)
                elif data['total_name'] not in self.download_anime_Thread:
                    self.create_tablewidgetitem(data=data)

    def create_tablewidgetitem(self, data=None, old=False):
        """
        創下載任務表，以及開 Thread 爬動漫。
        :param old:
        :param data: 指定動漫的資料。
        :param now: 現在下載任務的列表。
        :param init: 判斷是不是剛打開程式時的判斷。
        """
        if not old:
            self.download_queue.append(data['total_name'])
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
            self.download_anime_Thread.update(
                {data['total_name']: {'thread': DownloadVideo(data=data, anime=self),
                                      'over': False}})
            self.download_anime_Thread[data['total_name']]['thread'].download_video.connect(self.download_anime_task)
            self.download_anime_Thread[data['total_name']]['thread'].start()

    def download_anime_task(self, signal):
        """
        不斷的更新下載進度表。
        :param signal: 接收下載動漫的資料。
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
                # print(signal)
                print('應該是 Thread 被刪除，剛好 emit。')

    def config(self):
        """
        開啟設定介面。
        """
        self.config_windows = Config(anime=self)
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

    def anime_page_Visible(self, status=False, init=False):
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
        if init:
            self.load_anime_label.setVisible(False)
            self.load_end_anime_label.setVisible(False)

    def load_week_data(self):
        """
        開 Thread 爬每周動漫更新表。
        """
        self.week_data = WeeklyUpdate()
        self.week_data.week_data_signal.connect(self.week_data_task)
        self.week_data.start()

    def week_data_task(self, signal):
        """
        創建每周動漫。
        :param signal: 每周動漫更新表的資料。
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
                                                              "QPushButton:hover{background-color:transparent; color: #00aaff;}\n"
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
        """
        開 Thread 爬指定動漫資料。
        :param url: 指定動漫頁面的 URL。
        """
        self.load_anime_label.setVisible(True)
        self.load_anime_label_status = True
        self.anime_data = AnimeData(url=url)
        self.anime_data.anime_info_signal.connect(self.anime_info_data)
        self.anime_data.start()
        self.anime_info_tabWidget.setCurrentIndex(2)
        self.anime_page_Visible()

    def anime_info_data(self, signal):
        """
        創建指定動漫資訊。
        :param signal: 指定動漫的資料。
        """
        if signal.get('permission'):
            self.load_anime_label.setVisible(False)
            self.load_anime_label_status = False
            msg = QtWidgets.QMessageBox().information(self, "確定",
                                                      f"<font size=4  color=#000000>{signal['permission']}</font><br/><font size=4  color=#000000>請進行登入!</a>",
                                                      QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
            if msg == QtWidgets.QMessageBox.Ok:
                self.login_event()
        elif signal.get('error') or not signal['total']:
            self.load_anime_label.setVisible(False)
            self.load_anime_label_status = False
            QtWidgets.QMessageBox.information(self, "確定",
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
            self.web_label.setText(f"官方網站: <a href=\"{signal[4]}\">{signal[4]}</a>")
            self.remarks_label.setText(signal[5])
            self.type_label.setToolTip(signal[0])
            self.premiere_label.setToolTip(signal[1])
            self.total_set_label.setToolTip(signal[2])
            self.author_label.setToolTip(signal[3])
            self.web_label.setToolTip(signal[4])
            self.remarks_label.setToolTip(signal[5])
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
                    {'name': badname(signal['name']), 'num': badname(m), 'url': signal['total'][m],
                     # name_num 的參數有兩個 "全形空白" 是因為要跟下載清單頁面的右鍵選單功能配合。
                     'name_num': f"{badname(signal['name'])}　　{badname(m)}", 'schedule': 0,
                     'status': '準備中', 'total_name': badname(signal['name']) + badname(m),
                     'video_ts': 0, 'time': None, 'home': signal['home']})
                self.story_checkbox_dict.update({i: QtWidgets.QCheckBox(m)})
                self.story_checkbox_dict[i].setObjectName(data)
                self.story_list_scrollAreaWidgetContents_Layout.addWidget(self.story_checkbox_dict[i])
            self.anime_page_Visible(status=True)
            self.load_anime_label_status = False
            # self.anime_info.terminate()
            # self.anime_info.wait()
            # self.anime_info.quit()
            del self.anime_data

    def loading_end_anime(self):
        """
        開 Thread 爬完結列表。
        """
        self.end_anime = EndAnime()
        self.end_anime.end_anime_signal.connect(self.end_anime_list)
        self.end_anime.start()

    def end_anime_list(self, signal):
        """
        創建完界列表頁面的 Item。
        :param signal: 完界列表的所有資料。
        """
        # end_anime_list(self=self, signal=signal)
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
                                                           "color: #339900;\n"
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
        """
        主要是設定 TabWidget 的高度，讓版面看起來比較好看。
        :param index: 內建的信號判斷是哪一頁。
        """
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
        """
        判斷 Myself 網的的指定動漫頁面。
        """
        check_url(self=self)

    def load_history(self):
        """
        開 Thread 不斷讀取歷史紀錄資料匣的Json。
        """
        self.history_thread = History(anime=self)
        self.history_thread.history_signal.connect(self.create_history_tablewidget_item)
        self.history_thread.start()

    def create_history_tablewidget_item(self, signal):
        """
        新的歷史紀錄，創建新的 TableWidgetItem。
        :param signal: 新的歷史紀錄資料。
        """
        create_history_tablewidget_item(self=self, signal=signal)

    def update_end_anime(self):
        self.end_anime_data = EndAnimeData()
        self.end_anime_data.end_anime_data_signal.connect(self.update_end_anime_mission)
        self.end_anime_data.start()
        update_end_anime(self=self)

    def update_end_anime_mission(self, signal):
        update_end_anime_mission(self=self, signal=signal)
        self.create_end_anime_frame_and_page()

    def search_end_anime(self):
        search_data = search_end_anime(self=self)
        create_end_anime_frame(self=self, search_data=search_data, page=0, limit=8)
        all_page = get_all_page(data=search_data)
        create_end_anime_page(self=self, page=0, all_page=all_page)

    def page_event(self):
        sender = self.sender()
        pushButton = self.findChild(QtWidgets.QPushButton, sender.objectName())
        page = int(pushButton.objectName())
        search_data = search_end_anime(self=self)
        create_end_anime_frame(self=self, search_data=search_data, page=page, limit=8)
        all_page = get_all_page(data=search_data)
        create_end_anime_page(self=self, page=page, all_page=all_page)

    def login_event(self):
        login_event(self=self)

    def mouseHoverOnTabBar(self):
        """
        滑鼠移動到 TabWidget 不用點擊就能切換Tab新增到一個 List 裡面。
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

    def changeEvent(self, event):
        """
        觸發最小化時的事件判斷。
        """
        try:
            status_bar = self.status_bar
        except AttributeError:
            status_bar = True
        if status_bar:
            if event.type() == QtCore.QEvent.WindowStateChange and self.os_system != "Darwin":
                if self.isHidden():
                    tray_icon.showMessage("Message", "被發現了", tray_icon.icon)
                    tray_icon.hide()
                    self.show()
                else:
                    tray_icon.show()
                    tray_icon.showMessage("Message", "藏起來了", tray_icon.icon)
                    self.hide()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if QtCore.Qt.LeftButton and self.moveFlag:
            self.move(QMouseEvent.globalPos() - self.movePosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.moveFlag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))


if __name__ == '__main__':
    os_system = platform.system()
    # myself_anime_connect = False
    if os_system == "Darwin":
        # MAC 要改 工作路徑，此路徑為 Applications 絕對路徑。
        os.chdir('/Applications/MyselfAnime.app/Contents/Macos')
    app = QtWidgets.QApplication(sys.argv)
    if not connect_myself_anime():
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("請確認可以進入 <a href=https://myself-bbs.com/portal.php>MyselfAnime</a> 網站")
        msg.setWindowTitle("無法取得 MyselfAnime 網站資料!")
        msg.setWindowIcon(QtGui.QIcon('./image/logo.ico'))
        msg.exec_()
    else:
        # myStyle = MyProxyStyle()
        # app.setStyle(myStyle)
        anime = Anime(pid=os.getpid(), os_system=os_system)
        # config = Config(anime=anime)
        about = About()
        anime.menu.actions()[1].triggered.connect(about.show)
        anime.show()
        tray_icon = TrayIcon(anime)
        app.exec_()
        kill_pid(os.getpid())
