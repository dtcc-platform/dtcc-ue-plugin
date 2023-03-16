import matplotlib
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.image as mpimg


import PIL.Image as pimg
import OpenEXR, Imath

import netCDF4

import json
import unreal

from dtcc.config import Config

class VariableScaler:
    """Scale data to 0-1 range. Input is netcdf variable layer."""
    def __init__(self, variable):
        data = variable[:]
        self.fillValue = variable._FillValue
        data[data==self.fillValue] = np.nan
        self.min = np.nanmin(data)
        self.max = np.nanmax(data)
        self.unit = variable.units
        self.range = self.max - self.min
        self.name = variable.name

        print("VariableScaler:", variable.name, self.min, self.max, self.range)
        if self.range == 0:
            # Hack to allow for division by range
            self.range = 1
    
    def apply(self,layer):
        data = layer.data
        mask = data==self.fillValue
        # data[mask] = 0.0 # Set to zero here so it's zero after restoration
        print(np.max(data))
        data = (data - self.min) / self.range
        print(np.max(data))
        data[mask] = 0.0 # Set to zero here to match range 0-1
#        print("NOTE: Setting fill values to 0.0!")
        return data

class NCData:
    
    def __init__(self, filename=False,label=None):
        self.varscales = dict()
        self.ncfile = False
        self.label = label

        if filename:
            self.openNCFile(filename)

    def openNCFile(self,filename=True):
        """
        filename: without .nc extension. Defaults to last_data_file from config if set to True.
        """
        Config.load()
        # if filename == True:
        #     filename = Config.config_data["last_data_file"]
        # Remove .nc (if present)
        # if filename[-3:] == ".nc":
        #     filename = filename[:-3]
        self.filename = filename
        if self.label == None:
            self.label = filename
#        f = netCDF4.Dataset(Config.config_data["external_data_path"] + "/" + filename + ".nc", "r")
        f = netCDF4.Dataset(filename, "r")
