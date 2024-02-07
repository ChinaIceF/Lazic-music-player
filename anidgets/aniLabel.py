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
import gbvar

def ui_specified_change_func(self, g, o, c):
    # 几何
    self.setGeometry(int(g[0]), int(g[1]), int(g[2]), int(g[3]))
    
    # 透明度
    op = QtWidgets.QGraphicsOpacityEffect()
    op.setOpacity(o)
    self.parent.background_shadow.setGraphicsEffect(op)

def sinc_interpolation_func(t, pos_from, pos_to):
    k = 0.5 * (1 - numpy.cos(numpy.pi * t))
    interpolation = pos_from * (1-k) + pos_to * k
    return interpolation

def soft_in_out_interpolation_func(t, pos_from, pos_to):
    k = -2 * (t ** 3) + 3 * (t ** 2)
    interpolation = pos_from * (1-k) + pos_to * k
    return interpolation
    
def soft_in_out_interpolation_func_sqr(t, pos_from, pos_to):
    k = -2 * (t ** 6) + 3 * (t ** 4)
    interpolation = pos_from * (1-k) + pos_to * k
    return interpolation
    
def soft_in_out_interpolation_func_sqr_rev(t, pos_from, pos_to):
    k = 1 - (-2 * ((1-t) ** 6) + 3 * ((1-t) ** 4))
    interpolation = pos_from * (1-k) + pos_to * k
    return interpolation

def circle_out_func(t, pos_from, pos_to):
    k = (1 - (t - 1) ** 2) ** 0.5
    interpolation = pos_from * (1-k) + pos_to * k
    return interpolation

def cubic_root_func(t, pos_from, pos_to):
    k = t ** (1/3)
    interpolation = pos_from * (1-k) + pos_to * k
    return interpolation
    
def reversed_cubic_func(t, pos_from, pos_to):
    k = 1 - t ** (3)
    interpolation = pos_from * k + pos_to * (1-k)
    return interpolation

class AniLabel_Ani_Thread(QThread):
    time_changed_signal = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super(AniLabel_Ani_Thread, self).__init__(parent)
        self.parent = parent
        self.kill_thread_trigger = None
  
    def run(self):
        time_ticker = time.time() - 1
        start_time = time_ticker
        while (not self.parent.finish_flag) and (self.parent.state == self.sustain_thread_trigger):
            if time.time() - time_ticker >= 1 / 120:
                time_ticker = time.time()
                self.time_changed_signal.emit(0.5 * self.signal_direction)
            time.sleep(1/240)
        # 线程中止
        self.parent.finish_flag = False

class AniLabel(QLabel):
    def __init__(self, parent=None):
        super(AniLabel, self).__init__(parent)
        self.parent = parent
        self.interpolation_funcs = [sinc_interpolation_func] * 3   # 插值函数
        self.change_func = self.change_attribution
        self.additional_style = ''
        
        #gbvar.reg_hotkey('esc+a', self.Hotkey_handler)
        self.called_counts = 0
        
        # 绑定动画信号
        self.delta_pos = numpy.array((0, 0))
        self.finish_flag = False
        self.animation_progress = 0
        self.animation_finish_threshold = 16
        
        self.animation_forward_thread = AniLabel_Ani_Thread(self)
        self.animation_forward_thread.time_changed_signal.connect(self.change_position)
        self.animation_forward_thread.sustain_thread_trigger = 'forward'
        self.animation_forward_thread.signal_direction = 1
        
        self.animation_backward_thread = AniLabel_Ani_Thread(self)
        self.animation_backward_thread.time_changed_signal.connect(self.change_position)
        self.animation_backward_thread.sustain_thread_trigger = 'backward'
        self.animation_backward_thread.signal_direction = -1

    def attach_interpolation_func(self, func_g, func_o, func_c):
        self.interpolation_funcs = [func_g, func_o, func_c]

    def attach_geometry_keyframe(self, geometry_from, geometry_to):    #  几何属性应该是一个四个元素的数组
        self.geometry_from = numpy.array(geometry_from)
        self.geometry_to = numpy.array(geometry_to)
        
    def attach_opacity_keyframe(self, opacity_from, opacity_to):
        self.opacity_from = opacity_from
        self.opacity_to = opacity_to
        
    def attach_color_keyframe(self, color_from, color_to):
        self.color_from = numpy.array(color_from)
        self.color_to = numpy.array(color_to)

    def showEvent(self, event):
        self.original_position = numpy.array((self.x(), self.y()))

    def position_function(self, current_tick):
        x = 0
        y = (768 * (1 - 0.618) * 2) * ((-0.5 * (numpy.cos(numpy.pi * current_tick/self.animation_finish_threshold) - 1)) ** 1)
        return numpy.array((x, y), dtype = 'int16')
        #return numpy.array(-0.5 * (numpy.cos(numpy.pi * current_tick/self.animation_finish_threshold) - 1) * 24 * numpy.array((1, 0)), dtype = 'int16')
    
    def change_attribution(_, self, g, o, c):
        # 几何
        self.setGeometry(int(g[0]), int(g[1]), int(g[2]), int(g[3]))
        
        # 透明度
        op = QtWidgets.QGraphicsOpacityEffect()
        op.setOpacity(o)
        self.setGraphicsEffect(op)

        # 颜色
        self.setStyleSheet("background-color:rgba({},{},{},{})".format(int(c[0]), int(c[1]), int(c[2]), int(c[3]))+self.additional_style)
    
    def change_position(self, tick):
        self.animation_progress += tick
        if not (0 <= self.animation_progress < self.animation_finish_threshold):
            self.animation_progress = 0 if self.animation_progress < 0 else self.animation_progress
            self.animation_progress = self.animation_finish_threshold if self.animation_progress > self.animation_finish_threshold else self.animation_progress
            self.state = 'Finished'
        
        # 改变参数，更新一帧
        funcs = self.interpolation_funcs
        t = self.animation_progress / self.animation_finish_threshold
        g = funcs[0](t, self.geometry_from, self.geometry_to)
        o = funcs[1](t, self.opacity_from, self.opacity_to)
        c = funcs[2](t, self.color_from, self.color_to)
        
        self.change_func(self, g, o, c)

    def activate_forward_ani(self):
        #gbvar.gblog.log('forward 动画已激活，对象 {}'.format(self))
        self.state = 'forward'
        self.animation_forward_thread.start()

    def activate_backward_ani(self):
        #gbvar.gblog.log('backward 动画已激活，对象 {}'.format(self))
        self.state = 'backward'
        self.animation_backward_thread.start()
        
