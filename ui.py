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

import anidgets
import gbvar

def perfectFont(name, size, switch):
    font = QFont(name, size, switch)
    font.setStyleStrategy(QFont.PreferAntialias)
    font.setHintingPreference(QFont.PreferFullHinting)
    #font.setSmoothlyScalable(True)
    return font
    
def Hotkey_handler_UI(obj=None):
        obj.called_counts += 1
        if obj.called_counts % 2 == 0:
            obj.activate_backward_ani()
        else:
            obj.activate_forward_ani()

gbvar.Hotkey_handler_UI = Hotkey_handler_UI

def animation_trigger(obj=None):
        obj.called_counts += 1
        if obj.called_counts % 2 == 0:
            obj.activate_backward_ani()
        else:
            obj.activate_forward_ani()


class PlayerInterface(QLabel):
    def __init__(self, parent = None):
        super(PlayerInterface, self).__init__(parent)
        self.parent = parent
        
        gbvar.update_infomation = self.refresh_info
        self.playing_index_historial = -1
        
        ##  背景图
        self.player_head_bg = QtWidgets.QLabel(self)
        self.player_head_bg.setGeometry(0, 0, 400, 128)
        self.player_head_bg.setAlignment(QtCore.Qt.AlignCenter|Qt.AlignCenter)
        self.player_head_bg.setStyleSheet("background-image:url(./images/bgtest.png);border-radius:6px")

        #self.player_head_bg.setPixmap(QtGui.QPixmap('./images/bgtest.png'))
        
        ##  背景图阴影
        self.player_head_shadow = QtWidgets.QLabel(self)
        self.player_head_shadow.setGeometry(0, 0, 400, 128)
        self.player_head_shadow.setStyleSheet("background-color:#30000000;border-radius:6px")
        
        ##  歌曲名
        self.song_title_sd = QtWidgets.QLabel(self)
        self.song_title_sd.setGeometry(64, 13, 400 - 128, 32)
        self.song_title_sd.setStyleSheet("color:#222222")
        self.song_title_sd.setFont(perfectFont("微软雅黑",12, QFont.Normal))
        self.song_title_sd.setAlignment(QtCore.Qt.AlignCenter|Qt.AlignCenter)
        self.song_title_sd.setText('')
        
        self.song_title = QtWidgets.QLabel(self)
        self.song_title.setGeometry(64, 12, 400 - 128, 32)
        self.song_title.setStyleSheet("color:#ffffff")
        self.song_title.setFont(perfectFont("微软雅黑",12, QFont.Normal))
        self.song_title.setAlignment(QtCore.Qt.AlignCenter|Qt.AlignCenter)
        self.song_title.setText('')
        
        ##  作者
        self.song_author_sd = QtWidgets.QLabel(self)
        self.song_author_sd.setGeometry(63, 45, 400 - 128, 16)
        self.song_author_sd.setStyleSheet("color:#222222")
        self.song_author_sd.setFont(perfectFont("微软雅黑",8, QFont.Bold))
        self.song_author_sd.setAlignment(QtCore.Qt.AlignCenter|Qt.AlignCenter)
        self.song_author_sd.setText('')
        
        self.song_author = QtWidgets.QLabel(self)
        self.song_author.setGeometry(64, 44, 400 - 128, 16)
        self.song_author.setStyleSheet("color:#ffffff")
        self.song_author.setFont(perfectFont("微软雅黑",8, QFont.Bold))
        self.song_author.setAlignment(QtCore.Qt.AlignCenter|Qt.AlignCenter)
        self.song_author.setText('')

        ## 操作框阴影
        self.buttons_sd = QtWidgets.QLabel(self)
        self.buttons_sd.setGeometry(0, 74, 400, 128 - 74)
        self.buttons_sd.setStyleSheet("background-color:#90000000;border-bottom-left-radius:6px;border-bottom-right-radius:6px")

        ##  时长
        self.time_label = anidgets.anidgets.AniLabel(self)
        self.time_label.setGeometry(4, 116, 128, 12)
        self.time_label.attach_geometry_keyframe((4, 116, 128, 12), (4, 102, 128, 12))
        self.time_label.attach_opacity_keyframe(0, 0.999)
        self.time_label.attach_color_keyframe((0, 0, 0, 0), (0, 0, 0, 0))
        self.time_label.interpolation_funcs = [anidgets.aniLabel.soft_in_out_interpolation_func_sqr_rev] * 3
        self.time_label.setFont(perfectFont("微软雅黑",6, QFont.Bold))
        self.time_label.additional_style = ";color:#ffcc22;"
        self.time_label.setText('11:45 · 14:19')

        ##  进度条
        self.progress_bar_bg = anidgets.anidgets.AniProgressbarForSong(self)
        self.progress_bar_bg.attach_geometry_keyframe((0, 123, 400, 6), (0, 119, 400, 10))
        self.progress_bar_bg.setGeometry(0, 123, 400, 6)
        self.progress_bar_bg.setStyleSheet("background-color:#7aff9000;border-bottom-left-radius:6px;border-bottom-right-radius:6px")
        self.progress_bar_bg.parent = self
        
        self.progress_bar = anidgets.anidgets.AniProgressbarValueForSong(self.progress_bar_bg)
        self.progress_bar.setGeometry(0, 0, 0, 6)
        self.progress_bar.setStyleSheet("background-color:#ffcc22;border-bottom-right-radius:0px")
        
        ##  列表按键
        self.button_openlist = anidgets.anidgets.AniLabelLikeButton(self)
        self.button_openlist.setGeometry(400 - 45, 84, 32, 32)
        self.button_openlist.attach_geometry_keyframe((400 - 45, 84, 32, 32), (400 - 45, 84, 32, 32))
        self.button_openlist.attach_color_keyframe((255, 204, 34, 0), (255, 204, 34, 160))
        self.button_openlist.setAlignment(QtCore.Qt.AlignCenter|Qt.AlignCenter)
        self.button_openlist.setPixmap(QtGui.QPixmap('./images/openlist.png',))
        self.button_openlist.setScaledContents(False)
        self.button_openlist.additional_style = 'border-radius:6px'
        #self.button_openlist.setStyleSheet("background-color:#ffcc22;border-radius:6px")
        
        ##  设置按键
        self.button_settings = anidgets.anidgets.AniLabelLikeButton(self)
        self.button_settings.setGeometry(400 - 45 - 32 - 12, 84, 32, 32)
        self.button_settings.attach_geometry_keyframe((400 - 45 - 32 - 12, 84, 32, 32), (400 - 45 - 32 - 12, 84, 32, 32))
        self.button_settings.attach_color_keyframe((255, 204, 34, 0), (255, 204, 34, 160))
        self.button_settings.setAlignment(QtCore.Qt.AlignCenter|Qt.AlignCenter)
        self.button_settings.setPixmap(QtGui.QPixmap('./images/settings.png',))
        self.button_settings.setScaledContents(False)
        self.button_settings.additional_style = 'border-radius:6px'
        
        ##  下一曲
        self.button_next_song = anidgets.anidgets.AniLabelLikeButton(self)
        self.button_next_song.setGeometry(200 + 20 + 8, 84, 32, 32)
        self.button_next_song.attach_geometry_keyframe((200 + 20 + 8, 84, 32, 32), (200 + 20 + 8, 84, 32, 32))
        self.button_next_song.attach_color_keyframe((255, 204, 34, 0), (255, 204, 34, 160))
        self.button_next_song.setAlignment(QtCore.Qt.AlignCenter|Qt.AlignCenter)
        self.button_next_song.setPixmap(QtGui.QPixmap('./images/next_song.png',))
        self.button_next_song.setScaledContents(False)
        self.button_next_song.additional_style = 'border-radius:6px'
        self.button_next_song.attached_function.append(lambda : gbvar.musicplayer.change_song_and_play(delta = 1))
        
        ##  暂停
        self.button_pause_and_resume = QtWidgets.QLabel(self)
        self.button_pause_and_resume.setGeometry(200 - 20 - 4, 76, 40, 40)
        self.button_pause_and_resume.setAlignment(QtCore.Qt.AlignCenter|Qt.AlignCenter)
        self.button_pause_and_resume.setPixmap(QtGui.QPixmap('./images/pause.png',))
        self.button_pause_and_resume.setScaledContents(False)
        
        ##  上一曲
        self.button_prev_song = anidgets.anidgets.AniLabelLikeButton(self)
        self.button_prev_song.setGeometry(200 - 20 - 8 - 40, 84, 32, 32)
        self.button_prev_song.attach_geometry_keyframe((200 - 20 - 8 - 40, 84, 32, 32), (200 - 20 - 8 - 40, 84, 32, 32))
        self.button_prev_song.attach_color_keyframe((255, 204, 34, 0), (255, 204, 34, 160))
        self.button_prev_song.setAlignment(QtCore.Qt.AlignCenter|Qt.AlignCenter)
        self.button_prev_song.setPixmap(QtGui.QPixmap('./images/prev_song.png',))
        self.button_prev_song.setScaledContents(False)
        self.button_prev_song.additional_style = 'border-radius:6px'
        self.button_prev_song.attached_function.append(lambda : gbvar.musicplayer.change_song_and_play(delta = -1))



    def refresh_info(self, update_cover = False):  # 更新 UI 面板上的信息，使用 update_cover = True 强制刷新封面
        mp = gbvar.musicplayer
        time_passed = mp.timer.get_time_passed()
        duration = mp.playing_duration
        
        self.set_song_info(mp.playing_title, mp.playing_artist)
        self.set_time_info(time_passed, duration)
        
        if self.playing_index_historial != mp.playing_index or update_cover:
            self.playing_index_historial = mp.playing_index
            cover_path = mp.playing_cover_path
            self.player_head_bg.setStyleSheet("background-image:url({});border-radius:6px".format(cover_path))

    def set_time_info(self, time_passed, duration):
        self.set_progress(time_passed / duration, 'fromTimeChecking')  # 这里传递一个标签，防止交互时仍然刷新
        self.time_label.setText('{:02d}:{:02d} · {:02d}:{:02d}'.format(int(time_passed/60), int(time_passed%60), int(duration/60), int(duration%60),))

    def set_progress(self, precent, source = None):
        max_pixel = 400
        x = int(max_pixel * precent + 0.5)
        self.progress_bar.value_changed(x, source)
       
    def set_song_info(self, title, author):
        self.song_title_sd.setText(title)
        self.song_title.setText(title)
        self.song_author_sd.setText(author)
        self.song_author.setText(author)
    

