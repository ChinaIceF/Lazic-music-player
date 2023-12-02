import time

class Log(object):
    def __init__(self, debug = True, parent = None):
        self.parent = parent
        self.debug = debug
        self.start_time = time.time()
        self.level_text = ['INFO', 'WARN', 'ERROR', 'FATAL']
        
        self.all_log = []
    
    def time(self):
        return time.asctime()
    
    def log(self, text, level = 0):
        new_time = time.time()
        new_text = '[{}][{}] {}'.format(self.time(), self.level_text[level], text)
        self.all_log.append([new_time, level, text])
        if self.debug:
            print(new_text)