"""
Program name: Pithon Player
Author: *REDACTED*
Original Release Date: 24/03/20
Latest Build Release Date: 15/07/20
Build: 3.1
License: GNU GPL (General Public License)
"""

import tkinter as tk  # GUI
import tkinter.filedialog as filedialog  # File Explorer popup
import tkinter.messagebox as messagebox  # Messagebox
import threading, os, time, random, eyed3, platform  # Multi-Threading, Communicate with OS, Wait, Random, MP3 Tags, Get OS Name
from pygame import mixer  # Get Mixer From pygame Lib
from mutagen.mp3 import MP3  # Get MP3 Duration


global system_path  # Create global variable system_path
if platform.system() == "Windows":  # If OS is Windows
    system_path = '\\'  # Set path bar as this one

elif platform.system() == "Linux" or platform.system() == "Darwin":  # If OS is Linux or Mac
    system_path = '/'  # Set path bar as this one


class Pithon_Player:  # Main structure
    def __init__(self, master):  # Initialization
        mixer.init()  # Initialize mixer
        master.resizable(False, False)  # Do not allow resizing x or y
        master.geometry("900x400")  # Window size x, y
        master.title("Pithon Player")  # Window title
        if platform.system() == "Windows":  # Returns the platform "path", if it equals win32 (windows)
            master.iconbitmap(os.getcwd() + r"\Images\Icon.ico")  # Set icon as current location of file + string

        self.background_thread = threading.Thread(name="background", target=self.background)  # Create new thread
        # Create Int Vars
        self.loop_one_var = tk.IntVar()  # Loop one
        self.loop_all_var = tk.IntVar()  # Loop all
        self.shuffle_var = tk.IntVar()  # Shuffle
        self.current_song = tk.IntVar()  # Current Song
        self.query_var = tk.IntVar()  # Query box

        self.current_path = os.getcwd()  # Get current directory
        self.m1_pressed = False  # Store mouse state
        self.prev_query = 0  # Previous Query
        self.query_index = 0  # Query index
        self.isdark = False  # Light or Dark Theme
        self.fg = ""  # Foreground color
        self.bg = ""  # Background color
        self.light_images = []  # Store all light themed images
        self.dark_images = []  # Store all dark themed images
        self.default_images = []  # Store default theme images
        self.default_path = False  # Default path available
        self.allow_events = True  # Background thread can run
        self.index = '0'  # Skip index assignment

        # Load images
        try:  # Try to load images
            self.background_image = tk.PhotoImage(file=self.current_path + r'{}Images{}background.png'.format(system_path, system_path))  # Background

            self.light_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}previous.png'.format(system_path, system_path)))  # Previous
            self.light_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}play.png'.format(system_path, system_path)))  # Play
            self.light_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}next.png'.format(system_path, system_path)))  # Next
            self.light_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}loopall.png'.format(system_path, system_path)))  # Loop All
            self.light_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}loopsingle.png'.format(system_path, system_path)))  # Loop Single)
            self.light_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}shuffle.png'.format(system_path, system_path)))  # Loop Single)

            self.light_image = tk.PhotoImage(file=self.current_path + r'{}Images{}light.png'.format(system_path, system_path))  # Light mode)
            self.dark_image = tk.PhotoImage(file=self.current_path + r'{}Images{}dark.png'.format(system_path, system_path))  # Dark mode)

            self.dark_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}previous_dark.png'.format(system_path, system_path)))  # Dark Previous
            self.dark_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}play_dark.png'.format(system_path, system_path)))  # Dark Play
            self.dark_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}next_dark.png'.format(system_path, system_path)))  # Dark Next
            self.dark_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}loopall_dark.png'.format(system_path, system_path)))  # Dark Loop All
            self.dark_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}loopsingle_dark.png'.format(system_path, system_path)))  # Dark Loop Single
            self.dark_images.append(tk.PhotoImage(file=self.current_path + r'{}Images{}shuffle_dark.png'.format(system_path, system_path)))  # Dark Shuffle

        except Exception:
            messagebox.showerror(title="ERROR!", message="Could not load images, check if the folder images is in the program folder and if the images are not corrupt.")  # Show error
            master.destroy()  # Images could not be read

        try:  # Try to open file
            self.config = open(self.current_path + "{}config.txt".format(system_path))  # Open file

        except Exception:  # If file can't be open/doesn't exist
            try:
                open(self.current_path + "{}config.txt".format(system_path), 'x').close()  # Create file
                self.config = open(self.current_path + "{}config.txt".format(system_path))  # Open file

            except Exception:
                messagebox.showerror(title="ERROR!", message="Configuration file could not be opened/read, please restart the program, if this error persists delete conf.txt.")  # Show error
                master.destroy()

        self.options = self.config.read().split('\n')  # Read file and add each line to options list
        self.config.close()  # Close file
        for option in self.options:  # For all entries in options
            if option == "True":  # If dark mode in options
                self.isdark = True  # Set dark mode
                self.bg = "black"  # Set background as black
                self.fg = "white"  # Set foreground as white
                self.default_images = self.dark_images  # Set default images

            elif option == "False":  # If light mode in options
                self.isdark = False  # Set light mode
                self.bg = "white"  # Set background as white
                self.fg = "black"  # Set foreground as black
                self.default_images = self.light_images  # Set default images

            elif '\\' in option or '/' in option:  # If path is available in file
                self.current_path = option  # Current path is now path in file
                self.default_path = True  # Default path is available

            else:  # If no file/configuration found
                self.bg = "white"  # Set default background
                self.fg = "black"  # Set default foreground
                self.current_path = ""  # Set no path
                self.default_images = self.light_images  # Set default images

        # Create Canvas
        self.ui = tk.Canvas(master, width=910, height=410)  # Canvas will be on the master's window and will be controlled by it, but it will control all other widgets
        # Create Frame (owner, background color, border color, border width, width, heights)
        self.play_label_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.total_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.music_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.previous_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.play_button_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.next_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.light_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.dark_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.loop_all_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.loop_one_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.shuffle_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.query_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.song_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.music_bar_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)
        self.volume_frame = tk.Frame(self.ui, highlightbackground=self.fg, highlightthickness=2)

        # Create Label (owner, text, font style, border style, border width, background color, foreground color)
        self.play_time = tk.Label(self.play_label_frame, text="00:00", font=("TkDefaultFont", 12), relief="solid", borderwidth=0, bg=self.bg, fg=self.fg)
        self.total = tk.Label(self.total_frame, text="00:00", font=("TkDefaultFont", 12), relief="solid", borderwidth=0, bg=self.bg, fg=self.fg)
        self.music_info = tk.Label(self.music_frame, text="No Song Loaded\n\n\nWaiting For Song To Be Selected", font=("TkDefaultFont", 12), width=69, height=8, borderwidth=0, bg=self.bg, fg=self.fg)
        self.volume_info = tk.Label(self.volume_frame, text="100%", font=("TkDefaultFont", 10), relief="solid", borderwidth=0, bg=self.bg, fg=self.fg)

        # Create play Button (owner, image, do on click, background color, border style, border width, background color, foreground color)
        self.previous_button = tk.Button(self.previous_frame, image=self.default_images[0], command=self.previous_song, relief="solid", borderwidth=0, bg=self.bg, fg=self.fg)
        self.play_button = tk.Button(self.play_button_frame, image=self.default_images[1], command=self.plays_stops, relief="solid", borderwidth=0, bg=self.bg, fg=self.fg)
        self.next_button = tk.Button(self.next_frame, image=self.default_images[2], command=self.next_song, relief="solid", borderwidth=0, bg=self.bg, fg=self.fg)
        self.light_mode = tk.Button(self.light_frame, image=self.light_image, command=self.light_set, fg="white", relief="solid", borderwidth=0)
        self.dark_mode = tk.Button(self.dark_frame, image=self.dark_image, command=self.dark_set, bg="black", relief="solid", borderwidth=0)

        # Create loopall box (owner, text, image, checkbox's variable, on value change, border style, border width, background color, foreground color)
        self.loop_all_box = tk.Checkbutton(self.loop_all_frame, image=self.default_images[3], var=self.loop_all_var, command=self.loop_all_active, relief="solid", borderwidth=0, bg=self.bg, fg=self.fg)
        self.loop_one_box = tk.Checkbutton(self.loop_one_frame, image=self.default_images[4], var=self.loop_one_var, command=self.loop_one_active, relief="solid", borderwidth=0, bg=self.bg, fg=self.fg)
        self.shuffle_box = tk.Checkbutton(self.shuffle_frame, image=self.default_images[5], var=self.shuffle_var, command=self.shuffle_active, relief="solid", borderwidth=0, bg=self.bg, fg=self.fg)
        self.query_box = tk.Checkbutton(self.query_frame, var=self.query_var, command=self.query_active, relief="solid", borderwidth=0, bg=self.bg, fg=self.fg)

        # Single line textbox (owner, text, background, border style, border width, background color, foreground color)
        self.query = tk.Entry(self.query_frame, relief="solid", borderwidth=2, bg=self.bg, fg=self.fg)
        # Create Listbox (owner, how many selects allowed, height, border size, width, border style, border color, border width)
        self.song_list = tk.Listbox(self.song_frame, selectmode="SINGLE", height=24, width=40, relief="solid", highlightbackground="black", borderwidth=2, bg=self.bg, fg=self.fg)
        # Create scale bar (owner, min val, max val, vert/horizon, length, width, middle indicator width, command val change, hide label, border style, border color, border width)
        self.music_bar = tk.Scale(self.music_bar_frame, from_=0, to=0, orient=tk.HORIZONTAL, length=620, width=20, sliderlength=15, command=self.play_time_update, showvalue=0, relief="sunken",
                                  highlightbackground="black", borderwidth=0, bg=self.bg, fg=self.fg)
        # Create scale bar (owner, min val, max val, vert/horizon, length, value to add per move, width, middle indicator width, command val change, hide label, border style, border color, border width)
        self.volume_bar = tk.Scale(self.volume_frame, from_=0, to=1, orient=tk.HORIZONTAL, length=146, resolution=0.01, width=15, sliderlength=12, command=self.volume_change, showvalue=0,
                                   relief="raised", highlightbackground="black", borderwidth=0, bg=self.bg, fg=self.fg)

        self.song_list.insert(tk.END, "Empty")  # Insert empty into listbox
        self.song_list.select_set(0)  # Set selected index to 0
        self.volume_bar.set(1)  # Set volume bar start val to 100

        self.song_list.bind("<ButtonRelease-1>", self.begin)  # Bind mouse 1 click event to Listbox
        self.song_list.bind("<Double-Button-1>", self.path)  # Bind double mouse left click event to Listbox
        self.song_list.bind("<<ManualSelect>>", self.begin)  # Bind manual event to Listbox

        self.music_bar.bind("<Button-1>", self.mouse_press)  # Bind mouse 1 click event to musicbar
        self.music_bar.bind("<ButtonRelease-1>", self.music_bar_change)  # Bind mouse 1 release event to musicbar

        # There's also pack (random) and grid (table format), Place uses x, y (horizontal, vertical)
        self.ui.place(x=-5, y=-5)

        # Pack items into their frames (random position as long as it fits in it (frame size is dictated by item so it's centered))
        self.play_time.pack()
        self.total.pack()
        self.music_info.pack()
        self.previous_button.pack()
        self.play_button.pack()
        self.next_button.pack()
        self.light_mode.pack()
        self.dark_mode.pack()
        self.loop_all_box.pack()
        self.loop_one_box.pack()
        self.shuffle_box.pack()
        self.query_box.pack(side="right")
        self.query.pack()
        self.song_list.pack()
        self.music_bar.pack()
        self.volume_bar.pack()
        self.volume_info.pack()

        #  Create Image inside canvas
        self.ui.create_image(450, 200, image=self.background_image)  # Add image to widget (x, y, image)

        # Create Windows inside canvas (frames)
        self.ui.create_window(44, 264, window=self.play_label_frame)
        self.ui.create_window(626, 264, window=self.total_frame)
        self.ui.create_window(330, 130, window=self.music_frame)

        self.ui.create_window(256, 290, window=self.previous_frame)
        self.ui.create_window(328, 290, window=self.play_button_frame)
        self.ui.create_window(400, 290, window=self.next_frame)
        self.ui.create_window(18, 17, window=self.light_frame)
        self.ui.create_window(42, 16, window=self.dark_frame)

        self.ui.create_window(110, 275, window=self.loop_all_frame)
        self.ui.create_window(170, 275, window=self.loop_one_frame)
        self.ui.create_window(139, 317, window=self.shuffle_frame)

        self.ui.create_window(520, 290, window=self.query_frame)

        self.ui.create_window(780, 205, window=self.song_frame)
        self.ui.create_window(335, 235, window=self.music_bar_frame)
        self.ui.create_window(520, 330, window=self.volume_frame)

        if self.default_path:  # If there's a default path available
            self.get_songs()  # Get files from directory

    def path(self, event):  # File dialog actions
        try:  # Try doing this
            mixer.music.stop()  # Stop music
            self.current_path = filedialog.askdirectory()  # Get music files directory
            self.get_songs()  # Get files from directory

        except Exception:  # If you can't do above
            tk.messagebox.showerror(title="Error", message=" Couldn't Opening File Explorer Or No Path Selected")  # Return error in messagebox

    def begin(self, event):  # Listbox index changed
        if self.song_list.curselection() != self.current_song:  # If selected song is not song playing
            mixer.music.stop()  # Kill music
            self.music_bar.set(0)  # Set progbar to start position
            mixer.music.load(self.current_path + system_path + self.song_list.get(self.song_list.curselection()))  # Selected Location + / + selected item's text (If multiple returns tuple)
            self.totaltime = MP3(self.current_path + system_path + self.song_list.get(self.song_list.curselection())).info.length  # Store mp3 file total play_labelime in secs
            # Change left label's text to play_labelime on mp3 file (Format string 2 houses, replace empty houses with 0, integers only)
            self.total.config(text="{:02d}:{:02d}".format(self.format_time("min", self.totaltime), self.format_time("sec", self.totaltime)))
            try:
                music_name = eyed3.load(self.current_path + system_path + self.song_list.get(self.song_list.curselection()))  # Get MP3 file tags
                if "Single" in music_name.tag.album:  # If album is a single
                    album = "Single"  # Just write single
                else:  # If it isn't
                    album = music_name.tag.album  # Write full album name
                self.music_info.config(text="TITLE: " + music_name.tag.title + '\n\n\n' + "ARTIST: " + music_name.tag.artist + '    ' + "ALBUM: " + album)  # Configure label with tags

            except Exception:
                self.music_info.config(text="TITLE: " + str(self.song_list.get(self.song_list.curselection())) + '\n\n\n' + "ARTIST: N/A    ALBUM: N/A")  # If no tags, print name + N/A info

            self.music_bar.config(to=self.totaltime)  # Set musicbar max val to total time
            self.play_button.config(text="Pause")  # Change play button text
            mixer.music.play()  # Initiate music
            self.paused = False  # Music is playing so not paused
            self.current_song = self.song_list.curselection()  # Listbox returns index, stored in cursong
            if not self.background_thread.is_alive():  # If background thread dies
                self.background_thread.start()  # Start/Revive background thread
            else:  # If background is alive
                self.cur_sec = 0  # Reset second counter

    def background(self):  # Task on background
        # Second counter (mixer.music.get_position() The returned time only represents how long the mixer has been active.")
        self.cur_sec = 0
        while True:  # Loops
            if mixer.music.get_busy() and not self.paused and self.cur_sec <= self.totaltime:  # While song playing
                if not self.m1_pressed:  # If mouse 1 isn't pressed
                    self.cur_sec += 1  # Keep adding 1
                    self.music_bar.set(self.cur_sec)  # Set musicbar position to currrent seconds
                    time.sleep(1)  # Wait 1 sec

            elif not mixer.music.get_busy():  # If music is over or stopped
                if self.loop_all_var.get():  # Get value of tk var loop (defined by programmer, self.loop_one_var returns ID not value)
                    self.next_song()  # Invoke next_song function
                    self.index = '0'  # Skip index assignment

                elif self.loop_one_var.get() and self.song_list.curselection() == self.current_song:  # Get value of tk var loop (defined by programmer, self.loop_one_var returns ID not value)
                    mixer.music.play()  # Start music again
                    self.cur_sec = 0  # Reset second counter
                    self.index = '0'  # Skip index assignment

                elif self.shuffle_var.get():  # Get value of tk var shuffle (defined by programmer, self.shuffle_var returns ID not value)
                    self.index = random.randint(0, self.song_list.size() - 1)  # Get random number
                    while self.index == self.current_song:  # While random number is the same as current song's ID
                        self.index = random.randint(0, self.song_list.size() - 1)  # Get random number

                elif self.query_var.get():  # Get value of tk var query (defined by programmer, self.query_var returns ID not value)
                    if self.query.get() != self.prev_query:  # If current query is not the same as previous query (aka textbox value changed)
                        self.prev_query = self.query.get()  # Define new previous query as current query
                        self.query_list = []  # Clear query list
                        self.query_index = 0  # Reset query index
                        all_songs = self.song_list.get(0, tk.END)  # Get tuple of all songs (makes it easier to read, and ensures that nothing is changed since tuples can't be changed)
                        for song in all_songs:  # For all songs in all_songs list
                            if self.prev_query in song:  # If the current song contains the string inside the query textbox (This happens when the query changes, this var holds the current query)
                                self.query_list.append(all_songs.index(song))  # Append the index of the item (all_songs has the same structure as listbox so all indexes are the same)
                        self.index = self.query_list[0]  # Define current index as the first index stored in query list

                    else:  # If current query is the same as the previous query (aka it hasn't changed)
                        self.query_index += 1  # Add 1 to query_indexs value
                        if self.query_index > len(self.query_list) - 1:  # If query index value is bigger than list limit
                            self.query_index = 0  # Query indexs value is reset

                        if self.query_index != self.song_list.curselection():  # If query index is not the same index as the current song
                            self.index = self.query_list[self.query_index]  # Define new index as the index on the position query index
                        else:  # If query index is the same song
                            mixer.music.play()  # Restart mixer
                            self.cur_sec = 0  # Reset cursec counter

                else:
                    self.index = '0'  # Skip index assignment

                if self.index != '0':
                    self.song_list.selection_clear(0, tk.END)  # Clear Selection
                    self.song_list.select_set(self.index)  # Set selected index
                    self.song_list.event_generate("<<ManualSelect>>")  # Generate listbox manual click event

    def music_bar_change(self, event):  # If musicbar val changes
        if not mixer.music.get_busy():  # If mixer is not playing
            mixer.music.play()  # Start mixer
        self.barsec = self.music_bar.get()  # Store musicbar seconds
        mixer.music.set_pos(self.barsec)  # Set new position
        self.cur_sec = self.barsec  # Set cursec's new time
        self.m1_pressed = False  # Set m1pressed to false as mouse was released

    def volume_change(self, event):  # When volume bar val changes
        mixer.music.set_volume(self.volume_bar.get())
        self.volume_info.config(text=str(int(self.volume_bar.get() * 100)) + '%')

    def previous_song(self):  # Action on previous button press
        index = self.song_list.curselection()[0]  # Get index out of tuple of indexes (Single selection mode so selection is always at first index)
        index = int(index) - 1  # Save previous index
        if index < 0:  # If index is smaller than index range
            index = (self.song_list.size() - 1)  # Index is last index

        self.song_list.selection_clear(0, tk.END)  # Clear Selection
        self.song_list.select_set(index)  # Set selected index
        self.song_list.event_generate("<<ManualSelect>>")  # Generate listbox manual click event

    def plays_stops(self):  # Action on play button press
        if mixer.music.get_busy() and self.paused:  # If song is paused
            mixer.music.unpause()  # Unpause music
            self.play_button.config(text="Pause")  # Change play button text
            self.paused = False  # Music resumes so not paused

        elif mixer.music.get_busy() and not self.paused:  # If song is playing
            mixer.music.pause()  # Pause song
            self.play_button.config(text="Play")  # Change play button to original text
            self.paused = True  # Music has stopped temporarily so paused

    def next_song(self):  # Action on next button press
        index = self.song_list.curselection()[0]  # Get index out of tuple of indexes (Single selection mode so selection is always at first index)
        index = int(index) + 1  # Save next index
        if index > (self.song_list.size() - 1):  # If index is bigger than index range
            index = 0  # Index is 0

        self.song_list.selection_clear(0, tk.END)  # Clear Selection
        self.song_list.select_set(index)  # Set selected index
        self.song_list.event_generate("<<ManualSelect>>")  # Generate listbox manual click event

    def light_set(self):
        # Set isdark to false because theme is light
        self.isdark = False
        # Light mode is active, disable light button and enable dark button
        self.light_mode.config(state=tk.DISABLED)
        self.dark_mode.config(state=tk.NORMAL)
        # Configure frame's background and highlight background
        self.play_label_frame.config(highlightbackground="black")
        self.total_frame.config(highlightbackground="black")
        self.music_frame.config(highlightbackground="black")
        self.previous_frame.config(highlightbackground="black")
        self.play_button_frame.config(highlightbackground="black")
        self.next_frame.config(highlightbackground="black")
        self.loop_all_frame.config(highlightbackground="black")
        self.loop_one_frame.config(highlightbackground="black")
        self.shuffle_frame.config(highlightbackground="black")
        self.query_frame.config(highlightbackground="black")
        self.song_frame.config(highlightbackground="black")
        self.volume_frame.config(bg="white", highlightbackground="black")

        # Configure labels/buttons/etc background, text color and image
        self.play_time.config(bg="white", fg="black")
        self.total.config(bg="white", fg="black")
        self.music_info.config(bg="white", fg="black")
        self.volume_info.config(bg="white", fg="black")
        self.previous_button.config(bg="white", fg="black", image=self.light_images[0])
        self.play_button.config(bg="white", fg="black", image=self.light_images[1])
        self.next_button.config(bg="white", fg="black", image=self.light_images[2])
        self.loop_all_box.config(bg="white", fg="black", image=self.light_images[3])
        self.loop_one_box.config(bg="white", fg="black", image=self.light_images[4])
        self.shuffle_box.config(bg="white", fg="black", image=self.light_images[5])
        self.query_box.config(bg="white", fg="black")
        self.query.config(bg="white", fg="black")
        self.song_list.config(bg="white", fg="black")
        self.music_bar.config(bg="white", fg="black")
        self.volume_bar.config(bg="white", fg="black")

    def dark_set(self):
        # Set isdark to true because theme is dark
        self.isdark = True
        # Dark mode is active, disable dark button and enable light button
        self.dark_mode.config(state=tk.DISABLED)
        self.light_mode.config(state=tk.NORMAL)
        # Configure frame's background and highlight background
        self.play_label_frame.config(highlightbackground="white")
        self.total_frame.config(highlightbackground="white")
        self.music_frame.config(highlightbackground="white")
        self.previous_frame.config(highlightbackground="white")
        self.play_button_frame.config(highlightbackground="white")
        self.next_frame.config(highlightbackground="white")
        self.loop_all_frame.config(highlightbackground="white")
        self.loop_one_frame.config(highlightbackground="white")
        self.shuffle_frame.config(highlightbackground="white")
        self.query_frame.config(highlightbackground="white")
        self.song_frame.config(highlightbackground="white")
        self.volume_frame.config(bg="black", highlightbackground="white", highlightcolor="black")

        # Configure labels/buttons/etc background, text color and image
        self.play_time.config(bg="black", fg="white")
        self.total.config(bg="black", fg="white")
        self.music_info.config(bg="black", fg="white")
        self.volume_info.config(bg="black", fg="white")
        self.previous_button.config(bg="black", fg="white", image=self.dark_images[0])
        self.play_button.config(bg="black", fg="white", image=self.dark_images[1])
        self.next_button.config(bg="black", fg="white", image=self.dark_images[2])
        self.loop_all_box.config(bg="black", fg="white", image=self.dark_images[3])
        self.loop_one_box.config(bg="black", fg="white", image=self.dark_images[4])
        self.shuffle_box.config(bg="black", fg="white", image=self.dark_images[5])
        self.query_box.config(bg="black", fg="white")
        self.query.config(bg="black", fg="white")
        self.song_list.config(bg="black", fg="white")
        self.music_bar.config(bg="black", fg="white")
        self.volume_bar.config(bg="black", fg="white")

    def mouse_press(self, event):  # If mouse was pressed
        self.m1_pressed = True  # Set m1 pressed to true

    def loop_all_active(self):  # When loop all checkboxs value changes
        if self.loop_all_var.get():  # When loop all checkbox is checked
            self.loop_one_box.config(state=tk.DISABLED)  # Disable checkbox loop single
            self.shuffle_box.config(state=tk.DISABLED)  # Disable shuffle checkbox
            self.query_box.config(state=tk.DISABLED)  # Disable query checkbox
            self.query.config(state=tk.DISABLED)  # Disable query entry

        else:  # When loop all checkbox is NOT checked
            self.loop_one_box.config(state=tk.NORMAL)  # Enable checkbox loop single
            self.shuffle_box.config(state=tk.NORMAL)  # Enable checkbox shuffle
            self.query_box.config(state=tk.NORMAL)  # Enable checkbox query
            self.query.config(state=tk.NORMAL)  # Enable query entry

    def loop_one_active(self):  # When loop single checkboxs value changes
        if self.loop_one_var.get():  # When loop single checkbox is checked
            self.loop_all_box.config(state=tk.DISABLED)  # Disable checkbox loop all
            self.shuffle_box.config(state=tk.DISABLED)  # Disable shuffle checkbox
            self.query_box.config(state=tk.DISABLED)  # Disable query checkbox
            self.query.config(state=tk.DISABLED)  # Disable query entry

        else:  # When loop single checkbox is NOT checked
            self.loop_all_box.config(state=tk.NORMAL)  # Enable checkbox loop all
            self.shuffle_box.config(state=tk.NORMAL)  # Enable checkbox shuffle
            self.query_box.config(state=tk.NORMAL)  # Enable checkbox query
            self.query.config(state=tk.NORMAL)  # Enable query entry

    def shuffle_active(self):  # When shuffle checkboxs value changes
        if self.shuffle_var.get():  # When shuffle checkbox is checked
            self.loop_all_box.config(state=tk.DISABLED)  # Disable checkbox loop all
            self.loop_one_box.config(state=tk.DISABLED)  # Disable checkbox loop single
            self.query_box.config(state=tk.DISABLED)  # Disable query checkbox
            self.query.config(state=tk.DISABLED)  # Disable query entry

        else:  # When shuffle checkbox is NOT checked
            self.loop_all_box.config(state=tk.NORMAL)  # Enable checkbox loop single
            self.loop_one_box.config(state=tk.NORMAL)  # Enable checkbox loop single
            self.query_box.config(state=tk.NORMAL)  # Enable checkbox query
            self.query.config(state=tk.NORMAL)  # Enable query entry

    def query_active(self):  # When query checkboxs value changes
        if self.query_var.get():  # When query checkbox is checked
            self.loop_all_box.config(state=tk.DISABLED)  # Disable checkbox loop all
            self.loop_one_box.config(state=tk.DISABLED)  # Disable checkbox loop single
            self.shuffle_box.config(state=tk.DISABLED)  # Disable shuffle checkbox

        else:  # When query checkbox is NOT checked
            self.loop_all_box.config(state=tk.NORMAL)  # Enable checkbox loop single
            self.loop_one_box.config(state=tk.NORMAL)  # Enable checkbox loop single
            self.shuffle_box.config(state=tk.NORMAL)  # Enable checkbox shuffle

    def play_time_update(self, event):  # When musicbar val's change update label play_labelime
        self.play_time.config(text="{:02d}:{:02d}".format(self.format_time("min", self.music_bar.get()), self.format_time("sec", self.music_bar.get())))  # Set play_labelime label as musicbar's val

    def get_songs(self):
        self.song_list.delete(0, tk.END)  # Clear list so items don't repeat themselfs
        self.files = os.listdir(self.current_path)  # Get all files in directory (Tuple)
        for file in self.files:  # For each item in files (Tuple)
            if ".mp3" in file:  # If sub-string in string (If .mp3 in filename.extension)
                self.song_list.insert(tk.END, file)  # Add item to listbox songs, tk.END simply says that this item's id is the first available

    def format_time(self, minorsec, val):  # Format time, return minutes or seconds, and value (seconds)
        min, sec = divmod(val, 60)  # Divide total play_labelime by 60 (store in mins) and store remainder (secs) in sec
        if minorsec == "sec":  # If request sec
            return int(sec)  # Return as int

        elif minorsec == "min":  # If request secs
            return int(min)  # Return as int

    def exit_player(self, master):  # When program exits
        mixer.music.stop()  # Stop player
        try:  # Try to open file
            config = open(os.getcwd() + r"{}config.txt".format(system_path), 'a')  # Open config file

        except Exception:  # If file can't be open/doesn't exist
            try:
                open(os.getcwd() + "{}config.txt".format(system_path), 'x').close()  # Create file
                config = open(os.getcwd() + r"{}config.txt".format(system_path), 'a')  # Open config file

            except Exception:
                messagebox.showerror(title="ERROR!", message="Configuration file could not be opened/read, please restart the program, if this error persists delete conf.txt.")  # Show error

        config.truncate(0)  # Erase contents of file
        config.write(str(self.isdark) + '\n' + self.current_path)  # Write to file
        config.close()  # Close file
        master.destroy()  # Close window


