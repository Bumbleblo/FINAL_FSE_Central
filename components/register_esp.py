from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QGroupBox
from PySide6 import QtCore
from .signals import communicate
from .storage import mac_to_room, room_to_mac
from .csvlogger import customlogger

saved = dict()


class RegisterPanelWidget(QWidget):

    def __init__(self, name: str, esp_type: bool):
        super().__init__()

        self.mac: str = name

        self.esp_type = esp_type

        self.layout = QHBoxLayout()

        self.layout.addWidget(self.createGroup(self.mac))

        self.setLayout(self.layout)


    def createEditLayout(self, name):

        layout = QHBoxLayout()

        layout.addWidget(QLabel(name))

        edit = QLineEdit()
        layout.addWidget(edit)
        
        return layout, edit


    def createGroup(self, name):
        """
        Create Box
        """
        
        layout = QVBoxLayout()

        inlayout, self.comodo = self.createEditLayout('Comodo')
        layout.addLayout(inlayout)

        inlayout, self.output = self.createEditLayout('Nome da entrada')
        layout.addLayout(inlayout)

        if self.esp_type:

            inlayout, self.label_input = self.createEditLayout('Nome da saída')
            layout.addLayout(inlayout)


        button = QPushButton('Cadastrar')
        layout.addWidget(button)

        self.register_button = button
        self.register_button.clicked.connect(self.register_clicked)

        box = QGroupBox(name)
        box.setLayout(layout)

        return box

    def register_clicked(self):

        try:
            label_input_str = self.label_input.text()
        except:
            label_input_str = ''

        comodo_str = self.comodo.text()
        output_str = self.output.text()

        if self.register_button.text() == 'Cadastrar':

            customlogger.debug('Usuário cadastrou o dispositivo {self.mac}')

            self.register_button.setText('Remover')

            self.register_button.repaint()

            mac_to_room[self.mac] = comodo_str
            room_to_mac[comodo_str] = self.mac

            communicate.registerSig.emit(self.mac, comodo_str)
            communicate.monitorSig.emit(comodo_str, label_input_str, self.esp_type)

        elif self.register_button.text() == 'Remover':

            customlogger.info('Usuário removeu o dispositivo {self.mac}')
            communicate.removeSig.emit(self.mac)
            communicate.removeMonitorSig.emit(mac_to_room[self.mac])

class RegisterHardwareWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.slots = {}

        self.com = communicate

        self.layout = QVBoxLayout(self)

        self.elements = {}

        self.com.createSig.connect(self.addPanel)

        communicate.removeSig.connect(self.remove_register_panel)

    @QtCore.Slot(str)
    def remove_register_panel(self, mac):
        if self.elements.get(mac, None):
            widget = self.elements[mac]
            widget.hide()
            self.layout.removeWidget(widget)

            del self.elements[mac]
            del saved[mac]

            self.repaint()

    @QtCore.Slot(str, int)
    def addPanel(self, id_esp: str, esp_type: bool ):

        if saved.get(id_esp, None)  == None:
            widget = RegisterPanelWidget(id_esp, esp_type)
            self.elements[id_esp] = widget

            self.layout.addWidget(widget)

            saved[id_esp] = esp_type

            self.repaint()

            
