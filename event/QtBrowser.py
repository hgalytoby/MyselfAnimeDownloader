# def html(get_html=None, result_html=None, choose='one'):
#     """
#     兩種用法，結果都是一樣的。
#     1.
#     app = QtWidgets.QApplication(sys.argv)
#     browser = QtWebEngineWidgets.QWebEngineView()
#     browser.load(QtCore.QUrl(url))
#     browser.loadFinished.connect(on_load_finished)
#     app.exec_()
#     2.
#     r = render(url)
#     result_html.put(r)
#     """
#
#     def render(url):
#
#         class Render(QtWebEngineWidgets.QWebEngineView):
#             def __init__(self, url):
#                 self.html = None
#                 self.app = QtWidgets.QApplication(sys.argv)
#                 QtWebEngineWidgets.QWebEngineView.__init__(self)
#                 self.loadFinished.connect(self._loadFinished)
#                 self.load(QtCore.QUrl(url))
#                 while self.html is None:
#                     self.app.processEvents(
#                         QtCore.QEventLoop.ExcludeUserInputEvents | QtCore.QEventLoop.ExcludeSocketNotifiers | QtCore.QEventLoop.WaitForMoreEvents)
#                 self.app.quit()
#
#             def _callable(self, data):
#                 self.html = data
#
#             def _loadFinished(self, result):
#                 self.page().toHtml(self._callable)
#
#         return Render(url).html
#
#     def callback_function(html):
#         result_html.put(html)
#         browser.close()
#
#     def on_load_finished():
#         browser.page().runJavaScript("document.getElementsByTagName('html')[0].innerHTML", callback_function)
#
#     while True:
#         if get_html.qsize() > 0:
#             url = get_html.get()
#             if choose == 'one':
#                 r = render(url)
#                 result_html.put(r)
#             else:
#                 app = QtWidgets.QApplication(sys.argv)
#                 browser = QtWebEngineWidgets.QWebEngineView()
#                 browser.load(QtCore.QUrl(url))
#                 browser.loadFinished.connect(on_load_finished)
#                 app.exec_()
#             break
#         time.sleep(1)
