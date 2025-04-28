import win32con
import win32gui
import schedule
import time
def turnOffDekstop():
    SC_MONITORPOWER = 0xF170
    win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, SC_MONITORPOWER, 2)

schedule.every().day.at("15:36").do(turnOffDekstop)

while True:
    schedule.run_pending()
    time.sleep(1)