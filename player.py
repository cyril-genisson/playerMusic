#!/usr/bin/env python3
#
# Project: MusicPlayer
# Filename: main.py
# Created: 05/12/2024
#
# License: GPLv3
#
# Author: Cyril GENISSON
#
from tkinter import Tk, Label, Button, PhotoImage, Listbox, StringVar, Menu, Toplevel
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror, askquestion, showinfo
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.icons import Emoji

import os
import threading
import time

from PIL import Image, ImageTk
import pygame
from mutagen.mp3 import MP3


CURRENT_SONG_INDEX = 0
NUMBER_OF_SONGS_IN_LIST = 0
IMAGE_PATH = 'me.png'


class Player:
    pygame.mixer.init()
    
    def __init__(self, master):
        self.master = master

        self.PLAY = "►"
        self.PAUSE = "║║"
        self.RWD = "⏮"
        self.FWD = "⏭"
        self.STOP = "■"
        self.UN_PAUSE = "||"
        self.MUTE = "🔇"
        self.UN_MUTE = u"\U0001F50A"
        self.vol_mute = 0.0
        self.vol_unmute = 1.0

        self.scroll = ttk.Scrollbar(master, bootstyle="round")
        self.play_list = Listbox(master, font="Sanserif 12 bold", bd=5,
                                 bg="white", width=37, height=19, selectbackground="blue")
        self.play_list.place(x=600, y=77)
        self.scroll.place(x=946, y=80, height=389, width=15)
        self.scroll.config(command=self.play_list.yview)
        self.play_list.config(yscrollcommand=self.scroll.set)
        
        self.img1 = Image.open(IMAGE_PATH)
        self.img1 = self.img1.resize((600, 470), Image.Resampling.LANCZOS)
        self.img = ImageTk.PhotoImage(self.img1)
        self.lab = Label(master)
        self.lab.grid(row=0, column=0)
        self.lab["compound"] = LEFT
        self.lab["image"] = self.img

        self.var = StringVar()
        self.var.set("")
        self.song_title = Label(master, font="Helvetica 12 bold", bg="black", fg="white", width=55,
                                textvariable=self.var)
        self.song_title.place(x=3, y=0)

        self.master.bind("<space>", lambda x: self.play_thread())
        self.master.bind('<Left>', lambda x: self.prev())
        self.master.bind('<Right>', lambda x: self.next())

    def get_icon(self):
        win_icon = PhotoImage(file=IMAGE_PATH)
        self.master.iconphoto(True, win_icon)

    def append_listbox(self):
        global NUMBER_OF_SONGS_IN_LIST
        try:
            self.play_list.delete(0, 'end')
            directory = askdirectory()
            os.chdir(directory)
            song_list = os.listdir()
            song_list.sort()
            cleaned_list = [x for x in song_list if ".mp3" in x]
            
            NUMBER_OF_SONGS_IN_LIST = len(cleaned_list)
            self.play_list.insert(0, *song_list)
            
            active_song_index = 0
            self.play_list.selection_set(active_song_index)
            self.play_list.see(active_song_index)
            self.play_list.activate(active_song_index)
            self.play_list.selection_anchor(active_song_index)
            
        except:
            showerror("Erreir", "Choisit un bon répertoire musical")

        # =====run the append_listbox function on separate thread====== #

    def add_songs_playlist(self):
        my_threads = threading.Thread(target=self.append_listbox)
        my_threads.start()

    def get_time(self):
        current_time = pygame.mixer.music.get_pos() / 1000
        format_time = time.strftime("%H:%M:%S", time.gmtime(current_time))
        next_one = self.play_list.curselection()
        song = self.play_list.get(next_one)
        song_timer = MP3(song)
        song_length = int(song_timer.info.length)
        format_for_length = time.strftime("%H:%M:%S", time.gmtime(song_length))
        if str(format_time) == "23:59:59":
            format_time = "00:00:00"
        self.label_time.config(text=f"{format_for_length} / {format_time}")
        self.progress["maximum"] = song_length
        self.progress["value"] = int(current_time)
        self.master.after(100, self.get_time)

    def play_music(self):
        try:
            track = self.play_list.get(ACTIVE)
            pygame.mixer.music.load(track)
            self.var.set(str(track).split(".")[0])
            pygame.mixer.music.play()
            self.get_time()
        except Exception as e:
            print(e)
            showerror("Pas de musique", "Choisit un répertoire contenant des mp3")

    def update_song_index(self):
        global CURRENT_SONG_INDEX
        CURRENT_SONG_INDEX += 1
        self.play_all()
        
    def play_all(self):
        
        try:
            self.play_list.select_clear(0, END)
            self.play_list.selection_set(CURRENT_SONG_INDEX, last=None)
            self.play_list.see(CURRENT_SONG_INDEX)
            self.play_list.activate(CURRENT_SONG_INDEX)
            self.play_list.selection_anchor(CURRENT_SONG_INDEX)
            track = self.play_list.get(CURRENT_SONG_INDEX)
            pygame.mixer.music.load(track)
            self.var.set(str(track).split(".")[0])
            pygame.mixer.music.play()
            current_song = self.play_list.curselection()
            song = self.play_list.get(current_song)
            song_timer = MP3(song)
            song_length = int(song_timer.info.length) * 1000
            self.get_time()
            self.master.after(song_length, self.update_song_index)
        except:
            showerror("Pas de musique dans la Playlist", "Ajoute un répertoire")
                
    def pause_unpause(self):
        if self.button_pause['text'] == self.PAUSE:
            pygame.mixer.music.pause()
            self.button_pause['text'] = self.UN_PAUSE

        elif self.button_pause['text'] == self.UN_PAUSE:
            pygame.mixer.music.unpause()
            self.button_pause['text'] = self.PAUSE

    def play_thread(self):
        my_threads = threading.Thread(target=self.play_music)
        my_threads.start()

    def stop(self):
        pygame.mixer.music.stop()

    def volume(self, *args):
        if self.button_mute['text'] == self.UN_MUTE:
            pygame.mixer.music.set_volume(self.volume_slider.get())

    def muted(self):
        if self.button_mute['text'] == self.UN_MUTE:
            pygame.mixer.music.set_volume(self.vol_mute)
            self.button_mute['fg'] = "red"
            self.button_mute['text'] = self.MUTE
        elif self.button_mute['text'] == self.MUTE:
            pygame.mixer.music.set_volume(self.volume_slider.get())
            self.button_mute['fg'] = "white"
            self.button_mute['text'] = self.UN_MUTE

    def next_song(self):
        global NUMBER_OF_SONGS_IN_LIST

        try:
            cursor_select = self.play_list.curselection()[0]
            if int(cursor_select) == NUMBER_OF_SONGS_IN_LIST - 1:
                next_one = 0
            else:
                next_one = cursor_select + 1
            song = self.play_list.get(next_one)
            pygame.mixer.music.load(song)
            pygame.mixer.music.play()
            self.play_list.select_clear(0, END)
            self.play_list.activate(next_one)
            self.play_list.selection_set(next_one, last=None)
            self.var.set(str(song).split(".")[0])
            self.play_list.see(next_one)
            self.get_time()
        except:
            showerror("Tu es sur le dernier titre", "Presse Previous")
            
    def next(self):
        my_threads = threading.Thread(target=self.next_song)
        my_threads.start()

    def prev_song(self):
        global NUMBER_OF_SONGS_IN_LIST
        
        try:
            cursor_select = self.play_list.curselection()[0]
            if int(cursor_select) == 0:
                prev_one = NUMBER_OF_SONGS_IN_LIST - 1
            else:
                prev_one = cursor_select - 1
            song = self.play_list.get(prev_one)
            pygame.mixer.music.load(song)
            pygame.mixer.music.play()
            self.play_list.select_clear(0, END)
            self.play_list.activate(prev_one)
            self.play_list.selection_set(prev_one, last=None)
            self.var.set(str(song).split(".")[0])
            self.play_list.see(prev_one)
            self.get_time()
        except:
            showerror("Tu es sur le premier titre", "Presse Next.")

    def prev(self):
        my_threads = threading.Thread(target=self.prev_song)
        my_threads.start()

    def exit(self):
        msgbox = askquestion('Quitter', 'Voulez-vous vraiment fermer le MediaPlayer?',
                             icon='warning')
        if msgbox == 'yes':
            self.master.quit()
            self.master.after(100, exit)
        else:
            showinfo('Retour', 'Continue à écouter ton incroyable musique!!!')

    def help(self):
        top = Toplevel()
        top.title("Résumé des commandes")
        top.geometry("350x554+500+80")
        top.resizable(width=0, height=0)
        user_manual = [
            " MUSIC PLAYER MANUAL: \n",
            "1. play button =  ( ► )",
            "2. pause button = ║║ ",
            "3. unpause symbol = ||",
            "4. next button = ⏭ ",
            "5. previous button = ⏮",
            "6. mute button = '\U0001F50A' ",
            "7. unmute symbol = 🔇",
            "8. stop button = ■ ",
            "\n\n| Cyril GENISSON | Copyright @ 2023 |\n"
        ]
        for i in user_manual:
            manual = Label(top, text=i, width=50, height=3, font="Helvetica, 11", bg="black", fg="white")
            manual.pack(side=TOP, fill=BOTH)

    def main_window(self):
        self.get_icon()
        self.menu = Menu(self.lab, font="helvetica, 8",)
        self.master.config(menu=self.menu)
        self.menu.add_command(label="Help", command=self.help)
        self.menu.add_command(label="Exit", command=self.exit)
        
        self.button_play = Button(self.master, text=self.PLAY, width=5, bd=5, bg="black",
                            fg="white", font="Helvetica, 15", command=self.play_thread)
        self.button_play.place(x=150, y=423)
        
        self.button_prev = Button(self.master, text=self.FWD, width=5, bd=5,
                            font="Helvetica, 15", bg="black", fg="white", command=self.next)
        self.button_prev.place(x=300, y=423)
        
        self.button_next = Button(self.master, text=self.RWD, width=5, bd=5, bg="black",
                            fg="white", font="Helvetica, 15", command=self.prev)
        self.button_next.place(x=10, y=423)
        
        self.button_stop = Button(self.master, text=self.STOP, width=5, bd=5,
                            font="Helvetica, 15", bg="black", fg="white", command=self.stop)
        self.button_stop.place(x=225, y=423)
        
        self.button_play_all = Button(
            self.master, text='\U0001F500' , 
            bg='black', fg='white', font='Helvetica, 15' , bd=5,
            width=3,
            command=self.play_all)
        self.button_play_all.place(x=375, y=423)

        self.button_pause = Button(self.master, text=self.PAUSE, width=4, bd=5,
                            font="Helvetica, 15", bg="black", fg="white", command=self.pause_unpause)
        self.button_pause.place(x=85, y=423)

        self.button_mute = Button(self.master, text=self.UN_MUTE, width=2, bd=5,
                            font="Helvetica, 15", bg="black", fg="white", command=self.muted)
        self.button_mute.place(x=430, y=423)

        self.label_playlist = Label(self.master, text=u"♫ Playlist ♫ ",
                            width=33, font="Helvetica, 15")
        self.label_playlist.place(x=605, y=0)

        self.button_load_music = Button(self.master, text=f"{Emoji.get('open file folder')} ♫ ouvre ton répertoire musical ♫ ",
                                        width=40, height=2,
                                bd=5, font="Helvetica, 11", fg="black", command=self.add_songs_playlist)
        self.button_load_music.place(x=605, y=34)

        self.style = ttk.Style()

        self.style.configure("myStyle.Horizontal.TScale")

        self.volume_slider = ttk.Scale(self.lab, from_=0, to=1, bootstyle="SECONDARY", orient=HORIZONTAL,
                        value=1, length=120, command=self.volume, style="myStyle.Horizontal.TScale")
        self.volume_slider.place(x=470, y=430)
        
        self.style.configure("greyish.Horizontal.TProgressbar", troughcolor ="#E5E4E2")

        self.progress = ttk.Progressbar(self.lab, orient=HORIZONTAL, bootstyle="striped",
                                        value=0, length = 438, mode = 'determinate',
                                        style="greyish.Horizontal.TProgressbar")
        self.progress.place(x=10, y=396)

        self.label_time = Label(self.master, text="00:00:00 / 00:00:00",
                            width=17, font="Helvetica, 10", bg="black", fg="white")
        self.label_time.place(x=460, y=394)


def main():
    root = Tk()
    Player(root).main_window()
    root.geometry("963x470+200+100")
    root.title("Music Player")
    root.configure(bg="#E5E4E2")
    root.resizable(width=0, height=0)
    root.mainloop()

if __name__ == "__main__":
   main()
