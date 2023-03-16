from fileinput import filename
import os
from re import I
import sys
from unicodedata import name
from unittest import result
import unreal
import streamline_painter
import csv
from tkinter import Tk, mainloop
from tkinter.filedialog import askopenfilenames
from os import listdir, walk
from os.path import isfile,join
import json

unreal.log("Hello, is it me you're looking for?")
#script args:
#0 self
#1 steamline thickness
#2 streamline cap vertices
#3 min velocity override
#4 max velocity override
DTCC_HUB_SAVED_FOLDER_NAME='DTCC/'
IMPORTED_STREAMLINES_JSON_FILE_NAME='processed_streamlines.json'
STREAMLINE_ACTOR_TAG='StreamlineActor'
unreal.log_warning("Streamline thickness:" + sys.argv[1])
STREAMLINE_THICKNESS = (float)(sys.argv[1])
unreal.log_warning("Streamline cap vertices:" + sys.argv[2])
STREAMLINE_CAP_VERTICES = (int)(sys.argv[2])

MIN_VELOCITY=0
MAX_VELOCITY=0

MIN_USER_VELOCITY=(float)(sys.argv[3])
MAX_USER_VELOCITY=(float)(sys.argv[4])

global jsonStreamlines
jsonStreamlines=[]


def getWorldLocationFromCsv(row, contextStr):
    try:
        x = (float)(row[0])
        y = (float)(row[1])
        z = (float)(row[2])
        return unreal.Vector(x,y,z)
    except:
        unreal.log_error("An error occured when trying to parse world location from csv in line:" + contextStr)
        return unreal.Vector.ZERO
    
def getVelocityFromCsv(row, contextStr):
    try:
        u = (float)(row[3])
        v = (float)(row[4])
        w = (float)(row[5])
        return unreal.Vector(u,v,w)
    except:
        unreal.log_error("An error occured when trying to parse world velocity from csv in line:" + contextStr)
        return unreal.Vector.ZERO
    
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

class JsonStreamline:
    name="N/A"

    def __init__(self,streamlineName):
        self.name=streamlineName
        self.locations.clear()
        self.velocities.clear()

    def __init__(self,streamlineName,streamlineLocations,streamlineVelocities):
        self.name=streamlineName
        self.locations=streamlineLocations
        self.velocities=streamlineVelocities
    
    def toJsonObj(self):
        data={}
        data['Name']=self.name
        data['StreamlineName']=self.name
        data['Points']=self.createPointsDictionary()
        return data
        
    def createPointsDictionary(self):
        points=[]
        for i in range(len(self.locations)):
            p={}
            p["x"]=self.locations[i].x
            p["y"]=self.locations[i].y
            p["z"]=self.locations[i].z
            p["vx"]=self.velocities[i].x
            p["vy"]=self.velocities[i].y
            p["vz"]=self.velocities[i].z
            p["p"]=0.0
            points.append(p)
        return points

    def __str__(self) -> str:
        return "Streamline name:" + self.name + " P[0]:" + str(self.locations[0].x) + " , " + str(self.locations[0].y) +" , " + str(self.locations[0].z)
    
def parseStreamlineValues(file, streamlineIndex):

    with open(file, newline='') as csvFile:
        reader = csv.reader(csvFile, delimiter=',')
        
        rowNum = 1
        streamlineLocs=[]
        streamlineVels=[]    
        for row in reader:
            worldLocation = convertVectorToUE4Coords(getWorldLocationFromCsv(row, str(rowNum)))
            worldVelocity = convertVectorToUE4Coords(getVelocityFromCsv(row,str(rowNum)))

            updateMinMaxVelocities(worldVelocity)

            if not worldLocation.is_zero():
                streamlineLocs.append(worldLocation)
                streamlineVels.append(worldVelocity)
            rowNum+=1
        jsonStreamlines.append(JsonStreamline(str(streamlineIndex),streamlineLocs,streamlineVels))

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
        
    fileName = filePath + IMPORTED_STREAMLINES_JSON_FILE_NAME
    unreal.log_warning("Saving static streamlines in: " + fileName)
    with open(fileName, 'w') as outfile:
        json.dump(streamline_data_set,outfile)

#Parsing streamlines....
#files = next(walk(sys.argv[1]), (None, None, []))[2]
#unreal.log_warning("provided path:" + sys.argv[1])
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
generateMergedJsonFile()

unreal.log("Spawned " + (str)(len(files)) + " Streamlines!")
unreal.log_warning("Detected min velocity of: " + (str)(MIN_VELOCITY) +" and max velocity of: " + (str)(MAX_VELOCITY))
#streamline_painter.paintNewVelocities(MIN_VELOCITY,MAX_VELOCITY)
unreal.log_warning("Visualizing ["+(str)(MIN_USER_VELOCITY)+" - "+(str)(MAX_USER_VELOCITY)+"] to visualize streamlines...")
#streamline_painter.paintNewVelocities(MIN_USER_VELOCITY,MAX_USER_VELOCITY)
