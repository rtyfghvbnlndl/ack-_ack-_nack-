import numpy as np
import cv2 as cv
from time import sleep

class pixel_process(object):
    def __init__(self, img = cv.imread('./test.jpg',2), height =212 , width = 104):

        self.height = height
        self.width = width
        self.img = img
        self.mid=127

    def get_shape(self):
        self.pic_height = self.img.shape[0]
        self.pic_width = self.img.shape[1]

    def calculate_cut_size(self):
        self.cut_height = int(self.cut_width/self.width*self.height+0.555)

        self.cut_width_start = int((self.pic_width-self.cut_width)/2)
        self.cut_width_end = self.cut_width_start+self.cut_width
        self.cut_height_start = int((self.pic_height-self.cut_height)/2)
        self.cut_height_end = self.cut_height_start+self.cut_height

    def cut_pic(self):
        self.get_shape()
        if (self.height>self.width) != (self.pic_height>self.pic_width):
            self.img=np.rot90(self.img)
            self.get_shape()
        
        
        self.cut_width = self.pic_width
        self.calculate_cut_size()
        while self.cut_height>self.pic_height or self.cut_width>self.pic_width:
            self.cut_width = self.cut_width-1
            self.calculate_cut_size()
            
        self.img = self.img[self.cut_height_start:self.cut_height_end, self.cut_width_start:self.cut_width_end]

    def resize_pic(self):
        self.img = cv.resize(self.img, (self.width, self.height), interpolation=cv.INTER_LINEAR)
    
    def make_a_new_pic(self):
        self.cut_pic()
        self.resize_pic()

        return self.img
    
    def encode_test(self, mid):
        black=0
        white=0
        for y in range(self.height):
            for x in range(self.width):
                grat_level = self.img[y, x]
                if grat_level>mid:
                    black+=1
                else:
                    white+=1
        print(black, white,abs(black-white))
        return black, white

    def caculate_mid(self):
        result, abs_value=127,self.width*self.height
        for mid in range(0,255):
            black, white = self.encode_test(mid)
            if abs(black-white)< abs_value:
                abs_value=abs(black-white)
                result = mid
        self.mid=result
        print(abs_value,self.mid)

    def encode_generator(self):
        for y in range(self.height):
            x_interation = iter(range(self.width))

            for ii in range(int(self.width/8+0.99999)):
                tobyte_int=0
                for i in range(8):
                    try:
                        x = next(x_interation)
                    except StopIteration:
                        break
                    print(self.img[y,x])
                    gray_level = self.img[y,x]
                    if gray_level>self.mid:
                        tobyte_int += 2**(7-i)
                yield tobyte_int.to_bytes(1, byteorder='big', signed=False)
    def encode_bytes_RGB(self):
        bytes_ = bytes()
        for y in range(self.height):
            for x in range(self.width):
                for i in range(3):
                    bytes_ += int(self.img[y,x][i]).to_bytes(1, byteorder='big', signed=False)
        return bytes_
    
    def encode_list(self):
        generator = self.encode_generator()
        bytes_list = []
        while True:
            bytes_in_line = b''
            for num_in_line in range(int(self.width/8+0.99999)):
                try:
                    byte=next(generator)
                    bytes_in_line += byte
                except StopIteration:
                    return bytes_list
            bytes_list.append(bytes_in_line)
    
    def encode_bytes(self):
        generator = self.encode_generator()
        bytes_ = b''
        while True:
            try:
                byte=next(generator)
                bytes_ += byte
            except StopIteration:
                return bytes_

    def to_cpp_hex(self, blist):
        res_list=[]
        for line in blist:
            hex_list=list(line.hex())
            while hex_list:
                a0=hex_list.pop(0)
                a1=hex_list.pop(0)
                res_list.append('0X'+a0+a1)
        res_str = str(res_list)
        res_str=res_str.replace("'",'')[1:-1]
        res_str='{'+res_str+'}'
        return res_str



if __name__ == '__main__':
    img = cv.imread('./pic/1.jpg',1)
    a = pixel_process(img, height =212 , width = 104)
    
    #a.caculate_mid()
    #效果不好

    a.mid=127
    a.make_a_new_pic()
    cv.imshow('cuted_img',a.img)
    cv.waitKey(2000)

    bytes_ = a.encode_bytes_RGB()
    print(bytes_)

    byte_list = a.encode_list()
    print(byte_list)

    bytes_ = a.encode_bytes()
    print(bytes_)

    cpp_bytes_str = a.to_cpp_hex(byte_list)
    print(cpp_bytes_str)



        
    



