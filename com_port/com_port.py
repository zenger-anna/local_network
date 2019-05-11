import serial
import threading
from time import sleep


class OutgoingThread(threading.Thread):

    def __init__(self, provider):
        threading.Thread.__init__(self, target=self.sending_loop)
        # self.daemon = True
        self.provider = provider
        self.alive = True
        self.sending_state = False
        self.message = None

    def sending_loop(self):
        while self.alive:
            print(1)
            if self.sending_state:
                print('okok')
                self.provider.com_port.write(self.message)
                self.sending_state = False
                print('okok')
                sleep(1)


class IncomingThread(threading.Thread):

    def __init__(self, provider):
        threading.Thread.__init__(self, target=self.reading_loop)
        # self.daemon = True
        self.provider = provider
        self.alive = True
        self.reading_state = False
        self.message = None

    def reading_loop(self):
        while self.alive:
            if self.reading_state:
                self.message = self.provider.com_port.read()
                # todo тут надо дописать, куда пойдет дальше сообщение
                sleep(1)


class SerialProvider:

    def __init__(self,
                 provider,
                 device_port='COM1',
                 speed=9600,
                 byte_size=serial.EIGHTBITS,
                 stop_bits=serial.STOPBITS_ONE,
                 parity=serial.PARITY_NONE):
        self.provider = provider
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
        try:
            self.ser.write(message)
        except:
            print('Error sending message: please try again or check your connection')

    def read(self):
        line = b''
        while self.ser.inWaiting() > 0:
            line += self.ser.read()
        line = line.decode("utf-8")
        return line

    def close(self):
        self.ser.close()

# s = Provider()
# s.connect()
# s.sending(b'hello')