root = tk.Tk()  # New instance of Tk
root_player = Pithon_Player(root)  # Set root instance as Pithon_Player's master
root.protocol("WM_DELETE_WINDOW", lambda: root_player.exit_player(root))  # Execute on window manager exit button press
root.mainloop()  # Main loop

# https://www.pygame.org/docs/ref/music.html#pygame.mixer.music.get_position
# https://www.tutorialspoint.com/python/tk_scale.htm
# https://www.geeksforgeeks.org/python-add-image-on-a-tkinter-button/
# https://stackoverflow.com/questions/15462647/modify-the-default-font-in-python-tkinter
# https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter
# https://stackoverflow.com/questions/17584698/getting-rid-of-console-output-when-freezing-python-programs-using-pyinstaller
# https://stackoverflow.com/questions/1854/what-os-am-i-running-on
# Platform codes: Linux: Linux, Mac: Darwin, Windows: Windows
# https://stackoverflow.com/questions/39416021/border-for-tkinter-label
# Border styles: raised, sunken, ridge, solid & groove
# https://docs.python.org/3/library/functions.html#open
# https://effbot.org/tkinterbook/pack.htm
# https://stackoverflow.com/questions/29319445/tkinter-how-to-get-frame-in-canvas-window-to-expand-to-the-size-of-the-canvas
# https://stackoverflow.com/questions/51692178/tkinter-frame-not-displaying
# https://stackoverflow.com/questions/2769061/how-to-erase-the-file-contents-of-text-file-in-python
# https://docs.python.org/3.9/library/tkinter.messagebox.html
# https://stackoverflow.com/questions/15672552/python-tkinter-listbox-get-active-method
# https://bugs.python.org/issue33412 Not the problem with this program, but don't let any threads (besides main) generate events when closing, it makes the program get stuck.
# https://stackoverflow.com/questions/17584698/getting-rid-of-console-output-when-freezing-python-programs-using-pyinstaller

