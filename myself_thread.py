import shutil
import time
import os
import json
import datetime
from concurrent.futures.thread import ThreadPoolExecutor

import psutil
from PyQt5 import QtCore

from myself_tools import get_weekly_update, get_end_anime_list, get_anime_data, requests_RequestException, \
    requests_ChunkedEncodingError, requests_ConnectionError, download_request, get_total_page, get_now_page_anime_data, \
    download_end_anime_preview, badname, check_version


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
    """
    爬完結列表的動漫。
    """
    end_anime_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(EndAnime, self).__init__()

    def run(self):
        data = get_end_anime_list()
        self.end_anime_signal.emit(data)


class CheckVersion(QtCore.QThread):
    """
    爬完結列表的動漫。
    """
    check_version = QtCore.pyqtSignal(dict)

    def __init__(self, version):
        super(CheckVersion, self).__init__()
        self.version = version

    def run(self):
        result = check_version(VERSION)
        self.check_version.emit(result)


class AnimeData(QtCore.QThread):
    """
    爬指定動漫的資訊。
    """
    anime_info_signal = QtCore.pyqtSignal(dict)

    def __init__(self, url):
        super(AnimeData, self).__init__()
        self.anime_url = url

    def run(self):
        data = get_anime_data(anime_url=self.anime_url)
        self.anime_info_signal.emit(data)


class History(QtCore.QThread):
    """
    檢查歷史列表。
    """
    history_signal = QtCore.pyqtSignal(dict)

    def __init__(self, anime):
        super(History, self).__init__()
        self.data = list()
        self.anime = anime

    def run(self):
        # 不斷的檢查歷史紀錄資料夾下的動漫資料，加到 Qt內。
        while True:
            try:
                # 歷史紀錄資料夾下的動漫資料加到List。
                result = list()
                for i in os.listdir('./Log/history/'):
                    result.append(i)
                # 發現不等於就是有新的歷史紀錄了。
                if self.data != result:
                    self.anime.history_tableWidget.clearContents()
                    self.anime.history_tableWidget.setRowCount(0)
                    self.data = result
                    for i in self.data:
                        if i.endswith('.json'):
                            data = json.load(open(f'./Log/history/{i}', 'r', encoding='utf-8'))
                            self.history_signal.emit(data)
            # I/O好像會起衝突?
            except (NameError, FileNotFoundError):
                print('History Thread Error')
            time.sleep(1)


class LoadingConfigStatus(QtCore.QThread):
    """
    抓記憶體與CPU。
    Windows 工作管理員的記憶體與CPU會不同。
    Linux 好像差不多?
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
        """
        :param data:
        :param init: 判斷是不是一開始打開程式，就不寫入正在下載與等待下載到 Json了。
        :param anime: QT主頁面的東西。
        """
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

    def repeating_work(self):
        """
        刪除檔案要執行這三行，更新正在下載與等待下載列表與刪除檔案和動漫資料Json。
        :return:
        """
        if not self.del_download_order:
            self.del_download_order = True
            self.write_download_order()
            self.del_file_and_json()

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
                    self.repeating_work()
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
                    self.repeating_work()
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
                    self.repeating_work()
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


class EndAnimeData(QtCore.QThread):
    """
    爬完結動畫。
    """
    end_anime_data_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        """
        :param reset:
            謹慎檢查，如果等於 True 就是從第一頁爬到最尾頁，如果是 False 就是遇到資料已存在就不爬了。
            主要是避免還沒爬完就被關閉程式，導致沒爬到最尾頁的資料，下次爬的時候一開始就會止步了。
        """
        super(EndAnimeData, self).__init__()
        self.data = dict()
        self.page_count = 1
        self.preview_count = 0

    def get_now_page_anime_data(self, page):
        try:
            page_data = get_now_page_anime_data(page=page)
            self.data.update(page_data)
            self.page_count += 1
        except BaseException as e:
            print('爬完結動漫頁面 Thread 出錯了', e)

    def download_end_anime_preview(self, name, img_url):
        try:
            name = badname(name)
            if not os.path.isfile(f'./EndAnimeData/preview/{name}.jpg'):
                img_content = download_end_anime_preview(img_url)
                with open(f'./EndAnimeData/preview/{name}.jpg', 'wb') as img:
                    shutil.copyfileobj(img_content.raw, img)
            self.preview_count += 1
        except BaseException as e:
            print('爬完結動漫預覽圖 Thread 出錯了', e)

    def run(self):
        # 創資料夾
        if not os.path.isdir('./EndAnimeData'):
            os.mkdir('EndAnimeData')
        if not os.path.isdir('./EndAnimeData/preview'):
            os.mkdir('./EndAnimeData/preview')
        # 取得最後一頁，get_html=True 是指 拿回 html，False就是不拿取，因為是到第一頁的頁面取得總頁數，所以等等第一頁可以不要爬了。
        total_page = get_total_page(get_html=True)
        # 開執行續池爬快一點最多一次看16頁。
        executor = ThreadPoolExecutor(max_workers=16)
        for page in range(1, total_page['total_page'] + 1):
            if page == 1 and 'html' in total_page:
                # 因為有html，所以就不用爬了。
                page_data = get_now_page_anime_data(page=page, res=total_page['html'])
                self.data.update(page_data)
            else:
                executor.submit(self.get_now_page_anime_data, page)
        # 確認全部爬完了再進離開。
        while True:
            if self.page_count == total_page['total_page']:
                break
            time.sleep(0.5)
        # 總動漫數量
        total_preview_count = len(self.data)
        # 開執行續池爬圖片最多一次爬16個圖片。
        preview_executor = ThreadPoolExecutor(max_workers=16)
        for name in self.data:
            preview_executor.submit(self.download_end_anime_preview, name, self.data[name]['img'])
        # 確認圖片都爬完了。
        while True:
            if self.preview_count == total_preview_count:
                break
            time.sleep(0.5)
        # 取得更新日期
        date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        # 寫入資料
        json.dump({'Date': date}, open('./EndAnimeData/UpdateDate.json', 'w', encoding='utf-8'), indent=2)
        json.dump(self.data, open('./EndAnimeData/EndAnimeData.json', 'w', encoding='utf-8'), indent=2)
        result = {
            'data': self.data,
            'date': date,
        }
        self.end_anime_data_signal.emit(result)
