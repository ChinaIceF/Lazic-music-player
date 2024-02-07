import gbvar
import log
gbvar.gblog = log.Log()
gbvar.gblog.log('OSUMusicPlayer 日志记录开始')

import music
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore
import threading as td
import sys
import os

import ui as ui
import event_handler

def td_event_handler():
    gbvar.gblog.log('事件处理线程已启动')
    event_handler.start()

if __name__ == '__main__':

    gbvar.musicplayer = music.musicPlayer()

    for file in list(os.walk('./songListTest/'))[0][2]:
        try:
            gbvar.musicplayer.add('./songListTest/' + file)
        except:
            print('Ignored file {} which failed to load.'.format(file))

    gbvar.musicplayer.load_by_number(index = 0)

    os.environ['QT_FONT_DPI'] = '96'
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    App = QApplication(sys.argv)

    Window = ui.UserInterface()
    gbvar.ui = Window
    
    gbvar.gblog.log('正在启动事件处理线程')
    EventHandler_thread = td.Thread(target = td_event_handler, daemon = True)
    EventHandler_thread.start()
    
    gbvar.musicplayer.change_song_and_play(index = 0)  # 开始播放第一首歌
    
    Window.show()
    sys.exit(App.exec_())