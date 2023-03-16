from math import inf
import matplotlib
import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt

import matplotlib.image as mpimg


import PIL.Image as pimg

import glob
import os
import pathlib

from dtcc.config import Config

from dtcc.lines_data import LinesData
from dtcc.util import importDataTexture
from import_scripts.streamline_json import StreamLineJson

import OpenEXR, Imath, pathlib
import unreal
import json

DTCC_HUB_SAVED_FOLDER_NAME='DTCC'
# IMPORTED_STREAMLINES_JSON_FILE_NAME='imported_streamlines.json'

def include_All(sl,linedata):
    return True

def include_ByHeight(sl,linedata):
    try:
        return np.nanmean(linedata[:,2]) < sl.height_limit
    except AttributeError:
        return np.nanmean(linedata[:,2]) < 50

class StreamLinesData(LinesData):
    
    def __init__(self, data_path=False, label=False, force_reload=False):
        """ Set data_path to True to read default data at once """
        self.source_data_path = False
        self.label=label
        self.imdata = np.array([])

        if data_path:
            self.readData(data_path,force_reload)

    def readData(self,data_path=True,force_reload=False,inclusion_test=include_All):
        """
        data_path: Defaults to streamlines_data_path from config if set to True.
        """
        Config.load()
        # if data_path == True:
        #     data_path = Config.config_data["streamlines_data_path"]
        self.source_data_path = data_path

        if self.label == False:
            dpath = pathlib.Path(self.source_data_path)
            self.label = dpath.parts[-1]

        # if not force_reload:
        #     cache_filepath = Config.getTempFilepath("streamlines_source.npy")
        #     print("Trying to load from cache:" + cache_filepath)
        #     if os.path.exists(cache_filepath):
        #         self.imdata = np.load(cache_filepath)
        #         print("Loaded from cache:" + cache_filepath)
        #         self.pos_mins = np.nanmin(self.imdata[:,:],axis=(0,1))
        #         self.pos_maxs = np.nanmax(self.imdata[:,:],axis=(0,1))

        #         self.num_lines = np.sum(np.isfinite(self.imdata[:,0,0]))

        #         cache_filepath_vel = Config.getTempFilepath("streamlines_vel_source.npy")
        #         print("Trying to load from cache:" + cache_filepath_vel)
        #         if os.path.exists(cache_filepath_vel):
        #             self.imdata_vel = np.load(cache_filepath_vel)
        #             print("Loaded from cache:" + cache_filepath_vel)
        #             self.vel_mins = np.nanmin(self.imdata_vel[:,:],axis=(0,1))
        #             self.vel_maxs = np.nanmax(self.imdata_vel[:,:],axis=(0,1))
        #         return

        ks = 16 # 1024 * ks streamlines encoded
        self.imdata = np.empty([ks*1024, 1024, 3])
        self.imdata_vel = np.empty([ks*1024, 1024, 3])
        # Set to nan to get correct mean and range calculation below
        self.imdata[:] = np.nan
        self.imdata_vel[:] = np.nan
        
        # filepaths = glob.glob(self.source_data_path+"/stdStreamLine*Export.data")
        # for i in range(0,15000):
        #     fpath = f"{self.source_data_path}/stdStreamLine{i:04d}Export.data"
        #     if not os.path.isfile(fpath):
        #         break
        #     filepaths.append(fpath)

        filePath = pathlib.Path(unreal.Paths.project_saved_dir()).resolve() / DTCC_HUB_SAVED_FOLDER_NAME
        fname = filePath / "processed_streamlines.json"
        with open(fname,"r") as f:
            jsondata = json.load(f)

        total_frames = len(jsondata)
        text_label = f"Reading streamlines data ({total_frames})"
        total_points = 0
        j = 0
        self.speed_min = inf
        self.speed_max = 0.0
        texture_line_start = 0
        texture_line_maxlength = 1024
        texture_lines_padding = 2
        print("First point:",jsondata[0]["Points"][0])
        self.speeds = []
        with unreal.ScopedSlowTask(total_frames, text_label) as slow_task:
            slow_task.make_dialog(True)
            for i in range(len(jsondata)):
                if slow_task.should_cancel():         # True if the user has pressed Cancel in the UI
                    return
                slow_task.enter_progress_frame(1,f"Reading streamlines data {i}/{total_frames}")
#                fpath = filepaths[i]
#                my_data = np.genfromtxt(fpath, delimiter=',')
                points = jsondata[i]["Points"]
                length = np.min([len(points),texture_line_maxlength])
                if length > texture_line_maxlength - texture_line_start:
                    # Start to fill new line in texture if the streamline does not fit on the current line
                    j += 1
                    texture_line_start = 0
