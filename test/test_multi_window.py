import sched
from time import sleep, time
import win32gui, win32ui, win32con, win32api

# REF: https://learncodebygaming.com/blog/how-to-send-inputs-to-multiple-windows-and-minimized-windows-with-python

def main(window_names, inputs):
    # init window handle
    # hwnd = win32gui.FindWindow(None, window_name)
    # print(list_window_names())
    hwnds = find_all_windows(window_names)
    print(f'{hwnds}')

    s = sched.scheduler(time, sleep)

    # id_map = {v: i for i, v in enumerate(window_names)}
    id = 0
    for window_name in window_names:
        for hwnd in hwnds[window_name]:
            input = inputs[id % len(inputs)]
            redirect_input(hwnd, s, input)
            id += 1

    s.run()

# send a keyboard input to the given window
def redirect_input(hwnd, s, input):
    # priority = 2
    # foreground_time = 0.15

    #s.enter(start_sec, priority, win32api.SendMessage, argument=(hwnd, win32con.WM_KEYDOWN, key, 0))
    #s.enter(end_sec, priority, win32api.SendMessage, argument=(hwnd, win32con.WM_KEYUP, key, 0))

    # send input to the window, if no other inner windows are there
    for char in input:
        win32api.PostMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
        # win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, ord(char), 0)
        # sleep(0.01)
        # win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, ord(char), 0)

    # send input to all inner windows
    # this is effective on windows native apps, like Notepad
    for id, val in enumerate(get_inner_windows(hwnd).values()):
        for char in input:
            win32api.PostMessage(val, win32con.WM_CHAR, ord(char), 0)


def list_window_names():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(f'{hex(hwnd)}, "{win32gui.GetWindowText(hwnd)}"')

    win32gui.EnumWindows(winEnumHandler, None)


def get_inner_windows(whndl):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            hwnds[win32gui.GetClassName(hwnd)] = hwnd
        return True

    hwnds = {}
    win32gui.EnumChildWindows(whndl, callback, hwnds)
    print(hwnds)
    return hwnds

def find_all_windows(arr):
    res = {}

    def winEnumHandler(hwnd, _):
        for win_name in arr:
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == win_name:
                res[win_name] = res.get(win_name, []) + [hwnd]

    win32gui.EnumWindows(winEnumHandler, None)
    return res

if __name__ == '__main__':
    win_names = ["*test1.txt - Notepad", "*test2.txt - Notepad"]
    # win_names = ['Pygame']
    # win_names = ["New Tab - Google Chrome"]
    inputs = ["input for first doc", "input for second doc"]
    main(win_names, inputs)
# list_window_names()