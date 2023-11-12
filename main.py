from pynput import mouse
from pynput import keyboard
import sys
import time

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

    def logger(self, type, args):
        if type == 'M':
            pressed = ''
        else:
            pressed = '+' if args[-1] else '-'

        self.file.write(type + pressed + ', '
                   +', '.join([str(i) for i in args[:-1]])
                   + (f', { self.get_time_passed() }' if self.using_time else '')
                   + '\n')

    def logger_wrapper_factory(is_keyboard = False):
        def logger_wrapper(func):
            def wrapper(self, *args, **kwargs):
                #if len(args) == 1: # keyboard event
                self.logger('K' if is_keyboard else 'M', args)
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

        with open(path, 'wt', encoding='utf-8') as file:
            self.file = file
            Mlistener.start()
            Klistener.start()
            while self.listening: pass

if __name__ == '__main__':
    path = sys.argv[1]
    recorder = Recorder(path, is_using_time=True)
    recorder.listen()




