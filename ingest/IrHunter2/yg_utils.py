import win32con
import win32api
import win32gui
import ctypes
import ctypes.wintypes
import threading
import time
import numpy as np
import math

IR_OFFICE_APP = "IR Office"
IR_READER_APP = "IRReader"

FLAG_CONTROL = 0x4354524c

CMD_ONOFF = 0
CMD_WORKMODE = 1

VALUE_ON = 1
VALUE_OFF = 0

WORKMODE_38K = 0
WORKMODE_WIDE = 1
WORKMODE_NOCARRIER = 2
WORKMODE_CARRIER = 3
WORKMODE_56K = 4


class IRDATA(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.c_int),
        ('sys_code', ctypes.c_ulonglong),
        ('data_code', ctypes.c_ulonglong),
        ('sys_len', ctypes.c_int),
        ('data_len', ctypes.c_int),
        ('code_time', ctypes.c_int),
        ('format', ctypes.c_char * 50),
        ('full_code', ctypes.c_char * 255),
        ('wave_len', ctypes.c_int),
        ('wave_buf', ctypes.c_uint * 2048)
    ]
PIRDATA = ctypes.POINTER(IRDATA)


class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [
        ('dwData', ctypes.wintypes.LPARAM),
        ('cbData', ctypes.wintypes.DWORD),
        ('lpData', ctypes.c_void_p)
    ]
PCOPYDATASTRUCT = ctypes.POINTER(COPYDATASTRUCT)


class StaticParam():
    key_seq = 0

    def __init__(self):
        pass


class Listener():
    hWnd = None
    input = None

    def __init__(self):
#         threading.Thread.__init__(self)
        self.data_type = None
        self.data_sys_code = None
        self.data_data_code = None
        self.data_sys_len = None
        self.data_data_len = None
        self.data_code_time = None
        self.data_format = None
        self.data_full_code = None
        self.data_wave_len = None
        self.data_wave_buf = []
        self.data_wave_freq = None

    def run(self):
        message_map = {
            win32con.WM_COPYDATA: self.OnCopyData
        }
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = message_map
        wc.lpszClassName = 'IR'
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        classAtom = win32gui.RegisterClass(wc)
#         global hWnd
        Listener.hWnd = win32gui.CreateWindow(
            classAtom,
            "IR",
            0,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            hinst,
            None
        )
        #print "listening from %d" % self.hWnd
#         t = threading.Timer(15.0, self.OnTimer)  # Quit at timer fire
#         t = threading.Timer(1, self.onFireEnter)
#         t.start()

        win32gui.PumpMessages()

#         t.cancel()

        win32gui.DestroyWindow(Listener.hWnd)
        win32gui.UnregisterClass(classAtom, hinst)

    def OnCopyData(self, hwnd, msg, wparam, lparam):
        try:
            #print "hwnd:%d, msg:%d, wparam:%d, lparam:%d" % (hwnd, msg, wparam, lparam)

            pCDS = ctypes.cast(lparam, PCOPYDATASTRUCT)
            #print "CDS->dwData:%d, CDS->cbData:%d" % (pCDS.contents.dwData, pCDS.contents.cbData)

            pIR = ctypes.cast(pCDS.contents.lpData, PIRDATA)
            self.data_type = pIR.contents.type
            self.data_sys_code = pIR.contents.sys_code
            self.data_data_code = pIR.contents.data_code
            self.data_sys_len = pIR.contents.sys_len
            self.data_data_len = pIR.contents.data_len
            self.data_code_time = pIR.contents.code_time
            self.data_format = pIR.contents.format
            self.data_full_code = pIR.contents.full_code
            self.data_wave_len = pIR.contents.wave_len
            self.decode_yg920(pIR.contents.format,
                              pIR.contents.wave_len, pIR.contents.wave_buf)
            #self.data_wave_buf = pIR.contents.wave_buf

        except Exception, e:
            print e

        #print "Exiting message pump..."
        win32gui.PostQuitMessage(0)
        return 1

    def OnTimer(self):
        print "Listener timeout..."
        win32gui.PostMessage(Listener.hWnd, win32con.WM_QUIT, 0, 0)

    def msec2pulse_np(self, freq, length, buf):
        f = freq / 10000000.0
        #print "factor: ", f
        iterable = (int(buf[x] * f) for x in range(length))
        self.data_wave_buf = np.fromiter(iterable, np.int)
        #return self.data_wave_buf

    def msec2pulse(self, freq, length, buf):
        data_wave_buf = []
        for x in range(0, length, 2):
            pair = int(float((buf[x] + buf[x+1]) * freq) / 10000000.0)
            # "on" distorted by power amplification.
            on = math.floor(float(buf[x] * freq) / 10000000.0)
            data_wave_buf.extend([on, pair - on])
        return data_wave_buf

    def decode_yg920(self, fmt, length, buf):
        # based on observation, capture might be more accurate if converted as 38k/56k.
        # fine tune to measured frequency afterward with converted pulse count.
        self.data_wave_freq = 38000
        e = fmt.find("K)")
        if e > 0:
            self.data_wave_freq = int(float(fmt[fmt.find("(")+1:e]) * 1000)
        else:
            e = fmt.find("KHz)")
            if e > 0:
                self.data_wave_freq = int(float(fmt[fmt.find("(")+1:e]) * 1000)

        self.msec2pulse_np(self.data_wave_freq, length, buf)
        self.msec2pulse(self.data_wave_freq, length, buf)


def find_window(window_name):
    try:
        return win32gui.FindWindow(None, window_name)
    except Exception, e:
        print e
        return None


def find_analyzer():
    hwnd = find_window(IR_OFFICE_APP)
    if hwnd:
        print "Using \"%s\"..." % IR_OFFICE_APP
        return hwnd

    hwnd = find_window(IR_READER_APP)
    if hwnd:
        print "Using \"%s\"..." % IR_READER_APP
        return hwnd

    #print "IR analyzer is NOT running!" % APP_NAME
    return None


def onFireEnter():
    while True:
        try:
            Listener.input = raw_input()
            if not Listener.input: 
                print "Skip it"
                win32gui.PostMessage(Listener.hWnd, win32con.WM_QUIT, 0, 0)
            elif Listener.input == 'r':
                print "record again"
                StaticParam.key_seq = StaticParam.key_seq - 1
                win32gui.PostMessage(Listener.hWnd, win32con.WM_QUIT, 0, 0)
        except Exception, e:
            print e