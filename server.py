import tkinter
import struct
import socket
from PIL import ImageGrab
import cv2
import numpy as np
import threading
import time
import pyautogui as ag
import mouse
import keyboard
from PIL import Image, ImageTk
from tkinter import font
# 画面周期
IDLE = 0.05
# 鼠标滚轮灵敏度
SCROLL_NUM = 50
# 压缩比 1-100 数值越小，压缩比越高，图片质量损失越严重
IMQUALITY = 100
# 压缩后np图像
img = None
# 编码后的图像
imbyt = None

bufsize = 4096

official_virtual_keys = {
    0x08: 'backspace',
    0x09: 'tab',
    0x0c: 'clear',
    0x0d: 'enter',
    0x10: 'shift',
    0x11: 'ctrl',
    0x12: 'alt',
    0x13: 'pause',
    0x14: 'caps lock',
    0x15: 'ime kana mode',
    0x15: 'ime hanguel mode',
    0x15: 'ime hangul mode',
    0x17: 'ime junja mode',
    0x18: 'ime final mode',
    0x19: 'ime hanja mode',
    0x19: 'ime kanji mode',
    0x1b: 'esc',
    0x1c: 'ime convert',
    0x1d: 'ime nonconvert',
    0x1e: 'ime accept',
    0x1f: 'ime mode change request',
    0x20: 'spacebar',
    0x21: 'page up',
    0x22: 'page down',
    0x23: 'end',
    0x24: 'home',
    0x25: 'left',
    0x26: 'up',
    0x27: 'right',
    0x28: 'down',
    0x29: 'select',
    0x2a: 'print',
    0x2b: 'execute',
    0x2c: 'print screen',
    0x2d: 'insert',
    0x2e: 'delete',
    0x2f: 'help',
    0x30: '0',
    0x31: '1',
    0x32: '2',
    0x33: '3',
    0x34: '4',
    0x35: '5',
    0x36: '6',
    0x37: '7',
    0x38: '8',
    0x39: '9',
    0x41: 'a',
    0x42: 'b',
    0x43: 'c',
    0x44: 'd',
    0x45: 'e',
    0x46: 'f',
    0x47: 'g',
    0x48: 'h',
    0x49: 'i',
    0x4a: 'j',
    0x4b: 'k',
    0x4c: 'l',
    0x4d: 'm',
    0x4e: 'n',
    0x4f: 'o',
    0x50: 'p',
    0x51: 'q',
    0x52: 'r',
    0x53: 's',
    0x54: 't',
    0x55: 'u',
    0x56: 'v',
    0x57: 'w',
    0x58: 'x',
    0x59: 'y',
    0x5a: 'z',
    0x5b: 'left windows',
    0x5c: 'right windows',
    0x5d: 'applications',
    0x5f: 'sleep',
    0x60: '0',
    0x61: '1',
    0x62: '2',
    0x63: '3',
    0x64: '4',
    0x65: '5',
    0x66: '6',
    0x67: '7',
    0x68: '8',
    0x69: '9',
    0x6a: '*',
    0x6b: '=',
    0x6c: 'separator',
    0x6d: '-',
    0x6e: 'decimal',
    0x6f: '/',
    0x70: 'f1',
    0x71: 'f2',
    0x72: 'f3',
    0x73: 'f4',
    0x74: 'f5',
    0x75: 'f6',
    0x76: 'f7',
    0x77: 'f8',
    0x78: 'f9',
    0x79: 'f10',
    0x7a: 'f11',
    0x7b: 'f12',
    0x7c: 'f13',
    0x7d: 'f14',
    0x7e: 'f15',
    0x7f: 'f16',
    0x80: 'f17',
    0x81: 'f18',
    0x82: 'f19',
    0x83: 'f20',
    0x84: 'f21',
    0x85: 'f22',
    0x86: 'f23',
    0x87: 'f24',
    0x90: 'num lock',
    0x91: 'scroll lock',
    0xa0: 'left shift',
    0xa1: 'right shift',
    0xa2: 'left ctrl',
    0xa3: 'right ctrl',
    0xa4: 'left menu',
    0xa5: 'right menu',
    0xa6: 'browser back',
    0xa7: 'browser forward',
    0xa8: 'browser refresh',
    0xa9: 'browser stop',
    0xaa: 'browser search key',
    0xab: 'browser favorites',
    0xac: 'browser start and home',
    0xad: 'volume mute',
    0xae: 'volume down',
    0xaf: 'volume up',
    0xb0: 'next track',
    0xb1: 'previous track',
    0xb2: 'stop media',
    0xb3: 'play/pause media',
    0xb4: 'start mail',
    0xb5: 'select media',
    0xb6: 'start application 1',
    0xb7: 'start application 2',
    0xbb: '+',
    0xbc: ',',
    0xbd: '-',
    0xbe: '.',
    0xe5: 'ime process',
    0xf6: 'attn',
    0xf7: 'crsel',
    0xf8: 'exsel',
    0xf9: 'erase eof',
    0xfa: 'play',
    0xfb: 'zoom',
    0xfc: 'reserved ',
    0xfd: 'pa1',
    0xfe: 'clear',
    0xba: ';',
    0xde: '\'',
    0xdb: '[',
    0xdd: ']',
    0xbf: '/',
    0xc0: '`',
    0xdc: '\\',
}

