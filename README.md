### >> ACK? ACK?
### NACK!
### >> 摔！

### 日志
> 4.23
> 1. 完善了错误处理。
> 2. 增强打印信息的可读性。
>
> 4.26
> 1. 完成了分段接收信息（server+client）
> 2. 优化了字节处理部分
>
> 5.7
> 1. 修复溢出
> 2. 处理&回传

### 介绍

### 1. client发送指令
指定server运行的函数，和每次分段传送的字节长度
```python
start_signal(function_code=1, buf_len_code=4)
```
其中function_code对应server的
```python
self.function_list=[function0, function1, function2]
```
每次分段传送的字节长度为：2^buf_len_code即为2^4=16个字节。

### 2. server指定运行的function
    反复运行server类的router(),比如：
```python
a=e_paper(socket.gethostname(), 1234)
a.wait_for_connect()
while True:
    a.router()
```
其中e_paper继承了server类，如下：
```python
class e_paper(server):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.function_list=[self.re_start, self.receive_long_data_test, self.send_long_data_test]

    def receive_long_data_test(self):
        data = self.receive_long_data()
        self.function=self.start_signal
        print(data)

    def send_long_data_test(self):
        self.send_long_data(buf_len=self.buf_size, data=b'ahbgdu')
        self.function=self.start_signal
```