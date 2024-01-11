import tkinter
import tkinter.messagebox
import tkinter as tk
from tkinter import *
from tkinter import font
from tkinter import filedialog
import struct
import socket
import numpy as np
from PIL import Image, ImageTk
import threading
import re
import cv2
import time
import sys

# Khung thời gian
IDLE = 0.05
# Kích thước thu phóng
#scale = 0.75
# Mặc định cho màn 1920x1080
scale=0.6
# Kích thước màn hình truyền dẫn gốc
fixw, fixh = 0, 0
# socket  kích thước bộ đệm
bufsize = 1024

check = False

image_save = None

class STARTPAGE(tk.Frame):
    def __init__(self,parent,Appcontroller):
        tk.Frame.__init__(self,parent)
        image=Image.open("images/background.jpg")
        img_resize=image.resize((500,400))
        # Chuyển đổi hình ảnh thành đối tượng PhotoImage
        self.background_image = ImageTk.PhotoImage(img_resize)

        # Tạo một Label với hình ảnh làm nền
        background_label = tk.Label(self, image=self.background_image)
        background_label.place(relwidth=1, relheight=1)

        val1=tk.StringVar()
        val2=tk.StringVar()
        bold_font = font.Font(weight="bold",size=24)
        host_font = font.Font(weight="bold",size=14)
        name_label=tk.Label(self,text='REMOTE DESKTOP',font=bold_font,fg="red",highlightbackground="black",bg="black")

        enter_host=tk.Frame(self)
        nav=tk.Frame(self)

        ip_label = tk.Label(enter_host, text="IP",fg="red",font=host_font,highlightbackground="black",bg="black")
        Appcontroller.ip_entry = tk.Entry(enter_host, show=None, font=('Arial', 20), textvariable=val1,width=10,justify="center",bd=3,fg="red",bg="black")# Gia trị nhập vào được lưu vào biến val
        port_label = tk.Label(enter_host, text="PORT",fg="red",highlightbackground="black",bg="black",font=host_font)
        Appcontroller.port_entry = tk.Entry(enter_host, show=None, font=('Arial', 20), textvariable=val2,width=10,justify="center",bd=3,fg="red",bg="black")# Gia trị nhập vào được lưu vào biến val
        about_btn = tk.Button(nav,text="About",command=lambda: Appcontroller.showPage(About),bg="black",fg="red")
        connect_btn = tk.Button(nav, text="Connection",command= Appcontroller.SetSocket,bg="black",fg="red")
        livescreen_btn = tk.Button(nav, text="Live Screen",command= Appcontroller.LiveScreen,bg="black",fg="red")
        quit_btn = tkinter.Button(nav, text = "Quit", command = Appcontroller.Quit ,bg="black",fg="red")
        name_label.pack(side="top",pady=20)
        enter_host.pack(pady=70)

        ip_label.grid(row=0, column=0, padx=10, pady=4, ipadx=0, ipady=0)
        Appcontroller.ip_entry.grid(row=0, column=1, padx=10, pady=4, ipadx=0, ipady=0)

        port_label.grid(row=1, column=0, padx=10, pady=4, ipadx=0, ipady=0)
        Appcontroller.port_entry.grid(row=1, column=1, padx=10, pady=4, ipadx=0, ipady=0)

        enter_host.configure(bg="black")


        val1.set('127.0.0.1')
        val2.set('80')

        nav.pack()
        about_btn.grid(row=0,column=0,padx=10, pady=0, ipadx=30, ipady=5)
        connect_btn.grid(row=0, column=1, padx=10, pady=0, ipadx=20, ipady=5)
        livescreen_btn.grid(row=0, column=2, padx=10, pady=0, ipadx=20, ipady=5)
        quit_btn.grid(row=0, column=4,padx=10, pady=0, ipadx=20, ipady=5)
        nav.configure(bg="black")

