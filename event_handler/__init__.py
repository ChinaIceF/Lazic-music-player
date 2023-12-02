'''
Event Handler
各种键盘，鼠标事件的全局处理模块
'''
import time
import event_handler.keyevent
import event_handler.timeChecking
import gbvar

def test_func():
    gbvar.gblog.log('按下组合键')

Evt_monitor = event_handler.keyevent.EventMonitor()
Evt_monitor.register('esc+q', test_func)


def start():
    while True:
        time.sleep(0.001)
        if len(gbvar.musicplayer.playmisson_threadlized) > 0:
            gbvar.musicplayer.play(gbvar.musicplayer.playmisson_threadlized.pop(0))
        
        gbvar.musicplayer.timer.update_ui()