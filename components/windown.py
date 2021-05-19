import sys

from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton

from .register_esp import RegisterHardwareWidget
from .mqtt import MqttClient
from .constants import MQTT_TOPIC, MQTT_SERVER
from .signals import Communicate
from .monitor import MonitorPanel


class Windown(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout(self)
        self.tab_layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # add tabs

        self.com = Communicate()
        client = MqttClient(self)

        client.hostname = MQTT_SERVER
        client.connectToHost()

        client.subscribe(MQTT_TOPIC)

        tabs.addTab(RegisterHardwareWidget(), 'Register')
        tabs.addTab(MonitorPanel(), 'Monitor')

        self.layout.addWidget(tabs)

        exit_button = self.createExitButton()
        self.layout.addWidget(exit_button)

    def createExitButton(self):

        exit_button = QPushButton('Exit')
        exit_button.clicked.connect(lambda: self.close())

        return exit_button

