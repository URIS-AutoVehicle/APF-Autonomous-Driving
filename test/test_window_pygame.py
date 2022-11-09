from time import sleep
import win32gui, win32con, win32api

def main():
    window_name = '*test1.txt - Notepad'
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd != 0:
        hwndChild = win32gui.GetWindow(hwnd, win32con.GW_CHILD)
    print(f'{hwnd} {hwndChild}')

    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, ord('a'), 0)
    sleep(0.1)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, ord('a'), 0)

    for _ in range(5):
        win32api.PostMessage(hwndChild, win32con.WM_KEYDOWN, 0x41, 0)
        sleep(0.05)
        # win32api.PostMessage(hwndChild, win32con.WM_KEYUP, 0x41, 0)

        # win32api.PostMessage(hwndChild, win32con.WM_CHAR, ord('a'), 0)
        sleep(0.1)


if __name__ == '__main__':
    main()