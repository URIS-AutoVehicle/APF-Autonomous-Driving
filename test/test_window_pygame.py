from time import sleep
import win32gui, win32con, win32api

def main():
    window_name = 'Pygame'
    hwnd = win32gui.FindWindow(None, window_name)
    hwndChild = win32gui.GetWindow(hwnd, win32con.GW_CHILD)
    print(f'{hwnd} {hwndChild}')

    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x41, 0)
    sleep(0.1)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x41, 0)

    for _ in range(5):
        temp = win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, 0x44, 0)
        print(temp)
        sleep(1)


if __name__ == '__main__':
    main()