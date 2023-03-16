
import json
import pathlib

projpath = pathlib.Path(__file__).parent.resolve().parent.parent.parent.parent.parent
output_folder = projpath / "Content" / "DTCC"
print("Output folder:",output_folder)

fname = output_folder / "imported_streamlines.json"
print("Json file:",fname)

with open(fname,"r") as f:
    jsondata = json.load(f)

import pdb; pdb.set_trace()