#                print(i,my_data.shape,length)
#                self.imdata[i,0:length] = my_data[:length,0:3] # Position
#                if inclusion_test(self,my_data):
                for k in range(length):
                    p = points[k]
                    self.imdata[j,texture_line_start+k] = [p["x"],p["y"],p["z"]]
                    self.imdata_vel[j,texture_line_start+k] = [p["vx"],p["vy"],p["vz"]]
                    self.speeds.append(norm(np.array(self.imdata_vel[j,texture_line_start+k])))
                    speed = norm(np.array(self.imdata_vel[j,texture_line_start+k]))
                    if speed > self.speed_max:
                        self.speed_max = speed
                    if speed < self.speed_min:
                        self.speed_min = speed
                total_points += length
                texture_line_start += length + texture_lines_padding
            
        self.num_lines = total_frames
        self.data_lines_per_row = total_frames / j

        print( "Streamlines read. Total number of lines, points: ", j, total_points)

        self.pos_mins = np.nanmin(self.imdata[:,:],axis=(0,1))
        self.pos_maxs = np.nanmax(self.imdata[:,:],axis=(0,1))
        self.vel_mins = np.nanmin(self.imdata_vel[:,:],axis=(0,1))
        self.vel_maxs = np.nanmax(self.imdata_vel[:,:],axis=(0,1))

        # np.save(Config.getTempFilepath("streamlines_source"),self.imdata)
        # np.save(Config.getTempFilepath("streamlines_vel_source"),self.imdata_vel)

    def saveMetaData(self,clear_old=False):
        print("Saving metadata: ",clear_old)
        self.lines_type = "StreamLines"
        self.texture1 = f"Texture2D'/Game/DTCC/DataImages/streamlines_hi_{self.label}.streamlines_hi_{self.label}'"
        self.textureCombDivider = 100.0
        self.texture2 = f"Texture2D'/Game/DTCC/DataImages/streamlines_lo_{self.label}.streamlines_lo_{self.label}'"
        self.texture3 = f"Texture2D'/Game/DTCC/DataImages/streamlines_vel_{self.label}.streamlines_vel_{self.label}'"
        self.data_table = f"DataTable'/Game/DTCC/StreamlineData/{self.label}_DT.{self.label}_DT'"
        LinesData.saveMetaData(self,clear_old)

        # out_csv_path = unreal.Paths.project_content_dir()+"DTCC/DataImages/LineDataTextureSources.csv"
        # import_task = unreal.AssetImportTask()

        # import_task.filename = out_csv_path
        # unreal.log("Trying to import: " + out_csv_path)
        # import_task.destination_path = "/Game/DTCC/DataImages"
        # import_task.destination_name = "LineDataTextureSources_DT"
        # import_task.automated = True
        # import_task.replace_existing = True
        # import_task.save = True

        # unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
        #     [import_task]
        # )


    def generateTexture(self):
        if not self.imdata.any():
            return

        with unreal.ScopedSlowTask(5, "Generating textures") as slow_task:
            slow_task.make_dialog(True)

            slow_task.enter_progress_frame(1,"Initiating")
            print("Range: ", self.pos_mins, self.pos_maxs, self.pos_maxs-self.pos_mins )
            # Normalize data
            self.imdata = (self.imdata-self.pos_mins)/(self.pos_maxs-self.pos_mins)
            self.imdata_vel = (self.imdata_vel-self.vel_mins)/(self.vel_maxs-self.vel_mins)

            imdata8k = np.zeros((8192,2048,3), dtype=np.float32)
            imdata8k[:,0:1024,:] = self.imdata[:8192,:,:]
            imdata8k[:,1024:,:] = self.imdata[8192:,:,:]

            imdata8k_vel = np.zeros((8192,2048,3), dtype=np.float32)
            imdata8k_vel[:,0:1024,:] = self.imdata_vel[:8192,:,:]
            imdata8k_vel[:,1024:,:] = self.imdata_vel[8192:,:,:]
            imdata8k_vel = np.nan_to_num(imdata8k_vel)
            self.imdata8k_vel = imdata8k_vel

            # Split into two textures to get better precision.
            # Currently no support in unreal to load 32-bit textures from images, including from EXR.
            imdata8k = imdata8k * 100 # + 0.0001 # epsilon - unclear if this is needed/beneficial
            imdata8k = np.nan_to_num(imdata8k)
            self.imdata8k = imdata8k

            imdata8k_lo = np.copy(imdata8k)
            imdata8k_hi = np.copy(imdata8k)

            np.modf(imdata8k,imdata8k_lo,imdata8k_hi)
            imdata8k_hi = imdata8k_hi/100

            import array
            
            def saveStreamlineImage(out_image_path3,imdata8k):
                # im = pimg.fromarray(imdata2k)
                # im.save(out_image_path3)

                HEADER = OpenEXR.Header(2048,8192)
                # HEADER = OpenEXR.Header(1024,1024)
                # Setting channels as below makes OpenEXR crash!
                # Channels should default to FLOAT so should be able to do without.
                # Difference may be some (missing?) range information?
                # HEADER["channels"] = {
                #     "R": Imath.PixelType(Imath.PixelType.FLOAT),
                #     "G": Imath.PixelType(Imath.PixelType.FLOAT),
                #     "B": Imath.PixelType(Imath.PixelType.FLOAT)
                # }
                print("Converting data to bytes")
                Rs = imdata8k[:,:,0].tobytes()
                Gs = imdata8k[:,:,1].tobytes()
                Bs = imdata8k[:,:,2].tobytes()
            #    HEADER["compression"] = Imath.Compression.RLE_COMPRESSION
                print("Creating EXR", out_image_path3)
                exr = OpenEXR.OutputFile(out_image_path3.as_posix(), HEADER)
                print("Writing EXR")
                exr.writePixels({'R': Rs, 'G': Gs, 'B': Bs})
                exr.close()

                # writer = png.Writer(width=imdata8k.shape[1], height=imdata8k.shape[0], bitdepth=16, greyscale=False)
                # iimg = (imdata8k*65535).astype(np.uint16).reshape(-1,imdata8k.shape[1]*imdata8k.shape[2])
                # with open(out_image_path3,"wb") as f:
                #     writer.write(f,iimg)

            filePath = pathlib.Path(unreal.Paths.project_saved_dir()).resolve() / DTCC_HUB_SAVED_FOLDER_NAME
            slow_task.enter_progress_frame(1,"Saving HI texture")
            out_image_path_hi = filePath / f"streamlines_hi_{self.label}.exr"
            saveStreamlineImage(out_image_path_hi,imdata8k_hi)
            slow_task.enter_progress_frame(1,"Saving LO texture")
            out_image_path_lo = filePath / f"streamlines_lo_{self.label}.exr"
            saveStreamlineImage(out_image_path_lo,imdata8k_lo)
            slow_task.enter_progress_frame(1,"Saving VEL texture")
            out_image_path_vel = filePath / f"streamlines_vel_{self.label}.exr"
            saveStreamlineImage(out_image_path_vel,imdata8k_vel)

            slow_task.enter_progress_frame(1,"Importing textures")

            importDataTexture(out_image_path_hi,f"streamlines_hi_{self.label}")
            importDataTexture(out_image_path_lo,f"streamlines_lo_{self.label}")
            importDataTexture(out_image_path_vel,f"streamlines_vel_{self.label}")

