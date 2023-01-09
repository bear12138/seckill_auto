
import numpy as np
# from pic_save import locate_screen
# from paddleocr import PaddleOCR
# import base64
import cv2
def writeImg(self):
    # 图像融合
    # 第一张图和第三张图进行重叠，随后进行识别
    # IMG = []
    # combine=[]
    PATHNAME="./file/yzm_num1.png"
    IMG=cv2.imread(PATHNAME)
    sp=IMG.shape
    # COMBINE=[]
    print(sp, "图片大小")
    i=0
    while i<4:
        # img[i]=
        path_name1 = "./file/yzm_num" + str(i + 1) + ".png"
        path_name2= "./file/yzm_num" + str(i + 5) + ".png"
        img1=cv2.imread(path_name1)
        img2=cv2.imread(path_name2)
        combine= cv2.addWeighted(cv2.resize(img1, (sp[1], sp[0])), 0.5, cv2.resize(img2, (sp[1], sp[0])), 0.5, 0)
        # combine1 = cv2.addWeighted(cv2.resize(img3, (sp[1], sp[0])), 0.5, cv2.resize(img4, (sp[1], sp[0])), 0.5, 0)
        path_name_c1="./file/yzm_com1_"+str(i+1)+".png"
        # cv2.imshow('combine', combine)
        cv2.imwrite(path_name_c1, combine)
        i+=1
    i=0
    while i<2:
        Path_name1="./file/yzm_com1_" + str(i + 1) + ".png"
        Path_name2 = "./file/yzm_com1_" + str(i + 3) + ".png"
        img1=cv2.imread(Path_name1)
        img2=cv2.imread(Path_name2)
        combine=cv2.addWeighted(cv2.resize(img1, (sp[1], sp[0])), 0.5, cv2.resize(img2, (sp[1], sp[0])), 0.5, 0)
        Path_Name1="./file/yzm_com2_"+str(i+1)+".png"
        cv2.imwrite(Path_Name1,combine)
        i+=1
    Path_Name1="./file/yzm_com2_1.png"
    Path_Name2="./file/yzm_com2_2.png"
    img1=cv2.imread(Path_Name1)
    img2=cv2.imread(Path_Name2)
    combine=cv2.addWeighted(cv2.resize(img1, (sp[1], sp[0])), 0.5, cv2.resize(img2, (sp[1], sp[0])), 0.5, 0)
    cv2.imwrite("./file/YZM_NUM.png",combine)
    # cv2.imwrite('cv2-2.png', combine1)
    # 再合成
    # IMG=[]
    # COMBINE=[]
    # 将cv2-1.png 图片灰度化处理
    img = cv2.imread('./file/YZM_NUM.png')
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    t, gray1 = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    cv2.imwrite('./file/YZM_NUM.png', gray1)
# locate_screen()
# writeImg()


##数字识别，精度不错，库较大
"""
def verify_result(self):
    ocr = PaddleOCR()  # need to run only once to download and load model into memory
    img_path = './file/YZM_NUM.png'
    result = ocr.ocr(img_path, det=False)
    for line in result:
        # print(line)
        print(line[0])
"""



