import unreal
import dtcc

import os, re

from dtcc.config import Config

class DataManager:
    pass

# def getDefaultExternalPath():
#     Config.load()

#     return Config.config_data["external_data_path"]

from tkinter import Tk, mainloop
from tkinter.filedialog import askopenfilenames
def selectFiles():
    root = Tk()
    files = askopenfilenames()
    #mainloop()
    root.destroy()
    return files


def find_NC_files(path=False):
    if not path:
        print("No path provided!")
        return
    
    print("Finding NETCDF files at path: " + path)

    files = os.listdir(path)
    ncfiles = []
    for fname in files:
        m = re.search(r"^.+\.nc",fname)
        if m:
            ncfiles.append(fname)

    return ncfiles

import pathlib

def getLabelForDataFile(filename):
    return pathlib.Path(filename).stem
#     m = re.search(pattern,filename)
#    m = re.search("^cas_(S.+)_(.+Veg)_(wind.+)_av_3d\.nc",filename)
    # print(filename,pattern+r".+")
    # if not m:
    #     return pathlib.Path(filename).stem

    # label = ""
    # for i in range(1,len(m.groups())+1):
    #     label = label + m.group(i)
    # return label