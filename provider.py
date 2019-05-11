from com_port import com_port
import serial


class Provider:

    def __init__(self):
        self.outgoing_thread = com_port.OutgoingThread(self)
        self.incoming_thread = com_port.IncomingThread(self)
        self.com_port = None
        self.start_threads()

    def connect(self,
                device_port='COM1',
                speed=9600,
                byte_size=serial.EIGHTBITS,
                stop_bits=serial.STOPBITS_ONE,
                parity=serial.PARITY_NONE):
        self.com_port = com_port.SerialProvider(self,
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
        self.outgoing_thread.is_alive = False
        self.incoming_thread.is_alive = False

    def sending(self, message):
        self.outgoing_thread.message = message
        self.outgoing_thread.sending_state = True

    def quit(self):
        self.disconnect()
        self.quit_threads()
