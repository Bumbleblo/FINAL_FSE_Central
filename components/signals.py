from PySide6 import QtCore

class Communicate(QtCore.QObject):
    temperatureSig = QtCore.Signal(str, int)
    humiditySig = QtCore.Signal(str, int)
    createSig = QtCore.Signal(str, int)
    monitorSig = QtCore.Signal(str, str, bool)
    registerSig = QtCore.Signal(str, str)
    removeSig = QtCore.Signal(str)
    removeMonitorSig = QtCore.Signal(str)
    activationSig = QtCore.Signal(str, bool)

communicate = Communicate()
