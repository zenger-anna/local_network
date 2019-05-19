import serial
import threading
from time import sleep


class COMProvider:

    def __init__(self):
        self.outgoing_thread = OutgoingThread(self)
        self.incoming_thread = IncomingThread(self)
        self.com_port = None
        self.start_threads()

    def connect(self,
                device_port='COM1',
                speed=9600,
                byte_size=serial.EIGHTBITS,
                stop_bits=serial.STOPBITS_ONE,
                parity=serial.PARITY_NONE):
        self.com_port = SerialProvider(self,
                                       device_port=device_port,
                                       speed=speed,
                                       byte_size=byte_size,
                                       stop_bits=stop_bits,
                                       parity=parity)
        self.com_port.open()

    def disconnect(self):
        self.com_port.close()

    def start_threads(self):
        self.incoming_thread.start()
        self.outgoing_thread.start()

    def quit_threads(self):
        self.outgoing_thread.alive = False
        self.incoming_thread.alive = False

    def sending(self, message):
        self.outgoing_thread.message = message
        self.outgoing_thread.sending_state = True

    def quit(self):
        self.quit_threads()
        sleep(1)
        self.disconnect()


class OutgoingThread(threading.Thread):

    def __init__(self, provider):
        threading.Thread.__init__(self, target=self.sending_loop)
        self.com_provider = provider
        self.alive = True
        self.sending_state = False
        self.message = None

    def sending_loop(self):
        while self.alive:
            if self.sending_state:
                self.com_provider.com_port.write(self.message)
                self.sending_state = False
                sleep(1)


class IncomingThread(threading.Thread):

    def __init__(self, provider):
        threading.Thread.__init__(self, target=self.reading_loop)
        self.provider = provider
        self.alive = True
        self.reading_state = False
        self.message = None
        self.message_state = False

    def reading_loop(self):
        while self.alive:
            if self.reading_state:
                self.message = self.provider.com_port.read()
                if self.message != '':
                    self.message_state = True
                sleep(1)


class SerialProvider:

    def __init__(self,
                 provider,
                 device_port='COM1',
                 speed=9600,
                 byte_size=serial.EIGHTBITS,
                 stop_bits=serial.STOPBITS_ONE,
                 parity=serial.PARITY_NONE):
        self.com_provider = provider
        self.ser = serial.Serial()
        self.ser.port = device_port
        self.ser.baudrate = speed
        self.ser.bytesize = byte_size
        self.ser.stopbits = stop_bits
        self.ser.parity = parity

    def open(self):
        try:
            self.ser.open()
        except ConnectionError:
            print('Connection Error: please check your connection to port {}'.format(self.ser.port))

    def get_port_state(self):
        if self.ser.is_open:
            return 'Port is connected'
        else:
            return 'Port is disconnected'

    def write(self, message):
        # try:
        self.ser.write(message)
        # except:
            # print('Error sending message: please try again or check your connection')

    def read(self):
        line = b''
        while self.ser.inWaiting() > 0:
            line += self.ser.read()
        line = line.decode("utf-8")
        return line

    def close(self):
        self.ser.close()

# s = COMProvider()
# s.connect()
# sas = 'hello'
# sas = sas.encode()
# # s =
# s.sending(sas)
# print('yeah')
