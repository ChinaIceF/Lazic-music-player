from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.Qt import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit
import numpy
import time



class AniScrollAreaFrameThread(QThread):
    time_changed_signal = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super(AniScrollAreaFrameThread, self).__init__(parent)
        self.parent = parent
        self.duration_frames = 12  # 动画持续帧数，单位 帧
  
    def run(self):
        #print('线程启动')
        # 这个线程起到一个刷帧器的作用，每隔一定时间，发射一个信号
        # 而真正改变框架位置的函数在原来的对象里，不由该线程内的方法提供
        
        # time.sleep方法在win11上不能提供高精度的计时器，所以只能把延时关了，用if判断时移
        time_mark = time.time()
        miss_hit = 0
        fps_limit = 120
        self.left_frames = self.duration_frames
        self.reset_timer_requset = False
        while self.left_frames > 0:

            time.sleep(1/120)  # win11不能高精度计时
            # 检测是否重置计数器
            if self.reset_timer_requset:
                #print('计时器重置')
                self.left_frames = self.duration_frames - 1
                self.reset_timer_requset = False
                
            # 检查是否到达指定延时
            if time.time() - time_mark >= 1/fps_limit:
                #print(1/ (time.time() - time_mark), miss_hit)
                miss_hit = 0
                self.left_frames -= 1
                time_mark = time.time()
                self.time_changed_signal.emit((self.duration_frames - self.left_frames) / self.duration_frames)
            else:
                miss_hit += 1
        #print('线程已终止')

class AniScrollArea(QLabel):
    def __init__(self, parent = None):
        super(AniScrollArea, self).__init__(parent)
        self.parent = parent

        self.frame_current_y = 0
        self.frame_target_y = 0
        self.frame_thread = AniScrollAreaFrameThread(self)
        self.frame_thread.time_changed_signal.connect(self.frame_ani_pos_change_handler)

    def setScrollFrame(self, obj, frame_height, body_height):
        self.scroll_frame = obj
        self.frame_height = frame_height
        self.h = body_height
        
    def frame_ani_pos_change_handler(self, progress):
        sy = self.frame_start_y
        ty = self.frame_target_y
        
        k=7
        d=0.8
        m=0.2
        t = ((2/(1+numpy.e**(-k*progress)) - 1) * d + m * progress) / (m+d)
        changed_y = int(sy * (1-t) + ty * t )  # 加0.5是为了四舍五入
        self.move_frame(changed_y)

    def move_frame(self, changed_y):
        self.scroll_frame.move(0, changed_y)

    def wheelEvent(self, event):
        dy = event.angleDelta().y()
        y = self.frame_target_y
        #self.is_scroll_limited = 0

        # 判断何时不应该滚动
        # 如果高度根本不需要滚动，直接禁用滚动
        if self.frame_height <= self.h:
            print('长度不够', self.frame_height, self.h)
            return
        # 如果滚到顶了，不滚了
        if y >= 0 and dy > 0:
            if self.frame_thread.isRunning() == False:
                self.scroll_frame.move(0, 0)
            return
        # 如果滚到底了，不滚了
        if y <= -self.frame_height+self.h and dy < 0:
            if self.frame_thread.isRunning() == False:
                self.scroll_frame.move(0, -self.frame_height+self.h)
            return
        # 如果目标滚动位置不合法，强制合法化
        target_y = y + int(dy / 120 * 40*3)
        target_y = 0 if target_y > 0 else target_y
        target_y = -self.frame_height+self.h if target_y < -self.frame_height+self.h else target_y

        self.frame_target_y = target_y
        self.frame_start_y = self.scroll_frame.pos().y()

        # 检测线程是否在运行中，如果不在运行，启动线程；如果在运行，重置线程计时器
        if self.frame_thread.isRunning():
            self.frame_thread.reset_timer_requset = True   # 请求重置，防止同时写入导致无效
        else:
            self.frame_thread.start()
