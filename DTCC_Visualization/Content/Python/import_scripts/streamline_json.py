
import numpy as np

class StreamLineJson:

    def __init__(self,streamlineName="Noname",streamlineLocations=np.empty((0,3)),streamlineVelocities=np.empty((0,3)),streamlinePressures=np.empty((0,1))):
        self.name=streamlineName
        self.pressures = streamlinePressures
        self.locations=streamlineLocations
        self.velocities=streamlineVelocities

    def toJsonObj(self):
        data={}
        data['Name']=self.name
        data['StreamlineName']=self.name
        data['Points']=self.createPointsDictionary()
        return data

    def createPointsDictionary(self):
        self.locations = self.locations.astype(float)
        self.velocities = self.velocities.astype(float)
        self.pressures = self.pressures.astype(float)
        points=[]
        for i in range(len(self.locations)):
            p={}
            p["x"]=self.locations[i,0]
            p["y"]=self.locations[i,1]
            p["z"]=self.locations[i,2]
            p["vx"]=self.velocities[i,0]
            p["vy"]=self.velocities[i,1]
            p["vz"]=self.velocities[i,2]
            if self.pressures.size>0:
                p["p"]=self.pressures[i]
            else:
                p["p"]=0.0
#            print(p)
            points.append(p)
        return points
