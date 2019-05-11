# -*- coding: utf8 -*-
import tkinter
from tkinter import ttk
from tkinter import filedialog


class Gui:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.geometry("405x340")
        self.connect_panel = None
        self.connect_label = None
        self.connect_but = None
        self.main_panel = None
        self.connect_state = None
        self.connect = None
        self.state = False
        self.message = None
        self.general_chat = None
        self.history_messages = None
        self.previous_main = True
        self.file_entry = None
        self.history_panel = None

        self.connection(None)
        self.root.mainloop()

    def connection(self, event):
        try:
            self.main_panel.destroy()
        except: pass

        self.root.geometry("405x340")
        self.root.title("Bomonkagram")
        self.connect_panel =tkinter.Frame(self.root, width=450, height=350, relief=tkinter.GROOVE, bd=2)
        self.connect_panel.place(x=25, y=35)
        self.connect_label = tkinter.Label(self.root, text='Соединение')
        self.connect_label.place(x=25, y=5)
        self.connect_but = tkinter.Button(self.root, text='Соединить', width=12)
        self.connect_but.place(y=304, x=286)

        login_label = tkinter.Label(self.connect_panel, text='Логин')
        login_entry = tkinter.Entry(self.connect_panel, width=35)
        port_label = tkinter.Label(self.connect_panel, text='COM-порт')
        port_box = ttk.Combobox(self.connect_panel, width=35)
        port_box.config(values=[
            u"COM-port 1",
            u"COM-port 2",
            u"COM-port 3"
        ])
        port_box.set(u"COM-port 1")
        speed_label = tkinter.Label(self.connect_panel, text='Скорость (бит/с)')
        speed_box = ttk.Combobox(self.connect_panel, width=35)
        speed_box.config(values=[
            u"50",
            u"75",
            u"110",
            u"150",
            u"300",
            u"600",
            u"1200",
            u"2400",
            u"4800",
            u"9600",
            u"19200",
            u"38400",
            u"57600",
            u"115200"
        ])
        speed_box.set(u"9600")
        bit_data_label = tkinter.Label(self.connect_panel, text='Биты данных')
        bit_data_box = ttk.Combobox(self.connect_panel, width=35)
        bit_data_box.config(values=[
            u"5",
            u"6",
            u"7",
            u"8"
        ])
        bit_data_box.set(u"8")
        # тут возможны варианты 1, 1.5, 2
        stop_bit_label = tkinter.Label(self.connect_panel, text='Стоп биты')
        stop_bit_box = ttk.Combobox(self.connect_panel, width=35)
        stop_bit_box.config(values=[
            u"1",
            u"2"
        ])
        stop_bit_box.set(u"1")
        # тут возможны варианты NONE, EVEN, ODD, MARK, SPACE
        parity_label = tkinter.Label(self.connect_panel, text='Четность')
        parity_box = ttk.Combobox(self.connect_panel, width=35)
        parity_box.config(values=[
            u"НЕТ",
            u"ДА"
        ])
        parity_box.set(u"НЕТ")

        login_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)
        login_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)
        port_label.grid(row=1, column=0, sticky='w', padx=10, pady=10)
        port_box.grid(row=1, column=1, sticky='w', padx=10, pady=10)
        speed_label.grid(row=2, column=0, sticky='w', padx=10, pady=10)
        speed_box.grid(row=2, column=1, sticky='w', padx=10, pady=10)
        bit_data_label.grid(row=3, column=0, sticky='w', padx=10, pady=10)
        bit_data_box.grid(row=3, column=1, sticky='w', padx=10, pady=10)
        stop_bit_label.grid(row=4, column=0, sticky='w', padx=10, pady=10)
        stop_bit_box.grid(row=4, column=1, sticky='w', padx=10, pady=10)
        parity_label.grid(row=5, column=0, sticky='w', padx=10, pady=10)
        parity_box.grid(row=5, column=1, sticky='w', padx=10, pady=10)

        self.connect_but.bind('<Button-1>', self.main_window)

    def main_window(self, event):
        try:
            self.history_panel.destroy()
        except: pass
        try:
            self.connect_panel.destroy()
            self.connect_but.destroy()
        except: pass
        self.state = True
        self.previous_main = True

        self.connect_label.config(text='Главная')
        self.root.geometry('680x535')
        self.main_panel = tkinter.Frame(self.root, width=630, height=495)
        self.general_chat = tkinter.Text(self.main_panel, height=22, width=57, wrap=tkinter.WORD, state='disabled')
        users = tkinter.Text(self.main_panel, height=22, width=20, wrap=tkinter.WORD, state='disabled')
        message_label = tkinter.Label(self.main_panel, text='Сообщение:')
        self.message = tkinter.Entry(self.main_panel, width=75)
        file_label = tkinter.Label(self.main_panel, text='Файл:')
        self.file_entry = tkinter.Entry(self.main_panel, width=20)
        open_but = tkinter.Button(self.main_panel, text='Открыть', width=14)
        send_message = tkinter.Button(self.main_panel, text='Отправить', width=20)
        self.connect = tkinter.Button(self.main_panel, text='Разединить', width=15)
        self.connect_state = tkinter.Label(self.main_panel, text='Подключено')
        history = tkinter.Button(self.main_panel, text='История', width=15)
        quit = tkinter.Button(self.main_panel, text='Выход', width=15)

        self.main_panel.place(x=25, y=35)
        self.general_chat.place(x=0, y=0)
        users.place(x=480, y=0)
        message_label.place(x=0, y=370)
        self.message.place(x=0, y=395)
        file_label.place(x=0, y=425)
        self.file_entry.place(x=50, y=425)
        open_but.place(x=185, y=420)
        send_message.place(x=480, y=391)
        # x = 304, y = 420
        self.connect.place(x=0, y=460)
        self.connect_state.place(x=130, y=463)
        history.place(x=395, y=463)
        quit.place(x=515, y=463)

        self.connect.bind('<Button-1>', self.change_state)
        send_message.bind('<Button-1>', self.send)
        history.bind('<Button-1>', self.history_window)
        open_but.bind('<Button-1>', self.load_file)
        quit.bind('<Button-1>', self.connection)

    # def private_messages_window(self, event):
    #     self.connect_label.config(text='Личные сообщения')
    #     self.main_panel.destroy()
    #     self.previous_main = False

    def history_window(self, event):
        self.connect_label.config(text='История сообщений')
        self.main_panel.destroy()

        self.history_panel = tkinter.Frame(self.root, height=500, width=650)
        self.history_messages = tkinter.Text(self.history_panel, height=27, width=77, wrap=tkinter.WORD, state='disabled')
        save = tkinter.Button(self.history_panel, text='Сохранить', width=15)
        clean = tkinter.Button(self.history_panel, text='Очистить', width=15)
        escape = tkinter.Button(self.history_panel, text='Назад', width=15)

        self.history_panel.place(x=25, y=35)
        self.history_messages.place(x=0, y=0)
        save.place(x=275, y=460)
        clean.place(x=395, y=460)
        escape.place(x=515, y=460)

        save.bind('<Button-1>', self.save_history)
        clean.bind('<Button-1>', self.clean_history)
        escape.bind('<Button-1>', self.escape_handler)

    def save_history(self, event):
        hist = self.history_messages.get(1.0, 'end')
        # hist = u'{}'.format(hist)
        _file = filedialog.asksaveasfilename(initialdir="C:/Users/azeng/Documents/6 семестр/сети/курсач", title="Select file")
        if _file == '':
            return
        with open(_file, 'w') as file_txt:
            file_txt.write(hist)

    def clean_history(self, event):
        # сделать удаление из бд (документа, где будет храниться история)
        self.history_messages.delete(1.0, tkinter.END)

    def escape_handler(self, event):
        if self.previous_main:
            self.main_window(None)
        else:
            # дописать возврат к личным сообщениям определенного юзера
            self.private_messages_window(None)

    def change_state(self, event):
        if self.state:
            self.state = False
            self.connect_state.config(text='Отключено')
            self.connect.config(text='Соединить')
        else:
            self.state = True
            self.connect_state.config(text='Подключено')
            self.connect.config(text='Разъединить')

    def send(self, event):
        # это не работает, надо через поток
        mes = self.message.get()
        self.general_chat.insert(1.0, mes)
        self.message.delete(0, tkinter.END)

    def load_file(self, event):
        _file = filedialog.askopenfilename(initialdir="/", title="Select file")
        if _file == '':
            return
        self.file_entry.delete(0, 'end')
        self.file_entry.insert(0, _file)


