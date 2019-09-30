import time
import datetime
from ReadSheet import program_start
import PIL
from PIL import ImageTk
from PIL import Image
from tkinter import *
import tkinter as tk
from tkinter.filedialog import askopenfilename
import threading


start_time = time.time()
now = datetime.datetime.now()
print(now)

# path = filedialog.askopenfilename(initialdir="/", title="Select file",
#                                filetypes=(("xlsx files", "*.xlsx"), ("all files", "*.*")))

'''
path = 'C:\\Users\ArnoldGT\Desktop\ps4_01_08_15.xlsx'
# path = 'C:\\Users\ArnoldGT\Desktop\ns_price_change_8_10_18.xlsx'
# wb = openpyxl.load_workbook('C:\\Users\ArnoldGT\Desktop\ps4_01_08_15.xlsx')
wb = openpyxl.load_workbook(path)
sheet = wb.active
'''

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()


        self.image = PIL.Image.open('mario_small_bg.gif')
        self.bg_copy = self.image.copy()
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background = Label(self, image=self.background_image)
        self.background.place(x=0, y=0, relwidth=1, relheight=1)

        self.master = master
        self.master.bind('<Configure>', self._resize_image)
        #self.grid_rowconfigure(0,weight=1)
        self.create_widgets()





    def _resize_image(self, event):
        new_width = self.master.winfo_width()
        new_height = self.master.winfo_height()

        self.image = self.bg_copy.resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)

    def create_widgets(self):


        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.choose_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        system = ""
        file = ""
        retailer = ""

        platforms = ['Playstation 4', 'Playstation 3', 'Playstation 2', 'Playstation One', 'PS Vita', 'PSP',
                     'Nintendo Switch', 'Nintendo Wii U', 'Nintendo Wii', 'Nintendo Gamecube', 'Nintendo 64', 'SNES',
                     'NES', 'Nintendo 3DS',  'Nintendo DS', 'Nintendo Gameboy Advance', 'Nintendo Gameboy',
                     'Xbox One', 'Xbox 360', 'Xbox', 'Sega Genesis', 'Sega Saturn', 'Sega Dreamcast' ]

        retailers = ['Pricecharting', 'Gamestop']

        tkvar_platform = StringVar(self)
        tkvar_platform.set("None Selected")

        tkvar_retail = StringVar(self)
        tkvar_retail.set("None Selected")



        # Selection Labels / Options
        self.file_display = Label(self, text="", bg="#afcfee")
        self.file_display.grid(row=0, column=0, columnspan=2, padx=(70, 0))
        self.file_display.configure(width="55")


        self.platform_label = Label(self, text='Choose a platform', bg="#2395DC", font=("Helvetica", 14))
        self.platform_label.grid(row=1, column=0, padx=(70, 0), pady=(15, 0))

        game_dropdown = OptionMenu(self, tkvar_platform, *platforms, command=self.dropdown)
        game_dropdown.config(bg="#afcfee")

        game_dropdown.grid(row=1, column=1, pady=(15, 0))

        self.retailer_label = Label(self, text='Choose a retailer', bg="#2395DC", font=("Helvetica", 14))
        self.retailer_label.grid(row=2, column=0, padx=(70, 0))

        retailer_dropdown = OptionMenu(self, tkvar_retail, *retailers, command=self.ret_dropdown)
        retailer_dropdown.config(bg="#afcfee")
        retailer_dropdown.grid(row=2, column=1)

        self.start_row_label = Label(self, text='Enter Start Row', bg="#2395DC", font=("Helvetica", 14))
        self.start_row_label.grid(row=3, column=0, padx=(70, 0), pady=(15, 0))
        self.start_row = Entry(self, bg="#afcfee", width="8")
        self.start_row.insert(END, "1")
        self.start_row.grid(row=4, column=0, padx=(70, 0))

        self.end_row_label = Label(self, text='Enter End Row', bg="#2395DC", font=("Helvetica", 14))
        self.end_row_label.grid(row=3, column=1, pady=(15, 0))
        self.end_row = Entry(self, bg="#afcfee", width="8")
        self.end_row.insert(END, "Max Row")
        self.end_row.grid(row=4, column=1)

        self.save_to_label = Label(self, text='Type name for save file', bg="#2395DC", font=("Helvetica", 14))
        self.save_to_label.grid(row=5, column=0, columnspan=2, padx=(70, 0), pady=(10, 0))

        self.save_name = Entry(self, bg="#afcfee")
        self.save_name.grid(row=6, column=0, columnspan=2,padx=(70, 0))

        #self.run = Button(self, text="Run Program", fg="red", command=lambda: begin_read(self.system, self.file, self.save_name.get()))
        self.run = Button(self, text="Run Program", fg="red", command=self.start)
        self.run.grid(row=7, column=0, columnspan=2,padx=(70, 0), pady=(10,0))



    def dropdown(self, value):
        self.system = value
        return value

    def ret_dropdown(self, value):
        self.retailer = value
        return value

    def choose_file(self):
        file = askopenfilename(initialdir="/", title="Select file",
                               filetypes=(("xls files", "*.xls"), ("xlsx files", "*.xlsx"),  ("all files", "*.*")))
        self.file_display.config(text=file)
        self.file = file

    def start(self):
        threads = []


        print("Start Row: " + self.start_row.get() + " End Row: " + self.end_row.get())
        t = threading.Thread(target=program_start, args=(self.system,
                self.file, self.save_name.get(), self.retailer, self.start_row.get(), self.end_row.get()))
        #begin_read(self.system, self.file, self.save_name.get())
        #threads.append(t)
        t.start()

    def quit(self):
        sys.exit(0)


root = Tk()
root.geometry("540x325")


app = Application(master=root)
app.pack(fill=BOTH, expand=YES)
app.mainloop()

#begin_read('Playstation 4', 'C:\\Users\ArnoldGT\Desktop\ps4_01_08_15.xlsx', 'please')
print("--- %s seconds ---" % (time.time() - start_time))
