#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import threading

host = "localhost" # 伺服器預設 ip
port = 9999 # 伺服器預設 port
buffer_size = 32768 # 限制一次可傳送的資料量
loss = -1 # 斷線次數初始值
program_name = os.path.basename(__file__) # 程式名稱
# file_descriptor_data = open("tmp.txt", "wb") # 用以操作檔案的物件

# KB， MB, 和 GB 的位元組個數。
kb = 1024.0
mb = 1048576.0     # 1024 x 1024
gb = 1073741824.0  # 1024 x 1024 x 1024

def CheckArgv():
    """
    說明：檢查使用者輸入在指令後的參數是否符合要求。
    """
    global host, program_name

    os.chdir(os.path.dirname(__file__))

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        print("Sorry, we couldn't understand what you want to do.")
        print("Usage: ./{0} or ./{0} ip".format(program_name))
        input("Press enter to exit...")
        sys.exit(1)
    print(f"Use 「{host}」 as server ip...")

def CreateSocketAndConnectWithServer():
    """
    說明： 創建 socket 物件並嘗試與伺服器建立連線。
    """

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 創建 socket 物件
    except socket.error  as msg:
        print("Failed to create socket! Error code :", str(msg.errno), "Message", msg.strerror)
        input("Press enter to exit...")
        sys.exit(1)
    print("Create socket  successfully!")

    try:
        client.connect((host, port)) # 嘗試與伺服器建立連線
    except socket.error  as msg:
        print("Failed to connect server! Error code :", str(msg.errno), "Message", msg.strerror)
        input("Press enter to exit...")
        sys.exit(1)
    print("Connect server  successfully!")
    
    return client

def GetSuitableUnit(speed) -> (float, str):
    """
    說明： 取得適當的速度顯示單位。
    speed: 未處理的速度值。
    output: 適當的速度值及速度單位。
    """
    if speed > gb:
        speed /= gb
        suitable_unit = "GB"
    elif speed > mb:
        speed /= mb
        suitable_unit = "MB"
    elif speed > kb:
        speed /= kb
        suitable_unit = "KB"
    else:
        suitable_unit = "Bytes"

    return (speed, suitable_unit)

def CalculateSpeed(size):
    """ 
    說明:計算瞬時速度。
    size:間隔內已接受的檔案大小。
    """
    global loss

    speed, suitable_unit = GetSuitableUnit(size)
    if speed == 0.0:
        loss += 1
        
    sys.stdout.write(f"\rcurrent speed: {speed:.2f} {suitable_unit:<5}")

class RepeatTimer(threading.Timer):
    """
    說明：繼承 threading.Timer 的子類別
         並覆寫 run() function，目的是
         為了讓 timer 每秒都會執行 CalculateSpeed。
    """
    def __init__(self, interval, function, args=None, kwargs=None):
        super().__init__(interval, function)
        self.pre_size = 0.0
        self.total_size = 0.0

    def run(self):
        while not self.finished.is_set():
            self.function(self.total_size - self.pre_size) # 計算瞬時速度
            self.pre_size = self.total_size # 將目前接收到的檔案大小暫存
            self.finished.wait(self.interval)

    def printLastSpeed(self):
        self.function(self.total_size - self.pre_size) # 計算瞬時速度

def StartReciveData(client):
    global buffer_size
    # global file_descriptor_data

    while True:
        try:
            """
            說明： 開始接受伺服器傳送的資料，如果失敗就回報錯誤，並結束程式。
            """
            temp = client.recv(buffer_size)            
        except socket.error  as msg:
            print("Receiving error, Error code :", str(msg.errno), "Message", msg.strerror)
            break
        except KeyboardInterrupt:
            time_counter.printLastSpeed()
            print("\nClient closed")
            break
            
        if len(temp) == 0:
            """
            說明：len(temp) == 0 代表順利取完資料，
                 用 break 跳出迴圈。
            """
            time_counter.printLastSpeed()
            
            print("\nDowload complete!")
            break

        # file_descriptor_data.write(temp)
        time_counter.total_size += len(temp) # 更新目前下載的檔案大小。

def PrintStatistical(time_start, time_end):
    global host, port

    total, total_unit = GetSuitableUnit(time_counter.total_size)

    print(f"\n--- {host}:{port} socket static ---")
    print(f"{int(total):d} {total_unit} trasmitted, {loss:d} loss, time {time_end - time_start:.4f}s, ", end="") 
    
    try:
        avg_speed, avg_unit = GetSuitableUnit(time_counter.total_size / (time_end - time_start))
        print(f"avg speed {avg_speed:.2f} {avg_unit}/s")
    except ZeroDivisionError:
        print(f"avg speed infinite")

if __name__ == "__main__":
    CheckArgv()
    client =  CreateSocketAndConnectWithServer()

    time_counter = RepeatTimer(1, CalculateSpeed) # 創建每秒執行 CalculateSpeed 的 timer。
    time_counter.start() # 啟動 timer
    
    time_start = time.time() # 取得開始傳送的時間
    StartReciveData(client)
    time_end = time.time() # 取得傳送結束的時間

    # file_descriptor_data.close()
    time_counter.cancel()
    client.close()

    PrintStatistical(time_start, time_end)