"""
-------------------------------------------------------------------------------------------------------------------------------------
Changes on 15/07/20

- Fixed bug that caused the music bar to stop moving due to var self.index not existing (hadn't been referenced yet) and this also
fixed a small bug that would disrupt the normal flow of the songs (music could potentially loop or keep going forward because
self.index had a value that was being used by a previous checkbox (loop one, loop all, play only songs starting with x, etc...)

- Replaced the value of self.index "skip" with '0' for simplicity sake, the reason this does't outright use a 0 is because a song can
have their index as 0, and that would compromise the structure, so it was replaced with the char 0
-------------------------------------------------------------------------------------------------------------------------------------
Changes on 30/03/20

- Fixed bug when the python interpreter hanged and refused to close.
- Added exception when mp3 file doesn't contain an album tag/fails to load tags.
-------------------------------------------------------------------------------------------------------------------------------------
Improvements brought by changes done on 28/03/20

- Program obeys proper standards and not UBI's standards.
- Protection against mp3 file reading (music would outright refuse to play).
-------------------------------------------------------------------------------------------------------------------------------------
Changes on 28/03/20

- Canvas is now the master of all widgets and the widget that holds the background image
- Added dark and white theme
- Added frames to widgets to control border color
- Added a config file to store theme and last music folder path
-------------------------------------------------------------------------------------------------------------------------------------
Improvements brought by changes done on 28/03/20

- Improved UI.
- Improved user experience.
- Added functionality.
- Product Improvement.
-------------------------------------------------------------------------------------------------------------------------------------
Changes 25/03/20

- Music bar added.
- Interface Adjusted.
- If the album name is single it will simply say single and not "song name" + "single"
-------------------------------------------------------------------------------------------------------------------------------------
Improvements brought by changes done on 25/03/20

- Improved UI.
- Improved user experience.
- Added functionality.
- Product Improvement.
-------------------------------------------------------------------------------------------------------------------------------------
Changes 24/03/20

- Compatibilidade entre Windows e Linux.
- Remoção da função exit() e protocolo de saida uma vez que deixou de ser necessário.
-------------------------------------------------------------------------------------------------------------------------------------
Improvements brought by changes done on 24/03/20

- Compatibility between Windows and Linux.
- Removal of unecessary code.
-------------------------------------------------------------------------------------------------------------------------------------
Changes 22/03/20

- Added Shuffle function.
- Added query function.
- Added label that gets information about current song playing.
- Added functions to disable checkboxes to avoid conflict (more than one activated).
-------------------------------------------------------------------------------------------------------------------------------------
Improvements brought by changes done on 22/03/20

- Improved UI.
- Improved user experience.
- Added functionality.
- Product Finalization.
-------------------------------------------------------------------------------------------------------------------------------------
Changes 02/03/20

- Modefied previous algorith on background thread that allowed the program to loop the entire music folder so that it can be used...
for next button.
- Modefied previous algorith on background thread that allowed the program to loop the entire music folder so that it can be used...
for previous button, works similarly to next_song but instead of summing it subtracts and checks if index is smaller than 0 rather...
than bigger than max index range.
- Added previous and next buttons to allow to swap songs more easily.
- Added label that holds background image, as tkinter provides no way to change the window's background image natively.

Changes 29/02/20

- Binded mouse 1 release event on musicbar, this will update current play_labelime.
- Binded mouse 1 press event on musicbar, this will update bool var self.m1_presseds value.
- Binded play_time_update on musicbar's val change, this will update the label just as the native Scale label would.
- Limited self.cur_sec's reach so that it doesn't go beyond the music's length.
- Binded mouse 1 double click, replaces old file dialog button.
- Binded WM_DELETE_WINDOW event to program, when window manager shuts down the program, it kills the music and windows properly.

Changes ??/02/20

- Added loop song list function to program.
-------------------------------------------------------------------------------------------------------------------------------------
Improvements brought by changes done on 02/03/20

- Improved UI
- Improved user experience

Improvements brought by changes done on 29/02/20

- Music stutter removed.
- Improved performance.
- Improved UI.
-------------------------------------------------------------------------------------------------------------------------------------
Dev Notes:

30/03/20
NOT THE PROBLEM
- Tkinter doesn't deal well when other threads generate events, even if the event isn't supposed to generate, put a var to ensure it
wont generate when you're trying to exit the program. Apply a protocol when window manager's exit button is pressed:
root.protocol("WM_DELETE_WINDOW", function)  # Execute on window manager exit button press

PROBLEM
- When you want to add a protocol when the exit button is pressed, make sure at the end you specify master.destroy() else the program
hangs and refuses the exit, this has to be at the very bottom of the metehod/function.

- You can use lambda expressions when you want to pass parameters to a function/method:
lambda: class_instance.class_function(parameter)

??/??/20
- self.m1_pressed will prevent the background thread from changing the musicbar's value, this is done to stop the background thread
from stealing the user's control over the music bar. Once the user releases m1 button, the music will update according to music bar's
value.
-------------------------------------------------------------------------------------------------------------------------------------
"""
