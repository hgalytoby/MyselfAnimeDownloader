from PyQt5 import QtWidgets, QtCore


def create_history_tablewidget_item(self, signal):
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
