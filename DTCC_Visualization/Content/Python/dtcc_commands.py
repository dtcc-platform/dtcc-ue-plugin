import dtcc


from tkinter import Tk, mainloop
from tkinter.filedialog import askopenfilenames
from os import listdir, walk
from os.path import isfile,join
import json


def dtcc_selectfiles():

    root = Tk()
    files = askopenfilenames()
    #mainloop()
    root.destroy()
    
    return files

def dtcc_load_streamlines_to_json(sourcepath,fileformat):
    pass
