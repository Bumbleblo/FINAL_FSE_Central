from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QGroupBox, QLabel
from .signals import communicate
from PySide6 import QtCore
from .storage import room_to_mac, mac_to_room
from .csvlogger import customlogger

class MonitorElement(QWidget):

    def __init__(self, name: str, input_name: str, esptype: bool):
        super().__init__()

        self.esptype = esptype
        self.name: str = name
        self.input_name: str = input_name
        self.state: bool = False

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.createBox(self.name))
        self.setLayout(self.layout)

        communicate.humiditySig.connect(self.humidity_callback)
        communicate.temperatureSig.connect(self.temperature_callback)

    def createBox(self, name):
        """
        Create Box
        """

        layout = QHBoxLayout()

        if self.esptype:
            comodo = QLabel('Temperatura:')
            self.temperature = comodo
            layout.addWidget(comodo)

            output = QLabel('Humidade:')
            self.humidity = output
            layout.addWidget(output)

            button_state: bool = "Ativado" if self.state else "Desativado"
            button = QPushButton(f'{self.input_name} ({button_state})')
            self.activation_button = button

            button.clicked.connect(self.activation_callback)
            layout.addWidget(button)

            self.register_button = button
        else:

            layout.addWidget(QLabel("ESP32 BATERIA"))

        box = QGroupBox(name)
        box.setLayout(layout)

        return box

    def activation_callback(self):

        mac = room_to_mac[self.name]
        self.state = not self.state

        communicate.activationSig.emit(mac, self.state)
        button_state: bool = "Ativado" if self.state else "Desativado"

        custom.info('Usuário mudou o estado do dispositivo {mac} para {button_state}')

        self.activation_button.setText(f'{self.input_name} ({button_state})')

    @QtCore.Slot(str, int)
    def humidity_callback(self, comodo: str, value: int):

        if self.name == comodo:

            self.humidity.setText(f"Humidity: {value}")
            self.humidity.repaint()

    @QtCore.Slot(str, int)
    def temperature_callback(self, comodo: str, value: int):

        if self.name == comodo:
            self.temperature.setText(f"Temperature: {value}")
            self.temperature.repaint()


class MonitorPanel(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()
        self.layout = layout
        self.com = communicate
        self.setLayout(layout)

        self.com.monitorSig.connect(self.createMonitorCallback)

        communicate.removeMonitorSig.connect(self.remove_element)
        self.elements = {}

    @QtCore.Slot(str)
    def remove_element(self, name):
        print("REMOVING MONITOR")

        if self.elements.get(name):

            print("REMOVING MONITOR ELEMENT")

            self.elements[name].hide()
            self.layout.removeWidget(self.elements[name])

            del self.elements[name]

            self.repaint()

    @QtCore.Slot(str, str, bool)
    def createMonitorCallback(self, string, input_name, esptype):

        if self.elements.get(string, None) == None:

            self.layout.addWidget(self.addMonitorElement(string, input_name, esptype))
            self.repaint()

    def addMonitorElement(self, element :str, input_name: str, esptype: bool):

        widget = MonitorElement(element, input_name, esptype)
        self.elements[element] = widget

        return widget
