import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QTextBrowser
from PyQt5.QtCore import pyqtSlot
import aggregate_results

# from Ranker.MyRanker import get_search_result

'''
A simple UI displays user a query input and the results of the query search engine
'''


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'UIC Search Engine'
        self.left = 10
        self.top = 10
        self.width = 1280
        self.height = 720
        self.initUI()
        self.results_page = 10

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.input_text_field = QLineEdit(self)
        self.input_text_field.move(150, 400)
        self.input_text_field.resize(480, 35)

        self.button = QPushButton('Search UIC', self)
        self.button.move(315, 450)
        self.button.resize(110, 35)

        self.button.clicked.connect(self.on_click)
        self.result_view = QTextBrowser(self)
        self.result_view.move(750, 110)
        self.result_view.resize(650, 750)
        self.result_view.hide()
        self.next_n_results = QPushButton('Show more', self)
        self.next_n_results.move(1000, 50)
        self.next_n_results.resize(150, 35)
        self.next_n_results.clicked.connect(self.on_click_label)
        self.next_n_results.hide()
        # self.setStyleSheet(
        #     "background-image: url(background.jpg); background-attachment: stretch")
        self.show()

    @pyqtSlot()
    def on_click(self):
        self.results_page = 10
        query = self.input_text_field.text()
        search_result = aggregate_results.get_results(query, 500)
        display_html = ''
        self.url_list = []

        urls = ''.join(self.url_list[:self.results_page])
        self.result_view.setText(urls)
        self.result_view.setOpenExternalLinks(True)
        self.next_n_results.setText('Show more')
        self.next_n_results.show()

        self.setStyleSheet("")

        self.result_view.show()

    def add_href(self, url, score):
        return '<a href="' + url + '">' + url + '</a><br><br>'

    @pyqtSlot()
    def on_click_label(self):
        self.results_page = self.results_page + 10
        self.result_view.setText(''.join(self.url_list[:self.results_page]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