#        unreal.EditorDialog.show_message("DTCC","NetCDF file loaded...",unreal.AppMsgType.OK)
        self.ncfile = f

        self.resolution = self.ncfile.variables["x"].shape[0]

    def saveRanges(self):
        with open(Config.getPath("DataTextures/data_ranges.csv"),"w") as frange:
            frange.write("# Variable,Min,Max\n")
            for v in self.varscales.values():
                frange.write(f"{v.name},{v.min},{v.max}\n")

    def get_NC_variable_at_time(self,variable="kc_NO2", time=0):
        """
        time: Set to None if there is no time dimension.
        """
        if not self.ncfile:
            return

        ta = np.zeros((self.resolution * 8, self.resolution * 8))

        if not (variable in self.varscales):
            self.varscales[variable] = VariableScaler(self.ncfile.variables[variable])
        scale = self.varscales[variable]
        
        for height in range(0, 64):
            if time == None:
                kc_layer = self.ncfile.variables[variable][height]
            else:
                kc_layer = self.ncfile.variables[variable][time, height]
            x = height % 8
            y = height // 8
            ta[x * self.resolution : (x + 1) * self.resolution, y * self.resolution : (y + 1) * self.resolution] = kc_layer.data

        mask = ta==self.ncfile.variables[variable]._FillValue
        ta[mask] = np.nan
        tmin = np.nanmin(ta)
        tmax = np.nanmax(ta)
        self.varscales[variable].min = tmin
        self.varscales[variable].max = tmax
        ta = ta - tmin
        ta = ta / (tmax - tmin)
        ta[mask] = 0.0       
        return ta

    def get_NC_velocity_at_time(self, time=1):
        ta = np.zeros((self.resolution * 8, self.resolution * 8, 3))

        ta[:,:,0] = self.get_NC_variable_at_time("u",time)
        ta[:,:,1] = self.get_NC_variable_at_time("v",time)
        ta[:,:,2] = self.get_NC_variable_at_time("w",time)

        return ta


    def generate_DATA_texture(self, variable="kc_NO2", time=1):
        ta = self.get_NC_variable_at_time(variable, time)

        tt = ta == -9999
        ta[tt] = 0

        texname = "volumetric_data_"+self.label+"_"+variable[3:]
        out_image_path3 = Config.getContentDataPath(texname+".exr")
        self.saveEXRImage(out_image_path3,ta)

        self.importSavedTexture(out_image_path3,texname)

        print(
            "Exported "
            + variable
            + " data for time "
            + str(time)
            + " to: "
            + out_image_path3
            + " (data max: "
            + str(np.max(ta))
            + ")"
        )

        return out_image_path3


    def generate_WINDVEL_texture(self, time=0):
        ta = self.get_NC_velocity_at_time(time)

        tt = ta == -9999
        ta[tt] = 0

        texname = "volumetric_data_"+self.label+"_WIND"
        out_image_path3 = Config.getContentDataPath(texname+".exr")
        self.saveEXRImage(out_image_path3,ta)

        self.importSavedTexture(out_image_path3,texname)

        print(
            "Exported wind velocity data for time "
            + str(time)
            + " to: "
            + out_image_path3
            + " (data max: "
            + str(np.max(ta))
            + ")"
        )

        return out_image_path3

    def importSavedTexture(self,img_path,texname):
        import_task = unreal.AssetImportTask()

        import_task.filename = img_path
        unreal.log("Trying to import: " + img_path)
    #    import_task.destination_path = unreal.Paths.project_content_dir() + "Generated"
        import_task.destination_path = "/Game/DTCC/DataImages"
        import_task.destination_name = texname
        import_task.automated = True
        import_task.replace_existing = True
        import_task.save = True

        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
            [import_task]
        )

    def saveEXRImage(self,out_image_path3,imdata):
        # im = pimg.fromarray(imdata2k)
        # im.save(out_image_path3)

        imdata = imdata.astype(np.float32)

        HEADER = OpenEXR.Header(4096,4096)
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
        if (len(imdata.shape)==2):
            Rs = imdata.tobytes()
        else:
            Rs = imdata[:,:,0].tobytes()
            Gs = imdata[:,:,1].tobytes()
            Bs = imdata[:,:,2].tobytes()
    #    HEADER["compression"] = Imath.Compression.RLE_COMPRESSION
        print("Creating EXR")
        exr = OpenEXR.OutputFile(out_image_path3, HEADER)
        print("Writing EXR")
        if (len(imdata.shape)==2):
            exr.writePixels({'R': Rs, 'G': Rs, 'B': Rs})
        else:
            exr.writePixels({'R': Rs, 'G': Gs, 'B': Bs})
        exr.close()

        # writer = png.Writer(width=imdata8k.shape[1], height=imdata8k.shape[0], bitdepth=16, greyscale=False)
        # iimg = (imdata8k*65535).astype(np.uint16).reshape(-1,imdata8k.shape[1]*imdata8k.shape[2])
        # with open(out_image_path3,"wb") as f:
        #     writer.write(f,iimg)

""" 
import skvideo.io


def generate_DATA_video(data_filename,video_filename="data_texture_video.mp4", varkeys=["kc_NO","kc_NO2","kc_PM10"]):

    print("Generating data video")
    print("Variable keys:",varkeys)
    print("Output filename:",video_filename)

    max_time = 36
    frames_per_time = 1
    # nodata = np.zeros((max_time*frames_per_time,200*8,200*8,3))
    # nodata = nodata.astype(np.uint8)

    nc_file = openNETCDF(data_filename)

    writer = skvideo.io.FFmpegWriter(
        "cached_images/" + video_filename,
        outputdict={"-vcodec": "libx264", "-pix_fmt": "yuv420p", "-b:v": "300000000"},
        # outputdict={"-vcodec": "libxvid", "-pix_fmt": "yuv420p", "-b:v": "300000000"},
        # outputdict={"-vcodec": "libxvid", "-pix_fmt": "yuv444p10le", "-b:v": "300000000"},
    )

    framedata = np.zeros((200 * 8, 200 * 8, 3))
    framedata.astype(np.uint8)

    for time in range(0, max_time):
        print("Getting data for time ", time)
        framedata[:, :, 0] = get_NC_variable_at_time(nc_file, variable=varkeys[0], time=time)*255
        framedata[:, :, 1] = get_NC_variable_at_time(nc_file, variable=varkeys[1], time=time)*255
        framedata[:, :, 2] = get_NC_variable_at_time(nc_file, variable=varkeys[2], time=time)*255
        print("Adding frames for time ", time)
        for i in range(frames_per_time):
            writer.writeFrame(framedata)

    print("Saving video")
    writer.close()

    return video_filename


def generate_VELOCITY_video(filename):

    print("Vel vid")
    out_video_fname = generate_DATA_video(filename,video_filename="velocity_texture_video.mp4",varkeys=["u","v","w"])
    return out_video_fname
 """
