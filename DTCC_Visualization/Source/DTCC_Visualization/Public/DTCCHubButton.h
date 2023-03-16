// Based on MRTK Hub from Microsoft Corporation. Licensed under the MIT License.

#pragma once

#include "CoreMinimal.h"
#include "LevelEditor.h"

/**
 * The toolbar button for opening the MRTK Hub window.
 */
class FDTCCHubButton
{
public:
	FDTCCHubButton();
	~FDTCCHubButton();

private:
	void RegisterMenus();
	void OpenWindow();
	void OnLevelChanged(UWorld* World, EMapChangeType MapChangeType);
	TSharedRef<class SDockTab> SpawnTab(const class FSpawnTabArgs& SpawnTabArgs);

	TSharedPtr<FUICommandList> CommandList;
	static const FName TabId;
};
