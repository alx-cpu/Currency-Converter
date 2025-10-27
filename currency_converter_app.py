import xml.etree.ElementTree as ET
import urllib.request
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.start_convert = CurrencyChange()
        self.currencies_list = self.read_json()
        self.setWindowTitle("Currency Converter")
        self.setWindowIcon(QIcon("resoursces/app_icon.png"))
        self.setGeometry(100, 100, 400, 100)
        self.setStyleSheet("background-color: #2B2B2B;")
        self.UiComponents()
        self.show()


    def UiComponents(self):
        """create app interface"""
        #input labels
        self.convert_value_input = QLineEdit(self)
        self.convert_value_input.setFixedHeight(34)
        self.convert_value_input.setStyleSheet("background-color: #262626; color: white; border: 1px solid #171717; border-radius:8px;")
        self.convert_value_input.textEdited.connect(self.on_text_edited)
        self.convert_value_input.setAlignment(Qt.AlignCenter)


        self.combobox_input = QComboBox()
        self.combobox_input.addItems(self.currencies_list)
        self.combobox_input.setEditable(True)
        self.combobox_input.setFixedSize(70, 35)
        self.combobox_input.setStyleSheet("background-color: #262626; color: white; border: 1px solid #171717; border-radius:8px; ")

        self.button = QPushButton("\u21C4")
        self.button.setStyleSheet("color: white;border: 0px;font-size: 35px;")
        self.button.clicked.connect(self.swap_currencies_and_values)

        self.button_convert = QPushButton("Convert")
        self.button_convert.setFixedSize(70, 35)
        self.button_convert.setStyleSheet("background-color: #262626; color: white; border: 1px solid #171717;border-radius:8px;")
        self.button_convert.clicked.connect(self.convert)

        # output labels
        self.convert_value_output = QLineEdit(self)
        self.convert_value_output.setFixedHeight(34)
        self.convert_value_output.setStyleSheet("background-color: #262626; color: white; border: 1px solid #171717; border-radius:8px;")
        self.convert_value_output.setAlignment(Qt.AlignCenter)
        self.convert_value_output.setReadOnly(True)

        self.combobox_output = QComboBox()
        self.combobox_output.addItems(self.currencies_list)
        self.combobox_output.setEditable(True)
        self.combobox_output.setFixedSize(70, 35)
        self.combobox_output.setStyleSheet("background-color: #262626; color: white; border: 1px solid #171717; border-radius:8px;")

        #organize in a horizontal box
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.addWidget(self.convert_value_input)
        self.mainLayout.addWidget(self.combobox_input)
        self.mainLayout.addWidget(self.button)
        self.mainLayout.addWidget(self.convert_value_output)
        self.mainLayout.addWidget(self.combobox_output)
        self.mainLayout.addWidget(self.button_convert)

        #add in widget
        widget = QWidget()
        widget.setLayout(self.mainLayout)
        self.setCentralWidget(widget)


    def read_json(self):
      """read currencies_names.json file to get the list of currencies available"""
      path_file = os.path.abspath(os.getcwd())
      path_file = path_file+"\ini\currencies_names.json"
      if os.path.exists(path_file):
        with open(path_file,'r') as f:
          json_text = json.load(f)
          currencies_list = json_text["currencies"]
      else:
        raise Exception("Wrong path or currencies_names.json missing",path_file)
        return 0
      return currencies_list

    def convert(self):
        """ convert currency according to BNR """
        value = self.convert_value_input.text()
        currency_input = self.combobox_input.currentText()
        currency_output = self.combobox_output.currentText()
        if not value:
            self.convert_value_input.setText("Enter a valid value...")
            self.convert_value_input.setStyleSheet("color: red; border: 1px solid red;")
        else:
            value = float(value)
            self.convert_value_input.setStyleSheet("color: white; border: 1px solid white;")
            convert_value,trend = self.start_convert.today_currency(currency_input, currency_output, value)
            if convert_value:
                if trend:
                    self.convert_value_output.setText(str(convert_value) +'  \u2197')
                elif trend == 0:
                    self.convert_value_output.setText(str(convert_value) +'  \u2198')
                else:
                    self.convert_value_output.setText(convert_value)
        self.adjust_size(self.convert_value_output, padding=20, height=35)

    def swap_currencies_and_values(self):
      """swap currencies and values"""
      value_input = self.convert_value_input.text().split()[0]
      value_output = self.convert_value_output.text().split()[0]
      currency_input = self.combobox_input.currentText()
      currency_output = self.combobox_output.currentText()

      self.combobox_input.setCurrentText(currency_output)
      self.combobox_output.setCurrentText(currency_input)
      self.convert_value_input.setText(value_output)
      self.convert_value_output.setText(value_input)

    @staticmethod
    def adjust_size(label, padding, height):
      """adjust size of specific widget"""
      text_width = label.fontMetrics().boundingRect(label.text()).width()
      label.setFixedSize(text_width + padding, height)

    def on_text_edited(self):
      """adjust size while typing"""
      self.adjust_size(self.convert_value_input,padding=40,height=35)





