import binascii
import threading
import serial
from time import sleep


class CodingProvider:

    def __init__(self, com_provider):
        self.com_provider = com_provider
        self.incoming_message = None
        self.outgoing_message = None
        self.encoding_thread = EncodingThread(self)
        self.decoding_thread = DecodingThread(self)
        self.start_threads()
        self.my_login = None
        self.your_login = None
        self.speed = None
        self.response_connection = False

    def coding_connection(self, login, device_port, speed, byte_size, stop_bits, parity):
        self.my_login = login
        self.speed = speed
        self.encoding_thread.frame_type = 'S_connect'
        self.encoding_thread.encoding_state = True
        ports = {
            u"COM-port 1": 'COM1',
            u"COM-port 2": 'COM2',
            u"COM-port 3": 'COM3',
            u"COM-port 4": 'COM4'
        }
        device_port = ports[device_port]
        speed = int(speed)
        bytes = {
            u"5": serial.FIVEBITS,
            u"6": serial.SIXBITS,
            u"7": serial.SEVENBITS,
            u"8": serial.EIGHTBITS
        }
        byte_size = bytes[byte_size]
        stops = {
            u"1": serial.STOPBITS_ONE,
            u"1.5": serial.STOPBITS_ONE_POINT_FIVE,
            u"2": serial.STOPBITS_TWO
        }
        stop_bits = stops[stop_bits]
        par = {
            u"Отсутствует": serial.PARITY_NONE,
            u"Дополнение до четности": serial.PARITY_EVEN,
            u"Дополнение до нечетности": serial.PARITY_ODD,
            u"Всегда 1": serial.PARITY_MARK,
            u"Всегда 0": serial.PARITY_SPACE
        }
        parity = par[parity]
        self.com_provider.connect(device_port, speed, byte_size, stop_bits, parity)
        self.com_provider.sending(self.outgoing_message.encode())
        self.com_provider.incoming_thread.reading_state = True
        while not self.response_connection:
            sleep(1)
        self.com_provider.sending(self.outgoing_message.encode())
        return True

    def start_threads(self):
        self.encoding_thread.start()
        self.decoding_thread.start()

    def quit(self):
        self.encoding_thread.alive = False
        self.decoding_thread.alive = False

    def encoding_message(self, message):
        self.encoding_thread.message = message
        self.encoding_thread.encoding_state = True

    def decoding_message(self):
        self.decoding_thread.message = self.incoming_message
        self.decoding_thread.decoding_state = True

    @staticmethod
    def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
        bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

    def text_from_bits(self, bits, encoding='utf-8', errors='surrogatepass'):
        n = int(bits, 2)
        return self.int_to_bytes(n).decode(encoding, errors)

    @staticmethod
    def int_to_bytes(i):
        hex_string = '%x' % i
        n = len(hex_string)
        return binascii.unhexlify(hex_string.zfill(n + (n & 1)))


class EncodingThread(threading.Thread):

    def __init__(self, provider):
        threading.Thread.__init__(self, target=self.encoding_loop)
        self.coding_provider = provider
        self.alive = True
        self.message = None
        self.encoding_message = None
        self.encoding_state = False
        self.frame_type = None
        self.frame_count = 0

    def encoding_loop(self):
        while self.alive:
            if self.encoding_state:
                frame = self.generate_frame()
                self.encoding_message = frame
                self.loop()
                self.encoding_message = self.coding_provider.text_from_bits(self.encoding_message)
                self.coding_provider.outgoing_message = self.encoding_message
                self.encoding_state = False

    def generate_frame(self):
        if self.frame_count != 255:
            self.frame_count += 1
        else:
            self.frame_count = 0
        frame = []
        # todo переписать кадры, убрать скорость, добавить нумерацию кадров
        if self.frame_type == 'S_connect':
            # тип кадра
            frame.append(self.coding_provider.text_to_bits('S'))
            # длина данных
            len_data = str(bin(len(self.coding_provider.my_login)))[2:]
            count_null = 8 - len(len_data)
            frame.extend(['0'*count_null, len_data])
            # номер кадра
            frame_num = str(bin(self.frame_count))[2:]
            count_null = 8 - len(frame_num)
            frame.extend(['0'*count_null, frame_num])
            # данные
            frame.append('11111111')
            frame.append(self.coding_provider.text_to_bits(self.coding_provider.my_login))
            frame = ''.join(frame)
        elif self.frame_type == 'S_disconnect':
            # тип кадра
            frame.append(self.coding_provider.text_to_bits('S'))
            # номер кадра
            frame_num = str(bin(self.frame_count))[2:]
            count_null = 8 - len(frame_num)
            frame.extend(['0'*count_null, frame_num])
            # сессия
            frame.append('00000000')
        elif self.frame_type == 'I_inf':
            # тип кадра
            frame.append(self.coding_provider.text_to_bits('I'))
            # длина данных
            len_data = str(bin(len(self.message)))[2:]
            count_null = 8 - len(len_data)
            frame.extend(['0'*count_null, len_data])
            # номер кадра
            frame_num = str(bin(self.frame_count))[2:]
            count_null = 8 - len(frame_num)
            frame.extend(['0'*count_null, frame_num])
            # данные
            frame.append('10000001')
            # сообщение
            frame.append(self.coding_provider.text_to_bits(self.message))
            frame = ''.join(frame)
        return frame

    def loop(self):
        list_bits = list(self.encoding_message)
        new_list_bits = []
        for i in range(0, len(list_bits), 4):
            byte = list_bits[i:i+4]
            for j in range(0, len(byte)):
                byte[j] = int(byte[j])
            byte.extend([0, 0, 0])
            m = div(byte)
            # конкатенация
            for j in range(0, 3):
                byte[j + 4] = m[j]
            for j in range(0, len(byte)):
                byte[j] = str(byte[j])
            new_list_bits.append('0')
            new_list_bits.extend(byte)
        self.encoding_message = ''.join(new_list_bits)


