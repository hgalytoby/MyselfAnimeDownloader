from functools import reduce

import m3u8
import requests
from bs4 import BeautifulSoup

# 偽裝瀏覽器
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36 Edg/93.0.961.52',
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


def badname(name: str) -> str:
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
            print(f'請求有錯誤: {error}')
            return None

    @classmethod
    def week_animate(cls) -> dict:
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
    def animate_info_video_data(html: BeautifulSoup) -> list:
        """
        取得動漫網頁的影片 Api Url。
        :param html: BeautifulSoup 解析的網頁。
        :return: [{name: 第幾集名稱, url: 網址}]
        """
        data = []
        for main_list in html.select('ul.main_list'):
            for a in main_list.find_all('a', href='javascript:;'):
                name = a.text
                for display in a.parent.select("ul.display_none li"):
                    if display.select_one("a").text == '站內':
                        a = display.select_one("a[data-href*='v.myself-bbs.com']")
                        video_url = a["data-href"].replace('player/play', 'vpx').replace("\r", "").replace("\n", "")
                        data.append({'name': badname(name=name), 'url': video_url})
        return data

    @staticmethod
    def animate_info_table(html: BeautifulSoup) -> dict:
        """
        取得動漫資訊
        :return: {
            animate_type: 作品類型,
            premiere_date: 首播日期,
            episode: 播出集數,
            author: 原著作者,
            official_website: 官方網站,
            remarks: 備注,
            synopsis: 簡介
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
    def animate_total_info(cls, url: str) -> dict:
        """
        取得動漫業面全部資訊。
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
            synopsis: 簡介
        }
        """
        res = cls._req(url=url)
        data = {}
        if res and res.ok:
            html = BeautifulSoup(res.text, features='lxml')
            data.update(cls.animate_info_table(html=html))
            data.update({
                'url': url,
                'name': badname(html.find('title').text.split('【')[0]),
                'video': cls.animate_info_video_data(html=html)
            })
        return data

    @classmethod
    def finish_list(cls) -> list:
        """
        取得完結列表頁面的動漫資訊
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
    def finish_animate_page_data(cls, url: str) -> list:
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
                    'name': badname(elements.find('a')['title']),
                    'image': f"https://myself-bbs.com/{elements.find('a').find('img')['src']}"
                })
        return data

    @classmethod
    def get_vpx_json(cls, url: str, timeout: tuple = (10, 10)) -> dict:
        """
        :param url: 影集的 Api Url。
        :param timeout: 請求與讀取時間。
        :return: 官網回應 json 格式。
        """
        res = cls._req(url=url, timeout=timeout)
        if res and res.ok:
            return res.json()

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

    @classmethod
    def download_animate_simple_example(cls):
        """
        這是一個下載動漫簡單範例，肯定會發生請求錯誤，請自己修改邏輯判斷。
        :return:
        """
        # 取得白色相簿2的基本資訊。
        animate_info = cls.animate_total_info(url='https://myself-bbs.com/thread-43773-1-1.html')

        # 我要下載第一集，所以先拿出第一集的資料。
        episode1_info = animate_info['video'][0]

        # 拿 vpx 資料。
        vpx_json = cls.get_vpx_json(url=episode1_info['url'])

        # 整理 host 順序，我個人猜測 weight 越高的越好。
        host = sorted(vpx_json['host'], key=lambda x: x.get('weight'), reverse=True)

        # 將 weight 最高的 host 與 720p m3u8網址拿出來，組成完整 m3u8 網址。
        m3u8_url = f"{host[0]['host']}{vpx_json['video']['720p']}"

        # 取得 m3u8 的資料。
        m3u8_data = cls.get_m3u8_text(url=m3u8_url)

        # 使用 m3u8 套件讀取 m3u8 資料。
        m3u8_obj = m3u8.loads(m3u8_data)

        # 抓出 m3u8 的所有 url。
        for m3u8_data in m3u8_obj.segments:
            # 組成 ts 完整的 url 。
            ts_url = f"{host[0]['host']}{vpx_json['video']['720p'].replace('720p.m3u8', m3u8_data.uri)}"

            # 開始下載(這裡我就不使用 thread 下載了。)
            video_content = cls.get_content(url=ts_url)
            with open(m3u8_data.uri, 'wb') as f:
                f.write(video_content)

        # 下載完自己合併所有 ts 檔案。


if __name__ == '__main__':
    Myself.download_animate_simple_example()