class AniProgressbarForSong(QLabel):
    def __init__(self, parent=None):
        super(AniProgressbarForSong, self).__init__(parent)
        self.parent = parent
        self.interpolation_funcs = [soft_in_out_interpolation_func] * 3   # 插值函数
        self.change_func = self.change_attribution
        self.additional_style = ''
        self.m_flag = False

        self.called_counts = 0
        
        frames = 6
        # 绑定动画信号
        self.delta_pos = numpy.array((0, 0))
        self.finish_flag = False
        self.animation_progress = 0
        self.animation_finish_threshold = frames
        
        self.animation_forward_thread = AniLabel_Ani_Thread(self)
        self.animation_forward_thread.time_changed_signal.connect(self.change_position)
        self.animation_forward_thread.sustain_thread_trigger = 'forward'
        self.animation_forward_thread.signal_direction = 1
        
        self.animation_backward_thread = AniLabel_Ani_Thread(self)
        self.animation_backward_thread.time_changed_signal.connect(self.change_position)
        self.animation_backward_thread.sustain_thread_trigger = 'backward'
        self.animation_backward_thread.signal_direction = -1

    def attach_interpolation_func(self, func_g, func_o, func_c):
        self.interpolation_funcs = [func_g, func_o, func_c]

    def attach_geometry_keyframe(self, geometry_from, geometry_to):    #  几何属性应该是一个四个元素的数组
        self.geometry_from = numpy.array(geometry_from)
        self.geometry_to = numpy.array(geometry_to)

    def showEvent(self, event):
        self.original_position = numpy.array((self.x(), self.y()))

    def change_attribution(_, self, g, o, c):
        bar = self.parent.progress_bar
        self.setGeometry(int(g[0]), int(g[1]), int(g[2]), int(g[3]))
        bar.setGeometry(0, 0, bar.width(), int(g[3]))

    def change_position(self, tick):
        self.animation_progress += tick
        if not (0 <= self.animation_progress < self.animation_finish_threshold):
            self.animation_progress = 0 if self.animation_progress < 0 else self.animation_progress
            self.animation_progress = self.animation_finish_threshold if self.animation_progress > self.animation_finish_threshold else self.animation_progress
            self.state = 'Finished'
        
        # 改变参数，更新一帧
        funcs = self.interpolation_funcs
        t = self.animation_progress / self.animation_finish_threshold
        g = funcs[0](t, self.geometry_from, self.geometry_to)
        
        self.change_func(self, g, None, None)
        
    def enterEvent(self, event):
        #gbvar.gblog.log('forward 动画已激活，对象 {}'.format(self))
        self.state = 'forward'
        self.animation_forward_thread.start()
        
        self.parent.time_label.state = 'forward'
        self.parent.time_label.animation_forward_thread.start()
        
    def leaveEvent(self, event):
        #gbvar.gblog.log('backward 动画已激活，对象 {}'.format(self))
        self.state = 'backward'
        self.animation_backward_thread.start()

        self.parent.time_label.state = 'backward'
        self.parent.time_label.animation_backward_thread.start()

    def mousePressEvent(self, event):
        self.m_flag = True
    
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_flag:
            x = int(event.localPos().x())
            t = x / 400
            t = 0 if t < 0 else t
            t = 1 if t > 1 else t
            self.parent.set_progress(t, 'fromMouseMove')
            self.t = t
            
    def mouseReleaseEvent(self, event):
        self.m_flag = False
        x = int(event.localPos().x())
        t = x / 400
        t = 0 if t < 0 else t
        t = 1 if t > 1 else t
        self.t = t
        self.parent.set_progress(t)

        gbvar.musicplayer.playmisson_threadlized.append(self.t)

    def activate_forward_ani(self):
        #gbvar.gblog.log('forward 动画已激活，对象 {}'.format(self))
        self.state = 'forward'
        self.animation_forward_thread.start()

    def activate_backward_ani(self):
        #gbvar.gblog.log('backward 动画已激活，对象 {}'.format(self))
        self.state = 'backward'
        self.animation_backward_thread.start()

