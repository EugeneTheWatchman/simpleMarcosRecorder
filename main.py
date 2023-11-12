from pynput import mouse
from pynput import keyboard
import sys
import time

using_time = False

def loggerFactory(file):
    def logger(type, args, is_key_pressed):
        if is_key_pressed is None:
            pressed = ''
        elif is_key_pressed:
            pressed = '+'
        else:
            pressed = '-'

        global last_event_time
        now_time = time.time_ns()
        file.write(type + pressed + ', ' +
                   ', '.join([str(i) for i in args]) + ', ' +
                    f'{ round((now_time - last_event_time) / 1_000_000) }'
                             + '\n')
        last_event_time = now_time

    return logger

def logger_wrapper_factory(is_key_pressed = None):
    def logger_wrapper(func):
        def wrapper(*args, **kwargs):
            #if len(args) == 1: # keyboard event
            logger('K' if len(args) == 1 else 'M', args, is_key_pressed)
            return func(*args, **kwargs)
        return wrapper
    return logger_wrapper
@logger_wrapper_factory(False)
def keyboard_on_release(key): pass
    #print(key, '-', ': released')

@logger_wrapper_factory(True)
def keyboard_on_press(key): pass
    #print(key, ': pressed')

@logger_wrapper_factory()
def mouse_on_click(x, y, button, pressed): pass
    #print(f'{button} {pressed} at {(x, y)}')


if __name__ == '__main__':
    Mlistener = mouse.Listener(on_click=mouse_on_click)
    Klistener = keyboard.Listener(on_press=keyboard_on_press,
                           on_release=keyboard_on_release)

    path = sys.argv[1]
    with open(path, 'wt', encoding='utf-8') as file:
        logger = loggerFactory(file)
        last_event_time = time.time_ns()
        Mlistener.start()
        Klistener.start()
        while True: pass



