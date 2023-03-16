
from dtcc.config import Config
import dtcc.util

import unreal
import os
import pathlib

DTCC_HUB_SAVED_FOLDER_NAME='DTCC'
# IMPORTED_STREAMLINES_JSON_FILE_NAME='imported_streamlines.json'

class LinesData:

    def __init__(self):
        self.pos_maxs = False
        self.pos_mins = False
        self.source_data_path = False
        self.num_lines = 0
        self.lines_type = "None"
        self.texture1 = ""
        self.texture2 = ""
        self.texture3 = ""
        self.textureCombDivider = 0.0
        self.data_table = ""
        self.data_lines_per_row = 1.0
        self.label = False

    def saveMetaData(self,clear_old=False):
        # out_csv_path = unreal.Paths.project_content_dir()+"DTCC/DataImages/LineDataTextureSources.csv"

        filePath = pathlib.Path(unreal.Paths.project_saved_dir()).resolve() / DTCC_HUB_SAVED_FOLDER_NAME
        out_csv_path = filePath / "LineDataTextureSources.csv"

        # Save empty file (only header) if not exists, or clear requested, to allow rest of code to assume it exists
        if not os.path.isfile(out_csv_path) or clear_old:
            with open(out_csv_path,"w") as f:
                f.write("---,LineType,Label,SourcePath,NumLines,PositionMin,PositionMax,DataMin,DataMax,PositionTexture,TextureCombiningLoDivider,PositionTexture_Lo,DataTexture,VelocitySpeedMin,VelocitySpeedMax,DataTable,LinesPerTextureRow\n")

        with open(out_csv_path,"r") as f:
            lines = f.read().splitlines()

        newlines = [lines[0]]
        i = 1
        for l in lines[1:]:
            vals = l.split("\",\"")
            keytype = vals[0].split(",\"")
            print( "Line:", keytype[0], keytype[1], vals[1] )
            if keytype[1] == self.lines_type and vals[1] == self.source_data_path:
                continue
            keytype[0] = f"LineData{i}"
            i += 1
            vals[0] = ",\"".join(keytype)
            line = "\",\"".join(vals)
            newlines.append(line)

        def vec2str(v):
            return f"x={v[0]}, y={v[1]}, z={v[2]}"

        newlines.append(f"LineData{i},\"{self.lines_type}\",\"{self.label}\",\"{self.source_data_path}\",\"{self.num_lines}\",\"{vec2str(self.pos_mins)}\","
            + f"\"{vec2str(self.pos_maxs)}\",\"{vec2str(self.vel_mins)}\",\"{vec2str(self.vel_maxs)}\",\"{self.texture1}\",\"{self.textureCombDivider}\",\"{self.texture2}\",\"{self.texture3}\","
            + f"{self.speed_min}, {self.speed_max},\"{self.data_table}\",\"{self.data_lines_per_row}\"" )

        print("New lines:", "\n".join(newlines))
        with open(out_csv_path,"w") as f:
            f.write("\n".join(newlines))
