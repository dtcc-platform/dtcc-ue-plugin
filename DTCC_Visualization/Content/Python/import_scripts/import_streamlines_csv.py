from fileinput import filename
import os
from re import I
import sys
from unicodedata import name
from unittest import result
import unreal
import csv
from tkinter import Tk, mainloop
from tkinter.filedialog import askopenfilenames
from os import listdir, walk
from os.path import isfile,join
import json
import numpy as np
from import_scripts.streamline_json import StreamLineJson

DTCC_HUB_SAVED_FOLDER_NAME='DTCC'
IMPORTED_STREAMLINES_JSON_FILE_NAME='imported_streamlines.json'

MIN_VELOCITY=0
MAX_VELOCITY=0

global jsonStreamlines
jsonStreamlines=[]


def getWorldLocationFromCsv(row, contextStr):
    try:
        x = (float)(row[0])
        y = (float)(row[1])
        z = (float)(row[2])
        return np.array([x,y,z])
    except:
        unreal.log_error("An error occured when trying to parse world location from csv in line:" + contextStr)
        print(row)
        return np.zeros(3)
    
def getVelocityFromCsv(row, contextStr):
    try:
        u = (float)(row[3])
        v = (float)(row[4])
        w = (float)(row[5])
        return np.array([u,v,w])
    except:
        unreal.log_error("An error occured when trying to parse world velocity from csv in line:" + contextStr)
        print(row)
        return np.zeros(3)

def zeroLocation(location):
    return np.array_equal(np.zeros(3),location)
    
def convertVectorToUE4Coords(vector):
    vector.x *= 100
    vector.y *= -100
    vector.z *=100
    return vector

def updateMinMaxVelocities(vel):
    length = vel.length()
    global MIN_VELOCITY
    global MAX_VELOCITY
    if length<MIN_VELOCITY:
        MIN_VELOCITY = length
    elif length>MAX_VELOCITY:
        MAX_VELOCITY = length
    
def parseStreamlineValues(file, streamlineIndex):

    with open(file, newline='') as csvFile:
        reader = csv.reader(csvFile, delimiter=',')
        
        rowNum = 1
        streamlineLocs=np.empty((0,3))
        streamlineVels=np.empty((0,3)) 
        for row in reader:
            if row[0][0] == "#":
                rowNum+=1
                continue
            worldLocation = getWorldLocationFromCsv(row,str(rowNum))
            #print(worldLocation)
            worldVelocity = getVelocityFromCsv(row,str(rowNum))
            #worldLocation = convertVectorToUE4Coords(getWorldLocationFromCsv(row, str(rowNum)))
            #worldVelocity = convertVectorToUE4Coords(getVelocityFromCsv(row,str(rowNum)))

            #updateMinMaxVelocities(worldVelocity)

            if not zeroLocation(worldLocation):
                streamlineLocs = np.append(streamlineLocs, [worldLocation], 0)
                streamlineVels = np.append(streamlineVels, [worldVelocity], 0)
            rowNum+=1
        #print(streamlineLocs)
        jsonStreamlines.append(StreamLineJson(str(streamlineIndex),streamlineLocs,streamlineVels))

def generateMergedJsonFile():
    
    unreal.log("streamline json num:"+str(len(jsonStreamlines)))
    streamline_data_set=[]
    for i in range(len(jsonStreamlines)):
        streamline_data_set.append(jsonStreamlines[i].toJsonObj())

    #Check if save path exists, if not create a directory and save the file in there
    filePath = os.path.join(unreal.Paths.project_saved_dir(), DTCC_HUB_SAVED_FOLDER_NAME)
    pathExists = os.path.exists(filePath)

    if not pathExists:
        os.makedirs(filePath)
        
    fileName = os.path.join( filePath, IMPORTED_STREAMLINES_JSON_FILE_NAME )
    unreal.log_warning("Saving static streamlines in: " + fileName)
    with open(fileName, 'w') as outfile:
        json.dump(streamline_data_set,outfile)

# Open window to select files
root = Tk()
files = askopenfilenames()
#mainloop()
root.destroy()
print(files)
currentFileNum=0 # used for progress update
filesNum = len(files) # used for progress update
unreal.log("read:" + (str)(len(files)) + " files in total")
with unreal.ScopedSlowTask(filesNum, 'Parsing Streamline data...') as slow_task:
    slow_task.make_dialog(True)
    for i in files:
        currentFileNum+=1
        if slow_task.should_cancel():
            break
        slow_task.enter_progress_frame(1, 'Parsing Streamline data frame...' + str(currentFileNum) + ' / ' + str(filesNum))
        parseStreamlineValues(i,currentFileNum)

# Generate the merged json file containing all the data for the parsed streamlines        
generateMergedJsonFile()

#unreal.log("Spawned " + (str)(len(files)) + " Streamlines!")
unreal.log_warning("Detected min velocity of: " + (str)(MIN_VELOCITY) +" and max velocity of: " + (str)(MAX_VELOCITY))