class About(tk.Frame):
    def __init__(self,parent,Appcontroller):
        tk.Frame.__init__(self,parent)
        bold_font = font.Font(weight="bold",size=14)

        name_label=tk.Label(self,text='22CTT2 - HCMUS',font=bold_font)


        lable_member1=tk.Label(self,text='22120053 - Lê Thành Đạt',font=('Arial',12))
        lable_member2=tk.Label(self,text='22120065 - Trần Đại Đồng',font=('Arial',12))
        lable_member3=tk.Label(self,text='22120078 - Nguyễn Bá Duy',font=('Arial',12))
        lable_member4=tk.Label(self,text='22120058 - Nguyễn Thành Đạt',font=('Arial',12))
        lable_member5=tk.Label(self,text='22120086 - Nguyễn Công Giáp',font=('Arial',12))
        image1=Image.open("images/logo_khtn.png")
        image2=Image.open("images/hoamai.png")
        img_resize1=image1.resize((170,170))
        img_resize2=image2.resize((150,100))
        self.img1 = ImageTk.PhotoImage(img_resize1)
        self.img2 = ImageTk.PhotoImage(img_resize2)

        self.panel1 = tk.Label(self, image = self.img1)
        #self.panel1.place(x=250,y=150)
        self.panel1.pack(side="top")
        self.panel2 = tk.Label(self, image = self.img2)
        self.panel2.place(x=350, y=0)
        #self.panel2.pack()
        name_label.pack(pady=5)
        lable_member1.pack()
        lable_member2.pack()
        lable_member3.pack()
        lable_member4.pack()
        lable_member5.pack()
        #self.panel.pack()

        button_out=tk.Button(self,text=" EXIT ",command=lambda: Appcontroller.showPage(STARTPAGE))
        button_out.pack(pady=20)

