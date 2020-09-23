#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os

# KB， MB, 和 GB 的位元組個數。
units = {"kb": 1024,
         "mb": 1048576,     # 1024 x 1024
         "gb": 1073741824}  # 1024 x 1024 x 1024

def createBigFile(fileName, size):
    global units
    tmp = fileName.split(".")
    name = tmp[0]

    if len(tmp) > 1:
        ext = ".".join(tmp[1:])
    else: 
        ext = "txt"

    if name == "":
        print("File name error!")
        print("File name couldn't be empty")
        return

    try:
        iSize = int(size[:-2])
    except ValueError:
        print("Size error")
        return

    tmp = size[-2:].lower()
    if tmp not in units:
        print("Unit error, please type kb, mb, or gb as file size unit")
        return
    unit = units[tmp]
    data = os.urandom(units["kb"])
    with open(name + "." + ext, "wb") as f:
        for i in range(int(iSize * unit / units["kb"])):
            f.write(data)
        

fileName = sys.argv[1]
fileSize = sys.argv[2]
createBigFile(fileName, fileSize)