class SelecterInterface(QLabel):
    def __init__(self, parent = None):
        super(SelecterInterface, self).__init__(parent)
        self.parent = parent
        
        self.selecter_body = anidgets.aniLabel.AniLabel(self)
        self.selecter_body.setGeometry(0, 0, 400, 556)   #  初始折叠状态没有厚度
        self.selecter_body.attach_geometry_keyframe((0, 0, 400, 0), (0, 0, 400, 556))
        self.selecter_body.attach_opacity_keyframe(0, 1)
        self.selecter_body.attach_color_keyframe((51, 51, 51, 255), (51, 51, 51, 255))
        self.selecter_body.additional_style = ';border-radius:6px'
        self.selecter_body.interpolation_funcs = [anidgets.aniLabel.soft_in_out_interpolation_func_sqr_rev, anidgets.aniLabel.circle_out_func, anidgets.aniLabel.soft_in_out_interpolation_func_sqr_rev]
        # 此时已经定义完毕，可以给主界面的按钮绑定函数了
        print(type(self.parent))
        self.parent.parent.player_interface.button_openlist.attached_function.append(lambda : animation_trigger(self.selecter_body))
        
        
        
        
        
        
        


class moveWindow(QLabel):
    def __init__(self, parent, window):
        super(moveWindow, self).__init__(parent)
        self.parent = parent
        self.window = window
        self.flag = False
    
    def mousePressEvent(self, event):
        self.m_flag = True
        self.setCursor(QCursor(Qt.SizeAllCursor))
        self.m_Position = event.globalPos() - self.window.pos() 
    
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_flag:
            self.window.move(event.globalPos() - self.m_Position)  # 更改窗口位置
            event.accept()
 
    def mouseReleaseEvent(self, event):
        self.flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

class UserInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        gbvar.gblog.log('初始化图形界面')
        self._font_title = QFont("微软雅黑",11, QFont.Normal)
        
        self.initUI()
    
    def initUI(self):
        '''

        '''
    
        self.setWindowFlags(Qt.FramelessWindowHint)  # 去边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setGeometry(0, 0, 440, 740)
        self.setWindowTitle("Testing")
        self.setWindowFlag(Qt.WindowStaysOnTopHint,True)

        self._frame = QtWidgets.QLabel(self)
        self._frame.setGeometry(0, 0, 440, 740)
        
        self._frame_head = QtWidgets.QLabel(self)
        self._frame_head.setGeometry(0, 0, 440, 168)
        
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)  # 阴影模糊半径
        shadow.setColor(QtGui.QColor(0, 0, 0, 100))  # 阴影颜色和不透明度
        shadow.setOffset(0, 0)  # 阴影偏移量
        self._frame_head.setGraphicsEffect(shadow)
        
        self.player_head = QtWidgets.QLabel(self._frame_head)
        self.player_head.setGeometry(0 + 20, 0 + 20, 400, 128)
        
        ## 小窗口模式界面（主面板
        self.player_interface = PlayerInterface(self.player_head)
        self.player_interface.setGeometry(0, 0, 400, 128)
        self.player_interface.set_progress(0.4)
        #self.player_interface.set_infomation('Theres the name of songs', 'name of author')
        
        ##  拖动窗口事件handler 这个玩意要置顶（即必须最后实例化） 要不然摸不到
        self.window_mover = moveWindow(self.player_head, self)
        self.window_mover.setGeometry(0, 0, 400, 48)
        
        self.opreation_body = QtWidgets.QLabel(self._frame)
        self.opreation_body.setGeometry(0 + 20, 144 + 20, 400, 556)
        self.opreation_body.parent = self
        
        ##  选歌菜单
        self.selecter_interface = SelecterInterface(self.opreation_body)
        self.selecter_interface.setGeometry(0, 0, 400, 556)
        


        
        
        
        
        '''
        self.background_shadow = QtWidgets.QLabel(self)
        self.background_shadow.setGeometry(0, 0, 1366, 768)
        self.background_shadow.setStyleSheet("background-color:#70000000;")
        op = QtWidgets.QGraphicsOpacityEffect()
        op.setOpacity(0)
        self.background_shadow.setGraphicsEffect(op)
        
        self.interface_frame = anidgets.AniLabel(self)
        self.interface_frame.setGeometry(0, 768, 1366, 768)
        self.interface_frame.attach_interpolation_func(anidgets.aniLabel.soft_in_out_interpolation_func_sqr, anidgets.aniLabel.soft_in_out_interpolation_func_sqr, anidgets.aniLabel.soft_in_out_interpolation_func_sqr)
        self.interface_frame.attach_geometry_keyframe((0, 0, 1366, 768), (0, 768, 1366, 768))
        self.interface_frame.attach_opacity_keyframe(1, 0)
        self.interface_frame.attach_color_keyframe((0, 0, 0, 0), (0, 0, 0, 0))
        self.interface_frame.change_func = anidgets.aniLabel.ui_specified_change_func
        self.interface_frame.Hotkey_handler = lambda : Hotkey_handler_UI(self.interface_frame)
        gbvar.reg_hotkey('esc+a', self.interface_frame.Hotkey_handler)
        
        #  带颜色的主界面背景
        w = int(1366 * 0.8)
        h = int(768)
        self.main_interface = QtWidgets.QLabel(self.interface_frame)
        self.main_interface.setGeometry(int((1366 - w) / 2), 768 - h, w, h)
        self.main_interface.setStyleSheet("background-color:#302e39")
        
        #  原始界面框架
        self.interface_0_frame = QtWidgets.QLabel(self.main_interface)
        self.interface_0_frame.setGeometry(0, 0, w, h)
        
        self.interface_0_headbg = QtWidgets.QLabel(self.interface_0_frame)
        self.interface_0_headbg.setGeometry(0, 0, w, 128)
        self.interface_0_headbg.setPixmap(QtGui.QPixmap('./images/head_bg.png'))
        
        self.interface_0_title = QtWidgets.QLabel(self.interface_0_frame)
        self.interface_0_title.setGeometry(0, 128, w, 64)
        self.interface_0_title.setStyleSheet("background-color:#22202e")
        
        self.interface_0_title_icon = QtWidgets.QLabel(self.interface_0_title)
        self.interface_0_title_icon.setGeometry(80, 19, 26, 26)
        self.interface_0_title_icon.setPixmap(QtGui.QPixmap('./images/0_icon.png'))
        
        self.interface_0_title_text = QtWidgets.QLabel(self.interface_0_title)
        self.interface_0_title_text.setGeometry(128, 0, w, 64)
        self.interface_0_title_text.setFont(self._font_title)
        self.interface_0_title_text.setAlignment(QtCore.Qt.AlignLeft|Qt.AlignVCenter)
        self.interface_0_title_text.setStyleSheet("background-color:#00000000;color:#ffffff;")
        self.interface_0_title_text.setText('主菜单')
        
        
        
        
        

        self.test_widget = anidgets.AniLabel(self.main_interface)
        self.test_widget.setGeometry(0, 0, 1366, 768)
        self.test_widget.setStyleSheet("border-radius: 12px")
        self.test_widget.additional_style = ";border-radius: 12px;"
        self.test_widget.attach_interpolation_func(anidgets.aniLabel.soft_in_out_interpolation_func_sqr, anidgets.aniLabel.soft_in_out_interpolation_func_sqr, anidgets.aniLabel.soft_in_out_interpolation_func_sqr)
        self.test_widget.attach_geometry_keyframe((80, 60, 360, 120), (50, 50, 120, 48))
        self.test_widget.attach_opacity_keyframe(1, 1)
        self.test_widget.attach_color_keyframe((36, 35, 43, 255), (36, 35, 43, 255))
        self.test_widget.Hotkey_handler = lambda : Hotkey_handler_UI(self.test_widget)
        gbvar.reg_hotkey('esc+s', self.test_widget.Hotkey_handler)
        self.test_widge_2 = anidgets.aniLabel.aniDownloadLabel(self.main_interface)
        self.test_widge_2.move(64, 300)
        '''