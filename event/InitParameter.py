import os

from PyQt5 import QtWidgets, QtCore, QtGui


def init_parameter(self, pid, os_system):
    self.now_download_value = 0
    self.pid = pid
    self.os_system = os_system
    self.check_version_result = False
    self.load_end_anime_status = False
    self.load_week_label_status = False
    self.load_anime_label_status = False
    self.thread_write_download_order_status = False
    self.end_tab = dict()
    self.week_dict = dict()
    self.preview_dict = dict()
    self.end_qt_object = dict()
    self.week_layout_dict = dict()
    self.story_checkbox_dict = dict()
    self.download_anime_Thread = dict()
    self.history_tableWidget_dict = dict()
    self.download_progressBar_dict = dict()
    self.download_status_label_dict = dict()
    self.tableWidgetItem_download_dict = dict()
    self.week = {0: self.Monday_scrollAreaWidgetContents, 1: self.Tuesday_scrollAreaWidgetContents,
                 2: self.Wednesday_scrollAreaWidgetContents, 3: self.Thursday_scrollAreaWidgetContents,
                 4: self.Friday_scrollAreaWidgetContents, 5: self.Staurday_scrollAreaWidgetContents,
                 6: self.Sunday_scrollAreaWidgetContents}
    self.download_tableWidget.setColumnWidth(0, 400)
    self.download_tableWidget.setColumnWidth(1, 150)
    # self.download_tableWidget.setColumnWidth(2, 431)
    self.download_tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
    self.download_tableWidget.verticalHeader().setVisible(False)
    self.download_tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.download_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    self.download_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    self.download_tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    self.history_tableWidget.setColumnWidth(1, 150)
    self.history_tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    self.history_tableWidget.verticalHeader().setVisible(False)
    self.history_tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.history_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    self.history_tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    self.setWindowIcon(QtGui.QIcon('image/logo.ico'))
    self.user_icon_label.setPixmap(QtGui.QPixmap("./image/noavatar_small.gif"))
    self.setFixedSize(self.width(), self.height())
