import shutil
import time
import os
import json
import datetime
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import closing

import m3u8
import psutil
import websocket
import ssl
from PyQt5 import QtCore

from myself_tools import get_weekly_update, get_end_anime_list, get_anime_data, requests_RequestException, \
    requests_ChunkedEncodingError, requests_ConnectionError, download_request, get_total_page, get_now_page_anime_data, \
    download_end_anime_preview, badname, check_version, cpu_memory, myself_login, get_login_select, search_animate, \
    record

ws_opt = {
    'url': "wss://v.myself-bbs.com/ws",
    'header': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    },
    'host': 'v.myself-bbs.com',
    'origin': 'https://v.myself-bbs.com',
}


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
    check_version = QtCore.pyqtSignal(bool)

    def __init__(self, version):
        super(CheckVersion, self).__init__()
        self.version = version

    def run(self):
        result = check_version(self.version)
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
        if data:
            self.anime_info_signal.emit(data)
        else:
            self.anime_info_signal.emit({'error': True, 'home': self.anime_url})


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
            self.config.update(cpu_memory(self.info))
            self.loading_config_status_signal.emit(self.config)
            time.sleep(1)


class DownloadVideo(QtCore.QThread):
    """
    下載動漫。
    """
    download_video = QtCore.pyqtSignal(dict)

    def __init__(self, data, anime):
        """
        :param data:
        :param init: 判斷是不是一開始打開程式，就不寫入正在下載與等待下載到 Json了。
        :param anime: QT主頁面的東西。
        """
        super(DownloadVideo, self).__init__()
        self.anime = anime
        self.data = data
        self.path = json.load(open('config.json', 'r', encoding='utf-8'))
        self.folder_name = self.data['name']
        self.file_name = self.data['num']
        self.file_path = f'{self.path["path"]}/{self.folder_name}/{self.file_name}.mp4.download'
        if not os.path.isdir(f'{self.path["path"]}/{self.folder_name}'):
            os.makedirs(f'{self.path["path"]}/{self.folder_name}')
        if self.data['video_ts'] == 0 and os.path.isfile(self.file_path):
            os.remove(self.file_path)
        if os.path.isfile(self.file_path.split('.download')[0]):
            os.remove(self.file_path.split('.download')[0])
        json.dump({'queue': self.anime.download_queue}, open('./Log/DownloadQueue.json', 'w', encoding='utf-8'),
                  indent=2)
        json.dump(self.data, open(f'./Log/undone/{self.data["total_name"]}.json', 'w', encoding='utf-8'), indent=2)
        json.dump(self.data, open(f'./Log/history/{self.data["total_name"]}.json', 'w', encoding='utf-8'), indent=2)
        self.stop = False
        self.exit = False
        self.remove_file = False
        self.process_end = True
        # self.requests_error_count = 0
        # self.re_download_count = 200
        self.ts_time = time.time()

    def write_undone(self, index, m3u8_count):
        if self.data['video_ts'] == m3u8_count - 1 or self.data['video_ts'] == m3u8_count:
            status = '已完成'
            schedule = 100
        else:
            status = '下載中'
            schedule = int(self.data['video_ts'] / (m3u8_count - 1) * 100)
        self.data.update({
            'video_ts': index,
            'schedule': schedule,
            'status': status
        })
        json.dump(self.data, open(f'./Log/undone/{self.data["total_name"]}.json', 'w', encoding='utf-8'),
                  indent=2)

    def del_file(self):
        try:
            os.remove(self.file_path)
        except (PermissionError, FileNotFoundError):
            pass
        except BaseException as error:
            print(f'del_file error: {error}')

    def del_undone_json(self):
        try:
            if os.path.isfile(f'./Log/undone/{self.data["total_name"]}.json'):
                os.remove(f'./Log/undone/{self.data["total_name"]}.json')
        except (PermissionError, FileNotFoundError):
            pass
        except BaseException as error:
            print(f'del_json error: {error}')

    def turn_me(self):
        """
        判斷下載列表順序使否輪到自己。
        """
        while True:
            try:
                if self.exit:
                    break
                elif self.data["total_name"] in self.anime.download_queue[:self.anime.simultaneously_value] \
                        and self.anime.simultaneously_value > self.anime.now_download_value:
                    self.anime.now_download_value += 1
                    break
                time.sleep(1)
            except NameError as e:
                print(f'turn_me error: {e}')
                time.sleep(0.5)

    def get_host_video_data(self):
        """
        取得 Host資料。
        """
        error_value = 1
        self.data.update({'status': f'取得資料中'})
        while True:
            self.download_video.emit(self.data)
            try:
                res = download_request(url=self.data['url'], timeout=(15, 15))
                print(res, res.text, self.data['url'])
                if res:
                    data = res.json()
                    res.close()
                    self.data.update({'status': '成功取得資料'})
                    self.download_video.emit(self.data)
                    return data
            except BaseException as error:
                pass
            self.data.update({'status': f'取得資料中(失敗{error_value}次)'})
            error_value += 1
            time.sleep(5)

    def get_m3u8_data(self, res):
        """
        取得 m3u8 資料。
        """
        index = 0
        error_value = 1
        url = res['host'][index]['host'] + res['video']['720p']
        self.data.update({'status': '取得影片資料中'})
        while True:
            try:
                m3u8_data = download_request(url=url, timeout=(15, 15))
                if m3u8_data:
                    data = m3u8_data.text
                    m3u8_data.close()
                    self.data.update({'status': '成功取得影片資料'})
                    self.download_video.emit(self.data)
                    return data
            except BaseException as error:
                pass
            self.data.update({'status': f'取得影片資料中(失敗{error_value}次)'})
            self.download_video.emit(self.data)
            error_value += 1
            if index == len(res['host']) - 1:
                index = 0
            else:
                index += 1
            url = res['host'][index]['host'] + res['video']['720p']
            time.sleep(5)

    def get_m3u8_data_v2(self, url, tid, vid, video_id):
        """
        取得 m3u8 資料。
        """
        error_value = 1
        self.data.update({'status': '取得影片資料中'})
        while True:
            try:
                m3u8_data = download_request(url=url, timeout=(15, 15))
                if m3u8_data:
                    data = m3u8_data.text
                    m3u8_data.close()
                    self.data.update({'status': '成功取得影片資料'})
                    self.download_video.emit(self.data)
                    return data
            except BaseException as error:
                pass
            self.data.update({'status': f'取得影片資料中(失敗{error_value}次)'})
            self.download_video.emit(self.data)
            _, url = self.ws_get_host_and_m3u8_url(tid, vid, video_id)
            error_value += 1
            # if index == len(res['host']) - 1:
            #     index = 0
            # else:
            #     index += 1
            # url = res['host'][index]['host'] + res['video']['720p']
            time.sleep(5)

    @classmethod
    def ws_get_host_and_m3u8_url(cls, tid, vid, video_id):
        try:
            with closing(websocket.create_connection(**ws_opt)) as ws:
                ws.send(json.dumps({'tid': tid, 'vid': vid, 'id': video_id}))
                recv = ws.recv()
                res = json.loads(recv)
                m3u8_url = f'https:{res["video"]}'
                if video_id:
                    video_url = m3u8_url.split('/index.m3u8')[0]
                else:
                    video_url = m3u8_url[:m3u8_url.rfind('/')]
                return video_url, m3u8_url
        except ssl.SSLCertVerificationError:
            ws_opt['sslopt'] = {'cert_reqs': ssl.CERT_NONE}
            print(f'ssl 憑證有問題: ws_opt: {ws_opt}')
            return '', ''
        except BaseException as e:
            print(f'websocket 短時間連線太多會出問題: ws_opt: {ws_opt}')
            return '', ''

    def run(self):
        record()
        self.turn_me()
        if not self.exit:
            # v2
            temp = self.data['url'].split('/')
            if temp[-1].isdigit():
                tid, vid, video_id = temp[-2], temp[-1], ''
            else:
                tid, vid, video_id = '', '', temp[-1]
            video_url, m3u8_url = self.ws_get_host_and_m3u8_url(tid=tid, vid=vid, video_id=video_id)
            m3u8_data = self.get_m3u8_data_v2(m3u8_url, tid, vid, video_id)
            m3u8_obj = m3u8.loads(m3u8_data)
            m3u8_count = len(m3u8_obj.segments)
            # v1
            # res = self.get_host_video_data()
            # host = sorted(res['host'], key=lambda i: i.get('weight'), reverse=True)
            # video_url = f'https://{host}.myself-bbs.com/{tid}/{vid}/720p'
            executor = ThreadPoolExecutor(max_workers=self.anime.speed_value)
            for i in range(self.data['video_ts'], m3u8_count):
                # executor.submit(self.video, i, res, host, m3u8_count)
                executor.submit(self.video_v2, i, m3u8_obj.segments[i].uri, video_url, tid, vid, m3u8_count, video_id)
            while True:
                if self.data['video_ts'] == m3u8_count or self.exit:
                    break
                # if self.requests_error_count > self.re_download_count:
                #     self.data.update({
                #         'schedule': int(self.data['video_ts'] / (m3u8_count - 1) * 100),
                #         'status': '下載失敗',
                #     })
                if time.time() - self.ts_time > 120:
                    self.anime.re_download_dict.update({
                        self.data['total_name']:
                            {
                                'time': time.time(),
                                'data': self.data,
                            },
                    })
                    self.exit = True
                    break
                if self.data['status'] != '已完成':
                    self.data.update({
                        'schedule': int(self.data['video_ts'] / (m3u8_count - 1) * 100),
                        'status': '下載中',
                    })
                    self.download_video.emit(self.data)
                time.sleep(0.3)
            try:
                if self.data['video_ts'] == m3u8_count:
                    os.rename(self.file_path, self.file_path.split('.download')[0])
                    self.anime.download_queue.remove(self.data["total_name"])
                    json.dump({'queue': self.anime.download_queue},
                              open('./Log/DownloadQueue.json', 'w', encoding='utf-8'),
                              indent=2)
            except BaseException as e:
                print(f'抓刪除時 queue 有錯誤 {e}')
            self.download_video.emit(self.data)
            self.anime.now_download_value -= 1
        json.dump({'queue': self.anime.download_queue}, open('./Log/DownloadQueue.json', 'w', encoding='utf-8'),
                  indent=2)
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
            try:
                # if not self.stop and not self.exit and self.re_download_count > self.requests_error_count:
                if not self.stop and not self.exit:
                    data = download_request(url=url, stream=False, timeout=(5, 15))
                    if data.ok:
                        while True:
                            if self.stop or self.exit:
                                data.close()
                                del data
                                break
                            elif self.data['video_ts'] == i and self.process_end:
                                self.process_end = False
                                with open(self.file_path, 'ab') as v:
                                    self.write_undone(index=i, m3u8_count=m3u8_count)
                                    v.write(data.content)
                                    v.flush()
                                    # shutil.copyfileobj(data.raw, v)
                                self.data['video_ts'] += 1
                                self.write_undone(index=self.data['video_ts'], m3u8_count=m3u8_count)
                                if self.remove_file:
                                    self.del_file()
                                self.process_end = True
                                ok = True
                                data.close()
                                del data
                                break
                            # elif self.stop or self.exit or self.requests_error_count > self.re_download_count:
                            time.sleep(0.1)
                    if ok:
                        break
                # if self.exit or self.requests_error_count > self.re_download_count:
                if self.exit:
                    break
            except (requests_RequestException, requests_ConnectionError,
                    requests_ChunkedEncodingError, ConnectionResetError) as e:
                # self.requests_error_count += 1
                print('req error', url)
            except BaseException as error:
                # self.requests_error_count += 1
                print('BaseException', url)
                # print(error, url)
                # print('不明的錯: 暫時先換分流照做')
            if host_value == len(host) - 1:
                host_value = 0
            else:
                host_value += 1
            url = f"{host[host_value]['host']}{res['video']['720p'].split('.')[0]}_{i:03d}.ts"
            time.sleep(3)
        self.ts_time = time.time()

    def video_v2(self, i, uri, video_url, tid, vid, m3u8_count, video_id):
        """
        請求 URL 下載影片。
        """
        ok = False
        while True:
            url = f'{video_url}/{uri}'
            try:
                # if not self.stop and not self.exit and self.re_download_count > self.requests_error_count:
                if not self.stop and not self.exit:
                    data = download_request(url=url, stream=False, timeout=(5, 15))
                    if data.ok:
                        while True:
                            if self.stop or self.exit:
                                data.close()
                                del data
                                break
                            elif self.data['video_ts'] == i and self.process_end:
                                self.process_end = False
                                with open(self.file_path, 'ab') as v:
                                    self.write_undone(index=i, m3u8_count=m3u8_count)
                                    v.write(data.content)
                                    v.flush()
                                    # shutil.copyfileobj(data.raw, v)
                                self.data['video_ts'] += 1
                                self.write_undone(index=self.data['video_ts'], m3u8_count=m3u8_count)
                                if self.remove_file:
                                    self.del_file()
                                self.process_end = True
                                ok = True
                                data.close()
                                del data
                                break
                            # elif self.stop or self.exit or self.requests_error_count > self.re_download_count:
                            time.sleep(0.1)
                    elif not data.ok:
                        video_url, _ = self.ws_get_host_and_m3u8_url(tid=tid, vid=vid, video_id=video_id)
                        print(f'in not ok, new video_url: {url}{video_url}')
                    if ok:
                        break
                # if self.exit or self.requests_error_count > self.re_download_count:
                if self.exit:
                    break
            except (requests_RequestException, requests_ConnectionError,
                    requests_ChunkedEncodingError, ConnectionResetError) as e:
                # self.requests_error_count += 1
                print('req error', url)
                video_url, _ = self.ws_get_host_and_m3u8_url(tid=tid, vid=vid, video_id=video_id)
                print('s', video_url, url)

            except BaseException as error:
                # self.requests_error_count += 1
                print('BaseException', error, url)
                # print(error, url)
                # print('不明的錯: 暫時先換分流照做')
                video_url, _ = self.ws_get_host_and_m3u8_url(tid=tid, vid=vid, video_id=video_id)
                print('s', video_url, url)
            time.sleep(3)
        self.ts_time = time.time()