class CurrencyChange:
    bnrxml_url_today = "https://curs.bnr.ro/nbrfxrates.xml"
    bnrxml_url_prev = "https://curs.bnr.ro/nbrfxrates10days.xml"

    def take_xml(self):
      """take xml from BNR"""
      try:
        response_today = urllib.request.urlopen(self.bnrxml_url_today)
        self.xml_data = response_today.read()

        response_prev = urllib.request.urlopen(self.bnrxml_url_prev)
        self.xml_data_prev = response_prev.read()
      except Exception as e:
        print(e)

    def currency(self,currency_input,currency_output,value):
      """convert currency according to BNR"""
      try:
        root = ET.fromstring(self.xml_data)
        self.output_value = None
        self.currency_output = None
        self.currency_input = None
        #find all Rate elements and extract attributes
        for cub_element in root.findall('.//{*}Rate'):
            if "currency" in cub_element.attrib.keys():
                if cub_element.attrib["currency"] == currency_input:
                    self.currency_input =float(cub_element.text)
                if cub_element.attrib["currency"] == currency_output:
                    self.currency_output = float(cub_element.text)
                if self.currency_output is not None and self.currency_input is not None:
                    self.rate = round(self.currency_input/self.currency_output,2)
                    self.output_value = round(value*self.rate,2)
        return self.output_value
      except Exception as e:
        print(e)

    def extract_prev_currency(self,currency_input):
      """extract last 10 days of the currency"""
      root = ET.fromstring(self.xml_data_prev)
      self.currency_values=[]
      for cub_element in root.findall('.//{*}Rate'):
        currency_name = cub_element.attrib["currency"]
        if currency_name == currency_input:
            self.value = round(float(cub_element.text), 2)
            self.currency_values.append(self.value)

    def compare_last_days(self):
      """ compare last 10 days of the currency"""
      self.currency_values.sort()
      trend = None
      if self.currency_input < max(self.currency_values):
        trend = 0
      if self.currency_input > max(self.currency_values):
        trend = 1
      return trend

    def extract_all_currencies(self):
      """extract all currencies"""
      list_all_currencies=[]
      root = ET.fromstring(self.xml_data)
      for cub_element in root.findall('.//{*}Rate'):
        currency_name = cub_element.attrib["currency"]
        list_all_currencies.append(currency_name)

      return list_all_currencies

    def create_json(self):
      """create a .json file with all currencies"""
      path_project = os.path.abspath(os.getcwd())
      data = self.extract_all_currencies()
      data = {"currencies": data}

      ini_folder = os.path.join(path_project, "ini")
      if not os.path.exists(ini_folder):
        os.makedirs(ini_folder)

      json_path = os.path.join(ini_folder, "currencies_names.json")
      json_str = json.dumps(data, indent=4)
      with open(json_path,'w') as f:
          f.write(json_str)

    def today_currency(self,currency_input,currency_output,value):
      """start convert and compare currency"""
      self.take_xml()
      output_value =self.currency(currency_input,currency_output,float(value))
      self.extract_prev_currency(currency_input)
      trend = self.compare_last_days()
      self.create_json()

      return output_value,trend


app = QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
