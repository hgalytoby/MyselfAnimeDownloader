import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

requests_RequestException = requests.exceptions.RequestException
requests_ConnectionError = requests.ConnectionError
requests_ChunkedEncodingError = requests.exceptions.ChunkedEncodingError


def badname(name):
    ban = '//:*?"<>|.'
    """
    避免不正當名字出現導致資料夾或檔案無法創建。
    """
    for i in ban:
        name = str(name).replace(i, ' ')
    return name.strip()


def get_weekly_update():
    """
    爬首頁的每周更新表。
    :return: Dict。
    """
    res = requests.get(url='https://myself-bbs.com/portal.php', headers=headers)
    html = BeautifulSoup(res.text, features='lxml')
    week_dict = dict()
    for i in html.find_all('div', id='tabSuCvYn'):
        for index, j in enumerate(i.find_all('div', class_='module cl xl xl1')):
            num = j.find_all('a') + j.find_all('span')
            color = list()
            anime_data = dict()
            for k, v in enumerate(j.find_all('font')):
                if k % 3 == 2:
                    color.append(v.attrs['style'])
            for k in range(len(num) // 2):
                anime_data.update({num[k]['title']: {'update': num[k + len(num) // 2].text, 'color': color[k],
                                                     'url': f'https://myself-bbs.com/{num[k]["href"]}'}})
            week_dict.update({index: anime_data})
    res.close()
    res, html = None, None
    del res, html
    return week_dict


def get_end_anime_list():
    """
    爬完結列表頁面的動漫資訊
    :return: Dict。
    """
    url = 'https://myself-bbs.com/portal.php?mod=topic&topicid=8'
    res = requests.get(url=url, headers=headers)
    html = BeautifulSoup(res.text, features='lxml')
    data = dict()
    for index, i in enumerate(html.find_all('div', {'class': 'tab-title title column cl'})):
        month = dict()
        for j, m in enumerate(i.find_all('div', {'class': 'block move-span'})):
            anime = dict()
            for k in m.find('span', {'class': 'titletext'}):
                year = k
            for k in m.find_all('a'):
                anime.update({k['title']: f"https://myself-bbs.com/{k['href']}"})
            month.update({year: anime})
        data.update({index: month})
    res.close()
    return data


def get_anime_data(anime_url):
    """
    爬指定動漫頁面的資料
    :param anime_url: 給網址。
    :return: Dict。
    """
    res = requests.get(url=anime_url, headers=headers)
    html = BeautifulSoup(res.text, features='lxml')
    data = {'home': anime_url}
    total = dict()
    for i in html.select('ul.main_list'):
        for j in i.find_all('a', href='javascript:;'):
            title = j.text
            for k in j.parent.select("ul.display_none li"):
                a = k.select_one("a[data-href*='v.myself-bbs.com']")
                if k.select_one("a").text == '站內':
                    url = a["data-href"].replace('player/play', 'vpx').replace("\r", "").replace("\n", "")
                    total.update({title: url})
    data.update({'total': total})
    for i in html.find_all('div', class_='info_info'):
        for j, m in enumerate(i.find_all('li')):
            data.update({j: m.text})
    for i in html.find_all('div', class_='info_introduction'):
        for j in i.find_all('p'):
            data.update({'info': j.text})
    for i in html.find_all('div', class_='info_img_box fl'):
        for j in i.find_all('img'):
            image = requests.get(url=j['src'], headers=headers).content
            data.update({'image': image})
            image = None
            del image
    for i in html.find_all('div', class_='z'):
        for j, m in enumerate(i.find_all('a')):
            if j == 4:
                data.update({'name': m.text.split('【')[0]})
    res.close()
    res, html = None, None
    del res, html
    return data


def download_request(url=None, stream=False, timeout=None):
    """
    給 QT Thread 下載動漫用的。
    :param url:
    :param stream:
    :param timeout:
    :return:
    """
    return requests.get(url=url, headers=headers, stream=stream, timeout=timeout)


def get_total_page(get_html=False):
    """
    爬完結動漫總頁數多少。
    :param get_html: True = 將 requests.text 返回。
    :return: Dict。
    """
    res = requests.get(url='https://myself-bbs.com/forum-113-1.html', headers=headers).text
    html = BeautifulSoup(res, 'lxml')
    for i in html.find_all('div', class_='pg'):
        total_page = int(i.find('span')['title'].split(' ')[1])
        if get_html:
            return {'total_page': total_page, 'html': res}
        return {'total_page': total_page}


def download_end_anime_preview(img_url):
    """
    下載圖片預覽圖用的。
    :param img_url: 給圖片URL。
    """
    return requests.get(url=img_url, headers=headers, stream=True)


def get_now_page_anime_data(page, res=None):
    """
    完結動漫頁面的動漫資料。
    :param page:要爬第幾頁。
    :param res:給完結動漫某頁的HTML，就不用requests了
    :return: Dict。
    """
    url = f'https://myself-bbs.com/forum-113-{page}.html'
    if not res:
        res = requests.get(url=url, headers=headers).text
    html = BeautifulSoup(res, 'lxml')
    data = dict()
    for i in html.find_all('div', class_='c cl'):
        anime_url = f"https://myself-bbs.com/{i.find('a')['href']}"
        anime_name = badname(i.find('a')['title'])
        anime_img = f"https://myself-bbs.com/{i.find('a').find('img')['src']}"
        anime_total_episodes = i.find('p', class_='ep_info').text
        data.update({anime_name: {'url': anime_url, 'img': anime_img, 'total': anime_total_episodes}})
    return data


def check_version(version):
    res = requests.get(url='https://github.com/hgalytoby/MyselfAnimeDownloader', headers=headers).text
    new_version = res.split('版本ver ')[1].split('<')[0]
    if new_version != version:
        return True
    return False


if __name__ == '__main__':
    pass
