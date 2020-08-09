# Myself_Anime
## 瀏覽

![image](https://i.imgur.com/XStl1vg.gif)

## 運行
安裝 requirements.txt <br>
`
pip install -r -requirements.text
執行 main.py 即可
`

## 問題<br>
網頁上的 source 碼 與 requests.get後的結果。<br>
![image](https://i.imgur.com/9kG6vdj.png)
```python
import requests  
  
url = 'https://myself-bbs.com/forum.php?mod=viewthread&tid=43773&highlight=%E7%99%BD%E8%89%B2%E7%9B%B8%E7%B0%BF'  
headers = {  
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}  
res = requests.get(url=url, headers=headers)  
print(res.text)
```
發現沒辦法取得到圖上紅框的 url。<br>
但我發現每個 url 都是有規則的!，所以當下覺得抓不到也沒關係自己寫規則出來即可。<br>
```
第 01 話  https://v.myself-bbs.com/player/play/43773/001
第 02 話  https://v.myself-bbs.com/player/play/43773/002
第 03 話  https://v.myself-bbs.com/player/play/43773/003
以此類推...
```
正常的 url 都向上面 第一話001 第二話002 第三話003 ，但是發現有不按照規矩的 URL。<br>
![image](https://i.imgur.com/88FrgLG.png)
有些動漫有OVA、OAD以及有些動漫並沒有按照第1話001、第二話002的規矩。<br>
結論是一定得爬網頁上的 URL ! <br>
接著我用 Firefox 觀察網址碼<br><br>
點擊前
![image](https://i.imgur.com/qYxUiRs.png)

點擊後
![image](https://i.imgur.com/XSy5D2z.png)
發現網站是執行 javascript 後才能看到URL。<br>
我在Network 沒發現 json 檔的請求網址。<br>
之後用搜尋的方式，只有在原始網能找到<br><br>
![image](https://i.imgur.com/w8YZk3x.png)

## 解決問題
為了這個問題花了一整天時間在找答案。<br>
看了很多篇文章最多人回應的是此篇。<br>
參考網址: https://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python <br>
第一個參考答案。<br>
使用 dryscrape套件，但是並沒有支援Windows，所以就沒去實作。
```python
import dryscrape
```
第二個參考答案。<br>
使用 requests_html套件，此套件網路上說限制給 Python3.6，於是我安裝了 Python3.6 並嘗試使用這個套件去抓URL，結果依然無法抓到指定的URL。<br>
```python
from requests_html import HTMLSession
from bs4 import BeautifulSoup

session = HTMLSession()
r = session.get(a_page_url)
r.html.render()
html = BeautifulSoup(res, features='lxml')
print(html)
```
最後我選擇使用 Selenium 套件，此套件是我最初最後的選擇，因為使用者對應自己的瀏覽器下載驅動。<br>
Firefox，其下載地址是：https://github.com/mozilla/geckodriver/releases <br>
chrome，其下載地址是：https://chromedriver.chromium.org/downloads <br>
當我將 Selenium 與我的程式碼串接後，我發現了可以用 PyQt 內的瀏覽器，幫我取得網頁碼!<br>
參考網址: 
1. https://stackoverflow.com/questions/37754138/how-to-render-html-with-pyqt5s-qwebengineview <br>
2. https://stackoverflow.com/questions/57813303/how-to-get-html-of-a-page-loaded-in-qwebengineview <br>
最終我捨棄了 Selenium 套件，並將兩個網址的程式碼套到我的程式裡面，並可選擇要使用哪個方法! <br>
