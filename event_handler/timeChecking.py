import time
import gbvar

class timerForSong(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.song_info = None
        self.last_time_check = 0
    
    def reset_timer(self, precent):
        self.timer_start_point = time.time() - self.parent.playing_duration * precent  # 这首歌00:00时是什么时候
    
    def check_if_song_is_finished(self):
        if time.time() - self.timer_start_point >= self.parent.playing_duration:
            self.parent.trigger_test()
 
    def get_time_passed(self):
        return time.time() - self.timer_start_point
        
    def update_ui(self, force = False):
        if (int(self.last_time_check) != int(time.time()) and self.parent.is_playing == True) or force:
            self.last_time_check = time.time()
            gbvar.update_infomation()
        