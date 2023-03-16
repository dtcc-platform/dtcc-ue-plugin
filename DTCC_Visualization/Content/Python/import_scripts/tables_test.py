
from decimal import DivisionByZero
import tables as tb
import numpy as np

f = tb.open_file("D:\Perforce\DTCC-2020-Home\ExampleData\FluidResFluid002000.h5")

top = f.root.Topology
geom = f.root.Geometry

positions = np.zeros((top.shape[0],3))
extents = np.zeros((top.shape[0],3))
for i in range(top.shape[0]):
    poss = geom[top[i],:]
    positions[i] = np.mean(poss,0)
    extents[i] = np.max(poss,0)-np.min(poss,0)

minpos = np.min(positions,0)
maxpos = np.max(positions,0)
minext = np.min(extents,0)
maxext = np.max(extents,0)

npositions = (positions-minpos) / (maxpos-minpos)

nextents = np.ones(extents.shape)
extrange = maxext-minext
if np.all(extrange!=0):
    nextents = (extents-minext) / (maxext-minext)

res = 256
npositions.resize((res//2,res,3))
nextents.resize((res//2,res,3))

img = np.zeros((res,res,3))
img[:res//2,:,:] = npositions
img[res//2:,:,:] = nextents

import matplotlib.pyplot as plt
plt.imshow(img)
plt.show()
