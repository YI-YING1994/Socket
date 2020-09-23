#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
import multiprocessing

"""
說明： 客戶端 ip 及 port，
      若客戶端 ip = "",
      代表任何 ip 都可以連。
"""
host = ""
port = 9999
buffer_size = 32768 #8192
accept_connect = 5

try:
    file_name = sys.argv[1]
except IndexError:
    file_name = "big_file.txt"

try:
    """
    說明： 創建 socket 物件，並設定 socket 
          位址可以重複連線，如果失敗就回報錯
          誤，並結束程式。
          P.S. socket.AF_INET 代表使用 IPV4 Protocol,
               socket.SOCK_STREAM 代表使用 TCP 封包。
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except socket.error as msg:
    print("Failed to create socket! Error code: " + str(msg.errno) + " Error message " + msg.strerror)
    sys.exit(1)
print("Create socket successfully!")

try:
    """
    說明： 綁定客戶端位址，如果失敗就回報錯誤，並結束程式。
    """
    server.bind((host, port))
except socket.error as msg:
    print("Binding failed! Error code: " + str(msg.errno) + " Error message " + msg.strerror)
    sys.exit(1)
print("Binding socket complete!")

server.listen(accept_connect) # 開始聆聽是否有客戶端請求連線，同一時間最多接受 5 個客戶端連線。
print("Socket now listening!")

"""
說明： 與客戶端建立連線。
connect: 用來與客戶端傳送資料的 socket 物件。
addr: 客戶端的 ip 及 port。
"""
current_connet = []
def ReceiveData(connect):
    try:
        file_descriptor_data = open(file_name, "rb")
        """
        說明： 開啟檔案，如果成功，立即開始傳送資料。
        """
        print("Start sending...")
        while True:
            data = file_descriptor_data.read(buffer_size)
            connect.sendall(data)
            if len(data) == 0:
                break
        """
        說明： 傳送完畢，將伺服器與連線中的 socket 關閉。
        """
        print("Finished\n")
    except IOError as e:
        print("\n", e)
    finally:
        connect.close()
        file_descriptor_data.close()
    
    print("Waiting for new connection...")

while True:
    try:
        connect, addr = server.accept()
        print("\nConnected socket with " + addr[0] + ":" + str(addr[1]))

        p = multiprocessing.Process(target=ReceiveData,args=(connect,),)
        p.start()
        current_connet.append(p)
    except KeyboardInterrupt:
        for p in current_connet:
            p.terminate()
        print("Server closed")
        break
server.close()   
    
    
