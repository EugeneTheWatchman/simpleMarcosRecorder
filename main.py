from pynput import mouse
from pynput import keyboard
import sys
import time
import enum
from abc import ABC, abstractmethod
from functools import reduce

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
    should_stop = False
    listening = True
    # for stop listening
    exit_key = keyboard.Key.esc
    keysPressed = {exit_key: False,
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
        if self.using_time:
            command_line.append(self.get_time_passed())
        self.file.write(SEPARATOR.join(map(str, command_line)) + '\n')
    def logger_wrapper_factory(*, is_keyboard):
        def logger_wrapper(func):
            def wrapper(self, *args, **kwargs):
                self.logger(COMMAND.KEYBOARD if is_keyboard else COMMAND.MOUSE, args)
                return func(self, *args, **kwargs)

            return wrapper

        return logger_wrapper

    def check_exit_state(self):
        if self.keysPressed[self.exit_key] and self.keysPressed[keyboard.Key.ctrl]: # check exit condition
            self.should_stop = True
        elif self.should_stop and not any(self.keysPressed.values()): # check if 'all' keys released | note: 'all' means two keys in this implementation, ctrl and exit_key
            self.listening = False

    @logger_wrapper_factory(is_keyboard=True)
    def keyboard_on_event(self, key: keyboard.Key, is_pressed):
        # я растроен, что в match-case не нужно использование break
        match key:
            case keyboard.Key.ctrl | keyboard.Key.ctrl_l | keyboard.Key.ctrl_r:
                self.keysPressed[keyboard.Key.ctrl] = is_pressed
                self.check_exit_state()
            case self.exit_key:
                self.keysPressed[key] = is_pressed
                self.check_exit_state()

    def keyboard_on_press(self, key):
        self.keyboard_on_event(key, True)

    def keyboard_on_release(self, key):
        self.keyboard_on_event(key, False)

    @logger_wrapper_factory(is_keyboard=False)
    def mouse_on_click(self, x, y, button, pressed):
        pass

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
            print('Complete!')

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
                return KeyboardAction(False, *command)
            case COMMAND.MOUSE_UP:
                return MouseAction(False, *command)
            case _:
                raise NotImplementedError(f'{command[0]} in {command} is unexpected')

    @abstractmethod
    def execute(self):
        ...


class MouseAction(Action):
    controller = mouse.Controller()

    def __init__(self, is_pressed, x, y, button, dtime=0):
        self.is_pressed = is_pressed
        self.x = int(x)
        self.y = int(y)
        self.button = mouse.Button(eval(button))
        global times_faster
        self.dtime = int(dtime)/1000/times_faster

    def execute(self):
        time.sleep(self.dtime)
        self.move_to(self.x, self.y)
        if self.is_pressed:
            self.controller.press(self.button)
        else:
            self.controller.release(self.button)

    def move_to(self, x, y):
        self.controller.position = x, y


class KeyboardAction(Action):
    controller = keyboard.Controller()

    def __init__(self, is_pressed, key, dtime=0):
        self.is_pressed = is_pressed
        self.key = keyboard.KeyCode(int(key[1:-1])) if key[0] == '<' else key[1:-1]
        self.dtime = int(dtime)/1000/times_faster

    def execute(self):
        time.sleep(self.dtime)
        if self.is_pressed:
            self.controller.press(self.key)
        else:
            self.controller.release(self.key)


if __name__ == '__main__':
    class ARGUMENTS(enum.Enum):
        RECORD = 'w'
        EXECUTE = 'r'
        TIME = 't'

    # is_using_time = False
    # times_faster = 1
    match len(sys.argv):
        case 0:
            print('\n', 'Нулевым аргументом обычно (в windows) указан путь до файла программы', '\n')
            exit(0)
        case 1:
            print('\n', 'Первым аругментом укажите имя файла для записи/воспроизведения макроса', '\n')
            exit(0)
        case 2:
            print('\n', 'Вторым аргументом укажите "{0}" для записи или "{1}" для чтения'.format(
                ARGUMENTS.RECORD, ARGUMENTS.EXECUTE), '\n')
            exit(0)
        case 3:
            match ARGUMENTS(sys.argv[2]):
                case ARGUMENTS.RECORD:
                    is_using_time = False
                    # times_faster = 1
                    print(f'Третьим аргументом укажите "{ARGUMENTS.TIME}" для учета времени между кликами')
                case ARGUMENTS.EXECUTE:
                    print('\n', 'Третьим аргументом укажите число - кол-во раз в которое будет ускорено время между кликами', '\n')
                    exit(0)
        case 4:
            if sys.argv[3] == ARGUMENTS.TIME:
                is_using_time = True
            elif sys.argv[3].replace('.','').isdigit():
                times_faster = float(sys.argv[3])
                times_faster = times_faster if times_faster != 0 else 1
            else:
                is_using_time = False
                times_faster = 1

    path = sys.argv[1]

    match ARGUMENTS(sys.argv[2]):
        case ARGUMENTS.RECORD:
            recorder = Recorder(path, is_using_time=True)
            print('\n', 'Для выхода из программы зажмите ctrl +', recorder.exit_key.name, '\n')
            recorder.listen()
        case ARGUMENTS.EXECUTE:
            reader = Reader(path)
            reader.read()
