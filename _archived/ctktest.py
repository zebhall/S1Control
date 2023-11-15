import os
import sys
import threading
import time
#import hashlib
import pandas as pd
import json
import shutil
import socket
import xmltodict
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, font
from tkinter.ttk import Progressbar, Treeview
from concurrent import futures
import struct
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk



ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"







def asd():
    print('asdasd')







gui = ctk.CTk()
gui.title("S1Control")
#gui.wm_attributes('-toolwindow', 'True',)
gui.geometry('+0+0')
#gui.geometry('1500x1000')
gui.grid_columnconfigure(1, weight=1)
gui.grid_columnconfigure((2, 3), weight=0)
gui.grid_rowconfigure((0, 1, 2), weight=1)
gui.grid_rowconfigure(3, weight=0)






# Fonts
consolas24 = font.Font(family='Consolas', size=24)
consolas20 = font.Font(family='Consolas', size=20)
consolas18 = font.Font(family='Consolas', size=18)
consolas18B = font.Font(family='Consolas', size=18, weight = 'bold')
consolas16 = font.Font(family='Consolas', size=16)
consolas13 = font.Font(family='Consolas', size=13)
consolas12 = font.Font(family='Consolas', size=12)
consolas10 = font.Font(family='Consolas', size=10)
consolas10B = font.Font(family='Consolas', size=10, weight = 'bold')
consolas09 = font.Font(family='Consolas', size=9)
consolas08 = font.Font(family='Consolas', size=8)
consolas07 = font.Font(family='Consolas', size=7)
plotfont = {'fontname':'Consolas'}
ctkfont = ctk.CTkFont(family='Consolas', size=12)

# Colour Assignments
WHITEISH = "#FAFAFA"
NAVYGREY = "#566573"
CHARCOAL = "#181819"
GRAPHITE = "#29292B"

PSS_DARKBLUE = "#252D5C"
PSS_LIGHTBLUE = "#1B75BC"
PSS_ORANGE = "#D85820"
PSS_GREY = "#9E9FA3"

CROW_LGREY = "#4e576c"
CROW_DGREY = "#394d60"
CROW_LBLUE = "#316d90"
CROW_MBLUE = "#1e5073"
CROW_DBLUE = "#062435"

# Colours Used
buttonbg1 = CROW_LBLUE
buttonfg1 = WHITEISH
buttonbg2 = CROW_MBLUE
buttonfg2 = WHITEISH
buttonbg3 = CROW_DBLUE
buttonfg3 = WHITEISH
textfg1 = CHARCOAL

# Styles
Astyle = ttk.Style()
Astyle.configure('my.TMenubutton', font = consolas10)


# Frames
BHSframe = ctk.CTkFrame(gui, width=1200,corner_radius=0)     # bottom
BHSframe.grid(row=3,column=0, columnspan=4)

LHSframe = ctk.CTkFrame(gui, width=200,corner_radius=0)
LHSframe.grid(row=0,column=0, rowspan=3)

RHSframe = ctk.CTkFrame(gui, width=200,corner_radius=5)
RHSframe.grid(row=0,column=1, columnspan=3, rowspan=3)


ctrlframe = tk.LabelFrame(LHSframe, width = 100, height = 50, pady = 5, padx = 5, fg = "#566666", font = consolas10, text = "Control Instrument")
ctrlframe.grid(row=2, column=1, rowspan = 2, columnspan=2, pady = 0, padx = [8,4], sticky= tk.NSEW)

configframe = tk.LabelFrame(LHSframe, width = 100, height = 50, pady = 5, padx = 5, fg = "#545454", font = consolas10, text = "Configure Instrument")
configframe.grid(row=4, column=1, rowspan = 2, columnspan=2, pady = 0, padx = [8,4], sticky= tk.NSEW)

infoframe = tk.LabelFrame(LHSframe, width = 400, height = 50, pady = 5, padx = 5, fg = "#545454", font = consolas10, text = "Log")
infoframe.grid(row=6, column=1, rowspan = 6, columnspan=2, pady = 0, padx = [8,4], sticky= tk.NSEW)

spectraframe = tk.LabelFrame(RHSframe, width = 300, height = 50, pady = 5, padx = 5, fg = "#545454", font = consolas10, text = "Spectra")
spectraframe.grid(row=2, column=3, rowspan = 4, columnspan=7, pady = 0, padx = [4,8], sticky= tk.NSEW)

resultsframe = tk.LabelFrame(RHSframe, width = 300, height = 50, pady = 5, padx = 5, fg = "#545454", font = consolas10, text = "Results")
resultsframe.grid(row=6, column=3, rowspan = 6, columnspan=7, pady = 0, padx = [4,8], sticky= tk.NSEW)

