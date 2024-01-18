import  pickle
import os
import sendfile_server
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
BUFSIZ = 1024 * 4
SEPARATOR = "<SEPARATOR>"

def Show(sock):
    listD = []
    for c in range(ord('A'), ord('Z') + 1):
        path = chr(c) + ":\\"
        if os.path.isdir(path):
            listD.append(path)
    data = pickle.dumps(listD)
    sock.sendall(str(len(data)).encode())
    temp = sock.recv(BUFSIZ)
    sock.sendall(data)

def sendListDirs(sock):
    path = sock.recv(BUFSIZ).decode()
    if not os.path.isdir(path):
        return [False, path]

    try:
        listT = []
        listD = os.listdir(path)
        for d in listD:
            listT.append((d, os.path.isdir(path + "\\" + d)))
        
        data = pickle.dumps(listT)
        sock.sendall(str(len(data)).encode())
        temp = sock.recv(BUFSIZ)
        sock.sendall(data)
        return [True, path]
    except:
        sock.sendall("error".encode())
        return [False, "error"]    


def Sendfile(sock):
    received = sock.recv(BUFSIZ).decode()
    if (received == "-1"):
        sock.sendall("-1".encode())
        return
    filename, filesize, path = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)
    sock.sendall("received filename".encode())
    data = b""
    while len(data) < filesize:
        packet = sock.recv(999999)
        data += packet
    if (data == "-1"):
        sock.sendall("-1".encode())
        return
    try:
        with open(path + filename, "wb") as f:
            f.write(data)
        sock.sendall("received content".encode())
    except:
        sock.sendall("-1".encode())

def directory(client):
    isMod = False
    
    while True:
        if not isMod:
            mod = client.recv(BUFSIZ).decode()

        if (mod == "SHOW"):
            Show(client)
            while True:
                check = sendListDirs(client)
                if not check[0]:    
                    mod = check[1]
                    if (mod != "error"):
                        isMod = True
                        break


        elif (mod == "SENDFILE"):
            client.sendall("OK".encode())
            Sendfile(client)
            isMod = False


        elif (mod == "QUIT"):
            return
        
        else:
            client.sendall("-1".encode())