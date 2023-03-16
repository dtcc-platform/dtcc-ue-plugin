

import sys
import os

sys.path.append(os.path.abspath(".thirdparty"))

import shapefile as shp
import numpy as np
import matplotlib.tri as tri
import matplotlib.pyplot as plt

# sf = shp.Reader("D:\\Perforce\\DTCC-2020-Home\\Infravis\\NoisePedestrians2022\\case5\\Building")
sf = shp.Reader("c:\\Users\\dansjo\\Perforce\\daniel_Openlab_dtcc_stream\\projects\\NoisePedestrians2022\\case4\\Building")

import matplotlib.colors as mcolors
from matplotlib import cm

import shapely
from shapely.geometry import Polygon

viridis = cm.get_cmap('viridis', 10)

colors = [i for i in mcolors.XKCD_COLORS.keys()]
plt.figure()

final_polygons = []

for i, sr in enumerate(sf.shapeRecords()):
    x = [i[0] for i in sr.shape.points[:]]
    y = [i[1] for i in sr.shape.points[:]]
    floors = sr.record["NUMBEROF1"]
    triang = tri.Triangulation(x, y)

    poly = Polygon(sr.shape.points)

    mask = []
    centros = []
    for t in triang.triangles:
        pi = Polygon([sr.shape.points[i] for i in t])
        mask.append( not poly.contains( pi.centroid ) )
        centros.append(pi.centroid.coords.xy)
    # print(mask,len(triang.triangles))
    triang.set_mask(mask)
    
    plt.plot([c[0] for c in centros], [c[1] for c in centros], "+r")
    plt.triplot(triang)

    final_polygons.append( {
        "Name": f"Polygon%d" % i,
        "points": [{"X": p[0], "Y": p[1], "Z": 0} for p in sr.shape.points],
        "triangles": triang.get_masked_triangles().flatten().tolist(),
        "height": floors * 3.0
    })
    # plt.fill(x,y,colors[floors])
    # c = (floors/10,floors/10,floors/10)
    # plt.fill(x,y,color=c)#viridis(floors))

plt.show()

import json

with open("shapes.json","w") as jout:
    json.dump(final_polygons,jout,indent=2)