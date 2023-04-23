import socket

class client(object):
    def __init__(self):
        pass

    def connect(self,host,port):
        self.cliSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.cliSocket.connect((host,port))

    def send(self, buf=bytes()):
        self.cliSocket.send(buf)
        print('client:'+str(buf))
        return 1
        
        
    def recv(self, buf_len=1, timeout=2):
        print('wait server...')
        self.cliSocket.settimeout(timeout)
        buf = self.cliSocket.recv(buf_len)
        print('server:'+buf)
        return buf

    def close(self):
        self.cliSocket.close()

    def start_signal(self, function_code=0, next_buf_size=0):
        self.buf_size = 2 ** next_buf_size
        buf = ((function_code<<4) + (next_buf_size)).to_bytes(1, byteorder='big', signed=False)
        self.send(buf)
    
    def receive_long_data(self):
        pass
    
class e_paper(client):
    def send_long_data(self, buf_len_code=0, data=b'\x13\x23\x33\x43'):
        self.start_signal(1,buf_len_code)
        
        

if __name__ == '__main__':
    a=e_paper()
    a.connect(socket.gethostname(),8266)
    #a.send_long_data()



