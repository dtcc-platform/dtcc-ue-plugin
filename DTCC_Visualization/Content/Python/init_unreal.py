import unreal

def hello_unreal():
    unreal.log_warning("DTCC Visualization plugin: Python scripts initiated.")

hello_unreal()

import sys
import os

sys.path.append(os.path.abspath(unreal.Paths.project_plugins_dir() + "DTCC_Visualization/Content/Python/.thirdparty"))

from importlib import reload