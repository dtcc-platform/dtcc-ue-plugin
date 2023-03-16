# Script for dataprep of NETCDF file for CityAirSim

# 3 functions are expected: initializeDataprep, prepareData and finalizeDataprep
from dtcc.config import Config

data_info = []

def initializeDataprep():
    global data_info

    data_info = []

def prepareData(ncdata):
    global data_info
    print("Preparing data for CityAirSim")

    variables = ["NO2", "PM10"]

    for v in variables:
        print(" .. " + v + " volumetric data")
        ncdata.generate_DATA_texture(variable="kc_"+v,time=None)
        data_info.append( { "ScenarioLabel": ncdata.label, "VariableName": v, "DataMinValue": ncdata.varscales["kc_"+v].min, "DataMaxValue": ncdata.varscales["kc_"+v].max, "SourceFile": ncdata.filename, "DataUnit": ncdata.varscales["kc_"+v].unit})

    # WIND
    print(" .. WIND")
    ncdata.generate_WINDVEL_texture(time=None)
    data_info.append( { "ScenarioLabel": ncdata.label, "VariableName": "WIND",
        "DataMinValue": "x="+str(ncdata.varscales["u"].min)+", y="+str(ncdata.varscales["v"].min)+", z="+str(ncdata.varscales["w"].min)+"",
        "DataMaxValue": "x="+str(ncdata.varscales["u"].max)+", y="+str(ncdata.varscales["v"].max)+", z="+str(ncdata.varscales["w"].max)+"",
        "SourceFile": ncdata.filename, "DataUnit": ncdata.varscales["u"].unit})

def finalizeDataprep():
    global data_info

    with open(Config.getContentDataPath("DataTextureSources.csv"),"w") as frange:
        frange.write("---,SourceFile,ScenarioLabel,VariableName,DataMinValue,DataMaxValue,DataUnit,DataTexture\n")
        for di in data_info:
            rowname = di["ScenarioLabel"] + di["VariableName"]
            frange.write(rowname)
            for k in ["SourceFile","ScenarioLabel","VariableName","DataMinValue","DataMaxValue","DataUnit"]:
                frange.write(",\""+str(di[k])+"\"")
            texname = "volumetric_data_"+di["ScenarioLabel"]+"_"+di["VariableName"]
            texname = texname.replace(".","_") # Match Unreal name coding
            frange.write(",\"Texture2D'/Game/DTCC/DataImages/"+texname+"."+texname+"'\"")
            frange.write("\n")