def recvall(sock):
    data = b''
    while True:
        while True:
            try:
                part = sock.recv(bufsize)
                data += part
                if len(part) < bufsize:
                    break
            except socket.error:
                return 
        if data:
            break
    return data.decode().strip()

class STARTPAGE(tkinter.Frame):
    def __init__(self,parrent,Appcontroller):
        tkinter.Frame.__init__(self,parrent)
        bold_font = font.Font(weight="bold",size=20)
        self.configure(bg="black")
        name_label=tkinter.Label(self,text='SERVER',font=bold_font,fg="red",highlightbackground="black",bg="black")
        name_label.pack(pady=5)

        #button_log=tkinter.Button(self,text="Login",command=lambda: Appcontroller.showPage(HomePage))
       # button_log.configure(width=10)

        original_image = Image.open("images/ic_open.png")
        resized_image = original_image.resize((100, 100),  Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.NEAREST)
        self.photo = ImageTk.PhotoImage(resized_image)
        self.open_button = tkinter.Button(self, image=self.photo, command=lambda: Appcontroller.showPage(HomePage),bg="red",fg="red")
        self.open_button.pack(pady=50)

class HomePage(tkinter.Frame):
    def __init__(self,parrent,Appcontroller):
        tkinter.Frame.__init__(self,parrent)
        self.remote_ip = socket.gethostbyname(socket.gethostname())
        #self.remote_ip = '172.172.6.253'
        #self.remote_ip='127.0.0.1'
        self.remote_port = 80
        self.configure(bg="black")
        val1=tkinter.StringVar()
        val2=tkinter.StringVar()
        bold_font = font.Font(weight="bold",size=24)
        host_font = font.Font(weight="bold",size=14)
        enter_host=tkinter.Frame(self)
        nav=tkinter.Frame(self)
        ip_label = tkinter.Label(enter_host, text="IP",fg="red",font=host_font,highlightbackground="black",bg="black")
        ip_entry = tkinter.Entry(enter_host, show=None, font=('Arial', 20), textvariable=val1,width=10,justify="center",bd=3,fg="red",bg="black")# Gia trị nhập vào được lưu vào biến val
        port_label = tkinter.Label(enter_host, text="PORT",fg="red",highlightbackground="black",bg="black",font=host_font)
        port_entry = tkinter.Entry(enter_host, show=None, font=('Arial', 20), textvariable=val2,width=10,justify="center",bd=3,fg="red",bg="black")# Gia trị nhập vào được lưu vào biến val
        button_in=tkinter.Button(nav,text="CONNECTION",command=lambda: Appcontroller.buttonServer_click(),bg="black",fg="red")
        button_out=tkinter.Button(nav,text="DISCONNECTION",command=lambda: Appcontroller.showPage(STARTPAGE),bg="black",fg="red")
        #print(str(self.remote_ip))
        val1.set(self.remote_ip)
        val2.set(self.remote_port)
        enter_host.pack(pady=40)
        enter_host.configure(bg="black")
        ip_label.grid(row=0, column=0, padx=10, pady=4, ipadx=0, ipady=0)
        ip_entry.grid(row=0, column=1, padx=10, pady=4, ipadx=40, ipady=0)

        port_label.grid(row=1, column=0, padx=10, pady=4, ipadx=0, ipady=0)
        port_entry.grid(row=1, column=1, padx=10, pady=4, ipadx=40, ipady=0)
        nav.configure(bg="black")
        nav.pack()
        button_in.grid(row=0, column=0, padx=10, pady=4, ipadx=10, ipady=10)
        button_out.grid(row=0, column=1, padx=10, pady=4, ipadx=10, ipady=10)
        #Appcontroller.buttonServer_click()

