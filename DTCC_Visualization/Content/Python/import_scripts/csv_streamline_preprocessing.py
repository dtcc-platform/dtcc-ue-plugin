import json
import os
import sys
import numpy as np
import unreal
from import_scripts.streamline_json import StreamLineJson

DTCC_HUB_SAVED_FOLDER_NAME='DTCC/'
IMPORTED_STREAMLINES_JSON_FILE_NAME='imported_streamlines.json'
PROCESSED_STREAMLINES_JSON_FILE_NAME='processed_streamlines.json'


def scalePointLocation(inPoint, locationScale, flipY):
    modifiedPoint=np.array([inPoint["x"],inPoint["y"],inPoint["z"]])

    modifiedPoint[0]*=locationScale[0]
    modifiedPoint[1]*=locationScale[1]
    modifiedPoint[2]*=locationScale[2]
    
    return modifiedPoint

def scalePointVelocity(inPoint, velocityScale, flipY):
    modifiedPoint=np.array([inPoint["vx"], inPoint["vy"], inPoint["vz"]])

    modifiedPoint[0]*=velocityScale[0]
    modifiedPoint[1]*=velocityScale[1]
    modifiedPoint[2]*=velocityScale[2]

    return modifiedPoint
    
#Get static streamlines files
filePath = os.path.join(unreal.Paths.project_saved_dir(), DTCC_HUB_SAVED_FOLDER_NAME)
file = filePath + IMPORTED_STREAMLINES_JSON_FILE_NAME
f = open(file)
data = json.load(f)

modifiedStreamlines = []
index=1

locationScale = np.array([sys.argv[1], sys.argv[2], sys.argv[3]], dtype=np.float32)
velocityScale = np.array([sys.argv[4], sys.argv[5], sys.argv[6]], dtype=np.float32)
flipY=sys.argv[7]

if flipY=="true":
    locationScale[1]*=-1.0
    velocityScale[1]*=-1.0

unreal.log_warning("Starting preprocessing with location scale:" + str(locationScale) +" velocity scale:" + str(velocityScale) + " flip Y:" + str(flipY))
for i in data:
    #Modifying location & velocity of point
    points = i["Points"]
    modifiedLocations = np.empty((0,3))
    modifiedVelocities = np.empty((0,3))
    pressures = np.empty((0,1))
    for p in points:
        modifiedLocations = np.append(modifiedLocations, [scalePointLocation(p, locationScale, flipY)] , 0)
        modifiedVelocities = np.append(modifiedVelocities, [scalePointVelocity(p, velocityScale, flipY)] , 0)
        pressures = np.append(pressures,p["p"])

    modifiedStreamlines.append(StreamLineJson(str(index),modifiedLocations,modifiedVelocities,pressures))
    index+=1

#Saving processed streamline data...
unreal.log("Processed "+str(len(modifiedStreamlines)) + " streamlines")
streamline_data_set=[]
for i in range(len(modifiedStreamlines)):
    streamline_data_set.append(modifiedStreamlines[i].toJsonObj())

#Check if save path exists, if not create a directory and save the file in there
filePath = os.path.join(unreal.Paths.project_saved_dir(), DTCC_HUB_SAVED_FOLDER_NAME)
pathExists = os.path.exists(filePath)
if not pathExists:
    os.makedirs(filePath)
    
fileName = filePath + PROCESSED_STREAMLINES_JSON_FILE_NAME
unreal.log_warning("Saving processed static streamlines in: " + fileName)
with open(fileName, 'w') as outfile:
    json.dump(streamline_data_set,outfile)