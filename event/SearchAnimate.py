from PyQt5 import QtWidgets, QtGui, QtCore
from typing import Union

from UI.main_ui import Ui_Anime
from event.EndAnime import previous_next_button_setStyleSheet, button_setStyleSheet


def create_search_item(self: Union[QtWidgets.QMainWindow, Ui_Anime], data):
    for index, item in enumerate(data['animate']):
        self.search_animate_dict[item['name']] = QtWidgets.QPushButton(self.search_page_gridLayout_2)
        self.search_animate_dict[item['name']].setText(item['name'])
        self.search_animate_dict[item['name']].setObjectName(item['url'])
        self.search_animate_dict[item['name']].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.search_animate_dict[item['name']].setStyleSheet("QPushButton {\n"
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

        self.search_animate_dict[item['name']].clicked.connect(self.anime_info_event)
        row, col = divmod(index, 10)
        self.search_anime_info_gridLayout.addWidget(
            self.search_animate_dict[item['name']], col, row, 1, 1
        )
    create_pagination(self, data)


def create_pagination(self: Union[QtWidgets.QMainWindow, Ui_Anime], data):
    arr = ['<<', '第一頁', '最後一頁', '>>']
    for k in arr[:2]:
        self.search_pagination_dict[k] = QtWidgets.QPushButton(k)
        previous_next_button_setStyleSheet(self.search_pagination_dict[k], exist=False)
    if data['page'] > 1:
        self.search_pagination_dict['<<'].setObjectName(
            data['base_url'].replace('replace_page', f'page={str(data["page"] - 1)}'))
        self.search_pagination_dict['<<'].clicked.connect(self.search_animate_pagination_event)
        previous_next_button_setStyleSheet(self.search_pagination_dict['<<'], exist=True)
        self.search_pagination_dict['第一頁'].setObjectName(data['base_url'].replace('replace_page', 'page=1'))
        self.search_pagination_dict['第一頁'].clicked.connect(self.search_animate_pagination_event)
        previous_next_button_setStyleSheet(self.search_pagination_dict['第一頁'], exist=True)

    start = 0
    end = 7
    if data['page'] - 3 > 1 and data['total'] > data['page'] + 3:
        start = data['page'] - 4
        end = data['page'] + 3
    elif 0 >= data['page'] - 3 and data['page'] + 3 >= data['total']:
        start = 0
        end = data['total']
    elif 7 > data['total']:
        start = 0
        end = data['total']
    elif data['page'] + 4 >= data['total']:
        start = data['total'] - 7
        end = data['total']
    for i in range(start, end):
        self.search_pagination_dict[i] = QtWidgets.QPushButton(str(i + 1))
        if i + 1 == data['page']:
            button_setStyleSheet(self.search_pagination_dict[i], self=True)
        else:
            button_setStyleSheet(self.search_pagination_dict[i], self=False)
            if data['base_url']:
                self.search_pagination_dict[i].setObjectName(data['base_url'].replace('replace_page', f'page={i + 1}'))
            self.search_pagination_dict[i].clicked.connect(self.search_animate_pagination_event)
    for k in arr[2:]:
        self.search_pagination_dict[k] = QtWidgets.QPushButton(k)
        previous_next_button_setStyleSheet(self.search_pagination_dict[k], exist=False)
    if data['page'] < data['total']:
        self.search_pagination_dict['>>'].clicked.connect(self.search_animate_pagination_event)
        previous_next_button_setStyleSheet(self.search_pagination_dict['>>'], exist=True)
        self.search_pagination_dict['>>'].setObjectName(
            data['base_url'].replace('replace_page', f'page={str(data["page"] + 1)}'))
        self.search_pagination_dict['最後一頁'].clicked.connect(self.search_animate_pagination_event)
        previous_next_button_setStyleSheet(self.search_pagination_dict['最後一頁'], exist=True)

        self.search_pagination_dict['最後一頁'].setObjectName(
            data['base_url'].replace('replace_page', f'page={str(data["total"])}'))

    for k, v in self.search_pagination_dict.items():
        self.search_page_horizontalLayout.addWidget(v)
