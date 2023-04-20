import socket

class server(object):
    def __init__(self,address,port):
        self.serSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        self.serSocket.bind((address,port))
        self.serSocket.listen(10)
        self.buf_size = 1
        self.function = self.start_signal()
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
        return buf
    
    def recv_byte(self):
        print('wait 1 byte...')
        self.connect.settimeout(3)
        buf = self.connect.recv(1)
        return buf
    
    def send(self, buf):
        self.connect.send(buf)
        print('[server]:'+str(buf))
    
    def close(self):
        self.connect.close()

    def buf_to_int(self,buf=bytes()):
        if len(buf) == self.buf_size:
            int_buf = int.from_bytes(buf, byteorder='big', signed=False)
            return int_buf
        else:
            raise ValueError('length do not match')
        
    def set_function_and_size(self, function_code=0, buf_size_code=0):
        function_list=[self.re_start,self.receive_long_data]
        try:
            self.function = function_list[function_code]
            
        except IndexError:
            return 0
        self.buf_size = 2**buf_size_code
        self.ack()
        return 1

    def ack(self):
        self.send(self, b'\xff')

    def re_start(self):
        self.close()
        self.start_signal()

    def start_signal(self):
        while True:
            self.wait_for_connect()
            try:
                received_buf = self.recv(5,1)
                received_buf = self.buf_to_int(buf=received_buf)
            except (TimeoutError, ValueError):
                self.close()
                continue
            
            function_code = received_buf>>4
            buf_size_code = received_buf & 0b00001111
            if self.set_function_and_size(function_code, buf_size_code):
                return 1
            else:
                return 0

    def router(self):
        ret = self.function()
        if ret:
            return ret
        else:
            self.close()
            self.start_signal(self)

    def receive_long_data(self):
        working = 1
        server_page = 0
        data_list=[]
        ack = b'\xff'

        while working:
            self.send(ack)
            
            received_bytes = bytearray(self.recv(2))
            #working = received_bytes[-1] & 0b00000001
            if received_bytes[-1] & 0b00000001:
                #未到尾页
                cline_page = received_bytes[-1] >> 1   
            
                if server_page==cline_page:
                    try:
                        data_list[server_page]=received_bytes[0:-1]
                    except IndexError:
                        data_list.append(received_bytes[0:-1])
                    server_page+=1
                    ack = b'\xff'
                else: 
                    ack = server_page<<1
            
            else:
                #尾页
                end_index = received_bytes[-1] >> 1
                data_list.append(received_bytes[0:end_index+1])
                break
        
        result=bytearray()
        for i in data_list:
            result.extend(i)
        
        return result
    
    def send_long_data(self,buf_length=1,data=bytes()):
        page_list=[]
        for i in range(int(len(data)//(buf_length-1)+0.99999)):
            page_list.append(data[i*buf_length:i*buf_length+buf_length-1])
        
        last_page = len(page_list)-1
        not_done = True
        page = 0
        while not_done:
            header_data = self.buf_to_int(self.recv_byte())
            if not header_data&0b00000001:
                page = header_data>>1

            buf = page_list[page]
            if page != last_page:
                last_byte = 1 + (page<<1)
                self.send(buf + bytes(last_byte))
                page += 1
            else:
                last_byte = 0 + (len(buf-1)<<1)
                self.send(buf + bytes(last_byte))
                break
            


            






        



       
