import os
import tkinter as tk
import tkinter.ttk as ttk
import pickle
from tkinter import Canvas,  Text, Button, PhotoImage,  filedialog, messagebox
import sendfile_client
from PIL import Image, ImageTk
import sys
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
def abs_path(file_name):
    try:

        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, file_name)

def listDirs(client, path):
    client.sendall(path.encode())

    data_size = int(client.recv(BUFFER_SIZE))
    if (data_size == -1):
        messagebox.showerror(message = "Click SHOW button again to watch the new directory tree!")
        return []
    client.sendall("received filesize".encode())
    data = b""
    while len(data) < data_size:
        packet = client.recv(999999)
        data += packet
    if (data == "error"):
        messagebox.showerror(message = "Cannot open this directory!")
        return []
    
    loaded_list = pickle.loads(data)
    return loaded_list

class DirectoryTree_UI(Canvas):
    def __init__(self, parent, client):
        Canvas.__init__(self, parent)
        self.client = client
        self.currPath = " "
        self.nodes = dict()
        self.filename = filedialog.askopenfilename(title="Select File",
                                              filetypes=[("All Files", "*.*")])
        self.configure(
            bg="#FFFFFF",
            height=600,
            width=600,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        image = Image.open("images/sendfile.png")
        img_resize = image.resize((600, 600))
        # Chuyển đổi hình ảnh thành đối tượng PhotoImage
        self.image_image_1 = ImageTk.PhotoImage(img_resize)
        self.place(x=0,y=0)
        self.image_1 = self.create_image(
            200,
            200,
            image=self.image_image_1
        )
        self.frame = tk.Frame(self, height=500, width=500)
        self.tree = ttk.Treeview(self.frame)
        self.frame.place(
            x=70,
            y=70.0,
            width=374,
            height=400,
        )
        ysb = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.pack(fill = tk.BOTH)
        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        self.tree.bind("<<TreeviewSelect>>", self.select_node)
        self.path = Text(self.frame, height = 1, width = 26, state = "disable")
        self.Show()
        self.button_1 = Button(self, text = 'OK', width = 15, height = 5, fg = "blue",  bg="#FFFFFF",
            borderwidth=0,
            highlightthickness=0,
            command=self.Senfile,
            relief="flat"
        )
        self.button_1.place(
            x=80.0,
            y=300.0,
            width=135.0,
            height=53.0
        )
        self.button2 = Button(self, text='EXIT', width=15, height=5,fg="blue",
    bg="#FFFFFF",
                               # image=button_image_6,
                               borderwidth=0,
                               highlightthickness=0,
                               command=lambda: self.back(),
                               relief="flat"
                               )
        self.button2.place(
            x=300.0,
            y=300.0,
            width=135.0,
            height=53.0
        )

    def insert_node(self, parent, text, abspath, isFolder):
        node = self.tree.insert(parent, 'end', text=text, open=False)
        if abspath != "" and isFolder:
            self.nodes[node] = abspath
            self.tree.insert(node, 'end')

    def open_node(self, event):
        node = self.tree.focus()
        abspath = self.nodes.pop(node, None)
        if abspath:
            self.tree.delete(self.tree.get_children(node))
            try:
                dirs = listDirs(self.client, abspath)
                for p in dirs:
                    self.insert_node(node, p[0], os.path.join(abspath, p[0]), p[1])
            except:
                messagebox.showerror(message = "Cannot open this directory!")

    def select_node(self, event):
        item = self.tree.selection()[0]
        parent = self.tree.parent(item)
        self.currPath = self.tree.item(item,"text")
        while parent:
            self.currPath = os.path.join(self.tree.item(parent)['text'], self.currPath)
            item = parent
            parent = self.tree.parent(item)

        self.path.config(state = "normal")
        self.path.delete("1.0", tk.END)
        self.path.insert(tk.END, self.currPath)
        self.path.config(state = "disable")

    def deleteTree(self):
        self.currPath = " "
        self.path.config(state = "normal")
        self.path.delete("1.0", tk.END)
        self.path.config(state = "disable")
        for i in self.tree.get_children():
            self.tree.delete(i)

    def Show(self):
        self.deleteTree()
        self.client.sendall("SHOW".encode())
        data_size = int(self.client.recv(BUFFER_SIZE))
        self.client.sendall("received filesize".encode())
        data = b""
        while len(data) < data_size:
            packet = self.client.recv(999999)
            data += packet
        loaded_list = pickle.loads(data)
        
        for path in loaded_list:
            try:
                abspath = os.path.abspath(path)
                self.insert_node('', abspath, abspath, True)
            except:
                continue
    def Senfile(self):
        self.client.sendall("SENDFILE".encode())
        isOk = self.client.recv(BUFFER_SIZE).decode()
        if (isOk == "OK"):
            if self.filename == None or self.filename == "":
                self.client.sendall("-1".encode())
                temp = self.client.recv(BUFFER_SIZE)
                return 
            destPath = self.currPath + "\\"
            filesize = os.path.getsize(self.filename)
            self.client.send(f"{self.filename}{SEPARATOR}{filesize}{SEPARATOR}{destPath}".encode())
            isReceived = self.client.recv(BUFFER_SIZE).decode()
            if (isReceived == "received filename"):
                try:
                    with open(self.filename, "rb") as f:
                        data = f.read()
                        self.client.sendall(data)
                except:
                    self.client.sendall("-1".encode())
                isReceivedContent = self.client.recv(BUFFER_SIZE).decode()
                if (isReceivedContent == "received content"):
                    messagebox.showinfo(message = "Successfully!")
                    return True
        messagebox.showerror(message = "ERROR !")
        self.frame.destroy()
        return False

    def back(self):
        self.client.sendall("QUIT".encode())
        self.destroy()
        return