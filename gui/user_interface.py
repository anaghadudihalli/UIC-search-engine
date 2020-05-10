import os
import pickle
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QTextBrowser
from PyQt5.QtCore import pyqtSlot
from ir_system.aggregate_results import get_results
from gui.query_spellchecker import spell_check

global url_content_map
global url_title_map


def display_results(url):
    content = ' '.join(url_content_map[url].split(' ')[190:])
    return '<h6><b>' + url_title_map[url] + '</b></h6><a href="' + url + '">' + url + '</a><br><small><span>' + \
           content[: 450] + ' ...</span></small><br><br>'


def load_url_pickles():
    global url_content_map
    global url_title_map

    cur_dir = os.path.dirname(__file__)

    relative_path = '../pickles/url_title_map.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'rb') as handle:
        url_title_map = pickle.load(handle)

    relative_path = '../pickles/url_content_map.pickle'
    abs_file_path = os.path.join(cur_dir, relative_path)

    with open(abs_file_path, 'rb') as handle:
        url_content_map = pickle.load(handle)
    return


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 1440, 870)
        self.setWindowTitle('UIC Search')

        # Input text field for entering a user query
        self.query_input_field = QLineEdit(self)
        self.query_input_field.move(100, 240)
        self.query_input_field.resize(480, 35)

        # Button to submit the user query
        self.search_button = QPushButton('Search', self)
        self.search_button.move(270, 288)
        self.search_button.clicked.connect(self.search)

        # Label to display the auto-corrected query
        self.search_autocorrected_query = QLabel('', self)
        self.search_autocorrected_query.move(100, 350)
        self.search_autocorrected_query.resize(400, 35)
        self.search_autocorrected_query.hide()

        self.search_autocorrected_variable = QLabel('', self)
        self.search_autocorrected_variable.move(218, 350)
        self.search_autocorrected_variable.resize(400, 35)
        self.search_autocorrected_variable.hide()

        # Label to display the original query
        self.search_original_query = QPushButton('', self)
        self.search_original_query.move(90, 380)
        self.search_original_query.resize(300, 30)
        self.search_original_query.hide()
        self.search_original_query.clicked.connect(self.search_for_original)

        # UIC Logo
        self.logo = QLabel(self)
        self.logo.setPixmap(QtGui.QPixmap('uic_logo.png'))
        self.logo.move(205, 100)
        self.logo.resize(100, 100)

        # Text - Search
        self.search_label = QLabel('Search', self)
        self.search_label.move(310, 100)
        self.search_label.setStyleSheet('font-size: 45px; color: #353836')
        self.search_label.resize(400, 100)

        # Results box
        self.results_box = QTextBrowser(self)
        self.results_box.move(700, 30)
        self.results_box.resize(700, 750)
        self.results_box.hide()

        # Show more button
        self.show_more_button = QPushButton('Show more', self)
        self.show_more_button.move(990, 790)
        self.show_more_button.clicked.connect(self.show_more_results)
        self.show_more_button.hide()

        self.number_of_results_per_search = 10

    @pyqtSlot()
    def search_for_original(self):
        query = self.query_input_field.text()
        search_results = get_results(query, 300)

        self.search_original_query.hide()
        self.search_autocorrected_query.hide()
        self.search_autocorrected_variable.hide()
        self.results_box.clear()
        self.results_box.hide()
        self.results_box.show()

        self.ranked_results = []

        for url in search_results:
            self.ranked_results.append(display_results(url[0]))

        urls = ''.join(self.ranked_results[:self.number_of_results_per_search])
        self.results_box.setText(urls)
        self.results_box.setOpenExternalLinks(True)
        self.show_more_button.setText('Show more')
        self.show_more_button.show()
        self.results_box.show()

    @pyqtSlot()
    def search(self):
        is_autocorrected = False
        self.ranked_results = []
        urls = ''
        self.results_box.setText(urls)
        self.search_original_query.hide()
        self.search_autocorrected_query.hide()
        self.search_autocorrected_variable.hide()
        self.setGeometry(self.geometry())

        # Get the text from the input field
        query = self.query_input_field.text()

        # Check for spelling
        original_query, autocorrected_query = spell_check(query)
        if original_query.rstrip() == autocorrected_query.rstrip():
            search_results = get_results(original_query, 500)
        else:
            is_autocorrected = True
            search_results = get_results(autocorrected_query, 500)
            self.search_original_query.hide()
            self.search_autocorrected_query.hide()
            self.search_autocorrected_variable.hide()

        self.ranked_results = []
        self.results_box.clear()
        self.results_box.hide()
        self.results_box.show()

        for url in search_results:
            self.ranked_results.append(display_results(url[0]))

        urls = ''.join(self.ranked_results[:self.number_of_results_per_search])
        self.results_box.setText(urls)
        self.results_box.setOpenExternalLinks(True)
        self.show_more_button.setText('Show more')
        self.show_more_button.show()

        if is_autocorrected:
            text = 'Search instead for ' + '"' + original_query + '"'
            self.search_original_query.setText(text)
            self.search_original_query.show()

            updated_label = 'Showing results for '
            updated_data = '"' + autocorrected_query + '" ...'
            self.search_autocorrected_query.setText(updated_label)
            self.search_autocorrected_variable.setText(updated_data)
            self.search_autocorrected_variable.setStyleSheet("font-style:oblique; font-weight:bold; color: #03368a")
            self.search_autocorrected_query.setStyleSheet("font-style:oblique; color: #03368a")
            self.search_autocorrected_query.show()
            self.search_autocorrected_variable.show()

        self.results_box.show()

    @pyqtSlot()
    def show_more_results(self):
        self.number_of_results_per_search = self.number_of_results_per_search + 10
        self.results_box.setText(''.join(self.ranked_results[:self.number_of_results_per_search]))


def main():
    app = QApplication(sys.argv)
    search_engine = App()
    load_url_pickles()
    search_engine.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
