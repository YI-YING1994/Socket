import socketserver
import sys

 # 這個類別是用來處理 server 端
class ServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print('{} wrote:'.format(self.client_address[0]))
        print(self.data)
        self.request.sendall(self.data.upper())

if __name__ == '__main__':
    HOST, PORT = '', 9999

    with socketserver.TCPServer((HOST, PORT), ServerHandler) as ser:
        ser.serve_forever()
