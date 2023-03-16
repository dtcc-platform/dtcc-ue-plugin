import unreal

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import OpenEXR, Imath

def np2unreal(vec0):
    vec = np.zeros([3])
    vec[:vec0.size] = vec0
    return {"X": vec[0], "Y": vec[1], "Z": vec[2]}

def setup_matplotlib_figure(dpi=200,aspect_ratio=1.0):
    # matplotlib.use('Agg')

    # Based on/inspired by/stolen from https://github.com/20tab/UnrealEnginePython/blob/master/tutorials/PlottingGraphsWithMatplotlibAndUnrealEnginePython.md
    # set the Agg renderer as we do not need any toolkit

    width = 10
    height = width * aspect_ratio

    fig = plt.figure(1)
    fig.set_dpi(dpi)
    # FIXME: Does not work as expected
    fig.set_figwidth(width)
    fig.set_figheight(height)

    return fig

def import_figure_texture(img_path="",texname="MatplotlibGeneratedTextureTest"):
    import_task = unreal.AssetImportTask()

    if img_path == "":
        unreal.log_warning("Empty img_path for import figure")
        return
    import_task.filename = img_path
    unreal.log("Trying to import: " + img_path)
#    import_task.destination_path = unreal.Paths.project_content_dir() + "Generated"
    import_task.destination_path = "/Game/Generated"
    import_task.destination_name = texname
    import_task.automated = True
    import_task.replace_existing = True
    import_task.save = True

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
        [import_task]
    )


def importDataTexture(img_path="",texname="DataTexture"):
    import_task = unreal.AssetImportTask()

    if img_path == "":
        unreal.log_warning("Empty img_path for import figure")
        return
    img_path = img_path.as_posix()
    unreal.log("Trying to import: " + img_path)
    import_task.filename = img_path
#    import_task.destination_path = unreal.Paths.project_content_dir() + "Generated"
    import_task.destination_path = "/Game/DTCC/DataImages"
    import_task.destination_name = texname
    import_task.automated = True
    import_task.replace_existing = True
    import_task.save = True

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
        [import_task]
    )

def generate_ColorMap_texture(colormap):
    ta = np.zeros((256, 256))

    for x in range(28, 228):
        ta[x, :] = np.ones((1, 256)) * (x - 28)

    ta[0:10, :] = 0
    ta[228:256, :] = 200

    out_image_path3 = "colormap_" + colormap + ".png"
    mpimg.imsave("cached_images/" + out_image_path3, ta, cmap=colormap)

    return out_image_path3