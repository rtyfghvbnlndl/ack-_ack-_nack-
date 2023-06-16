import os
from shutil import copyfile

path='C:Users/rtyfg/Pictures/ACG'

cwd=os.getcwd()
if not os.path.exists('./pic'):
    os.mkdir('pic')

file_list=os.listdir(path)

i=0
for file_name in file_list:
    if os.path.isfile(path+'/'+file_name):
        print('copy'+file_name)
        for ext in ('.png', '.jpg', 'PNG', 'JPG', 'JPEG', 'jpeg'):
            try:
                file_name.index(ext)
                file_ext_name=ext
                break
            except ValueError:
                pass
        file_name = path+'/'+file_name
    
        copyfile(file_name, './pic/'+str(i)+file_ext_name)

    i+=1