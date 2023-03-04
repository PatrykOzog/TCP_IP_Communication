import win32api
import win32con

# Uruchamia pierwszą konsolkę i program
win32api.ShellExecute(0, "open", "cmd.exe", "/K python server.py", "", win32con.SW_SHOW)

# Uruchamia drugą konsolkę i program
win32api.ShellExecute(0, "open", "cmd.exe", "/K python client.py", "", win32con.SW_SHOW)
win32api.ShellExecute(0, "open", "cmd.exe", "/K python client.py", "", win32con.SW_SHOW)
#win32api.ShellExecute(0, "open", "cmd.exe", "/K python client.py", "", win32con.SW_SHOW)