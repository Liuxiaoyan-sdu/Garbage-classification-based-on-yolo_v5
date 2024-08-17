import serial.tools.list_ports
import time
class Ture:
    pass
def search_arduino(flag_1,flag_2):
    ports = ["COM9", "COM7"]
    comnum_list = [" ", " "]
    # 输出所有串口的信息
    for port in ports:
        comnum = port
    # ports = list(serial.tools.list_ports.comports())
    # comnum_list = [" ", " "]
    # # 输出所有串口的信息
    # for port in ports:
    #     comnum = list(port)[0]
        print("connect ", comnum)  # 设置要使用的串口号
        ser = serial.Serial(comnum, baudrate=9600, timeout=1)
        time.sleep(2)
        # 发送字符串
        s = 'F'
        ser.write('i,100,100,X'.encode())
        while Ture:
            if ser.in_waiting:
                # 读数据
                s = str(ser.read().decode())
                break
        print(s)
        ser.close()
        if s == flag_1:
            print('Received on port_1: ' + comnum)
            comnum_list[0] = comnum
        if s == flag_2:
            # 返回串口号
            print('Received on port_2: ' + comnum)
            comnum_list[1] = comnum
    return comnum_list
