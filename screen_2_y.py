from PyQt5 import uic
from PyQt5.Qt import QUrl
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimedia import QMediaPlaylist
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import sys
import os
import cv2
import arduino
import detect_with_API
import torch
import serial
import numpy as np
class Ture:
    pass
'''
下面两行代码不可删除
'''

# envpath = '/home/gjd/snap/anaconda/envs/yolov7-main/lib/python3.9/site-packages/PyQt5/Qt5/plugins/platforms'
# envpath = '/home/gjd/snap/anaconda/envs/yolov7-main/lib/python3.9/site-packages/cv2/qt/plugins/platforms'
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = envpath

row_start = 55
row_end = 450
col_start = 150
col_end = 545

geshu =0
garbage={}
garbage_thistime=[]
# 通过九点标定获取的圆心相机坐标
STC_points_camera = np.array([
    [82, 84],[193, 83],[305, 81],
    [84, 195],[195, 194],[306, 192],
    [85, 307],[196, 305],[307, 303],
])
# 通过九点标定获取的圆心机械臂坐标
STC_points_robot = np.array([
    [2150, 5130],[3900, 5150],[5620, 5170],
    [2160, 3380],[3910, 3400],[5640,3440],
    [2180, 1660],[3910, 1660],[5650, 1680],
])

cap = cv2.VideoCapture(1)  # 0
cap.set(3,640)#长
cap.set(4,640)#宽

cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25表示关闭自动曝光
# 设置曝光参数
cap.set(cv2.CAP_PROP_EXPOSURE, -8)  # 负值表示减少曝光

a = detect_with_API.detectapi('best_y.pt')
garbage_difficulty = { '0battery': 7, '1pill_b': 1, '2pill_d': 1,'3can':8,\
           '4bottle':8,'5potato':2,'6pbailuobo':0,'7phuluobo':3,'8china':5,\
           '9cob':5,'10tile':5,'11cup':9,'1tablet':1,\
         '2can':8,'5medicinebag':0,'6bailuobo':0,'16':3,\
    '17':3,'18':3,'19':3,'20':3,\
         '21Wapple':3,'22Wbanana':3,'23Wbocai':3,'24Whuluobo':3,\
         '25Wkiwi':3,'26Worange':3,'27Wpotato':3,'28Wqingcai':3,'29Wtomato':3,\
           "30Huluobotiao":3,"31Baicai":3,"32Tobatoo":0,"33Wood":2,"34Brick":2,"35pill":0,"36cup":1,"38youzipired":3}
fenlei = { '0battery': 0, '1pill_b': 0, '2pill_d': 0,'3can':1,\
           '4bottle':1,'5potato':3,'6pbailuobo':3,'7phuluobo':3,'8china':2,\
           '9cob':2,'10tile':2,'11cup':1,'1tablet':0,\
         '2can':1,'5medicinebag':0,'6bailuobo':3,'12':3,'16':3,\
    '17':3,'18':3,'19':3,'20':3,\
         '21Wapple':3,'22Wbanana':3,'23Wbocai':3,'24Whuluobo':3,\
         '25Wkiwi':3,'26Worange':3,'27Wpotato':3,'28Wqingcai':3,'29Wtomato':3,\
           "30Huluobotiao":3,"31Baicai":3,"32Tobatoo":0,"33Wood":2,"34Brick":2,"35pill":0,"36cup":1,"38youzipired":3}
