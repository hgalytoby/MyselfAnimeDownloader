# MyselfAnimeDownloader 版本ver 1.1.11

# 最後幾次更新了，希望大家動動小手手幫我右上角按星星，謝謝。

# 結束營運後不再更新此 Repo。
![image](https://user-images.githubusercontent.com/50397689/199484552-34664ef5-14c2-4b3b-928e-eeccf22c53b3.png)

## 預覽
圖(最後更新 2021/03/15)。<br><br>
![image](https://i.imgur.com/rXhfd67.gif)<br>
GitHub 支援 Gif 只到5MB，所以錄影時有暫停等待爬資料的時間，實際速度請別跟圖片相比。

圖(最後更新 2022/08/27)。<br><br>
增加搜尋動漫功能
![image](https://i.imgur.com/1yuc05s.gif)<br>


## 更新日誌(2022/11/18)
[查看更新日誌](https://github.com/hgalytoby/MyselfAnimeDownloader/blob/master/UpdateLog.md)	


## 下載檔案運行(對於不熟悉 Python 的使用者)
Windows、Mac、Linux 使用者可以[點擊下載Zip](https://github.com/hgalytoby/MyselfAnimeDownloader/releases)。<br><br>
Mac 使用者解壓縮後，請將 MyselfAnime.app 放到應用程式的資料夾。<br>
<br>
![image](https://i.imgur.com/0hPR31d.png)
<br><br>
一定要放到這裡！不然會無法開啟程式唷！

Mac 第一次開啟會有點慢請耐心稍等，如果程式都沒出現請告知。
<br>


## 運行
安裝 requirements.txt (就是安裝此程式依賴的套件)<br>

`pip install -r requirements.txt`<br>

執行 `main.py` <br>


## 注意事項
- 發生 Failed to execute script main 問題，參考 https://github.com/hgalytoby/MyselfAnimeDownloader/issues/25

![image](https://user-images.githubusercontent.com/112224504/187010076-5ae0f4f5-98c5-4ae4-af8b-26a2c0c0e28c.png)<br>

- 如果下載動漫都卡在 0 %，可能是防毒軟體擋住了，參考 https://github.com/hgalytoby/MyselfAnimeDownloader/issues/14
- 如果有動漫正在下載時，在設定介面更新下載速度，更新前正在下載動漫的速度還會是舊的下載速度，請重開程式。


## 作者想說的話
- 1.此專案依賴 [Myself 動漫網](https://myself-bbs.com/portal.php)，如果網站關閉此程式就無法使用!
- 2.此專案並不是非常`完善`難免會有`Bug`，如果有 `Bug` 或者 `程式打不開 `以及 `其他問題` 等等...，麻煩請告知我!我會盡快研究並且嘗試修復! (提出問題方法 -> 頁面左上方 -> Issues -> New issue)
- 3.2021/09/25 我發現長久以來下載影片會有卡住的問題，以前我以為修好了，結果並沒有修好，怎麼使用下載器下載影片的人都沒有這問題 = =?
- 4.此專案我從 2020 年 08 月時開始寫的，當時的我很菜沒經驗也沒工作，於是想到什麼功能就補什麼功能，程式語法也沒統一，所以現在只要不是太難的功能，只要我能做到的我都會更新。
- 5.如果您喜歡此專案，請幫我在頁面右上角按星星，謝謝您!

## 我整理出 Myself 網的方法
- [在 Share 資料夾下的 myself.py 可以點此連結過去](https://github.com/hgalytoby/MyselfAnimeDownloader/tree/master/Share)
- 我覺得我的程式寫得難看又不好修改，畢竟主要目的是下載動漫，所以會寫程式的可以參考我整理出來的方法，自己製作下載動漫的程式。

## 作者開發環境
- 作業系統
	- Windows(主要)
	- Mac 與 Linux
		- 版型會跑掉
			- Mac
				- QTabWidget tabBar 會在中間，所以版型會跑掉。
			- Linux
				-  不支援透明色，所以會有點難看。
- Python 3.7以上
	- 我是 3.7 開發的，3.6 應該也可以?，3.6 以下就不行了，因為我用 `f''` 這個功能在 3.6 以後才有。

