def pushbutton_clicked_connect(self):
    self.download_tableWidget.cellClicked.connect(self.print_row)
    self.download_tableWidget.customContextMenuRequested.connect(
        self.download_tableWidget_on_custom_context_menu_requested)
    self.history_tableWidget.customContextMenuRequested.connect(
        self.history_tableWidget_on_custom_context_menu_requested)
    self.menu.actions()[0].triggered.connect(self.config)
    self.menu.actions()[2].triggered.connect(self.check_version)
    self.menu.actions()[3].triggered.connect(self.closeEvent)
    self.story_list_all_pushButton.clicked.connect(self.check_checkbox)
    self.download_pushbutton.clicked.connect(self.download_anime)
    self.customize_pushButton.clicked.connect(self.check_url)
    self.anime_info_tabWidget.currentChanged.connect(self.click_on_tablewidget)
    self.end_anime_pushButton.clicked.connect(self.update_end_anime)
    self.end_anime_lineEdit.textChanged.connect(self.search_end_anime)
    self.login_pushButton.clicked.connect(self.login_event)
