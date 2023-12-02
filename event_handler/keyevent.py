import keyboard
import msvcrt
import gbvar

class EventMonitor(object):
    def __init__(self, parent = None):
        self.parent = None
        gbvar.reg_hotkey = self.register
        
    def register(self, keynames, event_function):
        keyboard.add_hotkey(keynames, event_function)
        gbvar.gblog.log(keynames + ' 已绑定到函数 ' + str(event_function))
