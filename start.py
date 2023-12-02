import gbvar
import log
gbvar.gblog = log.Log()
gbvar.gblog.log('OSUMusicPlayer 日志记录开始')

import music
from PyQt5.QtWidgets import QApplication, QMainWindow
import threading as td
import sys

import ui as ui
import event_handler

def td_event_handler():
    gbvar.gblog.log('事件处理线程已启动')
    event_handler.start()

if __name__ == '__main__':

    gbvar.musicplayer.add('インドア系ならトラックメイカー.flac')
    gbvar.musicplayer.add('Eric Fullerton - MinecraftEnd.mp3')
    gbvar.musicplayer.load_by_number(index = 0)
    gbvar.musicplayer.play(0.0)

    App = QApplication(sys.argv)
    Window = ui.UserInterface()
    
    gbvar.gblog.log('正在启动事件处理线程')
    EventHandler_thread = td.Thread(target = td_event_handler, daemon = True)
    EventHandler_thread.start()
    
    Window.show()
    sys.exit(App.exec_())