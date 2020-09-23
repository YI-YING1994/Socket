#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import socket
import threading

host = "localhost"
port = 9999

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    print('Failed to create socket. Error code: ' + str(msg.errno) + ' Message ' + msg.strerror)
    sys.exit(1)
print('Create socket successfully!')

client.connect((host, port))

data_sum = 0

while True:    
    try:
        time_begin = time.time()
        temp = client.recv(4096)
        time_end = time.time()
        elapsed_time = time_end - time_begin
        if elapsed_time >= 1:
            speed = data_sum // elapsed_time
            sys.stdout.write('\rcurrent speed: %d bytes' % speed)
            data_sum = 0
        else:
            data_sum += len(temp)

        '''
        current_speed = len(temp) // (time_end - time_begin)
        sys.stdout.write('\rcurrent speed: %d bytes' % ((len(temp)) // (time_end - time_begin)))
        '''
    except socket.error  as msg:
        print('Recieving error. Error code: ' + str(msg.errno) + ' Message ' + msg.strerror)
        sys.exit(1)
    if len(temp) == 0:
        client.close()
        print('\nDowload complete!')
        break
