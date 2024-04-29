# python 3

"""
Development of a program for visualization and analysis of spacecraft trajectory information

Modules:
sgp4         - positions and speeds of artificial earth satellites
skyfield     - satellite data conversion
requests   - connection to the server
PyQt          - App GUI

"""
import math
import os
import sys
import PyQt5.QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QFile
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.Qt import QDate
from sgp4.earth_gravity import wgs84
from sgp4.functions import jday
from sgp4.io import twoline2rv
from sgp4.model import Satrec
import requests
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import pandas as pd
import resources_rc


class GUI(PyQt5.QtWidgets.QMainWindow):
    """ Interface """

    def __init__(self):
        """ Constructor """

        super().__init__()

        # Button explore
        self.button_explore = PyQt5.QtWidgets.QPushButton('Explore', self)
        self.button_explore.setStyleSheet('QPushButton { '
                                          'font-family: Arial; font-size: 26px; font-weight: normal; '
                                          'color: #fff; background-color: blue; }')
        self.button_explore.setGeometry(150, 480, 200, 50)
        self.button_explore.clicked.connect(self.plot)
        self.button_explore.hide()

        # Button а
        self.button_a = PyQt5.QtWidgets.QPushButton('a (km)\nSemi-major axis', self)
        self.button_a.setStyleSheet('QPushButton {'
                                    'font-family: Arial; font-size: 18px; background-color: #FFF;}')
        self.button_a.setGeometry(5, 110, 316, 65)
        self.button_a.clicked.connect(lambda: self.set_graph(1))
        self.button_a.hide()

        # Button e
        self.button_e = PyQt5.QtWidgets.QPushButton('e\nEccentricity', self)
        self.button_e.setStyleSheet('QPushButton {'
                                    'font-family: Arial; font-size: 18px; background-color: #FFF;}')
        self.button_e.setGeometry(5, 179, 316, 65)
        self.button_e.clicked.connect(lambda: self.set_graph(2))
        self.button_e.hide()

        # Button i
        self.button_i = PyQt5.QtWidgets.QPushButton('i (°)\nTilting', self)
        self.button_i.setStyleSheet('QPushButton {'
                                    'font-family: Arial; font-size: 18px; background-color: #FFF;}')
        self.button_i.setGeometry(5, 248, 316, 65)
        self.button_i.clicked.connect(lambda: self.set_graph(3))
        self.button_i.hide()

        # Button Ω
        self.button_omega_up = PyQt5.QtWidgets.QPushButton('Ω (°)\nAscending node longitude', self)
        self.button_omega_up.setStyleSheet('QPushButton {'
                                           'font-family: Arial; font-size: 18px; background-color: #FFF;}')
        self.button_omega_up.setGeometry(5, 317, 316, 65)
        self.button_omega_up.clicked.connect(lambda: self.set_graph(4))
        self.button_omega_up.hide()

        # Button ω
        self.button_omega_low = PyQt5.QtWidgets.QPushButton('ω (°)\nPeriapsis argument', self)
        self.button_omega_low.setStyleSheet('QPushButton {'
                                            'font-family: Arial; font-size: 18px; background-color: #FFF;}')
        self.button_omega_low.setGeometry(5, 386, 316, 65)
        self.button_omega_low.clicked.connect(lambda: self.set_graph(5))
        self.button_omega_low.hide()

        # Button r (A)
        self.button_ra = PyQt5.QtWidgets.QPushButton('r (A) (km)\nApogee radius', self)
        self.button_ra.setStyleSheet('QPushButton {font-family: Arial; font-size: 18px; background-color: #FFF;}')
        self.button_ra.setGeometry(5, 455, 316, 65)
        self.button_ra.clicked.connect(lambda: self.set_graph(6))
        self.button_ra.hide()

        # Button r (P)
        self.button_rp = PyQt5.QtWidgets.QPushButton('r (P) (km)\nPerigee radius', self)
        self.button_rp.setStyleSheet('QPushButton {font-family: Arial; font-size: 18px; background-color: #FFF;}')
        self.button_rp.setGeometry(5, 524, 316, 65)
        self.button_rp.clicked.connect(lambda: self.set_graph(7))
        self.button_rp.hide()

        # Button Home
        self.button_home = PyQt5.QtWidgets.QPushButton('Home page', self)
        self.button_home.setStyleSheet(
            "QPushButton {font-family: Arial; font-size: 18px; color: #fff; background-color: #852525}")
        self.button_home.setGeometry(5, 593, 316, 55)
        self.button_home.clicked.connect(self.home)
        self.button_home.hide()

        # Button lang eng
        def lang_eng():
            """ Set english language"""

            self.button_explore.setText('Explore')
            self.button_a.setText('a (km)\nSemi-major axis')
            self.button_e.setText('e\nEccentricity')
            self.button_i.setText('i (°)\nTilting')
            self.button_omega_up.setText('Ω (°)\nAscending node longitude')
            self.button_omega_low.setText('ω (°)\nPeriapsis argument')
            self.button_ra.setText('r (A) (km)\nApogee radius')
            self.button_rp.setText('r (P) (km)\nPerigee radius')
            self.button_home.setText('Home page')
            self.button_params.setText('Options')
            self.button_params_apply.setText('Apply')
            self.button_params_cancel.setText('Cancel')
            self.button_params_default.setText('Default')
            self.options_label.setText('Options')
            self.canvas_label_text = [' No events found',
                                 ' Events: ']
            self.label_description.setText('The application is created to obtain data on the position '
                                           'of the spacecraft and its parameters. Enter the name, '
                                           'start date and end date in the fields below for information.')
            self.label_description.setGeometry(35, 150, 430, 100)
            self.label_title.setText('Name:')
            self.label_date_start.setText('Start date:')
            self.label_date_end.setText('End date:')
            self.label_canvas_title = [
                'Semi-major axis - a (km)',
                'Eccentricity - e',
                'Tilting - i (°)',
                'Ascending node longitude - Ω (°)',
                'Periapsis argument - ω (°)',
                'Apogee radius - r (A) (km)',
                'Perigee radius - r (P) (km)']
            self.label_a.setText(self.label_canvas_title[0])
            self.label_e.setText(self.label_canvas_title[1])
            self.label_i.setText(self.label_canvas_title[2])
            self.label_omega_up.setText(self.label_canvas_title[3])
            self.label_omega_low.setText(self.label_canvas_title[4])
            self.label_ra.setText(self.label_canvas_title[5])
            self.label_rp.setText(self.label_canvas_title[6])
            self.warning_date = 'No information was found for this period. Choose another period!'
            self.warning_name = 'Select the spaceship name frоm the list!'
            self.warning_rev = 'Correct the entered date!'
            self.warning_ops = 'Incorrect values!'
            self.label_title.setGeometry(95, 283, 150, 20)
            self.label_date_start.setGeometry(69, 343, 150, 20)
            self.label_date_end.setGeometry(74, 403, 150, 20)
            self.event_title = ['Aerodynamic disturbances, maneuvers',
                                "Aerodynamic disturbances"
                                'Maneuvers',
                                'Perturbations of the Earths gravitational field, maneuvers',
                                'Perturbations of the Earths gravitational field',
                                "Aerodynamic disturbances"
                                'Maneuvers']
            self.ant_param = ['Date:', 'Value:', 'Event:']

        self.button_lang_eng = PyQt5.QtWidgets.QPushButton('', self)
        self.button_lang_eng.setStyleSheet(
            "QPushButton {font-family: Arial; font-size: 18px; color: #fff; background-color: #852525}")
        self.button_lang_eng.setGeometry(140, 590, 96, 40)
        icon_eng = QIcon(':/files/lang_eng.jpg')
        self.button_lang_eng.setIcon(icon_eng)
        self.button_lang_eng.setIconSize(icon_eng.actualSize(QtCore.QSize(100, 40)))
        self.button_lang_eng.clicked.connect(lang_eng)
        self.button_lang_eng.hide()

        # Button lang rus
        def lang_rus():
            """ Set russian language """

            self.button_explore.setText('Поиск')
            self.button_a.setText('a (км)\nБольшая полуось')
            self.button_e.setText('e\nЭксцентриситет')
            self.button_i.setText('i (°)\nНаклонение')
            self.button_omega_up.setText('Ω (°)\nДолгота восходящего узла')
            self.button_omega_low.setText('ω (°)\nАргумент перицентра')
            self.button_ra.setText('r (А) (км)\nРадиус апогея')
            self.button_rp.setText('r (П) (км)\nРадиус перигея')
            self.button_home.setText('Назад')
            self.button_params.setText('Параметры')
            self.button_params_apply.setText('Применить')
            self.button_params_cancel.setText('Отмена')
            self.button_params_default.setText('Стандартные')
            self.options_label.setText('Параметры')
            self.canvas_label_text = [' События не найдены',
                                 ' Обнаружен сигнал: ']
            self.label_description.setText('Приложение предназначено для получения позиции '
                                           'космического аппарата и его параметров. Введите название, '
                                           'дату старта и завершения окончания в поля ниже.')
            self.label_description.setGeometry(35, 150, 450, 100)
            self.label_title.setText('Название:')
            self.label_date_start.setText('Дата старта:')
            self.label_date_end.setText('Дата завершения:')
            self.label_canvas_title = [
                'Большая полуось - a (км)',
                'Эксцентриситет - e',
                'Наклонение - i (°)',
                'Долгота восходящего узла - Ω (°)',
                'Аргумент перицентра - ω (°)',
                'Радиус апогея - r (А) (км)',
                'Радиус перигея - r (П) (км)']
            self.label_a.setText(self.label_canvas_title[0])
            self.label_e.setText(self.label_canvas_title[1])
            self.label_i.setText(self.label_canvas_title[2])
            self.label_omega_up.setText(self.label_canvas_title[3])
            self.label_omega_low.setText(self.label_canvas_title[4])
            self.label_ra.setText(self.label_canvas_title[5])
            self.label_rp.setText(self.label_canvas_title[6])
            self.warning_date = 'За этот период информации не найдено. Выберите другой период!'
            self.warning_name = 'Выберите аппарат из списка!'
            self.warning_rev = 'Неверные даты!'
            self.warning_ops = 'Неверные значения!'
            self.label_title.setGeometry(68, 283, 150, 20)
            self.label_date_start.setGeometry(49, 343, 150, 20)
            self.label_date_end.setGeometry(10, 403, 150, 20)
            self.event_title = ['Аэродиномические возмущения, манёвры',
                                'Аэродиномические возмущения',
                                'Манёвры',
                                'Возмущения гравитационного поля Земли, манёвры',
                                'Возмущения гравитационного поля Земли',
                                'Аэродиномические возмущения',
                                'Манёвры']
            self.ant_param = ['Дата:', 'Значение:', 'Событие:']

        self.button_lang_rus = PyQt5.QtWidgets.QPushButton('', self)
        self.button_lang_rus.setStyleSheet(
            "QPushButton {font-family: Arial; font-size: 18px; color: #fff; background-color: #852525}")
        self.button_lang_rus.setGeometry(270, 590, 96, 40)
        icon_rus = QIcon(':/files/lang_rus.jpg')
        self.button_lang_rus.setIcon(icon_rus)
        self.button_lang_rus.setIconSize(icon_rus.actualSize(QtCore.QSize(100, 40)))
        self.button_lang_rus.clicked.connect(lang_rus)
        self.button_lang_rus.hide()

        # Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.canvas.setGeometry(325, 5, 670, 600)
        self.current_plot = 1
        self.canvas.hide()
        self.canvas.unit = ['km', '', '°', '°', '°', 'km', 'km']
        self.pick_event = None

        # Point text
        self.canvas_label_text = [' No events found', ' Events: ']
        self.canvas_label = PyQt5.QtWidgets.QLabel('', self)
        self.canvas_label.setGeometry(325, 610, 670, 35)
        self.canvas_label.setStyleSheet('QLabel { font-family: Arial; font-size: 16px; font-weight: normal; '
                                        'color: #000; background-color: #fff;}')

        # Field title
        self.field_title = PyQt5.QtWidgets.QLineEdit(self)
        self.field_title.setStyleSheet('QLineEdit { '
                                       'font-family: Arial; font-size: 16px; font-weight: normal; '
                                       'color: #fff; background-color: black;}')
        self.field_title.setGeometry(150, 280, 300, 30)
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        file_path = os.path.join(base_path, 'satcat.csv')
        df = pd.read_csv(file_path, header=None)
        self.spaceship_list = df[0].tolist()
        completer = PyQt5.QtWidgets.QCompleter(self.spaceship_list)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(0)
        self.field_title.setCompleter(completer)
        self.field_title.textChanged.connect(self.show_completer)
        self.field_title.hide()

        # Field date start
        now = datetime.now()
        day = now.day
        month = now.month
        year = now.year
        self.field_date_start = PyQt5.QtWidgets.QDateEdit(self)
        self.field_date_start.setCalendarPopup(True)
        self.field_date_start.setStyleSheet('QDateEdit { '
                                            'font-family: Arial; font-size: 16px; font-weight: normal; '
                                            'color: #fff; background-color: black;}')
        self.field_date_start.setGeometry(150, 340, 150, 30)
        if month != 1:
            self.field_date_start.setDate(QDate(year, month - 1, day))
        else:
            self.field_date_start.setDate(QDate(year - 1, 12, day))
        self.field_date_start.hide()

        # Field date end
        self.field_date_end = PyQt5.QtWidgets.QDateEdit(self)
        self.field_date_end.setCalendarPopup(True)
        self.field_date_end.setStyleSheet('QDateEdit { '
                                          'font-family: Arial; font-size: 16px; font-weight: normal; '
                                          'color: #fff; background-color: black;}')
        self.field_date_end.setGeometry(150, 400, 150, 30)
        self.field_date_end.setDate(QDate(year, month, day))
        self.field_date_end.hide()

        # Label heading
        self.label_heading = PyQt5.QtWidgets.QLabel('Space Explorer', self)
        self.label_heading.setStyleSheet('QLabel { font-family: Arial; font-size: 42px; font-weight: bold; '
                                         'color: #fff; }')
        self.label_heading.setGeometry(0, 80, 500, 60)
        self.label_heading.setAlignment(Qt.AlignCenter)
        self.label_heading.hide()

        # Label description
        self.label_description = PyQt5.QtWidgets.QLabel('The application is created to obtain data on the position '
                                                        'of the spacecraft and its parameters. Enter the name, '
                                                        'start date and end date in the fields below for information.',
                                                        self)
        self.label_description.setStyleSheet('QLabel { font-family: Arial; font-size: 16px; font-weight: normal; '
                                             'color: #fff; }')
        self.label_description.setGeometry(35, 150, 430, 100)
        self.label_description.setAlignment(Qt.AlignCenter)
        self.label_description.setWordWrap(True)
        self.label_description.hide()

        # Label title
        self.label_title = PyQt5.QtWidgets.QLabel('Name:', self)
        self.label_title.setStyleSheet('QLabel { font-family: Arial; font-size: 16px; font-weight: normal; '
                                       'color: #fff; }')
        self.label_title.setGeometry(95, 283, 150, 20)
        self.label_title.hide()

        # Label date start
        self.label_date_start = PyQt5.QtWidgets.QLabel('Start date:', self)
        self.label_date_start.setStyleSheet('QLabel { font-family: Arial; font-size: 16px; font-weight: normal; '
                                            'color: #fff; }')
        self.label_date_start.setGeometry(69, 343, 150, 20)
        self.label_date_start.hide()

        # Label date end
        self.label_date_end = PyQt5.QtWidgets.QLabel('End date:', self)
        self.label_date_end.setStyleSheet('QLabel { '
                                          'font-family: Arial; font-size: 16px; font-weight: normal; color: #fff; }')
        self.label_date_end.setGeometry(74, 403, 150, 20)
        self.label_date_end.hide()

        # Label canvas title
        self.label_canvas_title = [
            'Semi-major axis - a (km)',
            'Eccentricity - e',
            'Tilting - i (°)',
            'Ascending node longitude - Ω (°)',
            'Periapsis argument - ω (°)',
            'Apogee radius - r (A) (km)',
            'Perigee radius - r (P) (km)']

        # Label spaceship title
        self.label_spaceship_title = PyQt5.QtWidgets.QLabel('', self)
        self.label_spaceship_title.setGeometry(5, 5, 316, 100)
        self.label_spaceship_title.setStyleSheet(
            "QLabel { font-family: Arial; font-size: 22px; font-weight: bold; color: #fff; background-color: #152A75; }"
        )
        self.label_spaceship_title.setAlignment(Qt.AlignCenter)
        self.label_spaceship_title.hide()

        # Mouse tracker
        self.setMouseTracking(True)

        # Window name
        self.setWindowTitle('Space Explorer')

        # Window size
        screen_geometry = PyQt5.QtWidgets.QDesktopWidget().screenGeometry()
        x = int((screen_geometry.width() - 1000) / 2)
        y = int((screen_geometry.height() - 650) / 2)
        self.setGeometry(x, y, 1000, 650)

        # Window Background
        self.background = PyQt5.QtWidgets.QLabel(self)
        pixmap_background = QPixmap(':/files/background.jpg')
        self.background.setPixmap(pixmap_background)
        self.setFixedSize(pixmap_background.width(), pixmap_background.height())
        self.background.setGeometry(0, 0, pixmap_background.width(), pixmap_background.height())

        # Objects
        self.points = None
        self.widget = None

        # Event titles
        self.ant_param = ['Date:', 'Value:', 'Event:']
        self.params = []
        self.default_params = [100, 0.1, 1, 1, 1, 100, 100]
        try:
            with open('prop.txt', 'r') as file:
                self.params = []
                for line in file:
                    self.params.append(float(line.strip()))
                for i in range(7):
                    a = (self.params[i] > 0)
        except:
            with open('prop.txt', 'w') as file:
                for i in range(len(self.default_params)):
                    file.write(str(self.default_params[i]) + '\n')
            with open('prop.txt', 'r') as file:
                self.params = []
                for line in file:
                    self.params.append(float(line.strip()))
        self.button_params = PyQt5.QtWidgets.QPushButton('Options', self)
        self.button_params.setStyleSheet(
            "QPushButton {font-family: Arial; font-size: 14px; color: #000; background-color: #fff}")
        self.button_params.setGeometry(370, 480, 80, 30)
        self.button_params.clicked.connect(self.options)
        self.button_params.hide()
        self.options_label = PyQt5.QtWidgets.QLabel('Options', self)
        self.options_label.setGeometry(0, 80, 500, 60)
        self.options_label.setStyleSheet(
            "QLabel { font-family: Arial; font-size: 36px; color: #fff; }"
        )
        self.options_label.setAlignment(Qt.AlignCenter)
        self.options_label.hide()

        self.label_a = PyQt5.QtWidgets.QLabel(self.label_canvas_title[0], self)
        self.label_a.setAlignment(Qt.AlignRight)
        self.label_a.setStyleSheet(
            "QLabel { font-family: Arial; font-size: 16px; color: #fff; }"
        )
        self.label_a.setGeometry(0, 180, 250, 50)
        self.label_a.hide()
        self.field_a = PyQt5.QtWidgets.QLineEdit(self)
        self.field_a.setStyleSheet('QLineEdit { '
                                   'font-family: Arial; font-size: 16px; font-weight: normal; '
                                   'color: #000; background-color: #fff;}')
        self.field_a.setGeometry(290, 177, 60, 25)
        self.field_a.hide()
        self.label_e = PyQt5.QtWidgets.QLabel(self.label_canvas_title[1], self)
        self.label_e.setAlignment(Qt.AlignRight)
        self.label_e.setStyleSheet(
            "QLabel { font-family: Arial; font-size: 16px; color: #fff; }"
        )
        self.label_e.setGeometry(0, 220, 250, 50)
        self.label_e.hide()
        self.field_e = PyQt5.QtWidgets.QLineEdit(self)
        self.field_e.setStyleSheet('QLineEdit { '
                                   'font-family: Arial; font-size: 16px; font-weight: normal; '
                                   'color: #000; background-color: #fff;}')
        self.field_e.setGeometry(290, 217, 60, 25)
        self.field_e.hide()
        self.label_i = PyQt5.QtWidgets.QLabel(self.label_canvas_title[2], self)
        self.label_i.setAlignment(Qt.AlignRight)
        self.label_i.setStyleSheet(
            "QLabel { font-family: Arial; font-size: 16px; color: #fff; }"
        )
        self.label_i.setGeometry(0, 260, 250, 50)
        self.label_i.hide()
        self.field_i = PyQt5.QtWidgets.QLineEdit(self)
        self.field_i.setStyleSheet('QLineEdit { '
                                   'font-family: Arial; font-size: 16px; font-weight: normal; '
                                   'color: #000; background-color: #fff;}')
        self.field_i.setGeometry(290, 257, 60, 25)
        self.field_i.hide()
        self.label_omega_up = PyQt5.QtWidgets.QLabel(self.label_canvas_title[3], self)
        self.label_omega_up.setAlignment(Qt.AlignRight)
        self.label_omega_up.setStyleSheet(
            "QLabel { font-family: Arial; font-size: 16px; color: #fff; }"
        )
        self.label_omega_up.setGeometry(0, 300, 250, 50)
        self.label_omega_up.hide()
        self.field_omega_up = PyQt5.QtWidgets.QLineEdit(self)
        self.field_omega_up.setStyleSheet('QLineEdit { '
                                          'font-family: Arial; font-size: 16px; font-weight: normal; '
                                          'color: #000; background-color: #fff;}')
        self.field_omega_up.setGeometry(290, 297, 60, 25)
        self.field_omega_up.hide()
        self.label_omega_low = PyQt5.QtWidgets.QLabel(self.label_canvas_title[4], self)
        self.label_omega_low.setAlignment(Qt.AlignRight)
        self.label_omega_low.setStyleSheet(
            "QLabel { font-family: Arial; font-size: 16px; color: #fff; }"
        )
        self.label_omega_low.setGeometry(0, 340, 250, 50)
        self.label_omega_low.hide()
        self.field_omega_low = PyQt5.QtWidgets.QLineEdit(self)
        self.field_omega_low.setStyleSheet('QLineEdit { '
                                           'font-family: Arial; font-size: 16px; font-weight: normal; '
                                           'color: #000; background-color: #fff;}')
        self.field_omega_low.setGeometry(290, 337, 60, 25)
        self.field_omega_low.hide()
        self.label_ra = PyQt5.QtWidgets.QLabel(self.label_canvas_title[5], self)
        self.label_ra.setAlignment(Qt.AlignRight)
        self.label_ra.setStyleSheet(
            "QLabel { font-family: Arial; font-size: 16px; color: #fff; }"
        )
        self.label_ra.setGeometry(0, 380, 250, 50)
        self.label_ra.hide()
        self.field_ra = PyQt5.QtWidgets.QLineEdit(self)
        self.field_ra.setStyleSheet('QLineEdit { '
                                    'font-family: Arial; font-size: 16px; font-weight: normal; '
                                    'color: #000; background-color: #fff;}')
        self.field_ra.setGeometry(290, 377, 60, 25)
        self.field_ra.hide()
        self.label_rp = PyQt5.QtWidgets.QLabel(self.label_canvas_title[6], self)
        self.label_rp.setAlignment(Qt.AlignRight)
        self.label_rp.setStyleSheet(
            "QLabel { font-family: Arial; font-size: 16px; color: #fff; }"
        )
        self.label_rp.setGeometry(0, 420, 250, 50)
        self.label_rp.hide()
        self.field_rp = PyQt5.QtWidgets.QLineEdit(self)
        self.field_rp.setStyleSheet('QLineEdit { '
                                    'font-family: Arial; font-size: 16px; font-weight: normal; '
                                    'color: #000; background-color: #fff;}')
        self.field_rp.setGeometry(290, 417, 60, 25)
        self.field_rp.hide()
        self.button_params_default = PyQt5.QtWidgets.QPushButton('Default', self)
        self.button_params_default.setStyleSheet(
            "QPushButton {font-family: Arial; font-size: 16px; color: #000; background-color: #fff}")
        self.button_params_default.setGeometry(87, 490, 100, 40)
        self.button_params_default.hide()

        def default_options():
            self.params = self.default_params[:]
            self.options()

        self.button_params_default.clicked.connect(default_options)
        self.button_params_apply = PyQt5.QtWidgets.QPushButton('Apply', self)
        self.button_params_apply.setStyleSheet(
            "QPushButton {font-family: Arial; font-size: 16px; color: #000; background-color: #fff}")
        self.button_params_apply.setGeometry(207, 490, 100, 40)

        def apply_options():
            try:
                new_params = []
                new_params.append(float(self.field_a.text()))
                new_params.append(float(self.field_e.text()))
                new_params.append(float(self.field_i.text()))
                new_params.append(float(self.field_omega_up.text()))
                new_params.append(float(self.field_omega_low.text()))
                new_params.append(float(self.field_ra.text()))
                new_params.append(float(self.field_rp.text()))
                self.params = new_params[:]
                with open('prop.txt', 'w') as file:
                    for i in range(len(self.params)):
                        file.write(str(self.params[i]) + '\n')
                self.home()
            except:
                GUI.warning(self, "ops")

        self.button_params_apply.clicked.connect(apply_options)
        self.button_params_apply.hide()
        self.button_params_cancel = PyQt5.QtWidgets.QPushButton('Cancel', self)
        self.button_params_cancel.setStyleSheet(
            "QPushButton {font-family: Arial; font-size: 16px; color: #000; background-color: #fff}")
        self.button_params_cancel.setGeometry(327, 490, 100, 40)
        self.button_params_cancel.clicked.connect(self.home)
        self.button_params_cancel.hide()

        # warnings
        self.warning_date = 'No information was found for this period. Choose another period!'
        self.warning_name = 'Select the spaceship name frоm the list!'
        self.warning_rev = 'Correct the entered date!'
        self.warning_ops = 'Incorrect values!'

        # Go home
        self.home()

    def home(self):
        """ Home page """

        self.label_heading.raise_()
        self.label_heading.show()
        self.label_description.raise_()
        self.label_description.show()
        self.label_title.raise_()
        self.label_title.show()
        self.label_date_start.raise_()
        self.label_date_start.show()
        self.label_date_end.raise_()
        self.label_date_end.show()
        self.field_title.raise_()
        self.field_title.show()
        self.field_date_start.raise_()
        self.field_date_start.show()
        self.field_date_end.raise_()
        self.field_date_end.show()
        self.button_explore.raise_()
        self.button_explore.show()
        self.button_lang_eng.raise_()
        self.button_lang_eng.show()
        self.button_lang_rus.raise_()
        self.button_lang_rus.show()
        self.button_params.raise_()
        self.button_params.show()

        self.label_spaceship_title.hide()
        self.button_a.hide()
        self.button_e.hide()
        self.button_i.hide()
        self.button_omega_low.hide()
        self.button_omega_up.hide()
        self.button_ra.hide()
        self.button_rp.hide()
        self.button_home.hide()
        self.canvas.hide()

        self.options_label.hide()
        self.label_a.hide()
        self.label_e.hide()
        self.label_i.hide()
        self.label_omega_up.hide()
        self.label_omega_low.hide()
        self.label_ra.hide()
        self.label_rp.hide()
        self.field_a.hide()
        self.field_e.hide()
        self.field_i.hide()
        self.field_omega_up.hide()
        self.field_omega_low.hide()
        self.field_ra.hide()
        self.field_rp.hide()
        self.button_params_default.hide()
        self.button_params_apply.hide()
        self.button_params_cancel.hide()
        self.canvas_label.hide()

    def plot(self):

        self.point_data = Compute.values(self)
        if self.point_data:
            self.draw(self.current_plot - 1)

            self.label_heading.hide()
            self.label_description.hide()
            self.label_title.hide()
            self.label_date_start.hide()
            self.label_date_end.hide()
            self.field_title.hide()
            self.field_date_start.hide()
            self.field_date_end.hide()
            self.button_explore.hide()
            self.button_lang_eng.hide()
            self.button_lang_rus.hide()

            self.label_spaceship_title.show()
            self.label_spaceship_title.raise_()
            self.button_a.show()
            self.button_a.raise_()
            self.button_e.show()
            self.button_e.raise_()
            self.button_i.show()
            self.button_i.raise_()
            self.button_omega_low.show()
            self.button_omega_low.raise_()
            self.button_omega_up.show()
            self.button_omega_up.raise_()
            self.button_ra.show()
            self.button_ra.raise_()
            self.button_rp.show()
            self.button_rp.raise_()
            self.button_home.show()
            self.button_home.raise_()
            self.canvas.show()
            self.canvas.raise_()
            self.canvas_label.show()
            self.canvas_label.raise_()

    def options(self):
        self.label_heading.hide()
        self.label_description.hide()
        self.label_title.hide()
        self.label_date_start.hide()
        self.label_date_end.hide()
        self.field_title.hide()
        self.field_date_start.hide()
        self.field_date_end.hide()
        self.button_explore.hide()
        self.button_lang_eng.hide()
        self.button_lang_rus.hide()
        self.button_params.hide()

        self.options_label.show()
        self.options_label.raise_()
        self.label_a.show()
        self.label_a.raise_()
        self.label_e.show()
        self.label_e.raise_()
        self.label_i.show()
        self.label_i.raise_()
        self.label_omega_up.show()
        self.label_omega_up.raise_()
        self.label_omega_low.show()
        self.label_omega_low.raise_()
        self.label_ra.show()
        self.label_ra.raise_()
        self.label_rp.show()
        self.label_rp.raise_()
        self.field_a.show()
        self.field_a.raise_()
        self.field_e.show()
        self.field_e.raise_()
        self.field_i.show()
        self.field_i.raise_()
        self.field_omega_up.show()
        self.field_omega_up.raise_()
        self.field_omega_low.show()
        self.field_omega_low.raise_()
        self.field_ra.show()
        self.field_ra.raise_()
        self.field_rp.show()
        self.field_rp.raise_()
        self.button_params_default.show()
        self.button_params_default.raise_()
        self.button_params_apply.show()
        self.button_params_apply.raise_()
        self.button_params_cancel.show()
        self.button_params_cancel.raise_()

        self.field_a.setText(str(self.params[0]))
        self.field_e.setText(str(self.params[1]))
        self.field_i.setText(str(self.params[2]))
        self.field_omega_up.setText(str(self.params[3]))
        self.field_omega_low.setText(str(self.params[4]))
        self.field_ra.setText(str(self.params[5]))
        self.field_rp.setText(str(self.params[6]))

    def draw(self, index, new_points=None):
        """ Draw the graph """

        def on_pick(event):
            # Получаем координаты кликнутой точки
            x = event.artist.get_xdata()[event.ind[0]]
            y = event.artist.get_ydata()[event.ind[0]]
            GUI.draw(self, index, {'x0': x, 'y0': y})

        def x_label_set(the_tuple):
            """ Generate X label"""

            list_of_dates = list(the_tuple)
            count_of_days = len(the_tuple)

            # Every day
            if count_of_days <= 5:
                return the_tuple

            # A few days
            elif 5 < count_of_days:
                if count_of_days >= 9:
                    item = 4
                else:
                    item = 3
                step = (count_of_days - 1) / item
                pos = 1
                way = []
                while len(way) < item + 1:
                    way.append(int(pos // 1))
                    pos += step

                main_dates = []
                for pos in way:
                    main_dates.append(list_of_dates[pos - 1])

                result = list(the_tuple)
                for i in range(len(result)):
                    if result[i] not in main_dates:
                        result[i] = ''
                new_result = [x if result.index(x) == i else '' for i, x in enumerate(result)]
                result = tuple(new_result)
                return result

        # Figure clear
        self.figure.clear()
        if self.pick_event:
            self.figure.canvas.mpl_disconnect(self.pick_event)

        # Add plot
        axis = self.figure.add_subplot(111)

        # Points
        data_history = self.point_data[0][index]
        data_predict = self.point_data[1][index]
        data_predict_new = data_predict[1:]
        x, y = zip(*data_history)
        x_p, y_p = zip(*data_predict_new)
        value = self.params[index]
        event_point = []
        i = 0
        while event_point == [] and i < len(y_p) - 1:
            if abs(y_p[i] - y[i + 1]) > value:
                event_point = [x[i], y[i]]
            i += 1

        # Style
        axis.plot(x, y, marker='o', linestyle='-', picker=5, color='#69c0ff', label='History')
        axis.plot(x_p, y_p, marker='o', linestyle='-', picker=5, color='#bf7fff', label='Predict')
        if event_point:
            x0 = event_point[0]
            axis.axvline(x=x0, color='#00de30', linestyle='-')
            self.canvas_label.setText(self.canvas_label_text[1] + str(x0))
            self.canvas_label.setStyleSheet('QLabel { font-family: Arial; font-size: 16px; font-weight: bold; '
                                            'color: #00871d; background-color: #fff;}')
        else:
            self.canvas_label.setText(self.canvas_label_text[0])
            self.canvas_label.setStyleSheet('QLabel { font-family: Arial; font-size: 16px; font-weight: normal; '
                                            'color: #000; background-color: #fff;}')
        axis.legend(loc='upper left', shadow=True, frameon=True)
        if new_points:
            x0 = new_points['x0']
            y0 = new_points['y0']
            y0_short = round(y0, 3)
            axis.plot(x0, y0, marker='o', color='#D40000', markersize=10)
            if event_point:
                if x0 == event_point[0] and y0 == event_point[1]:
                    axis.annotate(
                        f'{self.ant_param[0]} {x0}\n{self.ant_param[1]} {y0_short}'
                        f' {self.canvas.unit[index]}\n{self.ant_param[2]} {self.event_title[index]}',
                        (x0, y0), textcoords="offset points",
                        xytext=(0, 15), ha='center', bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=1))
                else:
                    axis.annotate(f'{self.ant_param[0]} {x0}\n{self.ant_param[1]} {y0_short} {self.canvas.unit[index]}',
                                  (x0, y0), textcoords="offset points",
                                  xytext=(0, 15), ha='center', bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=1))
            else:
                axis.annotate(f'{self.ant_param[0]} {x0}\n{self.ant_param[1]} {y0_short} {self.canvas.unit[index]}',
                              (x0, y0), textcoords="offset points",
                              xytext=(0, 15), ha='center', bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=1))
        axis.set_title(self.label_canvas_title[index])
        axis.set_xlabel('Date')
        axis.set_xticks(x_label_set(x))
        axis.set_ylabel('Value')
        axis.tick_params(axis='x', labelsize=9)
        axis.grid(True)

        # Назначаем обработчик события pick_event
        self.pick_event = self.figure.canvas.mpl_connect('pick_event', on_pick)

        # Draw
        self.canvas.draw()

    def set_graph(self, plot_num):
        """ Set graph """

        self.current_plot = plot_num
        self.draw(plot_num - 1)

    def show_completer(self, text):
        """ Autocomplete """

        self.field_title.completer().setCompletionPrefix(text)
        self.field_title.completer().complete()

    def warning(self, text):
        """ Input errors """

        msg = PyQt5.QtWidgets.QMessageBox()
        msg.setWindowTitle('Warning')
        if text == "name":
            msg.setText(self.warning_name)
        elif text == "date":
            msg.setText(self.warning_date)
        elif text == 'rev':
            msg.setText(self.warning_rev)
        elif text == 'ops':
            msg.setText(self.warning_ops)
        msg.setStandardButtons(PyQt5.QtWidgets.QMessageBox.Ok)
        msg.setIcon(PyQt5.QtWidgets.QMessageBox.Warning)
        msg.exec_()


