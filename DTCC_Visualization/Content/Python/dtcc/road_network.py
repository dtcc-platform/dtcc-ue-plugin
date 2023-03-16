import unreal

from dtcc.config import Config

import dtcc.util
from dtcc.lines_data import LinesData

import numpy as np
import matplotlib.pyplot as plt
import OpenEXR, Imath


import json

class RoadNetwork(LinesData):

    def __init__(self, filename=False):
        LinesData.__init__(self)
        """ Set filename to True to read default data at once """
        self.source_data_path = False

        if filename:
            self.readData(filename)

    def readData(self,filename=True):
        """
        filename: Defaults to road_network_source from config if set to True.
        """
        Config.load()
        # if filename == True:
        #     filename = Config.config_data["road_network_source"]
        self.source_data_path = filename

        data_path = Config.getPath("SourceData/") + self.source_data_path
        unreal.log_warning("Reading data from: " + data_path)

        self.data = []
        with open(data_path, "r") as f:
            self.data=json.load(f)

        unreal.log_warning("Data read: " + str(self.data))

    def processData(self):

        vertices = np.array(self.data["RoadNetwork"]["Vertices"])
        vertices = vertices.reshape(vertices.size//2,2)
        edges = np.array(self.data["RoadNetwork"]["Edges"])

        new_vertices = []

        last_edge_vertex = -1
        num_lines = 0
        for e in edges:
            if (e[0] == last_edge_vertex):
                new_vertices.append(vertices[e[1]])
            else:
                new_vertices.append([np.nan,np.nan])
                new_vertices.append([np.nan,np.nan])
                new_vertices.append([np.nan,np.nan])
                new_vertices.append([np.nan,np.nan])
                new_vertices.append([np.nan,np.nan])
                new_vertices.append(vertices[e[0]])
                new_vertices.append(vertices[e[1]])
                num_lines += 1
            last_edge_vertex = e[1]

        vertices = np.zeros((len(new_vertices),2))
        for i in range(0,len(new_vertices)):
            vertices[i,:] = new_vertices[i]

        vmin = np.nanmin(vertices,axis=0)
        vmax = np.nanmax(vertices,axis=0)
        vrange = vmax - vmin

        self.vertices = (vertices - vmin) / vrange

        unreal.log_warning(num_lines)

        dlines = int(np.ceil(self.vertices.shape[0]/250)) # Lines with length 250 required in a 256x256 image to fit data
        
        reshape_verts = np.zeros((250*dlines,3))
        reshape_verts[:self.vertices.shape[0],:2] = self.vertices

        self.data_image = np.zeros((256,256,3),dtype=np.float32)

        self.data_image[:dlines,:250,:] = reshape_verts.reshape((dlines,250,3))

        self.pos_mins = [vmin[0],vmin[1],0.0]
        self.pos_maxs = [vmax[0],vmax[1],0.0]

        self.num_lines = num_lines

    def saveMetaData(self):
        self.lines_type = "RoadNetwork"
        self.texture1 = "Texture2D'/Game/DTCC/DataImages/RoadNetwork.RoadNetwork'"
        self.textureCombDivider = 0.0
        self.texture2 = ""
        LinesData.saveMetaData(self)

    def test(self):
        image_path = unreal.Paths.project_content_dir() + "Generated/test_matplotlib.png"

        fig = dtcc.util.setup_matplotlib_figure(dpi=200)
        fig.clf()

        self.readData()
        self.processData()
        
        y = self.vertices[:,1]
        plt.plot(self.vertices[:,0],y,"-",linewidth=1,color="red")
        plt.ylabel('some numbers')
        plt.title('Road network test')
        # plt.show()

        fig.savefig(image_path)

        dtcc.util.import_figure_texture(texname="road_network")

    def generateDataTexture(self):

        def saveRoadsImage(out_image_path3,imdata):

            nan_mask = np.isnan(imdata)
            imdata[nan_mask] = 0.0
            HEADER = OpenEXR.Header(256,256)
            print("Converting data to bytes")
            Rs = imdata[:,:,0].tobytes()
            Gs = imdata[:,:,1].tobytes()
            Bs = imdata[:,:,2].tobytes()
            print("Creating EXR")
            exr = OpenEXR.OutputFile(out_image_path3, HEADER)
            print("Writing EXR")
            exr.writePixels({'R': Rs, 'G': Gs, 'B': Bs})
            exr.close()

        out_image_path3 = unreal.Paths.project_content_dir()+"DTCC/DataImages/RoadNetwork.exr"
        saveRoadsImage(out_image_path3,self.data_image)

        dtcc.util.importDataTexture(out_image_path3,"RoadNetwork")