def debugData():
    # Read back EXR to check precision

    def readEXR(out_image_path):
        f = OpenEXR.InputFile(out_image_path)

        channels = ['R', 'G', 'B']
        channelData = dict()
        
        def getChannel(c):
            C = f.channel(c, Imath.PixelType(Imath.PixelType.FLOAT))
            C = np.fromstring(C, dtype=np.float32)
            C = np.reshape(C, (8192,2048))
            
            return C

        imdata8k = np.zeros((8192,2048,3), dtype=np.float32)

        imdata8k[:,:,0] = getChannel("R")
        imdata8k[:,:,1] = getChannel("G")
        imdata8k[:,:,2] = getChannel("B")

        return imdata8k

    out_image_path_vel = unreal.Paths.project_content_dir()+"DTCC/DataImages/streamlines_vel.exr"
    imdata1 = readEXR(out_image_path_vel)

    plt.subplot(1,2,1)
    for i in range(15,20):
        plt.plot(imdata1[i,:1024,0],imdata1[i,:1024,2],marker="*")

    plt.subplot(1,2,2)
    for i in range(15,20):
        plt.plot(np.arange(1024),np.linalg.norm(imdata1[i,:1024,:],axis=1),marker="*")

    plt.show()

# import ipdb

# if __name__ == "__main__":
#     print("HI!")
# #    data = generate_Streamlines_texture()

#     # f = openNETCDF("cas_base_200_test_3d.001")
#     generate_VELOCITY_video("cas_base_200_test_3d.001")
#     generate_DATA_video("cas_base_200_test_3d.001")
#     saveRanges()
# #    vel = get_NC_velocity_at_time(f,20)

#     # u_layer = f.variables["u"]
# #    id = data[-2]
    
#     # ipdb.set_trace()