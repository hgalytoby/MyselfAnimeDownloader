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
    delete_end_anime_frame(self=self)
    self.preview_dict.clear()
    if len(search) > 0:
        for i, name in enumerate(self.localhost_end_anime_list):
            if search in name:
                search_data.append(self.localhost_end_anime_list[i])
        create_end_anime_frame(self=self, search_data=search_data)


def delete_end_anime_frame(self):
    for i in range(self.end_anime_gridLayout.count()):
        self.end_anime_gridLayout.itemAt(i).widget().deleteLater()


def create_end_anime_frame(self, search_data):
    for i, name in enumerate(search_data):
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
