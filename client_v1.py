#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import socket
import threading

# 取得伺服器 ip 及 port,
# "" 預設為 localhost
host = "".join(sys.argv[1:])
port = 9999

# KB， MB, 和 GB 的位元組個數。
kb = 1024
mb = 1048576     # 1024 x 1024
gb = 1073741824  # 1024 x 1024 x 1024


f = open("tmp.txt", "wb")
loss = -1


def get_suitable_unit(speed) -> (float, str):
    '''
    說明： 取得適當的速度顯示單位。
    speed: 未處理的速度值。
    output: 適當的速度值及速度單位。
    '''
    if speed > gb:
        speed /= gb
        suitable_unit = 'GB'
    elif speed > mb:
        speed /= mb
        suitable_unit = 'MB'
    elif speed > kb:
        speed /= kb
        suitable_unit = 'KB'
    else:
        suitable_unit = 'Bytes'

    return (speed, suitable_unit)

def calculate_speed(pre, total) -> int:
    global loss
    ''' 
    說明: 計算當前下載速度。
    pre: 前一秒，已下載的檔案大小。
    total: 目前已下載的檔案大小。
    output: 用來更新 time_counter 的 pre_size。
    '''
    speed, suitable_unit = get_suitable_unit(total - pre)

    if speed == 0.0:
        loss += 1
        
    sys.stdout.write('\rcurrent speed: %.2f %-5s' % (speed, suitable_unit))
    return total

class RepeatTimer(threading.Timer):
    def __init__(self, interval, function, args=None, kwargs=None):
        super().__init__(interval, function)
        self.pre_size = 0
        self.total_size = 0

    def run(self):
        '''
        說明： 繼承 threading.Timer 的子類別
              並覆寫 run() function，目的是
              為了讓 timer 每秒都會執行 calculate_speed。
        '''

        while not self.finished.is_set():
            self.pre_size = self.function(self.pre_size, self.total_size)
            self.finished.wait(self.interval)

try:
    '''
    說明： 創建 socket 物件，如果失敗就回報錯誤，並結束程式。
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error  as msg:
    print('Failed to create socket! Error code : ' + str(msg.errno) + ' Message ' + msg.strerror)
    sys.exit(1)
print('Create socket  successfully!')

client.connect((host, port)) # 與伺服器建立連線。

'''
說明： 創建每秒執行 calculate_speed 的 timer。
'''
time_counter = RepeatTimer(1, calculate_speed)
time_counter.start()

time_start = time.time() # 取得開始傳送的時間

while True:
    try:
        '''
        說明： 開始接受伺服器傳送的資料，如果失敗就回報錯誤，並結束程式。
        '''
        temp = client.recv(8192)
        
    except socket.error  as msg:
        print('Receiving error, Error code : ' + str(msg.errno) + ' Message ' + msg.strerror)
        time_counter.cancel()
        sys.exit(1)
        
    if len(temp) == 0:
        '''
        說明： len(temp) == 0 代表順利取完資料，
              將 timer 及 socket 關閉。
        '''
        time_counter.cancel()
        client.close()

        time_end = time.time() # 取得傳送結束的時間

        if time_end - time_start < 1:
            '''
            說明： 用來處理網速太快，不到 1 秒就結束傳送的情況。
            '''
            speed, suitable_unit = get_suitable_unit(time_counter.total_size // (time_end - time_start))
            sys.stdout.write('\rcurrent speed: %.2f %-5s' % (speed, suitable_unit))

        f.close()
        print('\nDowload complete!')
        break

    f.write(temp)
    time_counter.total_size += len(temp) # 更新目前下載的檔案大小。

print("\n--- %s:%s socket static ---"% (host, port))
speed, suitable_unit = get_suitable_unit(time_counter.total_size // (time_end - time_start))
total, total_unit = get_suitable_unit(time_counter.total_size)
print("%d %s trasmitted, %d loss, time %.4fs, avg time %.2f %s/s"% (total, total_unit, loss, time_end - time_start, speed, suitable_unit))
