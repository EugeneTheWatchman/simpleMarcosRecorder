from pynput import mouse
from pynput import keyboard
import sys
import time
import enum
from abc import ABC, abstractmethod, abstractproperty, abstractclassmethod, abstractstaticmethod

SEPARATOR = '\t'

class COMMAND(enum.Enum):
    KEYBOARD = "K"
    MOUSE = "M"
    KEYBOARD_DOWN = "K+"
    MOUSE_DOWN = "M+"
    KEYBOARD_UP = "K-"
    MOUSE_UP = "M-"


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
        match command:
            case COMMAND.KEYBOARD:
                if args[-1]:  # if pressed
                    command = COMMAND.KEYBOARD_DOWN
                else:  # if realease
                    command = COMMAND.KEYBOARD_UP
            case COMMAND.MOUSE:
                if args[-1]:  # if pressed
                    command = COMMAND.MOUSE_DOWN
                else:  # if realease
                    command = COMMAND.MOUSE_UP

        command_line = [command.value]
        for arg in args[:-1]:
            command_line.append(arg.value if isinstance(arg, enum.Enum) else arg)
        self.file.write(SEPARATOR.join(map(str, command_line)) + '\n')
    def logger_wrapper_factory(is_keyboard=False):
        def logger_wrapper(func):
            def wrapper(self, *args, **kwargs):
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
        pass  # print(f'{button} {pressed} at {(x, y)}')

    def listen(self):
        Mlistener = mouse.Listener(on_click=self.mouse_on_click)
        Klistener = keyboard.Listener(on_press=self.keyboard_on_press,
                                      on_release=self.keyboard_on_release)

        with open(self.file_path, 'wt', encoding='ascii') as file:
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
        with open(self.file_path, 'rt', encoding='ascii') as file:
            for line in file:
                self.handle(line)
            print('--------------all--------------')

    def handle(self, line):
        command = line[:-1].split(SEPARATOR)
        action = Action.create(COMMAND(command[0]), command[1:])
        action.execute()


class Action(ABC):
    @staticmethod
    def create(type, command):

        match type:
            case COMMAND.KEYBOARD_DOWN:
                return KeyboardAction(True, *command)
            case COMMAND.MOUSE_DOWN:
                return MouseAction(True, *command)
            case COMMAND.KEYBOARD_UP:
                return KeyboardAction(False, *command, 0)
            case COMMAND.MOUSE_UP:
                return MouseAction(False, *command, 0)
            case _:
                raise NotImplementedError(f'{command[0]} in {command} is unexpected')

    @abstractmethod
    def execute(self):
        ...


class MouseAction(Action):
    controller = mouse.Controller()

    def __init__(self, is_pressed, x, y, button, dtime):
        self.is_pressed = is_pressed
        self.x = int(x)
        self.y = int(y)
        self.button = mouse.Button(eval(button))
        self.dtime = int(dtime)

    def execute(self):
        time.sleep(self.dtime)
        self.move_to(self.x, self.y)
        if self.is_pressed:
            self.controller.press(self.button)
        else:
            self.controller.release(self.button)
        print(f"{'Pressed' if self.is_pressed else 'Released'} {self.button} at {self.x},{self.y}")

    def move_to(self, x, y):
        self.controller.position = x, y


class KeyboardAction(Action):
    controller = keyboard.Controller()

    def __init__(self, is_pressed, key, dtime):
        self.is_pressed = is_pressed
        self.key = keyboard.KeyCode(int(key[1:-1])) if key[0] == '<' else key[1:-1]
        self.dtime = int(dtime)

    def execute(self):
        time.sleep(self.dtime)
        if self.is_pressed:
            self.controller.press(self.key)
        else:
            self.controller.release(self.key)
        print(f"{'Pressed' if self.is_pressed else 'Released'} {self.key}")


if __name__ == '__main__':
    match len(sys.argv):
        case 0:
            print('\n', 'Первым аргументом обычно (в windows) указан путь до файла программы', '\n')
            exit(0)
        case 1:
            print('\n', 'Вторым аругментом укажите имя файла для записи/воспроизведения макроса', '\n')
            exit(0)
        case 2:
            print('\n', 'Третьим аргументом укажите "w" для записи или "r" для чтения', '\n')
            exit(0)

    path = sys.argv[1]
    readWriteArg = sys.argv[2]

    if readWriteArg == 'r':
        reader = Reader(path)
        reader.read()
    elif readWriteArg == 'w':
        recorder = Recorder(path, is_using_time=True)
        print('\n', 'Для выхода из программы зажмите ctrl +', recorder.exitKey.name, '\n')
        recorder.listen()
