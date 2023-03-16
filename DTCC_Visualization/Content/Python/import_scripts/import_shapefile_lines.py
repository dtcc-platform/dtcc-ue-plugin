

import sys
import os

sys.path.append(os.path.abspath(".thirdparty"))

import shapefile as shp
import numpy as np
import matplotlib.tri as tri
import matplotlib.pyplot as plt

sf = shp.Reader("D:\\Perforce\\daniel_HOME_dtcc-plugin\\projects\\NoisePedestrians2022\\case5\\SMoG_FrolundaCase\\Frolundacase_StreetNetworkCentrality")

import matplotlib.colors as mcolors
from matplotlib import cm

import shapely
from shapely.geometry import Polygon

viridis = cm.get_cmap('viridis', 10)

colors = [i for i in mcolors.XKCD_COLORS.keys()]
plt.figure()

final_polygons = []
# import pdb; pdb.set_trace()

for i, sr in enumerate(sf.shapeRecords()):
    x = [i[0] for i in sr.shape.points[:]]
    y = [i[1] for i in sr.shape.points[:]]
    centrality = sr.record["AI_w2k_wl"]
    id = sr.record["id"]
    
#    plt.plot([c[0] for c in centros], [c[1] for c in centros], "+r")

    final_polygons.append( {
        "Name": id,
        "points": [{"X": p[0], "Y": p[1]} for p in sr.shape.points],
        "centrality": centrality
    })
    # plt.fill(x,y,colors[floors])
    # c = (floors/10,floors/10,floors/10)
    # plt.fill(x,y,color=c)#viridis(floors))

# plt.show()

import json

with open("shape_lines.json","w") as jout:
    json.dump(final_polygons,jout,indent=2)