serialName_list = arduino.search_arduino('e','g')
print(serialName_list)
serialFd_z = serial.Serial(serialName_list[0], 9600)
time.sleep(2)
serialFd_m = serial.Serial(serialName_list[1], 9600)
time.sleep(2)
loop_signal = True
full_signal = True
class HandInEyeCalibration:

    def get_m(self, points_camera, points_robot):
        """
        取得相机坐标转换到机器坐标的仿射矩阵
        :param points_camera:
        :param points_robot:
        :return:
        """
        # 确保两个点集的数量级不要差距过大，否则会输出None
        m, _ = cv2.estimateAffine2D(points_camera, points_robot)
        return m

    def get_points_robot(self, x_camera, y_camera, m):
        """
        相机坐标通过仿射矩阵变换取得机器坐标
        :param x_camera:
        :param y_camera:
        :return:
        """
        # m = self.get_m(STC_points_camera, STC_points_robot)
        robot_x = (m[0][0] * x_camera) + (m[0][1] * y_camera) + m[0][2]
        robot_y = (m[1][0] * x_camera) + (m[1][1] * y_camera) + m[1][2]
        return int(robot_x), int(robot_y)



def connect(n):
    LIST_Rubbish = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    if int(garbage["position"][1] - garbage["position"][0]) > int(
            garbage["position"][3] - garbage["position"][2]):
        fangxiang = 'Y'
    else:
        fangxiang = 'X'
    hang_eye = HandInEyeCalibration()
    m = hang_eye.get_m(STC_points_camera, STC_points_robot)
    x, y = hang_eye.get_points_robot(
        int((garbage["position"][0] + garbage["position"][1]) / 2),
        int((garbage["position"][2] + garbage["position"][3]) / 2), m)
    xinhao = LIST_Rubbish[n] + ',' + str(int(x)) + ',' + str(int(y)) + ',' + fangxiang
    serialFd_z.write(xinhao.encode())
    print(xinhao)
    while Ture:
        QApplication.processEvents()
        if serialFd_z.in_waiting:
            command = serialFd_z.read().decode()
            s = str(command)
            return s



class BackendThread_1(QThread):
    # 通过类成员对象定义信号
    update_date = pyqtSignal(int)
    # 处理业务逻辑
    geshu_one = 0
    def run(self):
        global garbage
        global loop_signal
        global garbage_thistime
        counter = 0
        cache = {}
        last_cache = {}
        lang_gabage = 0
        geshu_last = 0
        while True:
            QApplication.processEvents()
            if loop_signal and full_signal:
                rec, img = cap.read()
                crop_img = img[row_start:row_end, col_start:col_end]
                result, names = a.detect([crop_img])
                crop_img = result[0][0]  # 每一帧图片的处理结果图片
                # 每一帧图像的识别结果（可包含多个物体）
                cv2.imshow("vedio", crop_img)
                current_result = []
                for cls, (x1, y1, x2, y2), conf in result[0][1]:
                    current_result.append({"name": names[int(cls)], "position": [x1, x2, y1, y2], "confidence": float(conf),
                                           "difficulty": garbage_difficulty[names[int(cls)]]})
                if set(item["name"] for item in current_result) == cache and len(current_result)==lang_gabage:
                    counter += 1
                    if counter == 4:  # 连续三次相同的检测结果
                        # 如果垃圾个数为1，直接输出垃圾信息
                        if len(cache) == 1 and len(current_result) == 1:
                            garbage_name = current_result[0]["name"]
                            print(garbage_name)
                            c = fenlei[garbage_name]
                            garbage = current_result[0]
                            n = int(c)
                            s = str(connect(n))
                            garbage_thistime.append(int(c))
                            geshu_one = len(garbage_thistime)
                            print(geshu_one)
                            if s == 'e':
                                print(geshu_one)
                                self.update_date.emit(int(geshu_one))
                            geshu_last = 0
                            counter = 0
                        else:
                            if len(cache) != 0:
                                # 冒泡排序
                                sorted_garbage = sorted(current_result, key=lambda x: x["difficulty"], reverse=True)
                                # 输出最佳抓取结果
                                best_garbage = sorted_garbage[0]["name"]
                                garbage = sorted_garbage[0]
                                print(best_garbage)
                                c = fenlei[best_garbage]
                                n = int(c+4)
                                command = str(connect(n))
                                counter = 1
                                print(command)
                                QApplication.processEvents()
                                garbage_thistime.append(int(c))

                                if geshu_last == len(current_result) and last_cache == cache:
                                    garbage_thistime = garbage_thistime[0:-1]

                                geshu_last = len(current_result)
                                last_cache = cache
                                # best_info = current_result[best_garbage]
                                # print(f"最佳抓取垃圾: {best_garbage}, 位置: {best_info['position']}, 置信度: {best_info['confidence']}")
                else:
                    # 重置计数器和缓存
                    counter = 1
                    lang_gabage = len(current_result)
                    cache = set(item["name"] for item in current_result)
                if cv2.waitKey(1) == ord('q'):
                    break

