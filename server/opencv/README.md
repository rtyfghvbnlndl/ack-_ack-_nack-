### 特点
1. 让Arduino的墨水屏demo显示自己的图片
2. 识别横图或是竖图，根据屏幕比例自动翻转图片
3. 输出可供C使用的 unsigned char[] 格式的文本。
4. 输出list或bytes

### 例子
``` python
from pixel_process import pixel_process
import cv2 as cv

#打开图片
img = cv.imread('./test.jpg',2)
a = pixel_process(img, height =212 , width = 104)

#【必须】处理图片指令
a.make_a_new_pic()

#预览图片
cv.imshow('cuted_img',a.img)
cv.waitKey(2000)

#输出按行划分的list
byte_list = a.encode_list()
print(byte_list)

#输出为一整个bytes
bytes_ = a.encode_bytes()
print(bytes_)

#输出c用的unsigned char[]
#直接粘贴到微雪驱动的ImageData.c里，可以显示自己的图片
cpp_bytes_str = a.to_cpp_hex(byte_list)
print(cpp_bytes_str)

```
### 额外功能
```python
#设定划分黑白的中间值，a.mid在range(0,256)内
a.mid=127

#a.caculate_mid()
#效果不好

```