class Server:
    """ Interaction with the server """

    def search(self, name, date_start, date_end):
        """ Get spaceship data """

        # Authorization on the server
        login_url = "https://www.space-track.org/ajaxauth/login"

        # Login credentials
        login = "dmitry.andresckul@gmail.com"
        password = "SpacetrackSpacetrack"

        # Creating the session
        session = requests.Session()

        # Authorization
        login_data = {"identity": login, "password": password}
        response = session.post(login_url, data=login_data)

        # Checking the success of authorization
        if response.status_code == 200 and "login_error" not in response.text:
            self.session = session
        else:
            return "Login error"

        # Search in the database
        if name not in self.spaceship_list:
            GUI.warning(self, "name")
            return None

        yesterday = ((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))

        # Date check
        if datetime.strptime(date_start, '%Y-%m-%d').date() > datetime.strptime(date_end, '%Y-%m-%d').date():
            return GUI.warning(self, 'rev')

        if datetime.strptime(date_start, '%Y-%m-%d').date() > datetime.now().date():
            return GUI.warning(self, 'date')

        # NORAD ID
        id_ = name.split('.')[0]
        self.label_spaceship_title.setText(name.split('.')[1])

        def url_search(date_start, date_end):
            """ URL search """

            # URL compilation
            url = ('https://www.space-track.org/basicspacedata/query/class/gp_history/NORAD_CAT_ID/'
                   + id_ + '/orderby/TLE_LINE1%20ASC/EPOCH/' + date_start + '--' + date_end + '/format/tle')

            # Check URL
            try:
                response = self.session.head(url)
                status = response.status_code == 200
            except:
                status = False

            # Get data
            if status:
                return (self.session.get(url)).text
            else:
                return GUI.warning(self, 'date')

        self.history_search = False

        if not ((date_start > yesterday) and (date_end > yesterday)):

            self.history_search = True
            return url_search(date_start, date_end)

        else:
            def scan(date):
                """ Scan latest date """

                def date_result(date, n_days):

                    # Преобразуем строку в объект datetime
                    date_obj = datetime.strptime(date, '%Y-%m-%d')

                    # Создаем объект timedelta с количеством дней для вычитания
                    delta = timedelta(days=n_days)

                    # Вычитаем из исходной даты delta
                    new_date = date_obj - delta

                    # Преобразуем новую дату в строку
                    return new_date.strftime('%Y-%m-%d')

                n = 30
                yesterday = ((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
                while True:
                    if date < yesterday:
                        return date
                    else:
                        date = date_result(date, n)
                        n += 30

            date_predict_start = scan(date_start)

            date_obj = datetime.strptime(date_predict_start, '%Y-%m-%d')
            date_predict_end = date_obj + timedelta(days=1)
            date_predict_end = date_predict_end.strftime('%Y-%m-%d')

            return url_search(date_predict_start, date_predict_end)

    def history_ask(self):

        return self.history_search


class Compute:
    """ Convert data to variables """

    def values(self):
        """ Generate values """

        def filter_(data):

            def zero(input_list):
                output_list = []
                prev_num = None
                for num in input_list:
                    if num == prev_num:
                        output_list.append('')
                    else:
                        output_list.append(num)
                    prev_num = num
                return output_list

            data_1 = []
            data_1_cut = []
            for i in range(0, len(data), 2):
                data_1.append(data[i])
            for i in range(0, len(data), 2):
                data_1_cut.append(data[i][20:23])
            data_1_cut = zero(data_1_cut)
            for i in range(len(data_1_cut)):
                if not data_1_cut[i]:
                    data_1[i] = ''

            data_2 = []
            for i in range(1, len(data), 2):
                data_2.append(data[i])

            data_collect = []
            for i in range(0, len(data) // 2):
                data_collect.append(data_1[i])
                data_collect.append(data_2[i])

            result_data = []
            i = 0
            while i in range(len(data_collect)):
                if not data_collect[i]:
                    i += 2
                else:
                    result_data.append(data_collect[i])
                    i += 1

            return (result_data)

        # Predict
        def vector_compute(line1, line2, date, param):
            """ Predict values """

            def vector_multiply(a, b):
                """ Vectors multiply """

                result = [a[1] * b[2] - a[2] * b[1],
                          a[2] * b[0] - a[0] * b[2],
                          a[0] * b[1] - a[1] * b[0]]
                return result

            satellite = Satrec.twoline2rv(line1, line2)

            (year, month, day, hour, minute, second) = (int(date[0:4]), int(date[5:7]),
                                                        int(date[8:]), 0, 0, 0)

            jd, fr = jday(year, month, day, hour, minute, second)

            # Получаем элементы орбиты спутника
            e, r, v = satellite.sgp4(jd, fr)

            # Вывод параметров орбиты
            # Гравитационный параметр Земли
            μ = 398600

            # Вычислить удельный момент импульса h:
            h = vector_multiply(r, v)

            # Вычислить вертикальную компоненту удельного момента импульса h_z:
            h_z = h[2]

            # Модули векторов
            r_mod = math.sqrt(r[0] ** 2 + r[1] ** 2 + r[2] ** 2)
            v_mod = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
            h_mod = math.sqrt(h[0] ** 2 + h[1] ** 2 + h[2] ** 2)

            # Вычислить горизонтальные компоненты удельного момента импульса h_x и h_y
            h_x = h[0]
            h_y = h[1]

            Ω = math.atan(h_z / h_x) * 180 / 3.14
            ω = math.atan(h_y / h_x) * 180 / 3.14
            a = 1 / (2 / r_mod - v_mod ** 2 / μ)
            e = math.sqrt(1 - h_mod ** 2 / (μ * a))
            i = math.acos(h_z / h_mod) * 180 / 3.14
            ra = a * (1 + e)
            rp = a * (1 - e)

            if param == 'a':
                return round(a, 10)
            if param == 'e':
                return round(e, 10)
            if param == 'i':
                return round(i, 10)
            if param == 'Ω':
                return round(Ω, 10)
            if param == 'ω':
                return round(ω, 10)
            if param == 'ra':
                return round(ra, 10)
            if param == 'rn':
                return round(rp, 10)

        # Dictionary create
        self.elements_history = {
            'a': {},
            'e': {},
            'i': {},
            'Ω': {},
            'ω': {},
            'ra': {},
            'rn': {}
        }

        self.elements_predict = {
            'a': {},
            'e': {},
            'i': {},
            'Ω': {},
            'ω': {},
            'ra': {},
            'rn': {}
        }

        self.points_history = []
        self.points_predict = []
        self.data = Server.search(
            self,
            self.field_title.text(),
            self.field_date_start.date().toString(Qt.ISODate),
            self.field_date_end.date().addDays(1).toString(Qt.ISODate)
        )
        if not self.data:
            return None

        # Slice
        self.data = self.data.replace('\r', '')
        self.data = self.data.split('\n')
        if Server.history_ask(self):
            self.data.pop()
            self.data = filter_(self.data)

        # Convert to orbital object
        if Server.history_ask(self):

            for i in range(0, len(self.data) - 1, 2):
                satellite = twoline2rv(self.data[i], self.data[i + 1], wgs84)

                # Elements
                self.elements_history['a'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[i],
                                                                                                      self.data[i + 1],
                                                                                                      Compute.extract_date(
                                                                                                          self,
                                                                                                          self.data[i]),
                                                                                                      'a')
                self.elements_predict['a'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[0],
                                                                                                      self.data[1],
                                                                                                      Compute.extract_date(
                                                                                                          self,
                                                                                                          self.data[i]),
                                                                                                      'a')
                self.elements_history['e'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[i],
                                                                                                      self.data[i + 1],
                                                                                                      Compute.extract_date(
                                                                                                          self,
                                                                                                          self.data[i]),
                                                                                                      'e')
                self.elements_predict['e'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[0],
                                                                                                      self.data[1],
                                                                                                      Compute.extract_date(
                                                                                                          self,
                                                                                                          self.data[i]),
                                                                                                      'e')
                self.elements_history['i'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[i],
                                                                                                      self.data[i + 1],
                                                                                                      Compute.extract_date(
                                                                                                          self,
                                                                                                          self.data[i]),
                                                                                                      'i')
                self.elements_predict['i'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[0],
                                                                                                      self.data[1],
                                                                                                      Compute.extract_date(
                                                                                                          self,
                                                                                                          self.data[i]),
                                                                                                      'i')
                self.elements_history['Ω'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[i],
                                                                                                      self.data[i + 1],
                                                                                                      Compute.extract_date(
                                                                                                          self,
                                                                                                          self.data[i]),
                                                                                                      'Ω')
                self.elements_predict['Ω'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[0],
                                                                                                      self.data[1],
                                                                                                      Compute.extract_date(
                                                                                                          self,
                                                                                                          self.data[i]),
                                                                                                      'Ω')
                self.elements_history['ω'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[i],
                                                                                                      self.data[i + 1],
                                                                                                      Compute.extract_date(
                                                                                                          self,
                                                                                                          self.data[i]),
                                                                                                      'ω')
                self.elements_predict['ω'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[0],
                                                                                                      self.data[1],
                                                                                                      Compute.extract_date(
                                                                                                          self,
                                                                                                          self.data[i]),
                                                                                                      'ω')
                self.elements_history['ra'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[i],
                                                                                                       self.data[i + 1],
                                                                                                       Compute.extract_date(
                                                                                                           self,
                                                                                                           self.data[
                                                                                                               i]),
                                                                                                       'ra')
                self.elements_predict['ra'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[0],
                                                                                                       self.data[1],
                                                                                                       Compute.extract_date(
                                                                                                           self,
                                                                                                           self.data[
                                                                                                               i]),
                                                                                                       'ra')
                self.elements_history['rn'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[i],
                                                                                                       self.data[i + 1],
                                                                                                       Compute.extract_date(
                                                                                                           self,
                                                                                                           self.data[
                                                                                                               i]),
                                                                                                       'rn')
                self.elements_predict['rn'][Compute.extract_date(self, self.data[i])] = vector_compute(self.data[0],
                                                                                                       self.data[1],
                                                                                                       Compute.extract_date(
                                                                                                           self,
                                                                                                           self.data[
                                                                                                               i]),
                                                                                                       'rn')

        # Points
        for key in self.elements_history:
            elements_list_1 = []
            for second_key in self.elements_history[key]:
                elements_list_1.append((second_key, self.elements_history[key][second_key]))
            self.points_history.append(elements_list_1)
        for key in self.elements_predict:
            elements_list_2 = []
            for second_key in self.elements_predict[key]:
                elements_list_2.append((second_key, self.elements_predict[key][second_key]))
            self.points_predict.append(elements_list_2)
        return self.points_history, self.points_predict

    def extract_date(self, tle_line):
        """ Date extract """

        # Year
        year = 2000 + int(tle_line[18:20])
        if int(tle_line[18:20]) > 50:
            year -= 100

        # Day
        day_of_year = int(tle_line[20:23])

        # Full date
        tle_timestamp = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
        return str(tle_timestamp)[0:10]


def run():
    """ Run code """
    if __name__ == '__main__':
        # App create
        app = PyQt5.QtWidgets.QApplication(sys.argv)

        # Window create
        window = GUI()

        # Window show
        window.show()

        # App exit
        sys.exit(app.exec_())


run()