class DecodingThread(threading.Thread):

    def __init__(self, provider):
        threading.Thread.__init__(self, target=self.decoding_loop)
        self.coding_provider = provider
        self.alive = True
        self.message = None
        self.decoding_message = None
        # self.decoding_state = False

    def decoding_loop(self):
        while self.alive:
            if self.coding_provider.com_provider.incoming_thread.message_state:
                self.message = self.coding_provider.com_provider.incoming_thread.message
                self.decoding_message = self.coding_provider.text_to_bits(self.message)
                self.error_search()
                self.unpack_frame()
                # self.decoding_message = self.coding_provider.text_from_bits(self.decoding_message)
                self.coding_provider.com_provider.incoming_thread.message_state = False

    def unpack_frame(self):
        # todo frame unpacking
        if len(self.decoding_message)//8 == 3:
            if self.coding_provider.text_from_bits(self.decoding_message[0:8]) == 'S':
                if self.decoding_message[16:24] == '00000000':
                    # todo сделать разъединение
                    pass
        elif self.coding_provider.text_from_bits(self.decoding_message[0:8]) == 'S':
            if self.decoding_message[24:32] == '11111111':
                j = 7
                res = 0
                for i in self.decoding_message[8:16]:
                    if i == '1':
                        res += 2 ** j
                    j -= 1
                res *= 8
                self.coding_provider.your_login = self.coding_provider.text_from_bits(self.decoding_message[32:32+res])
                self.coding_provider.response_connection = True
        #  todo сделать получение сообщений

    def error_search(self):
        list_bits = list(self.decoding_message)
        new_list_bits = []
        for i in range(0, len(list_bits), 8):
            byte = list_bits[i + 1:i + 8]
            for j in range(0, len(byte)):
                byte[j] = int(byte[j])
            syndrome = div(byte)
            syndrome_list = [[1, 0, 1], [1, 1, 1], [1, 1, 0], [0, 1, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
            if syndrome != [0, 0, 0]:
                j = syndrome_list.index(syndrome)
                byte[j] = int(not byte[j])
            byte = byte[0:4]
            for j in range(0, len(byte)):
                byte[j] = str(byte[j])
            new_list_bits.extend(byte)
        self.decoding_message = ''.join(new_list_bits)


def div(byte):
    # поиск единицы в m
    k = -1
    i = 0
    while k < 0:
        if byte[i] == 1:
            k = i
        else:
            if i == 3:
                k = 8
        i = i + 1
    m = []
    if k != 8:
        # деление m на образующий полином
        m.extend(byte[k:k + 4])
        g = [1, 0, 1, 1]
        k += 4
        while m[0] == 1:
            for i in range(0, 4):
                if m[i] == g[i]:
                    m[i] = 0
                else:
                    m[i] = 1
            while m[0] == 0 and k < 7:
                del m[0]
                m.append(byte[k])
                k = k + 1
        del m[0]
    else:
        m.extend(byte[4:7])
    return m


# s = CodingProvider()
# s.encoding_message('hello че как')
# sleep(5)
# s.decoding_message()
# s.quit()
