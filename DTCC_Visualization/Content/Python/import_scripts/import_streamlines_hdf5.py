import sys
import pathlib

if len(sys.argv) < 2:
    print("Usage: import_streamlines_hdf5 path_to_data_folder[path_to_output_folder]")
    exit()

DTCC_HUB_SAVED_FOLDER_NAME='DTCC'
IMPORTED_STREAMLINES_JSON_FILE_NAME='imported_streamlines.json'

data_folder = sys.argv[1]

projpath = pathlib.Path(__file__).parent.resolve().parent.parent.parent.parent.parent
output_folder = projpath / "Saved" / DTCC_HUB_SAVED_FOLDER_NAME
output_folder
if len(sys.argv) > 2:
    output_folder = sys.argv[2]
print("Output folder:",output_folder)

plugin_python_path = pathlib.Path(__file__).parent.resolve().parent
tppath = plugin_python_path / ".thirdparty"
sys.path.append(str(plugin_python_path))
sys.path.append(str(tppath))

print( "Third-party path:",tppath )


import tables
import glob
import numpy as np

from import_scripts.streamline_json import StreamLineJson

fname = data_folder
if fname[-3:] != ".h5":
    filepaths = glob.glob(data_folder+"/stdStreamLines*.h5")
    print("KJSFKASH",len(filepaths))
    if len(filepaths)>0:
        fname = filepaths[0]
    

print("Reading streamlines from: ", fname)

f = tables.open_file(fname)

topo = f.root.Topology
geom = f.root.Geometry
vel = f.root.Node.Velocity
pres = f.root.Node.Pressure

print( f"%d points in streamlines" % (len(geom)) )

line_continues = topo[:-1,2] == topo[1:,0]

line_breaks = np.where(line_continues == False )[0]+1
line_starts = np.concatenate([[0],line_breaks])
line_ends = np.concatenate([line_breaks,[len(topo)]])
line_lengths = line_ends - line_starts

streamline_json_data_set=[]

for i in range(len(line_starts)):
    llen = line_lengths[i]
    if (llen<2):
        print(f"Skipping line %i with length %i" % (i,llen))
        continue
    print(f"Line %i (length %i)" % (i,llen))
    lstart = topo[line_starts[i]][0]
    if line_ends[i] < len(topo):
        lend = topo[line_ends[i]][0]
    else:
        lend = len(geom)

    print(f"  %i - %i" % (lstart,lend-1))
    lpos = geom[lstart:lend]
    lvel = vel[lstart:lend]
    lpres = pres[lstart:lend]

    sl = StreamLineJson()
    sl.locations = lpos
    sl.velocities = lvel
    sl.pressures = lpres

    streamline_json_data_set.append(sl.toJsonObj())

    # print(lpos[:,0])

# import pdb; pdb.set_trace()

f.close()

import json, os

pathExists = os.path.exists(output_folder)

if not pathExists:
    os.makedirs(output_folder)

with open(output_folder / IMPORTED_STREAMLINES_JSON_FILE_NAME, 'w') as outfile:
    #json.dump(data_set, outfile)
    json.dump(streamline_json_data_set,outfile)


# import pdb; pdb.set_trace()