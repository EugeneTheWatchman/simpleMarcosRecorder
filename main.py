from pynput import mouse
from pynput import keyboard
import sys
import time

class Recorder:
    using_time = False
    last_event_time = -1
    file_path = None
    file = None

    def __init__(self, file_path, is_using_time):
        self.file_path = file_path
        self.using_time = is_using_time
        self.get_time_passed()

    def get_time_passed(self):
        now_time = time.time_ns()
        time_passed = round((now_time - self.last_event_time) / 1_000_000)
        self.last_event_time = now_time
        return time_passed

    def logger(self, type, args, is_key_pressed):
        if is_key_pressed is None:
            pressed = ''
        elif is_key_pressed:
            pressed = '+'
        else:
            pressed = '-'

        self.file.write(type + pressed + ', '
                   +', '.join([str(i) for i in args])
                   + (f', { self.get_time_passed() }' if self.using_time else '')
                   + '\n')

    def logger_wrapper_factory(is_key_pressed = None):
        def logger_wrapper(func):
            def wrapper(self, *args, **kwargs):
                #if len(args) == 1: # keyboard event
                self.logger('K' if len(args) == 1 else 'M', args, is_key_pressed)
                return func(self, *args, **kwargs)
            return wrapper
        return logger_wrapper

    @logger_wrapper_factory(False)
    def keyboard_on_release(self, key): pass
        #print(key, '-', ': released')

    @logger_wrapper_factory(True)
    def keyboard_on_press(self, key): pass
        #print(key, ': pressed')

    @logger_wrapper_factory()
    def mouse_on_click(self, x, y, button, pressed): pass
        #print(f'{button} {pressed} at {(x, y)}')

    def listen(self):
        Mlistener = mouse.Listener(on_click=self.mouse_on_click)
        Klistener = keyboard.Listener(on_press=self.keyboard_on_press,
                                      on_release=self.keyboard_on_release)

        with open(path, 'wt', encoding='utf-8') as file:
            self.file = file
            Mlistener.start()
            Klistener.start()
            while True: pass

if __name__ == '__main__':
    path = sys.argv[1]
    recorder = Recorder(path, is_using_time=True)
    recorder.listen()




