#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import threading

host = "" # 客戶端 ip，若客戶端 ip = ""，代表任何 ip 都可以連。
port = 9999 # 客戶端 port
buffer_size = 32768 # 一次可傳送的資料量
accept_connect = 5 # 允許連接的客戶端個數
file_name = "big_file.txt" # 預設用來傳送的檔案
program_name = os.path.basename(__file__) # 程式名稱
program_finished = False # 程式是否結束

def CheckArgv():
    """
    說明：檢查使用者輸入在指令後的參數是否符合要求。
    """
    global file_name, program_name, program_finished

    if len(sys.argv) == 1:
        print(f"Use default file 「{file_name}」 to test download speed...")
    elif len(sys.argv) == 2:
        file_name = sys.argv[1]
        print(f"Use file 「{file_name}」 to test download speed")
    else:
        print("Sorry, we couldn't understand what you want to do.")
        print("Usage: ./{0} or ./{0} {1}".format(program_name, file_name))
        program_finished = True
        return

    os.chdir(os.path.dirname(__file__))
    if not os.path.isfile(file_name):
        print("「{0}」 not exist, please put 「{0}」 and {1} at the same directory.".format(file_name, program_name))
        program_finished = True

def CreateSocket():
    global accept_connect, program_finished

    if program_finished: return
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
        program_finished = True
        return
    print("Create socket successfully!")

    try:
        """
        說明： 綁定客戶端位址，如果失敗就回報錯誤，並結束程式。
        """
        server.bind((host, port))
    except socket.error as msg:
        print("Binding failed! Error code: " + str(msg.errno) + " Error message " + msg.strerror)
        program_finished = True
        return
    print("Binding socket complete!")

    server.listen(accept_connect) # 開始聆聽是否有客戶端請求連線，同一時間最多接受 accept_connect 個客戶端連線。
    print("Socket now listening!")

    return server

def StartConnection(connect):
    try:
        """
        說明： 開啟檔案，如果成功，立即開始傳送資料，
              失敗或傳送完畢，將與伺服器連線中的 socket 關閉。
        """
        file_descriptor_data = open(file_name, "rb")
        print("Start sending...")
        while True:
            data = file_descriptor_data.read(buffer_size)
            connect.sendall(data)
            if len(data) == 0:
                break
        print("Finished\n")
    except IOError as e:
        print("\n", e)
    finally:
        connect.close()
        file_descriptor_data.close()
    
    print("Waiting for new connection...")


def WaitForConnection(server):
    global program_finished

    if program_finished: return
    while not program_finished:
        try:
            """
            說明： 與客戶端建立連線。
                    connect: 用來與客戶端傳送資料的 socket 物件。
                    addr: 客戶端的 ip 及 port。
            """
            connect, addr = server.accept()
            print("\nConnected socket with " + addr[0] + ":" + str(addr[1]))
            threading.Thread(target=StartConnection, args=(connect,), daemon=True).start()
        except Exception as e:
            print(e)
    server.close()

def GetUserInput():
    global program_finished

    while not program_finished:
        user_input = input("")
        if (user_input == "quit()"):
            program_finished = True
        else:
            print("Use quit() to exit")

if __name__ == "__main__":
    CheckArgv()
    server = CreateSocket()

    threading.Thread(target=WaitForConnection, args=(server,), daemon=True).start()
    threading.Thread(target=GetUserInput, daemon=True).start()

    while True:
        if program_finished:
            print("Server closed...")
            break
        time.sleep(0.2)
    input("Press enter to exit...")