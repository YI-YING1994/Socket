import socket   #for sockets
import sys  #for exit

try:
    #create an AF_INET, STREAM socket (TCP)
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    print('Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
    sys.exit(1)


print('Socket Created')
 
#host = 'www.mcu.edu.tw'
host = '127.0.0.1'
port = 88
 
try:
    remote_ip = socket.gethostbyname( host )
 
except socket.gaierror:
    #could not resolve
    print('Hostname could not be resolved. Exiting')
    sys.exit()
     
print ('IP address of ' + host + ' is ' + remote_ip)
 
#Connect to remote server
s.connect((remote_ip , port))
 
print ('Socket Connected to ' + host + ' on IP ' + remote_ip)

#Send some data to remote server
#message = "GET / HTTP/1.1\r\n\r\n"
message = "This is a test message"
'''

In python 3, bytes strings and unicodestrings are now two different types. Since sockets are not aware of string encodings, they are using raw bytes strings, that have a slightly differentinterface from unicode strings.

So, now, whenever you have a unicode stringthat you need to use as a byte string, you need toencode() it. And whenyou have a byte string, you need to decode it to use it as a regular(python 2.x) string.

Unicode strings are quotes enclosedstrings. Bytes strings are b”” enclosed strings

When you use client_socket.send(data),replace it by client_socket.send(data.encode()). When you get datausing data = client_socket.recv(512), replace it by data =client_socket.recv(512).decode()
'''

try:
   s.sendall(message.encode())
except socket.error:
    print('Send failed') 
    sys.exit()

print('Message send successfully')

#Now receive data
reply = s.recv(4096)
print(reply)