class EndAnimeData(QtCore.QThread):
    """
    爬完結動畫。
    """
    end_anime_data_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
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


class LoginInit(QtCore.QThread):
    """
    抓登入會員時需要的資料。
    """
    login_init_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(LoginInit, self).__init__()

    def run(self):
        result = get_login_select()
        self.login_init_signal.emit(result)


class MyselfLogin(QtCore.QThread):
    """
    登入會員。
    """
    myself_login_signal = QtCore.pyqtSignal(bool)

    def __init__(self, login_data):
        super(MyselfLogin, self).__init__()
        self.login_data = login_data

    def run(self):
        result = myself_login(self.login_data)
        self.myself_login_signal.emit(result)


class ProcessExit(QtCore.QThread):
    """
    結束程式時，等待所有下載動漫的 Thread 離開再關閉程式。
    """
    process_exit_signal = QtCore.pyqtSignal(bool)

    def __init__(self, anime):
        super(ProcessExit, self).__init__()
        self.anime = anime

    def run(self):
        for k, v in self.anime.download_anime_Thread.items():
            if not v['over']:
                v['thread'].exit = True
        for k, v in self.anime.download_anime_Thread.items():
            if not v['over']:
                while True:
                    if v['thread'].process_end:
                        break
                    time.sleep(0.5)
        time.sleep(1)
        self.process_exit_signal.emit(True)