class AniProgressbarValueForSong(QLabel):
    def __init__(self, parent=None):
        super(AniProgressbarValueForSong, self).__init__(parent)
        self.parent = parent
        self.interpolation_funcs = [soft_in_out_interpolation_func_sqr_rev] * 3   # 插值函数
        self.change_func = self.change_attribution
        self.additional_style = ''

        self.called_counts = 0
        
        frames = 6
        # 绑定动画信号
        self.delta_pos = numpy.array((0, 0))
        self.finish_flag = False
        self.animation_progress = 0
        self.animation_finish_threshold = frames
        
        self.animation_forward_thread = AniLabel_Ani_Thread(self)
        self.animation_forward_thread.time_changed_signal.connect(self.change_position)
        self.animation_forward_thread.sustain_thread_trigger = 'forward'
        self.animation_forward_thread.signal_direction = 1
        
        self.animation_backward_thread = AniLabel_Ani_Thread(self)
        self.animation_backward_thread.time_changed_signal.connect(self.change_position)
        self.animation_backward_thread.sustain_thread_trigger = 'backward'
        self.animation_backward_thread.signal_direction = -1

    def attach_interpolation_func(self, func_g, func_o, func_c):
        self.interpolation_funcs = [func_g, func_o, func_c]

    def attach_geometry_keyframe(self, geometry_from, geometry_to):    #  几何属性应该是一个四个元素的数组
        self.geometry_from = numpy.array(geometry_from)
        self.geometry_to = numpy.array(geometry_to)

    def showEvent(self, event):
        self.original_position = numpy.array((self.x(), self.y()))

    def change_attribution(_, self, g, o, c):
        self.setGeometry(int(g[0]), int(g[1]), int(g[2]), int(g[3]))

    def change_position(self, tick):
        self.animation_progress += tick
        if not (0 <= self.animation_progress < self.animation_finish_threshold):
            self.animation_progress = 0 if self.animation_progress < 0 else self.animation_progress
            self.animation_progress = self.animation_finish_threshold if self.animation_progress > self.animation_finish_threshold else self.animation_progress
            self.state = 'Finished'
        
        # 改变参数，更新一帧
        funcs = self.interpolation_funcs
        t = self.animation_progress / self.animation_finish_threshold
        g = funcs[0](t, self.geometry_from, self.geometry_to)
        
        self.change_func(self, g, None, None)

    def activate_forward_ani(self):
        self.animation_progress = 0
        #gbvar.gblog.log('forward 动画已激活，对象 {}'.format(self))
        self.state = 'forward'
        self.animation_forward_thread.start()

    def activate_backward_ani(self):
        #gbvar.gblog.log('backward 动画已激活，对象 {}'.format(self))
        self.state = 'backward'
        self.animation_backward_thread.start()

    def value_changed(self, value, source = None):
        if source == 'fromTimeChecking' and self.parent.m_flag:
            return
        self.attach_geometry_keyframe((0, 0, self.width(), self.height()), (0, 0, value, self.height()))  # value是整数
        self.activate_forward_ani()

