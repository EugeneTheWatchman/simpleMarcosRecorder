from pynput import mouse
from pynput import keyboard
import sys
import time
import enum

class COMMAND(enum.Enum):
    MOUSE = "M"
    KEYBOARD = "K"
    KEYBOARD_UP = "K+"
    KEYBOARD_DOWN = "K-"


class Recorder:
    using_time = False
    last_event_time = -1
    file_path = None
    file = None
    listening = True
    # for stop listening
    exitKey = keyboard.Key.esc
    keysPressed = {exitKey: False,
                   keyboard.Key.ctrl: False}

    def __init__(self, file_path, is_using_time):
        self.file_path = file_path
        self.using_time = is_using_time
        self.get_time_passed()

    def get_time_passed(self):
        now_time = time.time_ns()
        time_passed = round((now_time - self.last_event_time) / 1_000_000)
        self.last_event_time = now_time
        return time_passed

    def logger(self, command: COMMAND, args):
        if command == COMMAND.KEYBOARD:
            if args[-1]: # if pressed
                command = COMMAND.KEYBOARD_UP
            else:
                command = COMMAND.KEYBOARD_DOWN

        self.file.write(command + ', '
                   +', '.join([str(i) for i in args[:-1]])
                   + (f', { self.get_time_passed() }' if self.using_time else '')
                   + '\n')

    def logger_wrapper_factory(is_keyboard = False):
        def logger_wrapper(func):
            def wrapper(self, *args, **kwargs):
                #if len(args) == 1: # keyboard event
                self.logger(COMMAND.KEYBOARD if is_keyboard else COMMAND.MOUSE, args)
                return func(self, *args, **kwargs)
            return wrapper
        return logger_wrapper

    def check_exit_state(self):
        if self.keysPressed[self.exitKey] and self.keysPressed[keyboard.Key.ctrl]:
            self.listening = False
    @logger_wrapper_factory(True)
    def keyboard_on_event(self, key: keyboard.Key, is_pressed):
        # я растроен, что в match-case не нужно использование break
        match key:
            case keyboard.Key.ctrl | keyboard.Key.ctrl_l | keyboard.Key.ctrl_r:
                self.keysPressed[keyboard.Key.ctrl] = is_pressed
                self.check_exit_state()
            case self.exitKey:
                self.keysPressed[key] = is_pressed
                self.check_exit_state()

    def keyboard_on_press(self, key):
        self.keyboard_on_event(key, True)

    def keyboard_on_release(self, key):
        self.keyboard_on_event(key, False)

    @logger_wrapper_factory(False)
    def mouse_on_click(self, x, y, button, pressed):
        pass#print(f'{button} {pressed} at {(x, y)}')

    def listen(self):
        Mlistener = mouse.Listener(on_click=self.mouse_on_click)
        Klistener = keyboard.Listener(on_press=self.keyboard_on_press,
                                      on_release=self.keyboard_on_release)

        with open(self.file_path, 'wt', encoding='utf-8') as file:
            self.file = file
            Mlistener.start()
            Klistener.start()
            while self.listening: pass


class Reader:
    file_path = None
    file = None
    def __init__(self, file_path):
        self.file_path = file_path
    def read(self):
        with open(self.file_path, 'rt', encoding='utf-8') as file:
            for line in file:
                self.handle(line)
            print('--------------all--------------')
    def handle(self, line):
        command = line[:-1].replace(' ', '').split(',')
        match command[0]:
            case COMMAND.MOUSE:
                ...
            case COMMAND.KEYBOARD_UP:
                ...
            case COMMAND.KEYBOARD_DOWN:
                ...


if __name__ == '__main__':
    match len(sys.argv):
        case 0:
            print('\n','Первым аргументом обычно (в windows) указан путь до файла программы','\n')
            exit(0)
        case 1:
            print('\n','Вторым аругментом укажите имя файла для записи/воспроизведения макроса','\n')
            exit(0)
        case 2:
            print('\n','Третьим аргументом укажите "w" для записи или "r" для чтения','\n')
            exit(0)

    path = sys.argv[1]
    readWriteArg = sys.argv[2]

    if readWriteArg == 'r':
        reader = Reader(path)
        reader.read()
    elif readWriteArg == 'w':
        recorder = Recorder(path, is_using_time=True)
        print('\n','Для выхода из программы зажмите ctrl +', recorder.exitKey.name, '\n')
        recorder.listen()




