import time
import gbvar

class Timer:
    def __init__(self):
        self.start_time = None
        self.paused_time = None
        self.is_running = False

    def start(self, delta = 0):
        if not self.is_running:
            self.start_time = time.perf_counter() - delta
            self.is_running = True

    def stop(self):
        if self.is_running:
            self.paused_time = time.perf_counter() - self.start_time
            self.start_time = None
            self.is_running = False

    def pause(self):
        if self.is_running:
            self.paused_time = time.perf_counter() - self.start_time
            self.start_time = None
            self.is_running = False

    def resume(self):
        if not self.is_running and self.paused_time is not None:
            self.start_time = time.perf_counter() - self.paused_time
            self.paused_time = None
            self.is_running = True

    def elapsed_time(self):
        if self.is_running:
            return time.perf_counter() - self.start_time
        elif self.paused_time is not None:
            return self.paused_time
        else:
            return 0.0

    def reset(self):
        self.start_time = None
        self.paused_time = None
        self.is_running = False


class timerForSong(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.song_info = None
        self.last_time_check = 0
        self.timer = Timer()
    
    def reset_timer(self, precent):
        #self.timer_start_point = time.time() - self.parent.playing_duration * precent  # 这首歌00:00时是什么时候
        self.timer.stop()
        self.timer.reset()
        delta = self.parent.playing_duration * precent  # 这首歌00:00时是什么时候
        self.timer.start(delta = delta)
        

    
    def check_if_song_is_finished(self):
        if self.timer.elapsed_time() >= self.parent.playing_duration:
            self.parent.trigger_test()
 
    def get_time_passed(self):
        #print(self.timer.elapsed_time())
        return self.timer.elapsed_time()
        
    def update_ui(self, force = False):
        if (int(self.last_time_check) != int(time.time()) and self.parent.is_playing == True) or force:
            self.last_time_check = time.time()
            gbvar.update_infomation(lazy = True)
        