statusframe = tk.LabelFrame(BHSframe, width = 200, height = 50, pady = 5, padx = 5, fg = "#545454", font = consolas10, text = "Status")
statusframe.grid(row=12, column=1, rowspan = 1, columnspan=10, pady = [0,8], padx = [8,8], sticky= tk.NSEW)


# Buttons
button_reconnect = ctk.CTkButton(ctrlframe, width = 15, text = "Login",command = asd)
button_reconnect.grid(row=1, column=1, padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)

button_assay_text = tk.StringVar()
button_assay_text.set('Start Assay')
button_assay = ctk.CTkButton(ctrlframe, width = 15, textvariable = button_assay_text,command = asd)
button_assay.grid(row=2, column=1, padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)

#button_startlistener = ctk.CTkButton(width = 15, text = "start listen", font = consolas10, fg = buttonfg3, bg = buttonbg3, command = lambda:xrfListenLoop_Start(None)).pack(ipadx=8,ipady=2)

#button_getinstdef = ctk.CTkButton(width = 15, text = "get instdef", font = consolas10, fg = buttonfg3, bg = buttonbg3, command = getInfoClicked).pack(ipadx=8,ipady=2)
button_enablespectra = ctk.CTkButton(configframe, width = 15, text = "Enable Spectra",command = asd)
button_enablespectra.grid(row=4, column=1, padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)
button_disablespectra = ctk.CTkButton(configframe, width = 15, text = "Disable Spectra", command = asd)
button_disablespectra.grid(row=5, column=1, padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)
button_setsystemtime = ctk.CTkButton(configframe, width = 15, text = "Sync System Time",command = asd)
button_setsystemtime.grid(row=6, column=1, padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)

#button_getapplicationprefs = ctk.CTkButton(configframe, width = 25, text = "get current app prefs", font = consolas10, fg = buttonfg3, bg = buttonbg3, command = instrument_QueryCurrentApplicationPreferences)
#button_getapplicationprefs.grid(row=7, column=1, padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)

button_getapplicationphasetimes = ctk.CTkButton(configframe, width = 25, text = "Phase Times", command = asd)
button_getapplicationphasetimes.grid(row=8, column=1, padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)


# Current Instrument Info stuff
label_currentapplication_text = tk.StringVar()
label_currentapplication_text.set('Current Application: ')
label_currentapplication = tk.Label(configframe, textvariable=label_currentapplication_text, font = consolas10)
label_currentapplication.grid(row=9, column=1, padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)

# Consecutive Tests Section
repeats_choice_var = tk.StringVar()
repeats_choice_list = ['1','2','3','4','5','6','7','8','9','10','15','20','50','100']
dropdown_repeattests = ttk.OptionMenu(ctrlframe, repeats_choice_var, 'Consective Assays', *repeats_choice_list, command=asd, style='my.TMenubutton', direction='right')
dropdown_repeattests['menu'].configure(font=consolas10)

dropdown_repeattests.grid(row=3,column=1,padx=2, pady=2, ipadx=4, ipady=0, sticky=tk.NSEW)


# Log Box

logbox_xscroll = tk.Scrollbar(infoframe, orient = 'horizontal')
logbox_xscroll.grid(row = 3, column = 1, columnspan = 2, sticky = tk.NSEW)
logbox_yscroll = tk.Scrollbar(infoframe, orient = 'vertical')
logbox_yscroll.grid(row = 1, column = 3, columnspan = 1, rowspan= 2, sticky = tk.NSEW)
logbox = tk.Text(infoframe, height = 30, width = 40, font = consolas08, bg = CHARCOAL, fg = WHITEISH, wrap = tk.NONE, xscrollcommand=logbox_xscroll.set, yscrollcommand=logbox_yscroll.set)
logbox.grid(row = 1, column = 1, columnspan = 2, rowspan= 2, sticky = tk.NSEW)
logbox.config(state = 'disabled')
logbox_xscroll.config(command = logbox.xview)
logbox_yscroll.config(command = logbox.yview)

# Spectraframe Stuff

fig = Figure(figsize = (10, 4), dpi = 100)
fig.subplots_adjust(left=0.07, bottom=0.08, right=0.99, top=0.97, wspace=None, hspace=None)
fig.set_facecolor('#f0f0f0')
#plt.style.use('seaborn-v0_8-<paper>')
plt.rcParams["font.family"] = "Consolas"
spectra_ax = fig.add_subplot(111)
spectra_ax.set_xlim(xmin=0, xmax=2100)
#spectra_ax.set_ylim(ymin=0)
spectra_ax.autoscale_view()
#spectra_ax.axhline(y=0, color='k')
#spectra_ax.axvline(x=0, color='k')
spectracanvas = FigureCanvasTkAgg(fig,master = spectraframe)

spectracanvas.draw()
spectratoolbar = NavigationToolbar2Tk(spectracanvas,spectraframe)
spectracanvas.get_tk_widget().pack(side=tk.BOTTOM)


gui.mainloop()




