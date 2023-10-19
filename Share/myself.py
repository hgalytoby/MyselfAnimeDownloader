import json
import ssl
import m3u8
import requests
import websocket
from contextlib import closing
from functools import reduce
from typing import TypedDict, List, Tuple
from bs4 import BeautifulSoup

# 2023/10/19 最後更新

# 偽裝瀏覽器
headers = {
    'origin': 'https://v.myself-bbs.com',
    'referer': 'https://v.myself-bbs.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
}


class WeekAnimateItemDict(TypedDict):
    name: str
    url: str
    update_color: str
    color: str
    update: str


class WeekAnimateDict(TypedDict):
    Monday: List[WeekAnimateItemDict]
    Tuesday: List[WeekAnimateItemDict]
    Wednesday: List[WeekAnimateItemDict]
    Thursday: List[WeekAnimateItemDict]
    Friday: List[WeekAnimateItemDict]
    Saturday: List[WeekAnimateItemDict]
    Sunday: List[WeekAnimateItemDict]


class BaseNameUrlTypedDict(TypedDict):
    name: str
    url: str


class AnimateInfoVideoDataDict(BaseNameUrlTypedDict):
    pass


class AnimateInfoTableDict(TypedDict):
    animate_type: str
    premiere_date: str
    episode: str
    author: str
    official_website: str
    synopsis: str
    image: str


class AnimateTotalInfoTableDict(BaseNameUrlTypedDict):
    video: List[AnimateInfoVideoDataDict]


class FinishAnimatePageDataDict(BaseNameUrlTypedDict):
    image: str


class FinishListDataDict(TypedDict):
    title: str
    data: List[BaseNameUrlTypedDict]


class FinishListDict(TypedDict):
    data: List[FinishListDataDict]


# websocket 設定
ws_opt = {
    'header': headers,
    'url': "wss://v.myself-bbs.com/ws",
    'host': 'v.myself-bbs.com',
    'origin': 'https://v.myself-bbs.com',
}

# 星期一 ~ 星期日
week = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday',
}

# 動漫資訊的 Key 對照表
animate_table = {
    '作品類型': 'animate_type',
    '首播日期': 'premiere_date',
    '播出集數': 'episode',
    '原著作者': 'author',
    '官方網站': 'official_website',
    '備注': 'remarks',
}


def bad_name(name: str) -> str:
    """
    避免不正當名字出現導致資料夾或檔案無法創建。

    :param name: 名字。
    :return: '白色相簿2'
    """
    ban = r'\/:*?"<>|'
    return reduce(lambda x, y: x + y if y not in ban else x + ' ', name).strip()


