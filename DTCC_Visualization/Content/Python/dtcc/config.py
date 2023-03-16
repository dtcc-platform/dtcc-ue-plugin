import unreal
import json
import os

class Config:
    config_data = {}
    _loaded = False

    def getPath(subpath = ""):
        return  unreal.Paths.project_dir()+"DTCC/"+subpath
    
    def getContentDataPath(subpath = ""):
        return  unreal.Paths.project_content_dir()+"DTCC/DataImages/"+subpath

    def getTempFilepath(filename):
        dtcc_temp_folder = unreal.Paths.project_intermediate_dir()+"DTCC"
        if not os.path.exists(dtcc_temp_folder):
            os.makedirs(dtcc_temp_folder)
        return  dtcc_temp_folder + "/" + filename
    
    def save():
        pass
        # with open(Config.getPath("dtcc_config.json"),"w") as f:
        #     json.dump(Config.config_data,f,indent=4)

    def load(force=False):
        pass
        # if Config._loaded and not force:
        #     return
        # with open(Config.getPath("dtcc_config.json"),"r") as f:
        #     Config.config_data = json.load(f)
        # Config._loaded = True
