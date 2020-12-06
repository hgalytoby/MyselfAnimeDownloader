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