class RemoteDesktop:
    def __init__(self, root):
        self.server = None
        self.remote_ip = socket.gethostbyname(socket.gethostname())
        #self.remote_ip = '172.172.6.253'
        #self.remote_ip='127.0.0.1'
        self.remote_port = 80
        self.conn = None
        self.addr = None
        self.lock = threading.Lock()
        
        self.root = root
        self.root.geometry('400x300')
        self.root.title("SERVER REMOTE DESKTOP")
        self.root.resizable(height=False,width=False)

        container=tkinter.Frame()

        container.pack(side="top",fill="both",expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        self.frames={}
        for F in(STARTPAGE,HomePage):
            frame=F(container,self)
            frame.grid(row=0,column=0,sticky="nsew")
            self.frames[F]=frame

        self.frames[STARTPAGE].tkraise()
    def showPage(self,FrameClass):
        self.frames[FrameClass].tkraise()
        #open_button = tkinter.Button(fstart, text="OPEN", command = self.buttonServer_click)
        #close_button = tkinter.Button(fhost, text="CLOSE", command = self.buttonServer_click)
        #self.open_button.pack(pady=50)
        
    def buttonServer_click(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.remote_ip, self.remote_port))
        self.server.listen(5)
        try:
            self.conn, self.addr = self.server.accept()
            print("[SERVER] CONNECTED")
            str = ""
            while True:
                str = recvall(self.conn)
                if (str == "LIVE SCREEN"):
                    while True:
                        self.conn, self.addr = self.server.accept()
                        self.sendscreen_thread = threading.Thread(target=self.handle, args=(self.conn,))
                        self.detect_mouse_key_thread =threading.Thread(target=self.control, args=(self.conn,))
                        self.sendscreen_thread.start() 
                        self.detect_mouse_key_thread.start()
                elif (str == "QUIT"):
                    self.conn.close()
                    self.server.close()
                    break
                else: 
                    continue
        except socket.error:
            self.conn.close()
            self.server.close()

    def handle(self, conn):
        global img, imbyt
        self.lock.acquire()
        if imbyt is None:
            imorg = np.asarray(ImageGrab.grab())
            _, imbyt = cv2.imencode(".jpg", imorg, [cv2.IMWRITE_JPEG_QUALITY, IMQUALITY])
            imnp = np.asarray(imbyt, np.uint8)
            img = cv2.imdecode(imnp, cv2.IMREAD_COLOR)
        self.lock.release()
        lenb = struct.pack(">BI", 1, len(imbyt))
        conn.sendall(lenb)
        conn.sendall(imbyt)
        while True:
            # fix for linux
            time.sleep(IDLE)
            gb = ImageGrab.grab()
            imgnpn = np.asarray(gb)
            _, timbyt = cv2.imencode(".jpg", imgnpn, [cv2.IMWRITE_JPEG_QUALITY, IMQUALITY])
            imnp = np.asarray(timbyt, np.uint8)
            imgnew = cv2.imdecode(imnp, cv2.IMREAD_COLOR)
            # 计算图像差值
            imgs = imgnew ^ img
            if (imgs != 0).any():
                # 画质改变
                pass
            else:
                continue
            imbyt = timbyt
            img = imgnew
            # 无损压缩
            _, imb = cv2.imencode(".png", imgs)
            l1 = len(imbyt)  # 原图像大小
            l2 = len(imb)  # 差异图像大小
            if l1 > l2:
                # 传差异化图像
                lenb = struct.pack(">BI", 0, l2)
                conn.sendall(lenb)
                conn.sendall(imb)
            else:
                # 传原编码图像
                lenb = struct.pack(">BI", 1, l1)
                conn.sendall(lenb)
                conn.sendall(imbyt)

    def control(self, conn):
        def Op(key, op, ox, oy):
            print(key, op, ox, oy)
            if key == 4:
                mouse.move(ox, oy)
            elif key == 1:
                if op == 100:
                    ag.mouseDown(button=ag.LEFT)
                elif op == 117:
                    ag.mouseUp(button=ag.LEFT)
            elif key == 2:
                if op == 0:
                    ag.scroll(-SCROLL_NUM)
                else:
                    ag.scroll(SCROLL_NUM)
            elif key == 3:
                if op == 100:
                    ag.mouseDown(button=ag.RIGHT)
                elif op == 117:
                    ag.mouseUp(button=ag.RIGHT)
            else:
                k = official_virtual_keys.get(key)
                if k is not None:
                    if op == 100:
                        keyboard.press(k)
                    elif op == 117:
                        keyboard.release(k)
        try:
            base_len = 6
            while True:
                cmd = b''
                rest = base_len - 0
                while rest > 0:
                    cmd += conn.recv(rest)
                    rest -= len(cmd)
                key = cmd[0]
                op = cmd[1]
                x = struct.unpack('>H', cmd[2:4])[0]
                y = struct.unpack('>H', cmd[4:6])[0]
                Op(key, op, x, y)
        except:
            return
try:
    root = tkinter.Tk()
    App = RemoteDesktop(root)
    root.mainloop()

except:
    print("Error")