class RemoteDesktop(object): # Ứng dụng này kế thừa cái tk.Tk (tkinter)
    def __init__(self,root): # Mặc định tham số của hàm trong class là self
        #tk.Tk.__init__(self)
        self.client = None
        self.livescreen = None
        self.livescreen_thread = None
        self.showscreen = None
        self.showscreen_thread = None
        self.last_send = time.time()
        self.ip_entry=tk.Entry()
        self.port_entry=tk.Entry()

        self.root=root
        self.root.title('Remote desktop')
        self.root.iconbitmap('images/icon.ico')
        self.root.geometry('500x400')
        self.root.resizable(height=False,width=False)

        container=tk.Frame()
        container.configure(bg="red")

        container.pack(side="top",fill="both",expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        self.frames={}
        for F in(STARTPAGE,About):
            frame=F(container,self)
            frame.grid(row=0,column=0,sticky="nsew")
            self.frames[F]=frame

        self.frames[STARTPAGE].tkraise()
    def showPage(self,FrameClass):
        self.frames[FrameClass].tkraise()

    def SetSocket(self):
        global check
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = self.ip_entry.get()
        remote_port = self.port_entry.get()
        try:
            self.client.connect((remote_ip, int(remote_port)))
            check = True
        except Exception:
            tkinter.messagebox.showerror("Error", "Chưa kết nối đến server")
            return False
        if (check == True):
            tkinter.messagebox.showinfo("Info", "Kết nối đến server thành công")
            return True

    def LiveScreen(self):
        global check
        if (not check):
            tkinter.messagebox.showerror("Error", "Chưa kết nối đến server")
            return 
        self.client.sendall(bytes("LIVE SCREEN", "utf8"))
        self.DoLiveScreen()

    def DoLiveScreen(self):
        if self.livescreen is None:
            self.livescreen = tk.Toplevel(self.root)
            self.livescreen.title("Live Screen")
            self.livescreen.resizable(height=False,width=False)
            self.livescreen_thread = threading.Thread(target=self.RunLiveScreen)
            self.livescreen_thread.start()
            img = Image.open("images/screen.png")
            img_resize = img.resize((1200, 780), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.NEAREST)
            self.bg = ImageTk.PhotoImage(img_resize)
            self.bgImage = tk.Label(self.livescreen, image=self.bg, highlightthickness=0, borderwidth=0).grid(column=0, row=0, sticky=tk.S+tk.N+tk.W+tk.E)  
            save_button = tk.Button(self.livescreen, text=" Screenshot ", command=self.SaveImage,bg="black",fg="red")
            exit_button = tk.Button(self.livescreen, text=" Exit ", command=self.Exit,bg="black",fg="red")
            save_button.place(x=190,y=736)
            exit_button.place(x=980,y=736)
        else:
            self.client.close()
    
    def RunLiveScreen(self):
        global fixh, fixw, scale, image_save
        self.Reconnect()
        # Gửi thông tin nền tảng
        lenb = self.client.recv(5)
        imtype, le = struct.unpack(">BI", lenb)
        imb = b''   #Tạo một biến byte rỗng
        while le > bufsize:
            t = self.client.recv(bufsize)
            imb += t
            le -= len(t)
        while le > 0:
            t = self.client.recv(le)
            imb += t
            le -= len(t)
        data = np.frombuffer(imb, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        h, w, _ = img.shape
        if w==1366:
            scale=0.84
        h = int(h * scale)
        w = int(w * scale)
        #h, w = 639, 1136

        #img = cv2.resize(img, (w, h))
        imsh = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA) 
        imi = Image.fromarray(imsh)
        imgTK = ImageTk.PhotoImage(image=imi) 
        canvas = tk.Canvas(self.livescreen, width=w, height=h, bg="white")
        
        canvas.focus_set()
        self.BindEvents(canvas)
        
        canvas.place(x=30, y=40)
        canvas.create_image(0, 0, anchor=NW, image=imgTK)
        #canvas.configure(image=self.imgTk)
        #canvas.photo = imgTK
        #h = int(h * scale)
        #w = int(w * scale)

        while True:
            try:
                lenb = self.client.recv(5)
                imtype, le = struct.unpack(">BI", lenb)
                imb = b''
                while le > bufsize:
                    t = self.client.recv(bufsize)
                    imb += t
                    le -= len(t)
                while le > 0:
                    t = self.client.recv(le)
                    imb += t
                    le -= len(t)
                data = np.frombuffer(imb, dtype=np.uint8)
                ims = cv2.imdecode(data, cv2.IMREAD_COLOR)
                if imtype == 1:
                    img = ims
                else:
                    img = img ^ ims
                imt = cv2.resize(img, (w, h))
                imsh = cv2.cvtColor(imt, cv2.COLOR_RGB2RGBA)
                imi = Image.fromarray(imsh)
                #canvas.configure(image=self.imgTk)
                imgTK.paste(imi)
                image_save = imsh
                #canvas.photo=imi

            except:
                self.livescreen = None
                self.DoLiveScreen()
                return

    def BindEvents(self, canvas):
        def EventDo(data):
            self.client.sendall(data)

        def LeftDown(e):
            return EventDo(struct.pack('>BBHH', 1, 100, int(e.x/scale), int(e.y/scale)))

        def LeftUp(e):
            return EventDo(struct.pack('>BBHH', 1, 117, int(e.x/scale), int(e.y/scale)))
        canvas.bind(sequence="<1>", func=LeftDown)
        canvas.bind(sequence="<ButtonRelease-1>", func=LeftUp)

        def RightDown(e):
            return EventDo(struct.pack('>BBHH', 3, 100, int(e.x/scale), int(e.y/scale)))

        def RightUp(e):
            return EventDo(struct.pack('>BBHH', 3, 117, int(e.x/scale), int(e.y/scale)))
        canvas.bind(sequence="<3>", func=RightDown)
        canvas.bind(sequence="<ButtonRelease-3>", func=RightUp)

        def Wheel(e):
            if e.delta < 0:
                return EventDo(struct.pack('>BBHH', 2, 0, int(e.x/scale), int(e.y/scale)))
            else:
                return EventDo(struct.pack('>BBHH', 2, 1, int(e.x/scale), int(e.y/scale)))
        canvas.bind(sequence="<MouseWheel>", func=Wheel)

        def Move(e):
            cu = time.time()
            if cu - self.last_send > IDLE:
                self.last_send = cu
                return EventDo(struct.pack('>BBHH', 4, 0, int(e.x/scale), int(e.y/scale)))
        canvas.bind(sequence="<Motion>", func=Move)

        def KeyDown(e):
            return EventDo(struct.pack('>BBHH', e.keycode, 100, 0, 0))

        def KeyUp(e):
            return EventDo(struct.pack('>BBHH', e.keycode, 117, 0, 0))
        canvas.bind(sequence="<KeyPress>", func=KeyDown)
        canvas.bind(sequence="<KeyRelease>", func=KeyUp)

    def SaveImage(self):
        global image_save
        filename = filedialog.asksaveasfile( mode = 'wb',
                                        defaultextension="*.jgp",
                                        filetypes=[
                                            ("PNG file","*.png"),
                                            ("JPQ file", "*.jpg"),
                                            ("All files", "*.*"),
                                        ])
        if filename is None:
            return
        cv2.imwrite(filename.name, cv2.cvtColor(image_save, cv2.COLOR_RGBA2BGRA))
        print("Image saved as", filename.name)
    def Exit(self):
        self.livescreen.destroy()
    def Reconnect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = self.ip_entry.get()
        remote_port = self.port_entry.get()
        self.client.connect((remote_ip, int(remote_port)))

    def Quit(self):
        global check
        if (check):
            self.client.sendall(bytes("QUIT", "utf8"))
            self.client.close()
        self.root.destroy()
        return

try:
    root = tkinter.Tk()
    App = RemoteDesktop(root)
    root.mainloop()
except:
    print("Error")
