import paho.mqtt.client as mqtt
import logging
import simplejson
from os.path import join

from dataclasses import dataclass
from PySide6 import QtCore, QtWidgets
from .constants import MQTT_SERVER, PORT, MQTT_TOPIC_PREFIX
from .signals import communicate

logger = logging.getLogger(__name__)

@dataclass
class TopicMessage:
    device: str
    room_name: str
    info: str

class MqttClient(QtCore.QObject):
    Disconnected = 0
    Connecting = 1
    Connected = 2

    MQTT_3_1 = mqtt.MQTTv31
    MQTT_3_1_1 = mqtt.MQTTv311

    connected = QtCore.Signal()
    disconnected = QtCore.Signal()

    stateChanged = QtCore.Signal(int)
    hostnameChanged = QtCore.Signal(str)
    portChanged = QtCore.Signal(int)
    keepAliveChanged = QtCore.Signal(int)
    cleanSessionChanged = QtCore.Signal(bool)
    protocolVersionChanged = QtCore.Signal(int)

    messageSignal = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(MqttClient, self).__init__(parent)

        self.com = communicate

        self.m_hostname = MQTT_SERVER
        self.m_port = PORT
        self.m_keepAlive = 60
        self.m_cleanSession = True
        self.m_protocolVersion = MqttClient.MQTT_3_1

        self.m_state = MqttClient.Disconnected
        self.m_client =  mqtt.Client(clean_session=self.m_cleanSession,
            protocol=self.protocolVersion)

        self.m_client.on_connect = self.on_connect
        self.m_client.on_message = self.on_message
        self.m_client.on_disconnect = self.on_disconnect

        communicate.registerSig.connect(self.response_ESP32)
        communicate.removeSig.connect(self.remove_device)
        communicate.activationSig.connect(self.activation_device)


    @QtCore.Property(int, notify=stateChanged)
    def state(self):
        return self.m_state

    @state.setter
    def state(self, state):
        if self.m_state == state: return
        self.m_state = state
        self.stateChanged.emit(state) 

    @QtCore.Property(str, notify=hostnameChanged)
    def hostname(self):
        return self.m_hostname

    @hostname.setter
    def hostname(self, hostname):
        if self.m_hostname == hostname: return
        self.m_hostname = hostname
        self.hostnameChanged.emit(hostname)

    @QtCore.Property(int, notify=portChanged)
    def port(self):
        return self.m_port

    @port.setter
    def port(self, port):
        if self.m_port == port: return
        self.m_port = port
        self.portChanged.emit(port)

    @QtCore.Property(int, notify=keepAliveChanged)
    def keepAlive(self):
        return self.m_keepAlive

    @keepAlive.setter
    def keepAlive(self, keepAlive):
        if self.m_keepAlive == keepAlive: return
        self.m_keepAlive = keepAlive
        self.keepAliveChanged.emit(keepAlive)

    @QtCore.Property(bool, notify=cleanSessionChanged)
    def cleanSession(self):
        return self.m_cleanSession

    @cleanSession.setter
    def cleanSession(self, cleanSession):
        if self.m_cleanSession == cleanSession: return
        self.m_cleanSession = cleanSession
        self.cleanSessionChanged.emit(cleanSession)

    @QtCore.Property(int, notify=protocolVersionChanged)
    def protocolVersion(self):
        return self.m_protocolVersion

    @protocolVersion.setter
    def protocolVersion(self, protocolVersion):
        if self.m_protocolVersion == protocolVersion: return
        if protocolVersion in (MqttClient.MQTT_3_1, MQTT_3_1_1):
            self.m_protocolVersion = protocolVersion
            self.protocolVersionChanged.emit(protocolVersion)

    #################################################################
    @QtCore.Slot()
    def connectToHost(self):
        if self.m_hostname:
            self.m_client.connect(self.m_hostname, 
                port=self.port, 
                keepalive=self.keepAlive)

            self.state = MqttClient.Connecting
            self.m_client.loop_start()

    @QtCore.Slot()
    def disconnectFromHost(self):
        self.m_client.disconnect()

    def subscribe(self, path):
        #if self.state == MqttClient.Connected:
        self.m_client.subscribe(path)

    def unsubscribe(self, path):
        self.m_client.unsubscribe(path)

    def publish(self, topic, data):

        self.m_client.publish(topic, data)

    #################################################################
    # callbacks
    def on_message(self, mqttc, obj, msg):

        print(msg.topic)

        _, *message = msg.topic.split('/')

        try:
            topic_message = TopicMessage(message[0], message[1], message[2])
        except:
            topic_message = TopicMessage(message[0], '', '')

        json_data = simplejson.loads(msg.payload.decode('ascii'))
        logger.debug(json_data)

        if 'init' in json_data:
            logger.debug('Create a device')
            type_data = int(json_data['init'])

            self.com.createSig.emit(message[-1], type_data)

        if 'humidity' in json_data:

            logger.debug('Sending umidity message')
            communicate.humiditySig.emit(message[-2], int(json_data['humidity']))

        if  'temperature' in json_data:

            logger.debug('Sending temperature message')
            communicate.temperatureSig.emit(message[-2], int(json_data['temperature']))

        mstr = msg.payload.decode("ascii")
        # print("on_message", mstr, obj, mqttc)
        self.messageSignal.emit(mstr)

    @QtCore.Slot(str, str)
    def response_ESP32(self, mac: str, comodo: str):

        logger.info(f"Sending message to {mac}")
        
        topic = join(MQTT_TOPIC_PREFIX, 'dispositivos', mac)
        message = simplejson.dumps({'room': comodo})

        logger.debug((topic, message))
        self.publish(
            topic,
            message
        )

        self.subscribe(join(MQTT_TOPIC_PREFIX, comodo, 'temperatura'))
        self.subscribe(join(MQTT_TOPIC_PREFIX, comodo, 'umidade'))
        self.subscribe(join(MQTT_TOPIC_PREFIX, comodo, 'estado'))

    @QtCore.Slot(str)
    def remove_device(self, room: str):

        logger.info(f'Removendo dispositivo: {room}')
        
        topic = join(MQTT_TOPIC_PREFIX, 'dispositivos', room)
        message = simplejson.dumps({'output': 2})

        self.publish(
            topic,
            message,
        )

        self.unsubscribe(join(MQTT_TOPIC_PREFIX, room, 'temperatura'))
        self.unsubscribe(join(MQTT_TOPIC_PREFIX, room, 'umidade'))
        self.unsubscribe(join(MQTT_TOPIC_PREFIX, room, 'estado'))

    
    @QtCore.Slot(str, bool)
    def activation_device(self, mac, state):

        topic = join(MQTT_TOPIC_PREFIX, 'dispositivos', mac)

        message = simplejson.dumps({'output': int(state)})

        self.publish(
            topic,
            message
        )

    def on_connect(self, *args):
        # print("on_cmqttconnect", args)
        self.state = MqttClient.Connected
        self.connected.emit()

    def on_disconnect(self, *args):
        # print("on_disconnect", args)
        self.state = MqttClient.Disconnected
        self.disconnected.emit()

