import soundfile
import sounddevice
import event_handler
import mutagen
from PIL import Image
import io
import time
import hashlib
import os

import gbvar

def get_md5_checksum(data):
    md5_gen = hashlib.sha256()
    md5_gen.update(data)
    return md5_gen.hexdigest()

class Song(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.title, self.artist = self.get_info_from_file()
        self.uid = get_md5_checksum((self.title + self.artist + self.file_path).encode())
        
        self.cover_path = self.get_song_cover_to_temp()    #  缓存封面

    def load(self, lazy = False):   #  外部调用，用于获取这首歌的全部信息，缓存封面，以及音频数组
        if lazy:
            return ((self.title, self.artist, self.cover_path), None)
        sound_array, sound_sample_rate = soundfile.read(self.file_path, dtype = 'float32')
        duration = len(sound_array) / sound_sample_rate
        return ((self.title, self.artist, self.cover_path), (sound_array, sound_sample_rate, duration))

    def get_info_from_file(self):  #  这个函数用于区分不同的音乐文件，并返回曲名和作者

        file_path = self.file_path
        song_type = file_path.split('.')[-1].upper()    # 根据后缀获取文件类型
        _default_artist = 'Unknown Artist'

        name = None
        artist = None
        
        if song_type == 'WAV':
            file_path = file_path.replace('/', '\\')
            name = file_path.split('\\')[-1].split('.')[:-1][0]
            artist = _default_artist
            return name, artist
            
        if song_type == 'MP3':
            audio = mutagen.File(file_path)
            name = audio.tags["TALB"].text[0]
            artist = audio.tags["TPE1"].text[0]
            return name, artist
        
        if song_type == 'FLAC':
            audio = mutagen.File(file_path)
            name = audio.tags["TITLE"][0]
            artist = audio.tags["ARTIST"][0]
            return name, artist
        
        return file_path.split('\\')[-1].split('.')[:-1], _default_artist

    def get_song_cover_to_temp(self):  #  将歌曲封面存入缓存
        
        if os.path.exists('./temp/cover_{}.png'.format(self.uid)):   # 如果已经缓存过
            return './temp/cover_{}.png'.format(self.uid)
        
        file_path = self.file_path
        song_type = file_path.split('.')[-1].upper()    # 根据后缀获取文件类型
        audio = mutagen.File(file_path)
        
        try:
            if song_type.upper() == 'FLAC':
                cover_data = audio.pictures[0].data
            
            if song_type.upper() != 'FLAC':  #  其他封面
                for tag in audio.tags:
                    if str(tag)[0:4] == 'APIC':
                        cover_data = audio.tags[tag].data
                        break
            
            image_io = io.BytesIO(cover_data)
            filename = './temp/cover_{}.png'.format(self.uid)
            cover_pil = Image.open(image_io)
            width, height = cover_pil.size
            resize_rate = 400 / width
            cover_pil = cover_pil.resize((int(width * resize_rate), int(height * resize_rate)), Image.LANCZOS )
            cover_pil = cover_pil.transform((400,128), Image.EXTENT, (0, int(height * resize_rate / 2) - 64, 400, (int(height * resize_rate / 2) + 64)))
            cover_pil.save(filename)
            cover_path = filename
        
        except:
            cover_path = './images/bgtest.png'
            
        return cover_path

    def __str__(self):
        return '\t<> Song Object\n\tTitle:\t{}\n\tArtist:\t{}\n'.format(self.title, self.artist)

class musicPlayer(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.songs = []
        self.playmisson_threadlized = []
        self.changemisson_threadlized = []
        self.timer = event_handler.timeChecking.timerForSong(parent = self)
        
        self.playing_index = 0
        self.is_playing = False
        
        self.playing_title = None
        self.playing_artist = None
        self.playing_cover_path = None
        
        self.playing_uid = None
        
        self.playing_sound_array = None
        self.playing_sample_rate = None
        self.playing_duration = None
        
        
    def add(self, path):  # 按照文件路径，实例化一个 Song 类，并添加到 self.songs 中
        new_song = Song(path)
        self.songs.append(new_song)
        print(new_song)
        return new_song  # 有的时候回传一个对象是有用的

    def load(self, song):  # 将一个 Song 加载到正在播放，调用 Song.load() 方法
        song_info, song_data = song.load()
        self.playing_uid = song.uid
        self.playing_title, self.playing_artist, self.playing_cover_path = song_info
        self.playing_sound_array, self.playing_sample_rate, self.playing_duration = song_data
        gbvar.gblog.log('歌曲 {} 已载入'.format(self.playing_title))
    
    def play(self, precent):
        self.is_playing = True
        sounddevice.play(self.playing_sound_array[int(precent * len(self.playing_sound_array)):], self.playing_sample_rate)
        self.timer.reset_timer(precent)
    
    def load_by_number(self, index = None, delta = 0):  # 按编号运行 self.load() 方法
        if self.songs == []:
            print('还没有歌曲')
            return

        if index is None:
            index = self.playing_index
        index += delta
        index = index % len(self.songs)

        self.playing_index = index
        song = self.songs[index]
        self.playing_title, self.playing_artist, self.playing_cover_path = song.load(lazy = True)[0]  #  预加载
        gbvar.update_infomation(True)
        
        self.load(song)

    def load_by_uid(self, uid):
        if self.songs == []:
            print('还没有歌曲')
            return
        
        for index, song in enumerate(self.songs):
            if song.uid == uid:
                self.load_by_number(index)
                return
       
        print('未找到该歌曲uid', uid)
        return
       
    def change_song_and_play(self, index = None, delta = 0):  # ui 调用这个方法，加载歌曲并播放
        self.load_by_number(index = index, delta = delta)
        self.play(0.0)

    def trigger_test(self):
        self.load_by_number(delta = 1)
        self.play(0.0)
        gbvar.ui.selecter_interface.updatePlaying()
        #self.changemisson_threadlized.append([None, 1])

    def get_playing_info(self, lazy = False):
        if lazy:
            return ((self.playing_title, self.playing_artist, self.playing_cover_path), (None, self.playing_sample_rate, self.playing_duration))
        return ((self.playing_title, self.playing_artist, self.playing_cover_path), (self.playing_sound_array, self.playing_sample_rate, self.playing_duration))








