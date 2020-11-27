import shutil
import time
import os
import json
from concurrent.futures.thread import ThreadPoolExecutor

import psutil
from PyQt5 import QtCore

from myself_tools import get_weekly_update, get_end_anine_data, get_anime_data, requests_RequestException, \
    requests_ChunkedEncodingError, requests_ConnectionError, download_request


class WeeklyUpdate(QtCore.QThread):
    """
    爬每周動漫資訊。
    """
    week_data_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(WeeklyUpdate, self).__init__()

    def run(self):
        week_dict = get_weekly_update()
        self.week_data_signal.emit(week_dict)


class EndAnime(QtCore.QThread):
    end_anime_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(EndAnime, self).__init__()

    def run(self):
        data = get_end_anine_data()
        self.end_anime_signal.emit(data)


class AnimeData(QtCore.QThread):
    """
    爬動漫資訊。
    """
    anime_info_signal = QtCore.pyqtSignal(dict)

    def __init__(self, url):
        super(AnimeData, self).__init__()
        self.anime_url = url

    def run(self):
        data = get_anime_data(anime_url=self.anime_url)
        self.anime_info_signal.emit(data)


class History(QtCore.QThread):
    history_signal = QtCore.pyqtSignal(dict)

    def __init__(self, anime):
        super(History, self).__init__()
        self.data = list()
        self.anime = anime

    def run(self):
        while True:
            try:
                result = list()
                for i in os.listdir('./Log/history/'):
                    result.append(i)
                if self.data != result:
                    self.anime.history_tableWidget.clearContents()
                    self.anime.history_tableWidget.setRowCount(0)
                    self.data = result
                    for i in self.data:
                        if i.endswith('.json'):
                            data = json.load(open(f'./Log/history/{i}', 'r', encoding='utf-8'))
                            self.history_signal.emit(data)
            except (NameError, FileNotFoundError):
                print('History Thread Error')
            time.sleep(1)


class LoadingConfigStatus(QtCore.QThread):
    """
    抓記憶體與CPU。
    """
    loading_config_status_signal = QtCore.pyqtSignal(dict)

    def __init__(self, pid):
        super(LoadingConfigStatus, self).__init__()
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


class DownloadVideo(QtCore.QThread):
    """
    下載動漫。
    """
    download_video = QtCore.pyqtSignal(dict)

    def __init__(self, data, init, anime):
        super(DownloadVideo, self).__init__()
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
        self.anime = anime
        if not init:
            self.write_download_order()

    def write_download_order(self):
        while True:
            try:
                if not self.anime.thread_write_download_order_status:
                    self.anime.thread_write_download_order_status = True
                    download = {'wait': self.anime.wait_download_video_mission_list,
                                'now': self.anime.now_download_video_mission_list}
                    json.dump(download, open('./Log/download_order.json', 'w', encoding='utf-8'), indent=2)
                    self.anime.thread_write_download_order_status = False
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
                elif self.data["name"] + self.data["num"] in self.anime.now_download_video_mission_list:
                    self.anime.now_download_value += 1
                    break
                elif len(self.anime.wait_download_video_mission_list) > 0 and \
                        self.anime.wait_download_video_mission_list[0] == \
                        self.data["name"] + self.data[
                    "num"] and self.anime.simultaneously_value > self.anime.now_download_value:
                    self.anime.now_download_value += 1
                    self.anime.now_download_video_mission_list.append(
                        self.anime.wait_download_video_mission_list.pop(0))
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
                    res = download_request(url=self.data['url'], timeout=5)
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
                    m3u8_data = download_request(url=url, timeout=5)
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
            executor = ThreadPoolExecutor(max_workers=self.anime.speed_value)
            for i in range(self.data['video_ts'], m3u8_count):
                executor.submit(self.video, i, res, host, m3u8_count)
            while True:
                if self.data['video_ts'] == m3u8_count:
                    # self.data.update({'status': '已完成'})
                    self.anime.now_download_video_mission_list.remove(self.data['total_name'])
                    self.write_download_order()
                    self.anime.now_download_value -= 1
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
                    data = download_request(url=url, stream=True, timeout=3)
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
            except (requests_RequestException, requests_ConnectionError,
                    requests_ChunkedEncodingError, ConnectionResetError):
                if host_value - 1 > len(host):
                    host_value = 0
                else:
                    host_value += 1
                url = f"{host[host_value]['host']}{res['video']['720p'].split('.')[0]}_{i:03d}.ts"
                print(url)
                time.sleep(1)
            except BaseException as error:
                print('基礎錯誤', error)
