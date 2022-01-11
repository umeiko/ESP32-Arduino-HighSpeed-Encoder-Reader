import serial
import matplotlib.pyplot as plt
import time
import json
from collections import deque
import struct
import threading
from matplotlib.animation import FuncAnimation



class encoder_decoder:
    """一个简单的微分器"""
    def __init__(self, filter_len=20, dt=2e-3):
        self.temps = deque(maxlen=filter_len+1)
        self.dt = dt
        self.t_len_1 = (filter_len) * dt
    
    def spd_calc(self, dis_mm):
        
        self.temps.append(dis_mm)
        spd = (self.temps[-1] - self.temps[0]) / self.t_len_1
        return spd
    
    def __call__(self, dis_mm):
        return self.spd_calc(dis_mm)


def data_finder(encoder_uart):
    """从串口中寻找起始符（7FFF）,并读取后续数据"""
    check = deque(maxlen=2)
    check.append(encoder_uart.read())
    msg = None
    for i in range(300):
        check.append(encoder_uart.read())
        if check[0] == b"\x7f" and check[1] == b"\xff":
            msg = encoder_uart.read(200)
            break
    return msg



def data_deal_s(data, last_s):
    dis_mm = []
    s = []
    v = 0
    if data is not None:
        data = struct.unpack(">100h", data)    
        for k, i in  enumerate(data):
            dis_mm.append(i * 0.1047197551)
            s.append(last_s + (k+1)*100e-6)
        v = (dis_mm[-1] - dis_mm[0]) / ((k+1)*100e-6)
    return dis_mm, s, v


class uart_flasher(threading.Thread):
    def __init__(self, uart, options) -> None:
        threading.Thread.__init__(self)
        self.vs = deque(maxlen=options["MAXLEN"])
        self.ds = deque(maxlen=100*options["MAXLEN"])
        self.frames_d = deque(maxlen=100*options["MAXLEN"])
        self.frames_v = deque(maxlen=options["MAXLEN"])
        self.uart = uart
        self.Calc = encoder_decoder(options["FILTER_LEN"], options["TIME_INTERVAL"])
    
    def run(self):
        frame =  0
        last_s = 0
        while uart.isOpen():
            if uart.in_waiting:
                frame += 1
                data = data_finder(self.uart)
                dis_mm, t_dis, v_mmps = data_deal_s(data, last_s)
                self.vs.append(v_mmps)
                self.ds += dis_mm
                self.frames_v.append(frame*10000e-6)
                self.frames_d += t_dis
                last_s = t_dis[-1]


if __name__ == "__main__":
    with open("config.json", "r") as f:
        options = json.load(f)

    uart = serial.Serial(port=options["PORT_NAME"], baudrate=options["BAUDRATE"])
    
    
    Flasher = uart_flasher(uart, options)
    Flasher.start()
    fig, ax = plt.subplots(2,1)
    fig.canvas.set_window_title(options["PORT_NAME"]+","+str(options["BAUDRATE"]))
    plt.subplots_adjust(wspace=0, hspace=0.3)
    
    ln0, = ax[0].plot([], [])
    ln1, = ax[1].plot([], [])

    def init():
        ax[0].set_title("Distanse: mm")
        ax[1].set_title("Speed: mm/s")
        
        return ln0, ln1,

    def update(frame):
        ax[0].set_xlim(Flasher.frames_d[0], Flasher.frames_d[-1])
        ax[0].set_ylim(min(Flasher.ds)-10, max(Flasher.ds)+10)
        ln0.set_data(Flasher.frames_d, Flasher.ds)

        ax[1].set_xlim(Flasher.frames_v[0], Flasher.frames_v[-1])
        ax[1].set_ylim(min(Flasher.vs)-10, max(Flasher.vs)+10)
        ln1.set_data(Flasher.frames_v, Flasher.vs)
        ax[0].set_title("Distanse: {:.2f} mm".format(Flasher.ds[-1]))
        ax[1].set_title("Speed: {:.2f} mm/s".format(Flasher.vs[-1]))
        return ln0, ln1,
    
    ani = FuncAnimation(fig, update,
                        init_func=init, interval=1)
    
    plt.show()
    print("退出程序")
    uart.close()
    exit()