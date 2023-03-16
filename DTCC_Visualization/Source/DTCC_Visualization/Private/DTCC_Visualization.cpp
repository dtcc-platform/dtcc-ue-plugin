// Copyright Epic Games, Inc. All Rights Reserved.

#include "DTCC_Visualization.h"
#include "DTCCHubButton.h"
#include "LevelEditor.h"

#define LOCTEXT_NAMESPACE "FDTCC_VisualizationModule"

void FDTCC_VisualizationModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module

	ToolbarButton = new FDTCCHubButton();

}

void FDTCC_VisualizationModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.
	delete ToolbarButton;
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FDTCC_VisualizationModule, DTCC_Visualization)