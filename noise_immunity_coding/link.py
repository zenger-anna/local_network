import binascii
import threading
from time import sleep


class CodingProvider:

    def __init__(self):
        self.message = None
        self.encoding_thread = EncodingThread(self)
        self.decoding_thread = DecodingThread(self)
        self.start_threads()

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
        self.decoding_thread.message = self.message
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

    def encoding_loop(self):
        while self.alive:
            if self.encoding_state:
                self.encoding_message = self.coding_provider.text_to_bits(self.message)
                self.loop()
                self.generate_frame()
                self.encoding_message = self.coding_provider.text_from_bits(self.encoding_message)
                print(self.encoding_message)
                self.coding_provider.message = self.encoding_message
                self.encoding_state = False

    def generate_frame(self):
        # todo generate frames
        pass

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
        self.decoding_state = False

    def decoding_loop(self):
        while self.alive:
            if self.decoding_state:
                self.decoding_message = self.coding_provider.text_to_bits(self.message)
                self.unpack_frame()
                self.error_search()
                self.decoding_message = self.coding_provider.text_from_bits(self.decoding_message)
                print(self.decoding_message)
                self.decoding_state = False

    def unpack_frame(self):
        # todo frame unpacking
        pass

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


s = CodingProvider()
s.encoding_message('hello че как')
sleep(5)
s.decoding_message()
s.quit()
