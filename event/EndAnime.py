from PyQt5 import QtWidgets, QtGui, QtCore


def update_end_anime(self):
    self.end_anime_pushButton.setText('正在更新中')
    self.end_anime_pushButton.setEnabled(False)
    self.end_anime_lineEdit.setEnabled(False)


def update_end_anime_mission(self, signal):
    self.end_anime_pushButton.setText('更新')
    self.end_anime_pushButton.setEnabled(True)
    self.end_anime_lineEdit.setPlaceholderText('搜尋')
    self.end_anime_lineEdit.setEnabled(True)
    self.localhost_end_anime_dict = signal['data']
    self.localhost_end_anime_list = list(signal['data'].keys())
    self.end_anime_last_update_date.setText(f'最後更新日期: {signal["date"]}')


def search_end_anime(self):
    search = self.end_anime_lineEdit.text()
    search_data = list()
    if len(search) > 0:
        for i, name in enumerate(self.localhost_end_anime_list):
            if search in name:
                search_data.append(self.localhost_end_anime_list[i])
        return search_data
    return self.localhost_end_anime_list


def delete_end_anime_frame(self):
    self.preview_dict.clear()
    for i in range(self.end_anime_gridLayout.count()):
        self.end_anime_gridLayout.itemAt(i).widget().deleteLater()


def delete_end_anime_page(self):
    self.page_button_dict.clear()
    for i in range(self.page_button_horizontalLayout.count()):
        self.page_button_horizontalLayout.itemAt(i).widget().deleteLater()


