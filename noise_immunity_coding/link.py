import binascii
import threading
import serial
from time import sleep


class CodingProvider:

    def __init__(self, com_provider):
        self.com_provider = com_provider
        self.encoding_thread = EncodingThread(self)
        self.decoding_thread = DecodingThread(self)
        self.my_login = None
        self.your_login = None
        self.speed = None
        self.byte_size = None
        self.stop_bits = None
        self.parity = None
        self.connection = True
        self.to_main_window = None
        self.quit_gui = None

        self.start_threads()

    def disconnection(self, state):
        if state:
            # установка логического соединения
            self.connection = True
        else:
            # разрыв логического соединения
            self.connection = False

    def coding_disconnection(self):
        self.encoding_thread.frame_type = 'S_disconnect'
        self.encoding_thread.encoding_state = True

    def coding_message(self, message):
        # кодирование и отправка короткого сообщения (при нажатии кнопки Отправить)
        if len(message) > 127:
            self.encoding_thread.message_error = True
        else:
            self.encoding_thread.frame_type = 'I_inf'
            self.encoding_thread.message = message
            self.encoding_thread.encoding_state = True

    def coding_connection(self, login, speed, byte_size, stop_bits, parity):
        # кодирование и отправка сообщения на соединение и ожидание ответного сообщения
        self.my_login = login
        self.speed = speed
        speeds = [u"50", u"75", u"110", u"150", u"300", u"600", u"1200", u"2400", u"4800", u"9600", u"19200", u"38400",
                  u"57600", u"115200"]
        self.speed = speeds.index(speed)
        speed = int(speed)
        bytes = [u"5", u"6", u"7", u"8"]
        self.byte_size = bytes.index(byte_size)
        bytes = {
            u"5": serial.FIVEBITS,
            u"6": serial.SIXBITS,
            u"7": serial.SEVENBITS,
            u"8": serial.EIGHTBITS
        }
        byte_size = bytes[byte_size]
        stops = [u"1", u"1.5", u"2"]
        self.stop_bits = stops.index(stop_bits)
        stops = {
            u"1": serial.STOPBITS_ONE,
            u"1.5": serial.STOPBITS_ONE_POINT_FIVE,
            u"2": serial.STOPBITS_TWO
        }
        stop_bits = stops[stop_bits]
        par = [u"Отсутствует", u"Дополнение до четности", u"Дополнение до нечетности", u"Всегда 1", u"Всегда 0"]
        self.parity = par.index(parity)
        par = {
            u"Отсутствует": serial.PARITY_NONE,
            u"Дополнение до четности": serial.PARITY_EVEN,
            u"Дополнение до нечетности": serial.PARITY_ODD,
            u"Всегда 1": serial.PARITY_MARK,
            u"Всегда 0": serial.PARITY_SPACE
        }
        parity = par[parity]
        device_port = 'COM1'
        self.com_provider.connect(device_port, speed, byte_size, stop_bits, parity)
        self.encoding_thread.frame_type = 'S_connect'
        self.encoding_thread.encoding_state = True

    def start_threads(self):
        self.encoding_thread.start()
        self.decoding_thread.start()

    def quit(self):
        self.encoding_thread.alive = False
        self.decoding_thread.alive = False

    #     Методы для работы с битовыми строками
    @staticmethod
    def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
        # bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
        bits = bin(int(binascii.hexlify(text.encode()), 16))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

    def text_from_bits(self, bits, encoding='utf-8', errors='surrogatepass'):
        n = int(bits, 2)
        # return self.int_to_bytes(n).decode(encoding, errors)
        return self.int_to_bytes(n).decode()

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
        self.textbox = None
        self.message_error = False
        self.correct_message = False

    def encoding_loop(self):
        # кодирование кадров на отправку
        while self.alive:
            if self.coding_provider.connection:
                if self.message_error:
                    self.textbox.insert(1.0, u'Ошибка! Длина сообщения не должна превышать 255 символов.')
                    self.message_error = False
                if self.encoding_state:
                    self.encoding_message = self.generate_frame()
                    self.loop()
                    self.encoding_message = self.coding_provider.text_from_bits(self.encoding_message)
                    self.coding_provider.com_provider.sending(self.encoding_message.encode())
                    if self.frame_type == 'S_connect':
                        self.coding_provider.com_provider.incoming_thread.reading_state = True
                    if self.frame_type == 'I_inf':
                        self.correct_message = True
                    self.encoding_state = False
                if self.correct_message:
                    self.textbox.insert(1.0, self.coding_provider.my_login + u' >> ' + self.message + '\n')
                    print(self.coding_provider.my_login + u' >> ' + self.message)
                    self.correct_message = False

    def int_to_bin(self, all_len, integer):
        bin_str = str(bin(integer))[2:]
        count_null = all_len - len(bin_str)
        res_list = ['0' * count_null, bin_str]
        return res_list

    def generate_frame(self):
        # генерация кадра
        if self.frame_count != 255:
            self.frame_count += 1
        else:
            self.frame_count = 0
        frame = []
        if self.frame_type == 'S_connect':
            # тип кадра - 1 byte
            frame.append(self.coding_provider.text_to_bits('S'))
            # длина данных - 1 byte (255 byte of data only)
            frame.extend(self.int_to_bin(8, len(self.coding_provider.my_login)))
            # номер кадра - 1 byte
            frame.extend(self.int_to_bin(8, self.frame_count))
            # параметры соединения - 3 byte
            frame.extend(self.int_to_bin(4, self.coding_provider.speed))
            frame.extend(self.int_to_bin(4, self.coding_provider.byte_size))
            frame.extend(self.int_to_bin(4, self.coding_provider.stop_bits))
            frame.extend(self.int_to_bin(4, self.coding_provider.parity))
            # данные - 255 + 1 byte max
            frame.append('11111111')
            frame.append(self.coding_provider.text_to_bits(self.coding_provider.my_login))
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
            len_data = str(bin(len(self.message)*2))[2:]
            count_null = 8 - len(len_data)
            frame.extend(['0'*count_null, len_data])
            # номер кадра
            frame_num = str(bin(self.frame_count))[2:]
            count_null = 8 - len(frame_num)
            frame.extend(['0'*count_null, frame_num])
            # данные
            frame.append('10000001')
            # сообщение
            all_message = []
            for letter in self.message:
                bin_letter = self.coding_provider.text_to_bits(letter)
                count_null = 16 - len(bin_letter)
                all_message.extend(['0'*count_null, bin_letter])
            frame.extend(all_message)
        frame = ''.join(frame)
        return frame

    def loop(self):
        # циклический код
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
        self.correct_message = False
        self.textbox = None
        self.frame_type = None
        self.success_connection = False
        # self.decoding_state = False

    def decoding_loop(self):
        # декодирование полученных кадров
        while self.alive:
            if self.coding_provider.connection:
                if self.coding_provider.com_provider.incoming_thread.message_state:
                    self.message = self.coding_provider.com_provider.incoming_thread.message
                    print(self.message)
                    self.decoding_message = self.coding_provider.text_to_bits(self.message)
                    self.error_search()
                    self.unpack_frame()
                    self.coding_provider.com_provider.incoming_thread.message_state = False
                if self.correct_message:
                    self.textbox.insert(1.0, self.coding_provider.your_login + u' >> ' + self.message + '\n')
                    self.correct_message = False

    def unpack_frame(self):
        # todo frame unpacking
        if len(self.decoding_message)//8 == 3:
            if self.coding_provider.text_from_bits(self.decoding_message[0:8]) == 'S':
                if self.decoding_message[16:24] == '00000000':
                    self.coding_provider.coding_disconnection()
                    sleep(1)
                    self.coding_provider.com_provider.incoming_thread.reading_state = False
                    self.coding_provider.quit_gui()
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
                if not self.success_connection:
                    self.coding_provider.encoding_thread.frame_type = 'S_connect'
                    self.coding_provider.encoding_thread.encoding_state = True
                    self.coding_provider.to_main_window()
                    self.success_connection = True
        elif self.coding_provider.text_from_bits(self.decoding_message[0:8]) == 'I':
            if self.decoding_message[24:32] == '10000001':
                res = int(self.decoding_message[8:16], 2) * 16
                print(self.coding_provider.your_login + ' >> ' +
                      self.coding_provider.text_from_bits(self.decoding_message[32:32+res]))
                self.message = self.coding_provider.text_from_bits(self.decoding_message[32:32+res])
                self.correct_message = True

    def error_search(self):
        # декодирование циклического кода, поиск ошибок
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
