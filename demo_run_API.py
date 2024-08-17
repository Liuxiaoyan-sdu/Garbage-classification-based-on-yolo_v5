import cv2
import detect_with_API
import torch
import pyrealsense2 as rs
import numpy as np

import time
row_start = 55
row_end = 450
col_start = 150
col_end = 545
cap = cv2.VideoCapture(1)  # 0
cap.set(3,640)#长
cap.set(4,640)#宽

cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25表示关闭自动曝光
# 设置曝光参数
cap.set(cv2.CAP_PROP_EXPOSURE, -8)  # 负值表示减少曝光

a = detect_with_API.detectapi(weights='best_1207      .pt')

if __name__ == '__main__':
    m = 0
    GG_last = 0
    GG_new = -1
    with torch.no_grad():
        while True:
            rec, img = cap.read()
            crop_img = img[row_start:row_end, col_start:col_end]  # 剪裁
            result, names = a.detect([crop_img])
            img = result[0][0]  # 每一帧图片的处理结果图片
            # 每一帧图像的识别结果（可包含多个物体）
            n = 0

            for cls, (x1, y1, x2, y2), conf in result[0][1]:
                n=n+1
                #print(names[cls], x1, y1, x2, y2, conf)  # 识别物体种类、左上角x坐标、左上角y轴坐标、右下角x轴坐标、右下角y轴坐标，置信度
                '''
                cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0))
                cv2.putText(img,names[cls],(x1,y1-20),cv2.FONT_HERSHEY_DUPLEX,1.5,(255,0,0))         
                '''
                GG_new = names[cls]
            if n == 1 and GG_new == GG_last :
                m = m + 1
            else :
                m = 0
            GG_last = GG_new

            if m == 2:
                print (GG_last )
                m = 0
                GG_last = 0
                GG_new = -1

            cv2.imshow("vedio",img)

            if cv2.waitKey(1) == ord('q'):
                break