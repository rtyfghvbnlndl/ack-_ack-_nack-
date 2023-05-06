import socket
from time import sleep

class client(object):
    def __init__(self):
        self.receive_tomeout=2
        pass

    def connect(self,host,port):
        self.cliSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.cliSocket.connect((host,port))

    def send(self, buf=bytes()):
        self.cliSocket.send(buf)
        print('[client]:'+str(buf))
        return 1
        
        
    def recv(self, buf_len=1, timeout=2):
        print('wait server...')
        self.cliSocket.settimeout(timeout)
        buf = self.cliSocket.recv(buf_len)
        print('[server]:'+str(buf))
        return buf

    def close(self):
        self.cliSocket.close()

    def start_signal(self, function_code=0, next_buf_size=0):
        self.buf_size = 2 ** next_buf_size
        print('buf_length:', self.buf_size)
        buf = ((function_code<<4) + (next_buf_size)).to_bytes(1, byteorder='big', signed=False)
        self.send(buf)

        self.recv(1,2)
    
    def send_long_data(self, buf_len_code=1, data=b'abcd'):
        #字节页数计算
        buf_len = 2**buf_len_code-1
        if len(data)%(buf_len)!=0:
            largest_page = len(data)//(buf_len)
        else:
            largest_page = len(data)/(buf_len)-1
        page = 0
        while True:
            print('page:',page)
            recv_buf = int.from_bytes(self.recv(buf_len, 2), 'big', signed=False)
            #判断同步指令
            if not (recv_buf & 0b00000001):
                page = recv_buf
                print('sync page:',page)
            #判断结束
            if page>largest_page:
                break
            send_buf = data[page*buf_len:(page+1)*buf_len]
            #构建页码
            if page==largest_page:
                last_byte = (len(send_buf)-1)<<1
                while len(send_buf)<buf_len:
                    send_buf+=b'\x00'
            else: 
                
                last_byte = (page<<1)|0b00000001
           
            send_buf += last_byte.to_bytes(1, byteorder='big', signed=False)
            self.send(send_buf)
            page+=1
        
    def receive_long_data(self):
        working, page, data_list, ack = 1, 0, [], b'\xff'

        while working:
            self.send(ack)
            received_bytes = self.recv(self.buf_size,self.receive_tomeout)
            last_byte_int = received_bytes[-1]
            
            if last_byte_int & 0b00000001:
                #未到尾页
                remote_page = last_byte_int >> 1   
                if page==remote_page:
                    try:
                        data_list[page]=received_bytes[0:-1]
                    except IndexError:
                        data_list.append(received_bytes[0:-1])
                    page+=1
                    #确认信号
                    ack = b'\xff'
                else: 
                    #同步指令
                    ack = (page<<1).to_bytes(1, byteorder='big', signed=False)
            
            else:
                #尾页
                end_index = last_byte_int >> 1
                print(end_index+1)
                data_list.append(received_bytes[0:end_index+1])
                break
        #结束信号
        self.send(b'\xfe')

        result=bytes()
        for i in data_list:
            result+=i

        return result
    
    def test(self):
        self.send(b'adgsdjasd')
        self.recv(10,2)

class e_paper(client):
    def test(self,buf_size=2):
        self.start_signal(1,buf_size)
        self.send_long_data(buf_size,b'123asdasdsadasd4455')

        self.start_signal(2,buf_size)
        a=self.receive_long_data()

        print(a)
        self.close() 

    def test1(self, pic='./opencv/picd/142.jpg',buf_size=2):
        self.start_signal(3,buf_size)
        with open(pic, mode='rb+') as f:
            self.send_long_data(buf_size, f.read())
        
        self.receive_tomeout=6
        a=self.receive_long_data()
        with open('2.jpg', mode='ab+') as f:
            f.write(a)
        print(a)
        self.close() 
    
    def data_process(self, buf_size=2, file_name = '1.jpg'):
        self.start_signal(4,buf_size)
        self.send_long_data(buf_size, file_name.encode())
        self.receive_tomeout=10
        data = self.receive_long_data()
        print(data)


if __name__ == '__main__':
    a=e_paper()
    a.connect(socket.gethostname(), 8266)
    #a.test()
    #a.test1(buf_size=7)
    a.data_process(buf_size=5, file_name = '4.jpg')



