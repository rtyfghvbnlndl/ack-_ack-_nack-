import socket

class server(object):
    def __init__(self,address,port):
        self.serSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        self.serSocket.bind((address,port))
        self.serSocket.listen(10)
        self.buf_size = 1
        self.function_list=[self.re_start, self.receive_long_data,]
        self.function = self.start_signal
        print('server on')        
    
    def wait_for_connect(self):
        print("wait for connecting...")
        connect, address = self.serSocket.accept()
        print(str(address)+'connected')
        self.connect=connect

    def recv(self, timeout):
        print('wait client...',timeout)
        self.connect.settimeout(timeout)
        buf = self.connect.recv(self.buf_size)
        print('[client]:'+str(buf))
        if buf == b'':
            raise ConnectionError("receive a b''")
        return buf
    
    def recv_byte(self):
        print('wait 1 byte...')
        self.connect.settimeout(90)
        buf = self.connect.recv(1)
        print('[client]:'+str(buf))
        if buf == b'':
            raise ConnectionError("receive a b''")
        return buf
    
    def send(self, buf):
        self.connect.send(buf)
        print('[server]:'+str(buf))
    
    def close(self):
        self.connect.close()

    def buf_to_int(self,buf=bytes()):
        if len(buf) == self.buf_size or len(buf) == 1:
            int_buf = int.from_bytes(buf, byteorder='big', signed=False)
            return int_buf
        else:
            raise ValueError('length do not match')
        
    def set_function_and_size(self, function_code=0, buf_size_code=0):
        if buf_size_code<=7:
            self.buf_size = 2**buf_size_code
        else:
            raise ValueError('buf_size_code must be less than or equal to 7')
        self.function = self.function_list[function_code]
        self.ack()

    def ack(self):
        self.send(b'\xff')

    def re_start(self):
        self.close()
        self.start_signal()

    def start_signal(self):
        self.wait_for_connect()
        received_buf = self.recv_byte()
        received_buf = self.buf_to_int(buf=received_buf)
        
        function_code = received_buf>>4
        buf_size_code = received_buf & 0b00001111
        try:
            self.set_function_and_size(function_code, buf_size_code)
        except IndexError:
            print('unexpected function')
                

    def router(self):
        try:
            print('<function>'+str(self.function.__name__))
            ret = self.function()
        except (ValueError, TimeoutError) as err:
            print('!!Error:' + str(err))
            self.close()
            self.function = self.start_signal
        except (ConnectionError,OSError):
            self.wait_for_connect()

    def receive_long_data(self):
        working, page, data_list, ack = 1, 0, [], b'\xff'

        while working:
            self.send(ack)
            received_bytes = self.recv(2)
            last_byte_int = received_bytes[-1]
            
            if last_byte_int & 0b00000001:
                #未到尾页
                cline_page = last_byte_int >> 1   
                if page==cline_page:
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
                data_list.append(received_bytes[0:end_index+1])
                break
        #结束信号
        self.send(b'\xfe')
        
        result=bytes()
        for i in data_list:
            result+=i

        return result
    
    def send_long_data(self,data=bytes()):
        #字节页数计算
        buf_len = self.buf_size-1
        if len(data)%(buf_len)!=0:
            largest_page = len(data)//(buf_len)
        else:
            largest_page = len(data)/(buf_len)-1
        page = 0
        while True:
            print('page:',page)
            recv_buf = int.from_bytes(self.recv(2), 'big', signed=False)
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

class e_paper(server):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.function_list=[
            self.re_start, 
            self.receive_long_data_test, 
            self.send_long_data_test,
            self.receive_send_test,
            self.data_process,
            ]
    #0：单纯的接收数据
    def receive_long_data_test(self):
        data = self.receive_long_data()
        self.function=self.start_signal
        print(data)
        return data
    #1：单纯的发送数据
    def send_long_data_test(self,data=b'ajsdhsja'):
        self.send_long_data(data=data)
        self.function=self.start_signal
    #2：接收数据再发出同样的数据
    def receive_send_test(self):
        from time import sleep
        data = self.receive_long_data()

        self.send_long_data(data=data)
        self.function=self.start_signal
    
    def data_process(self):
        from opencv.pixel_process import pixel_process
        import cv2 as cv
        import os

        file_name = self.receive_long_data()
        file_path = './opencv/pic/' + file_name.decode()
        print('hagdigsahidha',file_path)

        if os.path.exists(file_path):
            img = cv.imread(file_path, 2)
            pp = pixel_process(img, height =212 , width = 104)
            pp.mid = 127
            pp.make_a_new_pic()
            bytes_ = pp.encode_bytes()
        else:
            bytes_ = b'None'

        self.send_long_data(data = bytes_)
        self.function=self.start_signal

if __name__ == '__main__':
    a=e_paper(socket.gethostname(), 8266)
    a.wait_for_connect()
    while True:
        a.router()


            






        



       
