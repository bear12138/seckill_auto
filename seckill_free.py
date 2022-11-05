# -*- coding: utf-8 -*-  #防中文乱码
# !/usr/bin/env python3
#调用文件的第三方库
# from pic_save import locate_screen
# from paddleocr import PaddleOCR
# #
# import sys
# from io import BytesIO
# import onnxruntime
# import torch
# import torchvision

##used for choose place without  prepration to see if it is choosed
##窗口测试
from interval import Interval
##面向对象的gui程序
##源代码，模拟浏览器
# from lxml import etree
from selenium import webdriver
# import selenium.webdriver as webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
##自动关闭弹窗
# import win32gui, win32api, win32con
# import ctypes

from selenium.webdriver.common.keys import Keys
##未知的库，之前用过，勿删
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.select import Select
##界面库
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
# from tkinter.messagebox import *
##导入图片库
from PIL import ImageTk, Image
###生成window临时文件夹（找不到）
import os
# import os.path
#随机数
import random
# 识别
from slide_verify import onnx_model_main
import numpy as np
#
from verfy_num import *


class Application(Frame):
    global value_list,x_cdi_num,G_cdi_num
    value_list = {'光谷体育馆': "/html/body/div[2]/div/ul/li[1]/div[1]/div[2]/span/a",
                  '西边体育馆': "/html/body/div[2]/div/ul/li[6]/div[1]/div[2]/span/a",
                  '早8-10': '//*[@id="starttime"]/option[1]','早10-12': '//*[@id="starttime"]/option[2]','午12-14': '//*[@id="starttime"]/option[3]',
                  '午2-4':'//*[@id="starttime"]/option[4]','午4-6':'//*[@id="starttime"]/option[5]',
                  '晚6-8': '//*[@id="starttime"]/option[6]','晚8-10': '//*[@id="starttime"]/option[7]',
                  ##西体场地
                  '4号_x': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[6]',
                  '5号_x': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[5]',
                  '6号_x': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[4]',
                  '7号_x': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[3]',
                  ##光体场地
                  '6号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[4]/td[2]',
                  '7号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[4]/td[3]',
                  '8号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[4]/td[4]',
                  '9号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[4]/td[5]',
                  '10号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[4]/td[6]',
                  '11号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[2]',
                  '12号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[3]',
                  '13号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[4]',
                  '14号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[5]',
                  '15号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[6]',
                  '16号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[6]/td[2]',
                  '17号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[6]/td[3]',
                  '18号_G': '/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[6]/td[4]'
                  }
    x_cdi_num=['/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[6]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[5]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[4]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[3]']
    G_cdi_num=['/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[4]/td[2]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[4]/td[3]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[4]/td[4]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[4]/td[5]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[4]/td[6]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[2]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[3]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[4]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[5]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[5]/td[6]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[6]/td[2]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[6]/td[3]','/html/body/div[2]/div[2]/div[2]/form/div[1]/table/tbody/tr[6]/td[4]']


    # self相当于java的this，是实例对象本身，不是类，而是类的实例，相当于指针，方便调用
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()  #大窗口打包
        self.createWidget()  # 调用下面


    def createWidget(self):
        ###登录界面设置
        global  photo1,list1, list2, list3, photo2, bg2
        self.bg = tk.Canvas(sec, width=800, height=400, bd=0, highlightthickness=0)
        img = Image.open('file/背景图.gif')
        photo1 = ImageTk.PhotoImage(img)
        self.bg.create_image(400, 200, image=photo1)
        self.bg.pack()


        # self.start = Button(root, text='启动', command=self.window2(), bg="yellow").place(relx=0.1, rely=0.8,relwidth=0.2,relheight=0.1)  # 创建按钮,进入网站
        # # self.log_in = Button(root, text="登录", command=self.login, bg="yellow").place(relx=0.7, rely=0.8, relwidth=0.2,relheight=0.1)  # 调用另一个页面，登录网站
        # # self.btn1quit=Button(self,text="登录",command=root.destroy)
        # # self.btn1quit.pack()
        self.account = Label(sec, text="学号:", font=("黑体", 12), bg="Hotpink").place(relx=0.09, rely=0.3, relwidth=0.1,relheight=0.1)
        self.password = Label(sec, text="密码:", font=('黑体', 12), bg="Hotpink").place(relx=0.09, rely=0.42, relwidth=0.1,relheight=0.1)
        #
        entry1 = StringVar()
        self.entry1 = Entry(sec, textvariable=entry1)
        #
        self.entry1.place(relx=0.2, rely=0.3, relwidth=0.4, relheight=0.1)
        entry2 = StringVar()
        self.entry2 = Entry(sec, textvariable=entry2, show='*')
        self.entry2.place(relx=0.2, rely=0.42, relwidth=0.4, relheight=0.1)
        self.toggle_btn = tk.Button(sec, text='显示密码', font=('宋体', 10), command=self.pd, bg="Hotpink")
        self.toggle_btn.place(relx=0.65, rely=0.42, relwidth=0.2, relheight=0.1)


        filename = 'file/acc_pd.txt'
        with open(filename,'r') as data_file:
            n, p = data_file.read().strip().split(',')
            entry1.set(n)
            entry2.set(p)
        def write_in():
            # 获取用户名和密码
            name = self.entry1.get()
            pwd = self.entry2.get()
            with  open(filename, 'w') as data_file:
                data_file.write(','.join((name, pwd)))

            # 创建按钮组件，同时设置按钮事件处理函数

        # write_in()
        self.remeber = tk.Button(sec,text='保存账号',command=write_in,bg='Hotpink',font=('宋体', 10,'bold')).place(relx=0.65, rely=0.3, relwidth=0.2, relheight=0.1)



        def change(*args):  # *args必须有，类似于字典，储存传送数据
            global list1  # 单独定义list1，使其页面切换后能与list2联系起来
            if (list1.get() == "西体"):
                list2.config(values=["4号_x", "5号_x", "6号_x", "7号_x"])
                list2.current(0)
            else:
                list2["value"] = ["6号_G", "7号_G", "8号_G", "9号_G", "10号_G", "11号_G", "12号_G", "13号_G", "14号_G","15号_G",
                                  "16号_G", "17号_G",
                                  "18号_G"]
                list2.current(0)
            return

        ##
        # global gym,num,Time
        gym = tk.StringVar()
        num = tk.StringVar()
        Time = tk.StringVar()
        ##列表，下拉框
        list1 = ttk.Combobox(sec, textvariable=gym, state="readonly", width=10)
        list1.bind("<<ComboboxSelected>>", change)  # 切换第二个框选
        list1['value'] = ("西体", "光体")
        list1.current(0)
        list2 = ttk.Combobox(sec, textvariable=num, state="readonly", width=50)
        list2.config(values=["4号_x", "5号_x", "6号_x", "7号_x"])
        list2.current(0)
        list3 = ttk.Combobox(sec, textvariable=Time, state="readonly", width=20)
        list3['value'] = ("8:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00")
        list3.current(0)
        list1.place(relx=0.07, rely=0.1, relwidth=0.24, relheight=0.1)
        list2.place(relx=0.38, rely=0.1, relwidth=0.24, relheight=0.1)
        list3.place(relx=0.69, rely=0.1, relwidth=0.24, relheight=0.1)
        Label(sec, text="体育馆", font=("宋体", 12), borderwidth=0.01, relief="groove", bg="Hotpink").place(relx=0.07,rely=0.03,relwidth=0.24,relheight=0.05)
        Label(sec, text="场地号", font=("宋体", 12), borderwidth=0.01, relief="groove", bg="Hotpink").place(relx=0.38,rely=0.03,relwidth=0.24,relheight=0.05)
        Label(sec, text="时间段", font=("宋体", 12), borderwidth=0.01, relief="groove", bg="Hotpink").place(relx=0.69,rely=0.03,relwidth=0.24,relheight=0.05)
        self.go = Button(sec, text='预约', command=self.sec_kill, font=("宋体", 12)).place(relx=0.4, rely=0.8,relwidth=0.2,relheight=0.1)  # 创建按钮


    def sec_kill(self):

        while (True):
            # 当前时间
            now_localtime = time.strftime("%H:%M:%S", time.localtime())
            # 当前时间（以时间区间的方式表示）
            now_time = Interval(now_localtime, now_localtime)
            # print(now_time)
            time_interval = Interval("07:59:00", "22:15:00")

            if now_time in time_interval:
                print("success")
                break
            else:
                time.sleep(10)

        while(True):
            try:

                browser.get(login_url)
                browser.maximize_window()
                # messagebox.askokcancel(title="场馆登录", message="请输入账号和验证码")
                # 验证码识别
                element = browser.find_element(by=By.XPATH,value='//*[@id="codeImage"]')
                # 数字验证码识别，成功，但cv2库容量太大
                num = 0
                while num < 8:
                    path_name = "./file/yzm_num" + str(num + 1) + ".png"
                    element.screenshot(path_name)
                    num += 1
                writeImg(self)
                #识别数字
                ocr = PaddleOCR()  # need to run only once to download and load model into memory
                img_path = './file/YZM_NUM.png'
                result = ocr.ocr(img_path, det=False)
                filename_pd = 'file/acc_pd.txt'
                filename_yzm= 'file/yzm_num.txt'
                for line in result:
                    yzm_num="".join(list(filter(str.isdigit, line[0])))
                    with open(filename_yzm, 'w') as data_file:
                        data_file.write(''.join((yzm_num)))



                with open(filename_pd, 'r') as data_file:
                    n, p = data_file.read().split(',')

                with open(filename_yzm, 'r') as data_file:
                    yzm_num = data_file.read()


                account = n
                password = p
                yzm = yzm_num
                browser.find_element(by=By.ID, value='un').send_keys(account)
                browser.find_element(by=By.ID, value='pd').send_keys(password)
                browser.find_element(by=By.ID, value='code').send_keys(yzm)
                # time.sleep(0.5)

                browser.find_element(by=By.ID, value='index_login_btn').click()  # 点击登录按钮
                browser.find_element(by=By.CSS_SELECTOR, value='#main > ul > li:nth-child(2) > a').click()  # 场地预约栏

                break
            except:

                # time.sleep(5)
                pass

        # write_in()
        # self.remeber = tk.Button(root,text='记住密码',command=write_in,bg='yellow',font=('Arial', 10,'bold')).place(relx=0.4, rely=0.8, relwidth=0.2, relheight=0.1)
        # time.sleep(0.1)
        a = 1  # 输入参数控制无限请求
        # 循环点击（弹出窗口界面需要一直点击抢先进去）
        # global list1, list2, list3, gym, value_list, value1, value2, value3
        try:
            def choice(*args):  # 必须有，类似于字典，储存传送数据

                if (list1.get() == "西体"):
                    global value1, b
                    b = 1
                    value1 = value_list['西边体育馆']
                else:
                    b = 2
                    value1 = value_list['光谷体育馆']
                if (list2.get() == "4号_x"):
                    global value2
                    value2 = value_list['4号_x']
                elif (list2.get() == "5号_x"):
                    value2 = value_list['5号_x']
                elif (list2.get() == "6号_x"):
                    value2 = value_list['6号_x']
                elif (list2.get() == "7号_x"):
                    value2 = value_list['7号_x']
                ##光体场地
                elif (list2.get() == "6号_G"):
                    value2 = value_list['6号_G']
                elif (list2.get() == "7号_G"):
                    value2 = value_list['7号_G']
                elif (list2.get() == "8号_G"):
                    value2 = value_list['8号_G']
                elif (list2.get() == "9号_G"):
                    value2 = value_list['9号_G']
                elif (list2.get() == "10号_G"):
                    value2 = value_list['10号_G']
                elif (list2.get() == "11号_G"):
                    value2 = value_list['11号_G']
                elif (list2.get() == "12号_G"):
                    value2 = value_list['12号_G']
                elif (list2.get() == "13号_G"):
                    value2 = value_list['13号_G']
                elif (list2.get() == "14号_G"):
                    value2 = value_list['14号_G']
                elif (list2.get() == "15号_G"):
                    value2 = value_list['15号_G']
                elif (list2.get() == "16号_G"):
                    value2 = value_list['16号_G']
                elif (list2.get() == "17号_G"):
                    value2 = value_list['17号_G']
                else:
                    value2 = value_list['18号_G']
                if (list3.get() == "8:00-10:00"):
                    global value3
                    value3 = value_list['早8-10']
                elif (list3.get() == "10:00-12:00"):
                    value3 = value_list['早10-12']
                elif (list3.get() == "12:00-14:00"):
                    value3 = value_list['午12-14']
                elif (list3.get() == "14:00-16:00"):
                    value3 = value_list['午2-4']
                elif (list3.get() == "16:00-18:00"):
                    value3 = value_list['午4-6']
                elif (list3.get() == "18:00-20:00"):
                    value3 = value_list['晚6-8']
                else:
                    value3 = value_list['晚8-10']
                return

            choice()

            while a == 1:
                try:
                    browser.find_element(by=By.XPATH,value=value1).click()  # 体育馆进去按钮/html/body/div[2]/div/ul/li[6]/div[1]/div[2]/span/a
                    ##
                    time.sleep(0.1)
                    # WebDriverWait(browser, 1, 0.1).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#dialog_0 > div.window-button.clearfix > div > div > div.btn-inner > div')))
                    browser.find_element(by=By.CSS_SELECTOR,value='#dialog_0 > div.window-button.clearfix > div > div > div.btn-inner > div').click()
                    # browser.find_element_by_xpath('//*[@id="dialog_0"]/div[2]/div/div/div[2]/div').click()#点击开放时间确认小窗口
                    a = 1
                except:
                    # time.sleep(num)
                    WebDriverWait(browser, 600, 0.1).until(EC.element_to_be_clickable((By.CLASS_NAME, 'next_day')))
                    browser.find_element(by=By.CLASS_NAME, value="next_day").click()  # 切换明天，两个路径一样
                    a = 0
            # 请求成功后
            WebDriverWait(browser, 600, 0.1).until(EC.element_to_be_clickable((By.CLASS_NAME, 'next_day')))
            browser.find_element(by=By.CLASS_NAME,value='next_day').click()  # 切换后天，两个路径一样
            WebDriverWait(browser, 600, 0.1).until(EC.element_to_be_clickable((By.ID, 'starttime')))
            browser.find_element(by=By.ID, value='starttime').click()  #点击时间点框  # 点击时间点框
            browser.find_element(by=By.XPATH, value=value3).click()  # 切换到抢的时间
            judge=True
            while (judge):
                try:
                    WebDriverWait(browser, 0.2, 0.1).until(EC.text_to_be_present_in_element((By.XPATH, value2), u'已预约'))
                    # WebDriverWait(browser, 60, 0.1).until(EC.element_to_be_clickable((By.XPATH,value2)))
                     # s所有确定按钮
                    judge=False
                except:
                    WebDriverWait(browser, 600, 0.1).until(EC.text_to_be_present_in_element((By.XPATH, value2), u'可预约'))
                    # WebDriverWait(browser, 60, 0.1).until(EC.text_to_be_present_in_element(By.XPATH,value2),u'已预约')
                    # 选择同伴
                    browser.find_element(by=By.CSS_SELECTOR,value='body > div.margin_center.width_1000.clearfix.content > div.content_right.fr > div.tab_content > form > table > tbody > tr:nth-child(4) > td > input[type=button]').click()
                    # 点击同伴信息
                    browser.find_element(by=By.CSS_SELECTOR,value='body > div.stepModal > div.stepModalMain > div > div.datagrid.stepFourMain > table > tbody > tr:nth-child(2)').click()
                    # 场地号
                    browser.find_element(by=By.XPATH, value=value2).click()
                    browser.find_element(by=By.CSS_SELECTOR,value='body > div.margin_center.width_1000.clearfix.content > div.content_right.fr > div.tab_content > form > div.star_app > input[type=submit]:nth-child(3)').click()
                    #滑动验证码
                    while(True):
                        try:
                            WebDriverWait(browser, 10, 0.1).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="captcha"]/canvas[1]')))
                            browser.find_element(by=By.XPATH, value='//*[@id="captcha"]/canvas[1]').screenshot('./file/slide.png')
                            onnx_model_main('./file/slide.png')
                            with open('file/slide.txt', 'r') as data_file:
                                result_slide = data_file.read().strip()
                            # slide = browser.find_element(by=By.CSS_SELECTOR,value='#captcha > div.jigsaw__sliderContainer--1ZGEE > div > div')
                            result_slide=int(result_slide)
                            slide_instance=browser.find_element(by=By.XPATH,value='//*[@id="captcha"]/div[3]/div/div')
                            # 参考`drag_and_drop_by_offset(eleDrag,offsetX-10,0)`的实现，使用move方法
                            # simulateDragX(browser,slide_instance,result_slide)#
                            self.slide_simple(slide_instance,result_slide)

                            #提交
                            # time.sleep(0.5)
                            WebDriverWait(browser, 0.5, 0.1).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="submitbtn"]')))
                            browser.find_element(by=By.XPATH, value='//*[@id="submitbtn"]').click()
                            messagebox.showinfo(title="预约情况",message="success")
                            break
                            # return False
                        except:
                            # browser.find_element(by=By.XPATH, value='//*[@id="captcha"]/div[2]').click()
                            value_CSS = '#dialog_' + str(num) + ' > div.window-button.clearfix > div > div > div.btn-inner > div'
                            browser.find_element(by=By.CSS_SELECTOR, value=value_CSS).click()
                            break

            browser.find_element(by=By.XPATH, value='out').click()#设置错误跳出try


        except:

            value4 = value2

            cicle = 0

            while cicle < 15:

                value_CSS = '#dialog_' + str(cicle) + ' > div.window-button.clearfix > div > div > div.btn-inner > div'

                try:

                    if value1 == value_list["西边体育馆"]:

                        x_cdi_num.remove(value4)

                        value4 = random.choice(x_cdi_num)

                        # WebDriverWait(browser, 3, 0.1).until(EC.element_to_be_clickable(('#dialog_0 > div.window-button.clearfix > div > div > div.btn-inner > div')))  # s所有确定按钮

                        # browser.find_element(by=By.CSS_SELECTOR, value=value_CSS).click()  # s所有确定按钮

                    else:

                        G_cdi_num.remove(value4)

                        value4 = random.choice(G_cdi_num)
                    WebDriverWait(browser, 0.2, 0.1).until(EC.text_to_be_present_in_element((By.XPATH, value4), u'已预约'))
                    cicle += 1

                except:
                    WebDriverWait(browser, 0.2, 0.1).until(EC.text_to_be_present_in_element((By.XPATH, value4), u'可预约'))
                    browser.find_element(by=By.XPATH, value=value4).click()  # 场地号
                    #提交
                    browser.find_element(by=By.CSS_SELECTOR,value='body > div.margin_center.width_1000.clearfix.content > div.content_right.fr > div.tab_content > form > div.star_app > input[type=submit]:nth-child(3)').click()
                    # time.sleep(0.2)
                    while(True):
                        try:
                            browser.find_element(by=By.XPATH, value='//*[@id="captcha"]/canvas[1]').screenshot('./file/slide.png')
                            onnx_model_main('./file/slide.png')
                            with open('file/slide.txt', 'r') as data_file:
                                result_slide = data_file.read().strip()
                            # slide = browser.find_element(by=By.CSS_SELECTOR, value='#captcha > div.jigsaw__sliderContainer--1ZGEE > div > div')
                            result_slide = int(result_slide)
                            slide_instance = browser.find_element(by=By.XPATH, value='//*[@id="captcha"]/div[3]/div/div')
                            # 参考`drag_and_drop_by_offset(eleDrag,offsetX-10,0)`的实现，使用move方法
                            # simulateDragX(browser,slide_instance,result_slide)
                            self.slide_simple(slide_instance,result_slide)
                            # time.sleep(0.2)
                            #
                            # browser.find_element(by=By.XPATH, value='//*[@id="submitbtn"]').click()
                            messagebox.showinfo(title="预约情况",message="未知场地")
                            # browser.find_element(by=By.XPATH, value='/html/body/div[2]/div[2]/form/div/div[4]/input[1]').click()#取消
                            # browser.find_element(by=By.XPATH, value='??').click()
                            break
                            # return False
                        except:
                            pass





    def pd(self):
        if self.entry2.cget('show') == '':
            self.entry2.config(show='*')
            self.toggle_btn.config(text='显示密码')
        else:
            self.entry2.config(show='')
            self.toggle_btn.config(text='隐藏密码')


    #简化后的滑动
    def slide_simple(self,slide_instance,result_slide):
        action_chains = webdriver.ActionChains(browser)
        # 点击，准备拖拽
        action_chains.click_and_hold(slide_instance)
        action_chains.pause(0.2)
        action_chains.move_by_offset(result_slide - 10, 2)
        action_chains.pause(0.3)
        action_chains.move_by_offset(10, 3)
        action_chains.pause(0.2)
        action_chains.release()
        action_chains.perform()
    def write_in(self):
        print(self.entry1.get())

        name = self.entry1.get()
        pwd = self.entry2.get()

        with  open('file/acc_pd.txt', 'w') as data_file:
            data_file.write(','.join((name, pwd)))

    #调用无效，只能直接用
    # def auto_in(self):
    #     T=True
    #     while(T):
    #         try:
    #
    #             self.sec_kill()
    #             # self.sec_kill()
    #             T= False
    #         except:
    #             pass
    #         # self.sec_kill()
    #     messagebox.showinfo("预约成功")
# 主程序
if __name__ == "__main__":
    sec = tk.Tk()
    sec.geometry("800x400+200+200")
    sec.title("华中科技大学体育馆")
    # self.toggle_btn.place(relx=0.15, rely=0.5, relwidth=0.2, relheight=0.2)
    app = Application(master=sec)
    login_url = "http://pecg.hust.edu.cn/cggl/index1"
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["pageLoadStrategy"] = "none"

    browser = webdriver.Chrome(executable_path='chromedriver.exe')
    sec.mainloop()
    browser.quit()  # 退出程序后浏览器关闭













