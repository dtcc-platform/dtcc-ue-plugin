# Usage

## Overview

DTCC Visualization Plugin consists of two modules:

    DTCC_Visualization
    StreamlinesPlugin

The DTCC Visualization module is the basis of the plugin. It contains all
the BP related systems, such Niagara Particle Systems, Data Tables,
In-Editor Widgets and activates the StreamlinesPlugin when loaded up.

The StreamlinesPlugin is a C++ plugin used for procedural mesh creation
for Streamline Data. It contains 3 C++ classes that work together
to create an efficient mesh generation in a level inside Unreal Engine.

### Importing Data - Required Dependencies

Before importing any data you have to install the required python dependencies.
In case you want to use the plugin just for visualization purposes without importing any data you can skip this step.
The plugin contains a .bat file that will download and install everything for you.

In case you downloaded the plugin via the UE Marketplace, close your project and run the following file:

    [Your-UE-Installation-Directory]->Engine->Plugins->DTCC_Visualization->setup_python.bat

In case you have installed the plugin to a local project instead go to:

    [Your-UE-Project-Directory]->Plugins->DTCC_Visualization->setup_python.bat

The .bat file will make sure to install all the required dependencies for importing data.

### Importing Data

Once you have installed the required dependencies you can import data
by following the steps described below:

* Go to Window->DTCC Hub
* Select the import tab

To import Streamline data from the import menu:
* Select Streamlines on the import category
* Click on either 'Import streamlines from HDF5' or 'Import streamlines from CSV files. By selecting all the required files in this step the plugin will create an intermediate .json file in project's saved folder
* On 2.Configure settings (Preprocess) category adjust the settings based on your data
* On 3.Process for visualization click the 'Prepare data for visualization'. By clicking this button the plugin will apply the preprocess settings to the intermediate .json file and will convert everything to UE native types that the visualization systems will use.

To import Volumetric data from the import menu:
* Select Volumetric data on the import category
* More details about this are upcoming.

### Visualizing results - Streamlines

Once your have imported data in your project, select the 'Visualizations' tab on the DTCC Hub.
The plugin requires a StreamlinesActor to exist in the level. If the actor doesn't exist the plugin
will prompt you to spawn one by clicking the 'Add Streamlines to Level' button.
Once the actor exists, you can adjust the settings displayed in the widget to match your visualization requirements.

>**Note:**In case you don't want to use the DTCC Hub, you can select the StreamlinesActor in your level and modify its properties on the Editor's Details Panel.

### Visualizing results - Volumetric Data
Upcoming.