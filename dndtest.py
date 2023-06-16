from tkinter import StringVar, TOP
from tkinterdnd2 import TkinterDnD, DND_ALL
import customtkinter as ctk

class CTkdnd(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

a = 'abcdefg'
print(a[-3:])

ctk.set_appearance_mode("dark")
#ctk.set_default_color_theme("blue")

def get_dnd_path(event):
    pathLabel.configure(text = event.data)

#root = TkinterDnD.Tk()
root = CTkdnd()
root.geometry("350x100")
root.title("Get file path")

nameVar = StringVar()

entryWidget = ctk.CTkEntry(root)
entryWidget.pack(side=TOP, padx=5, pady=5)

pathLabel = ctk.CTkLabel(root, text="Drag and drop file in the entry box")
pathLabel.pack(side=TOP)

entryWidget.drop_target_register(DND_ALL)
entryWidget.dnd_bind("<<Drop>>", get_dnd_path)



root.mainloop()