class BackendThread_2(QThread):
    # 通过类成员对象定义信号
    update_date = pyqtSignal(int)
    # 处理业务逻辑
    def run(self):
        while True:
            QApplication.processEvents()
            serialFd_m.write('g,100,100,X'.encode())
            time.sleep(10)
            c_m = serialFd_m.read().decode()
            s = str(c_m)
            if s == 'a' or s == 'b' or s == 'c' or s == 'd':
                LIST_Rubbisz = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
                self.update_date.emit(int(LIST_Rubbisz[s]))


class Demo(QWidget):
    def __init__(self):
        super(Demo, self).__init__()
        self.playlist = QMediaPlaylist(self)
        # 从文件中加载UI定义
        self.ui = uic.loadUi("GUI.ui")
        self.initUI()
        # 视频播放器
        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)
        self.player.setVideoOutput(self.ui.wgt_player)
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('AAAAA.mp4')))
        self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        self.player.play()
        # 暂停键去掉
        # self.ui.Button.clicked.connect(self.playPause)  # 暂停 当按钮被点击时用括号里的函数来处理
        # self.ui.Button.clicked.connect(self.playPause)  # 暂停 当按钮被点击时用括号里的函数来处理

    def initUI(self):
        # 创建线程
        self.thread_1 = QThread()
        self.thread_2 = QThread()

        self.backend_1 = BackendThread_1()
        self.backend_2 = BackendThread_2()
        # 连接信号
        self.backend_1.update_date.connect(self.classify_rubbish)
        self.backend_1.moveToThread(self.thread_1)

        self.backend_2.update_date.connect(self.full)
        self.backend_2.moveToThread(self.thread_2)
        # 开始线程
        self.thread_1.started.connect(self.backend_1.run)
        self.thread_2.started.connect(self.backend_2.run)
        self.thread_1.start()
        self.thread_2.start()

        # 表格空间创建


    def full(self, n: int):
        global full_signal
        full_signal = False
        if n < 4:
            LIST_Rubbish = ['有害垃圾', '可回收垃圾' ,'其他垃圾', '厨余垃圾']
            reply = QMessageBox.warning(self, "消息框标题", LIST_Rubbish[n] + "已满！！！！(清理完毕请按Yes，退出程序请按No)",QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.No:
                print('退出')
                sys.exit(app.exec_())
            else:
                full_signal = True
                print("继续")
            QApplication.processEvents()

    def classify_rubbish(self, n: int):
        # 对外输出指挥动作
        global garbage_thistime
        list_show = [' ,有害垃圾', ' ,可回收垃圾', ' ,其他垃圾', ' ,厨余垃圾']
        global geshu
        geshu += 1
        print(geshu)
        self.ui.text.append(str(geshu))
        self.ui.text.ensureCursorVisible()
        for i in garbage_thistime:
            self.ui.text.insertPlainText(list_show[i])
            self.ui.text.ensureCursorVisible()
        self.ui.text.insertPlainText(' ' + str(len(garbage_thistime))+'  OK!!')
        garbage_thistime = []
        QApplication.processEvents()

    def playPause(self):
        if self.player.state() == 1:
            self.player.pause()
        else:
            self.player.play()

def screen():
    app = QApplication(sys)
    stats = Demo()
    stats.ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication([])
    stats = Demo()
    stats.ui.show()
    sys.exit(app.exec_())