class AniLabelLikeButton(QLabel):
    def __init__(self, parent=None):
        super(AniLabelLikeButton, self).__init__(parent)
        self.parent = parent
        self.interpolation_funcs = [soft_in_out_interpolation_func_sqr_rev] * 3   # 插值函数
        self.change_func = self.change_attribution
        self.additional_style = ''
        
        self.attached_function = []
        
        #gbvar.reg_hotkey('esc+a', self.Hotkey_handler)
        self.called_counts = 0
        
        frames = 8
        # 绑定动画信号
        self.delta_pos = numpy.array((0, 0))
        self.finish_flag = False
        self.animation_progress = 0
        self.animation_finish_threshold = frames
        
        self.animation_forward_thread = AniLabel_Ani_Thread(self)
        self.animation_forward_thread.time_changed_signal.connect(self.change_position)
        self.animation_forward_thread.sustain_thread_trigger = 'forward'
        self.animation_forward_thread.signal_direction = 1
        
        self.animation_backward_thread = AniLabel_Ani_Thread(self)
        self.animation_backward_thread.time_changed_signal.connect(self.change_position)
        self.animation_backward_thread.sustain_thread_trigger = 'backward'
        self.animation_backward_thread.signal_direction = -1

    def attach_interpolation_func(self, func_g, func_o, func_c):
        self.interpolation_funcs = [func_g, func_o, func_c]

    def attach_geometry_keyframe(self, geometry_from, geometry_to):    #  几何属性应该是一个四个元素的数组
        self.geometry_from = numpy.array(geometry_from)
        self.geometry_to = numpy.array(geometry_to)
        
    def attach_opacity_keyframe(self, opacity_from, opacity_to):
        self.opacity_from = opacity_from
        self.opacity_to = opacity_to
        
    def attach_color_keyframe(self, color_from, color_to):
        self.color_from = numpy.array(color_from)
        self.color_to = numpy.array(color_to)

    def showEvent(self, event):
        self.original_position = numpy.array((self.x(), self.y()))
        
    def change_attribution(_, self, g, o, c):
        # 几何
        self.setGeometry(int(g[0]), int(g[1]), int(g[2]), int(g[3]))

        # 颜色
        self.setStyleSheet("background-color:rgba({},{},{},{});".format(int(c[0]), int(c[1]), int(c[2]), int(c[3]))+self.additional_style)

    
    def change_position(self, tick):
        self.animation_progress += tick
        if not (0 <= self.animation_progress < self.animation_finish_threshold):
            self.animation_progress = 0 if self.animation_progress < 0 else self.animation_progress
            self.animation_progress = self.animation_finish_threshold if self.animation_progress > self.animation_finish_threshold else self.animation_progress
            self.state = 'Finished'
        
        # 改变参数，更新一帧
        funcs = self.interpolation_funcs
        t = self.animation_progress / self.animation_finish_threshold
        g = funcs[0](t, self.geometry_from, self.geometry_to)
        c = funcs[2](t, self.color_from, self.color_to)
        #print(t, self.animation_progress)
        self.change_func(self, g, None, c)

    def activate_forward_ani(self):
        #gbvar.gblog.log('forward 动画已激活，对象 {}'.format(self))
        self.state = 'forward'
        self.animation_forward_thread.start()

    def activate_backward_ani(self):
        #gbvar.gblog.log('backward 动画已激活，对象 {}'.format(self))
        self.state = 'backward'
        self.animation_backward_thread.start()

    def enterEvent(self, event):
        self.activate_forward_ani()
        
    def leaveEvent(self, event):
        self.activate_backward_ani()
        
    def mousePressEvent(self, event):
        for func in self.attached_function:
            func()










class aniDownloadLabel(QLabel):
    def __init__(self, parent=None):
        super(aniDownloadLabel, self).__init__(parent)
        self.parent = parent

    def showEvent(self, event):
        self.initalize()
        
    def initalize(self):
        self.setStyleSheet("background-color:#3e3e3e; border-radius: 10px")
        self.resize(560, 64)
        
        self.progress_bar = AniLabel(self)
        self.progress_bar.setGeometry(64, 52, 480, 6)
        self.progress_bar.setStyleSheet("border-radius: 3px")
        self.progress_bar.additional_style = ";border-radius: 3px;"
        self.progress_bar.attach_interpolation_func(soft_in_out_interpolation_func, soft_in_out_interpolation_func, soft_in_out_interpolation_func)
        self.progress_bar.attach_geometry_keyframe((64, 58, 0, 6), (64, 58, 480, 6))
        self.progress_bar.attach_opacity_keyframe(1, 1)
        self.progress_bar.attach_color_keyframe((200, 160, 0, 255), (200, 160, 0, 255))
        self.progress_bar.Hotkey_handler = lambda : gbvar.Hotkey_handler_UI(self.progress_bar)
        gbvar.reg_hotkey('esc+w', self.progress_bar.Hotkey_handler)
        self.progress_bar.show()

