def create_end_anime_frame(self, search_data, page, limit):
    delete_end_anime_frame(self=self)
    data = search_data[page * limit:page * limit + limit]
    for i, name in enumerate(data):
        self.preview_dict.update({
            name: {
                'img_label': QtWidgets.QLabel(),
                'total_label': QtWidgets.QLabel(),
                'name_button': QtWidgets.QPushButton(),
                'preview_frame': QtWidgets.QFrame(),
                'layout': QtWidgets.QVBoxLayout()
            }
        })
        self.preview_dict[name]['img_label'].setPixmap(QtGui.QPixmap(f'./EndAnimeData/preview/{name}.jpg'))
        self.preview_dict[name]['img_label'].setScaledContents(True)
        self.preview_dict[name]['total_label'].setText(self.localhost_end_anime_dict[name]['total'])
        self.preview_dict[name]['name_button'].setText(name)
        self.preview_dict[name]['name_button'].setToolTip(name)
        self.preview_dict[name]['name_button'].setObjectName(self.localhost_end_anime_dict[name]['url'])
        self.preview_dict[name]['name_button'].clicked.connect(self.anime_info_event)
        self.preview_dict[name]['layout'].addWidget(self.preview_dict[name]['img_label'])
        self.preview_dict[name]['layout'].addWidget(self.preview_dict[name]['total_label'], 0,
                                                    QtCore.Qt.AlignHCenter)
        self.preview_dict[name]['layout'].setContentsMargins(0, 0, 0, 0)
        self.preview_dict[name]['layout'].addWidget(self.preview_dict[name]['name_button'])
        self.preview_dict[name]['preview_frame'].setFrameShape(QtWidgets.QFrame.Box)
        self.preview_dict[name]['preview_frame'].setLayout(self.preview_dict[name]['layout'])
        self.preview_dict[name]['preview_frame'].setMinimumSize(QtCore.QSize(231, 210))
        self.preview_dict[name]['preview_frame'].setMaximumSize(QtCore.QSize(231, 210))
        self.end_anime_gridLayout.addWidget(self.preview_dict[name]['preview_frame'], i // 4, i % 4)


def button_setStyleSheet(button, self):
    if self:
        button.setStyleSheet("QPushButton {\n"
                             "color: white;\n"
                             "border-style:none;\n"
                             "padding:5px;\n"
                             "background-color:#55aaff;\n"
                             "border-radius:6px;\n"
                             "}")
        return
    button.setStyleSheet("QPushButton {\n"
                         "color: #55aaff;\n"
                         "border-style:none;\n"
                         "padding:5px;\n"
                         "background-color:White;\n"
                         "border-radius:6px;\n"
                         "}")


def previous_next_button_setStyleSheet(button, exist):
    if exist:
        button.setStyleSheet("QPushButton {\n"
                             "color: #55aaff;\n"
                             "border-style:none;\n"
                             "padding:5px;\n"
                             "background-color:White;\n"
                             "border-radius:6px;\n"
                             "}")
        return
    button.setStyleSheet("QPushButton {\n"
                         "color: black;\n"
                         "border-style:none;\n"
                         "padding:5px;\n"
                         "background-color:White;\n"
                         "border-radius:6px;\n"
                         "}")


def create_end_anime_page(self, page, all_page):
    delete_end_anime_page(self=self)
    start = 0
    end = 7
    if page == all_page == 0:
        return
    self.page_button_dict.update({'<<': QtWidgets.QPushButton('<<')})
    if page != 0:
        self.page_button_dict['<<'].setObjectName(str(page - 1))
        self.page_button_dict['<<'].clicked.connect(self.page_event)
        previous_next_button_setStyleSheet(self.page_button_dict['<<'], exist=True)
    else:
        previous_next_button_setStyleSheet(self.page_button_dict['<<'], exist=False)
    self.page_button_horizontalLayout.addWidget(self.page_button_dict['<<'], 0, QtCore.Qt.AlignHCenter)
    self.page_button_dict.update({'first': QtWidgets.QPushButton('第一頁')})
    button_setStyleSheet(self.page_button_dict['first'], self=False)
    self.page_button_horizontalLayout.addWidget(self.page_button_dict['first'], 1, QtCore.Qt.AlignHCenter)
    if page - 3 > -1 and all_page > page + 3:
        start = page - 3
        end = page + 4
    elif 0 >= page - 3 and page + 3 >= all_page:
        start = 0
        end = all_page
    elif 7 > all_page:
        start = 0
        end = all_page
    elif page + 4 >= all_page:
        start = all_page - 7
        end = all_page
    for i in range(start, end):
        self.page_button_dict.update({f'button{i + 1}': QtWidgets.QPushButton(f'{i + 1}')})
        self.page_button_dict[f'button{i + 1}'].setObjectName(str(i))
        self.page_button_dict[f'button{i + 1}'].clicked.connect(self.page_event)
        if page != i:
            button_setStyleSheet(self.page_button_dict[f'button{i + 1}'], self=False)
        else:
            button_setStyleSheet(self.page_button_dict[f'button{i + 1}'], self=True)
        self.page_button_horizontalLayout.addWidget(self.page_button_dict[f'button{i + 1}'], i + 2,
                                                    QtCore.Qt.AlignHCenter)
    self.page_button_dict.update({'last': QtWidgets.QPushButton('最後一頁')})
    button_setStyleSheet(self.page_button_dict['last'], self=False)
    self.page_button_horizontalLayout.addWidget(self.page_button_dict['last'], -2, QtCore.Qt.AlignHCenter)
    if page != 1 and all_page != 1:
        self.page_button_dict['first'].setObjectName('0')
        self.page_button_dict['last'].setObjectName(str(all_page - 1))
        self.page_button_dict['first'].clicked.connect(self.page_event)
        self.page_button_dict['last'].clicked.connect(self.page_event)

    self.page_button_dict.update({'>>': QtWidgets.QPushButton('>>')})
    if page + 1 != all_page:
        self.page_button_dict['>>'].setObjectName(str(page + 1))
        self.page_button_dict['>>'].clicked.connect(self.page_event)
        previous_next_button_setStyleSheet(self.page_button_dict['>>'], exist=True)
    else:
        previous_next_button_setStyleSheet(self.page_button_dict['>>'], exist=False)
    self.page_button_horizontalLayout.addWidget(self.page_button_dict['>>'], -1, QtCore.Qt.AlignHCenter)

    object_average = 10 // self.page_button_horizontalLayout.count()
    for i in range(self.page_button_horizontalLayout.count()):
        self.page_button_horizontalLayout.setStretch(i, object_average)
    pass