class CheckTsStatus(QtCore.QThread):
    """
    暫時棄用。
    """
    check_ts_status = QtCore.pyqtSignal(dict)

    def __init__(self, anime):
        super(CheckTsStatus, self).__init__()
        self.anime = anime

    def run(self):
        while True:
            for k, v in self.anime.download_anime_Thread.items():
                if not v['over'] and time.time() - self.anime.download_anime_Thread[k]['thread'].ts_time > \
                        self.anime.re_download_min + 60:
                    self.anime.download_anime_Thread[k]['thread'].requests_error_count += 200
                    time.sleep(10)
                    self.anime.re_download_dict.update({
                        k:
                            {
                                'time': time.time() - 60 * (self.anime.re_download_min + 1),
                                'data': self.anime.download_anime_Thread[k]['thread'].data,
                            },
                    })
            time.sleep(1)


class ReDownload(QtCore.QThread):
    """
    因失敗太多，等待一定的時間後，重新下載的動漫。
    """
    re_download = QtCore.pyqtSignal(dict)

    def __init__(self, anime):
        super(ReDownload, self).__init__()
        self.anime = anime

    def run(self):
        _ = []
        while True:
            if self.anime.re_download_dict:
                for k, v in self.anime.re_download_dict.items():
                    self.re_download.emit(v['data'])
                    _.append(k)
                for k in _:
                    del self.anime.re_download_dict[k]
                _.clear()
            time.sleep(1)


class SearchAnimateThread(QtCore.QThread):
    """
    搜尋動漫。
    """
    result = QtCore.pyqtSignal(dict)

    def __init__(self, search_name: str = None, url=None):
        super(SearchAnimateThread, self).__init__()
        self.search_name = search_name
        self.url = url

    def run(self):
        result = search_animate(name=self.search_name, url=self.url)
        self.result.emit(result)
