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
        function_list=[self.re_start,self.text_message]
        try:
            self.function = function_list[function_code]
            
        except IndexError:
            self.re_start(self)
        self.buf_size = 2**buf_size_code
        self.ack()

    def ack(self):
        self.send(self, b'\xff')
    def start_signal(self):
        while True:
            self.wait_for_connect()
            try:
                received_buf = self.recv(5,1)
                received_buf = self.buf_to_int(buf=received_buf)
            except (TimeoutError, ValueError):
                self.re_start()
            
            function_code = received_buf>>4
            buf_size_code = received_buf & 0b00001111
            self.set_function_and_size(function_code, buf_size_code)

    def re_start(self):
        self.close()
        self.start_signal()

    def router(self):
         self.function()

    def receive_long_data(self):
        working = 1
        server_page = 0
        data_list=[]
        while working:
            self.ack()
            try:
                received_bytes = bytearray(self.recv(2))
            except TimeoutError:
                self.re_start(self)
            working = received_bytes[-1] & 0b00000001
            cline_page = received_bytes[-1] >> 1
            
            if server_page>cline_page:
                server_page=cline_page
            elif server_page<cline_page:
                while server_page<cline_page:
                    try:
                        data_list[server_page]
                    except IndexError:
                        data_list.append(bytearray(self.buf_size-1))
                    server_page += 1
            
            if server_page==cline_page:
                try:
                    data_list[server_page]=received_bytes[0:-1]
                except IndexError:
                    data_list.append(received_bytes[0:-1])
            server_page+=1
        
        result=bytearray()
        for i in data_list:
            result.extend(i)
        
        return result



        



       