class Myself:
    @staticmethod
    def _req(url: str, timeout: tuple = (5, 5)) -> requests:
        try:
            return requests.get(url=url, headers=headers, timeout=timeout)
        except requests.exceptions.RequestException as error:
            raise ValueError(f'請求有錯誤: {error}')

    @classmethod
    def week_animate(cls) -> WeekAnimateDict:
        """
        爬首頁的每週更新表。

        :return: dict。
        {
            'Monday': [{
                'name': 動漫名字,
                'url': 動漫網址,
                'update_color: 網頁上面"更新"的字體顏色'
                'color': 字體顏色,
                'update': 更新級數文字,
            }, ...],
            'Tuesday': [{...}],
            ...
        }
        """
        res = cls._req(url='https://myself-bbs.com/portal.php')
        data = {}
        if res and res.ok:
            html = BeautifulSoup(res.text, features='lxml')
            elements = html.find('div', id='tabSuCvYn')
            for index, elements in enumerate(elements.find_all('div', class_='module cl xl xl1')):
                animates = []
                for element in elements:
                    animates.append({
                        'name': element.find('a')['title'],
                        'url': f"https://myself-bbs.com/{element.find('a')['href']}",
                        'update_color': element.find('span').find('font').find('font')['style'],
                        'update': element.find('span').find('font').text,
                    })

                data.update({
                    week[index]: animates
                })

        return data

    @staticmethod
    def animate_info_video_data(html: BeautifulSoup) -> List[AnimateInfoVideoDataDict]:
        """
        取得動漫網頁的影片 Api Url。

        :param html: BeautifulSoup 解析的網頁。
        :return: [{name: 第幾集名稱, url: 網址}]
        """
        data = []
        for main_list in html.select('ul.main_list'):
            for a in main_list.find_all('a', href='javascript:;'):
                name = a.text
                for display in a.parent.select('ul.display_none li'):
                    if display.select_one('a').text == '站內':
                        a = display.select_one("a[data-href*='v.myself-bbs.com']")
                        video_url = a['data-href'].replace(
                            'player/play',
                            'vpx',
                        ).replace(
                            '\r',
                            '',
                        ).replace('\n', '')
                        data.append({
                            'name': bad_name(name=name),
                            'url': video_url,
                        })

        return data

    @staticmethod
    def animate_info_table(html: BeautifulSoup) -> AnimateInfoTableDict:
        """
        取得動漫資訊。

        :return: {
            animate_type: 作品類型,
            premiere_date: 首播日期,
            episode: 播出集數,
            author: 原著作者,
            official_website: 官方網站,
            remarks: 備注,
            synopsis: 簡介,
            image: 圖片網址,
        }
        """
        data = {}
        for elements in html.find_all('div', class_='info_info'):
            for element in elements.find_all('li'):
                text = element.text
                key, value = text.split(': ')
                data.update({animate_table[key]: value})

            for element in elements.find_all('p'):
                data.update({'synopsis': element.text})

        for elements in html.find_all('div', class_='info_img_box fl'):
            for element in elements.find_all('img'):
                data.update({'image': element['src']})

        return data

    @classmethod
    def animate_total_info(cls, url: str) -> AnimateTotalInfoTableDict:
        """
        取得動漫頁面全部資訊。

        :param url: str -> 要爬的網址。
        :return: dict -> 動漫資料。
        {
            url: 網址,
            video: [{name: 第幾集名稱, url: 網址}]
            name: 名字,
            animate_type: 作品類型,
            premiere_date: 首播日期,
            episode: 播出集數,
            author: 原著作者,
            official_website: 官方網站,
            remarks: 備注,
            synopsis: 簡介,
            image: 圖片網址,
        }
        """
        res = cls._req(url=url)
        data = {}
        if res and res.ok:
            html = BeautifulSoup(res.text, features='lxml')
            data.update(cls.animate_info_table(html=html))
            data.update({
                'url': url,
                'name': bad_name(html.find('title').text.split('【')[0]),
                'video': cls.animate_info_video_data(html=html)
            })

        return data

    @classmethod
    def finish_list(cls) -> List[FinishListDict]:
        """
        取得完結列表頁面的動漫資訊。

        :return: [{
            'data': [
                {'title': '2013年10月（秋）','data': [{'name': '白色相簿2', 'url': '動漫網址'}, {...}]},
                {'title': '2013年07月（夏）', 'data': [{...}]}.
                {...},
            ]
        }]
        """
        res = cls._req(url='https://myself-bbs.com/portal.php?mod=topic&topicid=8')
        data = []
        if res and res.ok:
            html = BeautifulSoup(res.text, features='lxml')
            for elements in html.find_all('div', {'class': 'tab-title title column cl'}):
                year_list = []
                for element in elements.find_all('div', {'class': 'block move-span'}):
                    year_month_title = element.find('span', {'class': 'titletext'}).text
                    season_list = []
                    for k in element.find_all('a'):
                        season_list.append({'name': k['title'], 'url': f"https://myself-bbs.com/{k['href']}"})

                    year_list.append({'title': year_month_title, 'data': season_list})

                data.append({'data': year_list})

        return data

    @classmethod
    def finish_animate_page_data(cls, url: str) -> list[FinishAnimatePageDataDict]:
        """
        完結動漫頁面的動漫資料。

        :param url: 要爬的網址。
        :return: [{'url': 'https://myself-bbs.com/thread-43773-1-1.html', 'name': '白色相簿2'}, {...}]。
        """
        res = cls._req(url=url)
        data = []
        if res and res.ok:
            html = BeautifulSoup(res.text, 'lxml')
            for elements in html.find_all('div', class_='c cl'):
                data.append({
                    'url': f"https://myself-bbs.com/{elements.find('a')['href']}",
                    'name': bad_name(elements.find('a')['title']),
                    'image': f"https://myself-bbs.com/{elements.find('a').find('img')['src']}"
                })

        return data

    @classmethod
    def get_m3u8_text(cls, url: str, timeout: tuple = (10, 10)) -> str:
        """
        :param url: m3u8 的 Api Url。
        :param timeout: 請求與讀取時間。
        :return: 官網回應 m3u8 格式。
        """
        res = cls._req(url=url, timeout=timeout)
        if res and res.ok:
            return res.text
        raise ValueError('掛了')

    @classmethod
    def get_content(cls, url: str, timeout: tuple = (30, 30)) -> bytes:
        """
        :param url: 影片或圖片的 Url。
        :param timeout: 請求與讀取時間。
        :return: 影片或圖片的格式。
        """
        res = cls._req(url=url, timeout=timeout)
        if res and res.ok:
            return res.content
        raise ValueError('掛了')

    @classmethod
    def ws_get_host_and_m3u8_url(
            cls,
            tid: str,
            vid: str,
            video_id: str,
    ) -> Tuple[str, str]:
        """
        Websocket 取得 Host 和 M3U8 資料。

        :param tid:
        :param vid:
        :param video_id:
        :return: Host, M3U8 的 URL。
        """
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
            print(f'ssl 憑證有問題: ws_opt: {ws_opt}')

            if 'sslopt' in ws_opt:
                raise ValueError('不知道發生什麼錯誤了!')

            # 有些人電腦會有 SSL 問題，加入 sslopt 設定並重新請求一次。
            ws_opt['sslopt'] = {'cert_reqs': ssl.CERT_NONE}
            return cls.ws_get_host_and_m3u8_url(
                tid=tid,
                vid=vid,
                video_id=video_id,
            )
        except Exception as e:
            raise ValueError(f'websocket 其餘未捕抓問題: {e}')

    @classmethod
    def download_animate_simple_example(cls):
        """
        這是一個下載動漫簡單範例，有機率會發生請求錯誤，請自己修改邏輯判斷。

        :return:
        """
        # 取得白色相簿2的基本資訊。
        animate_info = cls.animate_total_info(url='https://myself-bbs.com/thread-43773-1-1.html')

        # 我要下載第一集，所以先拿出第一集的資料。
        episode1_info = animate_info['video'][0]

        # 拆解 url 資料
        temp = episode1_info['url'].split('/')

        # 將需要的資料拆解，url 拆解有兩種模式。
        if temp[-1].isdigit():
            tid, vid, video_id = temp[-2], temp[-1], ''
        else:
            tid, vid, video_id = '', '', temp[-1]

        # 取得影片 url 與 m3u8 url 的資料。
        video_url, m3u8_url = cls.ws_get_host_and_m3u8_url(
            tid=tid,
            vid=vid,
            video_id=video_id,
        )

        # 取得 m3u8 資料
        m3u8_data = cls.get_m3u8_text(url=m3u8_url)

        # 使用 m3u8 套件讀取 m3u8 資料。
        m3u8_obj = m3u8.loads(m3u8_data)

        # 抓出 m3u8 的所有 url。
        for m3u8_data in m3u8_obj.segments:
            # 組成 ts 完整的 url 。
            ts_url = f'{video_url}/{m3u8_data.uri}'
            #
            # # 開始下載(這裡我就不使用 thread 下載了。)
            video_content = cls.get_content(url=ts_url)
            with open(m3u8_data.uri, 'wb') as f:
                f.write(video_content)

        # 下載完自己合併所有 ts 檔案。


if __name__ == '__main__':
    # 完結動畫第一頁。
    # Myself.finish_animate_page_data(url='https://myself-bbs.com/forum-113-1.html')

    # 每週更新表
    # print(Myself.week_animate())

    # 完結列表動漫資訊
    # Myself.finish_list()

    # 下載影片範例
    Myself.download_animate_simple_example()
