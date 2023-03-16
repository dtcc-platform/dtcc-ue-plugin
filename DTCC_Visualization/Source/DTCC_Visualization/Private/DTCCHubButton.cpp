// Based on MRTK Hub from Microsoft Corporation. Licensed under the MIT License.

#include "DTCCHubButton.h"

#include "DTCC_Visualization.h"
#include "ToolMenus.h"
#include "WidgetBlueprint.h"
#include "LevelEditor.h"

#include "Blueprint/UserWidget.h"
#include "Interfaces/IPluginManager.h"
#include "Styling/SlateStyle.h"
#include "Styling/SlateStyleRegistry.h"

#define LOCTEXT_NAMESPACE "DTCCHub"

class FDTCCHubButtonStyle
{
public:
	static void Register();
	static void Unregister();

	static const ISlateStyle& Get();

	static const FName StyleSetName;

private:
	static class FSlateStyleSet* ButtonStyle;
};

class FDTCCHubButtonCommands : public TCommands<FDTCCHubButtonCommands>
{
public:
	FDTCCHubButtonCommands();

	virtual void RegisterCommands() override;

	TSharedPtr<FUICommandInfo> OpenWindow;
};

const FName FDTCCHubButton::TabId = "DTCCHub";
const FName FDTCCHubButtonStyle::StyleSetName = "DTCCHubButtonStyle";
FSlateStyleSet* FDTCCHubButtonStyle::ButtonStyle = nullptr;

FDTCCHubButton::FDTCCHubButton()
{
	FDTCCHubButtonStyle::Register();
	FDTCCHubButtonCommands::Register();

	CommandList = MakeShared<FUICommandList>();
	CommandList->MapAction(
		FDTCCHubButtonCommands::Get().OpenWindow, FExecuteAction::CreateRaw(this, &FDTCCHubButton::OpenWindow), FCanExecuteAction());

	UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FDTCCHubButton::RegisterMenus));

	FGlobalTabmanager::Get()
		->RegisterNomadTabSpawner(TabId, FOnSpawnTab::CreateRaw(this, &FDTCCHubButton::SpawnTab))
		.SetDisplayName(LOCTEXT("DisplayName", "DTCC Hub"))
		.SetMenuType(ETabSpawnerMenuType::Hidden);

	FLevelEditorModule& LevelEditor = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");

	LevelEditor.OnMapChanged().AddRaw(this, &FDTCCHubButton::OnLevelChanged);
	//LevelEditor.OnMapChanged().AddUObject(this, &FDTCCHubButton::OnLevelChanged);
}

void FDTCCHubButton::OnLevelChanged(UWorld* World, EMapChangeType MapChangeType)
{
	// Recreate UI widget with reference to new world.
	UE_LOG(LogTemp, Warning, TEXT("Level Changed!"));

	auto fTab = FGlobalTabmanager::Get()->FindExistingLiveTab(TabId);
	if (fTab.IsValid()) {
		TSharedRef<SDockTab> Tab = fTab.ToSharedRef();
		Tab->RequestCloseTab();
	}
}

FDTCCHubButton::~FDTCCHubButton()
{
	FGlobalTabmanager::Get()->UnregisterNomadTabSpawner(TabId);

	UToolMenus::UnRegisterStartupCallback(this);
	UToolMenus::UnregisterOwner(this);

	FDTCCHubButtonCommands::Unregister();
	FDTCCHubButtonStyle::Unregister();
}

void FDTCCHubButton::RegisterMenus()
{
	const FToolMenuOwnerScoped ScopedOwner(this);

	UToolMenu* ToolbarMenu = UToolMenus::Get()->ExtendMenu("LevelEditor.LevelEditorToolBar");
	FToolMenuSection& ContentSection = ToolbarMenu->FindOrAddSection("Content");
	ContentSection.AddEntry(FToolMenuEntry::InitToolBarButton(FDTCCHubButtonCommands::Get().OpenWindow)).SetCommandList(CommandList);

	UToolMenu* DropdownMenu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Window");
	FToolMenuSection& WindowLayoutSection = DropdownMenu->FindOrAddSection("WindowGloba b ni       gfcg ");
	WindowLayoutSection.AddMenuEntryWithCommandList(FDTCCHubButtonCommands::Get().OpenWindow, CommandList);
}

void FDTCCHubButton::OpenWindow()
{
	FGlobalTabmanager::Get()->TryInvokeTab(TabId);
}

TSharedRef<class SDockTab> FDTCCHubButton::SpawnTab(const class FSpawnTabArgs& SpawnTabArgs)
{
	TSharedRef<SDockTab> Tab = SNew(SDockTab).TabRole(ETabRole::NomadTab);

	if (UWidgetBlueprint* WidgetBlueprint =
		Cast<UWidgetBlueprint>(StaticLoadObject(UWidgetBlueprint::StaticClass(), nullptr, TEXT("/DTCC_Visualization/UI/DTCCHub"))))
	{
		const TSubclassOf<UUserWidget> WidgetClass = static_cast<TSubclassOf<UUserWidget>>(WidgetBlueprint->GeneratedClass);
//		UUserWidget* Widget = NewObject<UUserWidget>(GetTransientPackage(), WidgetClass);
		UUserWidget* Widget = NewObject<UUserWidget>(GEditor->GetEditorWorldContext().World(), WidgetClass);
//		UUserWidget* Widget = NewObject<UUserWidget>(GEditor, WidgetClass);
		Tab->SetContent(Widget->TakeWidget());
	}
	else
	{
		const FText ErrorMessage = LOCTEXT("WidgetNotFound", "Failed to load the DTCC Hub widget.");

		Tab->SetContent(SNew(SBox).HAlign(HAlign_Center).VAlign(VAlign_Center)[SNew(STextBlock).Text(ErrorMessage)]);
//		UE_LOG(DTCC_Visualization, Error, TEXT("%s"), *ErrorMessage.ToString());
	}

	return Tab;
}

void FDTCCHubButtonStyle::Register()
{
	if (!ButtonStyle)
	{
		ButtonStyle = new FSlateStyleSet(StyleSetName);
		ButtonStyle->SetContentRoot(IPluginManager::Get().FindPlugin("DTCC_Visualization")->GetBaseDir() / TEXT("Resources"));

		const FString IconPath = ButtonStyle->RootToContentDir(TEXT("ButtonIcon"), TEXT(".png"));
		ButtonStyle->Set("DTCCHubButton.OpenWindow", new FSlateImageBrush(IconPath, { 40.0f, 40.0f }));

		FSlateStyleRegistry::RegisterSlateStyle(*ButtonStyle);
		if (FSlateApplication::IsInitialized())
		{
			FSlateApplication::Get().GetRenderer()->ReloadTextureResources();
		}
	}
}

void FDTCCHubButtonStyle::Unregister()
{
	if (ButtonStyle)
	{
		FSlateStyleRegistry::UnRegisterSlateStyle(*ButtonStyle);
		delete ButtonStyle;
	}
}

const ISlateStyle& FDTCCHubButtonStyle::Get()
{
	return *ButtonStyle;
}

FDTCCHubButtonCommands::FDTCCHubButtonCommands()
	: TCommands<FDTCCHubButtonCommands>("DTCCHubButton", LOCTEXT("DisplayName", "DTCC Hub"), NAME_None, FDTCCHubButtonStyle::StyleSetName)
{
}

void FDTCCHubButtonCommands::RegisterCommands()
{
	UI_COMMAND(OpenWindow, "DTCC Hub", "Opens the DTCC Hub", EUserInterfaceActionType::Button, FInputGesture());
}

#undef LOCTEXT_NAMESPACE
