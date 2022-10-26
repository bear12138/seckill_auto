#coding = utf-8
#批量安装库
import os  #引入os 库，os是python自带的库
#将要批量安装的第三方库写进一个列表
libs = ["interval","selenium","time","tkinter","PIL","os","random","numpy","cv2","paddleocr","sys","io","onnxruntime","torch","torchvision"]

#使用try，expect结构运行，如果try部分出错，则执行except部分的代码
#对列表libs进行遍历，执行os.system命令
try:
    for lib in libs:
        os.system("pip install " + lib)
    print("批量安装成功")
except:
    print("安装库失败")