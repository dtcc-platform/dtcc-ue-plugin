// Fill out your copyright notice in the Description page of Project Settings.


#include "StreamlineSegmentGenerator.h"
#include "DrawDebugHelpers.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/DataTable.h"
#include "Streamline.h"

TMap<FCell,FCellDataWrapper> UStreamlineSegmentGenerator::CellMap = TMap<FCell,FCellDataWrapper>();

bool UStreamlineSegmentGenerator::NeedToRegenerateStreamlineSegments(const TArray<FCell>& NewCells)
{
	if(PreviousGenerationCells.Num() != NewCells.Num() || PreviousGenerationCells.Num()==0) return true;

	for (int32 i = 0; i < PreviousGenerationCells.Num(); i++)
	{
		if (!NewCells.Contains(PreviousGenerationCells[i]))
		{
			return true;
		}
	}

	return false;
}

TArray<FCell> UStreamlineSegmentGenerator::IdentifyNearbyCells() const
{
	TArray<FCell> NearbyCells;
	

	FCell CurrentCell;
//	UCellLibrary::WorldLocationToCell(GetOwner()->GetActorLocation(),AssignedCellSize,CurrentCell);
	UCellLibrary::WorldLocationToCell(DrawCenterPosition, AssignedCellSize, CurrentCell);

	//X axis
	for (int32 x = -NearbyCellCount; x <= NearbyCellCount; x++)
	{
		int32 pivotX = CurrentCell.X_Index + x;

		for (int32 y = -NearbyCellCount; y <= NearbyCellCount; y++)
		{
			int32 pivotY = CurrentCell.Y_Index + y;

			for (int32 z = -NearbyCellCount; z <= NearbyCellCount; z++)
			{
				int32 pivotZ = CurrentCell.Z_Index + z;

				FCell NewCell = FCell(pivotX,pivotY,pivotZ);
				NearbyCells.Add(NewCell);
			}
		}
	}
	return NearbyCells;
}

void UStreamlineSegmentGenerator::DestroyPreviousStreamlines()
{
	UWorld* WorldRef = GetOwner()->GetWorld();
	TArray<AActor*> PreviousStreamlines;

	UGameplayStatics::GetAllActorsOfClass(WorldRef, AStreamline::StaticClass(), PreviousStreamlines);

	for (int32 i = PreviousStreamlines.Num() - 1; i >= 0; i--)
	{
		if (PreviousStreamlines[i])
		{
			PreviousStreamlines[i]->Destroy();
		}
	}
}

TMap<FString, FStreamlinePointsWrapper> UStreamlineSegmentGenerator::CreateStreamlinesMap()
{
	TArray<FCell> NearbyCells = IdentifyNearbyCells();

	TMap<FString, FStreamlinePointsWrapper> StreamlinesMap;

	for (int32 i = 0; i < NearbyCells.Num(); i++)
	{
		FCellDataWrapper* CellData = CellMap.Find(NearbyCells[i]);
		//If cell exists
		if (CellData)
		{
			for (int32 PIndex = 0; PIndex < CellData->StreamlinePoints.Num(); PIndex++)
			{
				FString StreamlineName = CellData->PointStreamlineName[PIndex];
				FVCStreamlinePoint CurrentStreamlinePoint = CellData->StreamlinePoints[PIndex];
				int32 OriginalIndex = CellData->StreamlinePointsIndex[PIndex];

				FStreamlinePointsWrapper* PointsWrapper = StreamlinesMap.Find(StreamlineName);
				if (PointsWrapper)
				{
					PointsWrapper->Points.Add(CurrentStreamlinePoint);
					PointsWrapper->PointsOriginalIndex.Add(OriginalIndex);
				}
				else
				{
					FStreamlinePointsWrapper NewPointWrapper;
					NewPointWrapper.Points.Add(CurrentStreamlinePoint);
					NewPointWrapper.PointsOriginalIndex.Add(OriginalIndex);
					StreamlinesMap.Add(StreamlineName,NewPointWrapper);
				}
			}
		}
	}
	return StreamlinesMap;
}

// Sets default values for this component's properties
UStreamlineSegmentGenerator::UStreamlineSegmentGenerator()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;

	// ...
}

void UStreamlineSegmentGenerator::AssignStreamlinesToCells()
{
	if (!StreamlinesDT) return;
	
	TArray<FVCStreamline*> StreamlinesArray;
	FString ContextStr;
	StreamlinesDT->GetAllRows(ContextStr,StreamlinesArray);
	for (int32 i = 0; i < StreamlinesArray.Num(); i++)
	{
		FVCStreamline* Streamline = StreamlinesArray[i];
		if (Streamline)
		{
			TArray<FVCStreamlinePoint> Points = Streamline->Points;

			//Storing extended data
			for (int32 PIndex = 0; PIndex < Points.Num(); PIndex++)
			{
				FVCStreamlinePoint StreamlinePoint = Points[PIndex];
				FCell AssignedCell;
				UCellLibrary::WorldLocationToCell(StreamlinePoint.GetLocation(),AssignedCellSize,AssignedCell);

				
				FCellDataWrapper* CellData = CellMap.Find(AssignedCell);
				if (CellData)
				{
					//We have already defined a cell so add the required details to it
					CellData->StreamlinePoints.Add(StreamlinePoint);
					CellData->StreamlinePointsIndex.Add(PIndex);
					CellData->PointStreamlineName.Add(Streamline->StreamlineName);
				}
				else
				{
					//This is the first time we have data for this cell so define it
					//And initialize it with the required data
					FCellDataWrapper NewCellData;
					NewCellData.StreamlinePoints.Add(StreamlinePoint);
					NewCellData.StreamlinePointsIndex.Add(PIndex);
					NewCellData.PointStreamlineName.Add(Streamline->StreamlineName);
					CellMap.Add(AssignedCell,NewCellData);
				}
			}
		}
	}
}

void UStreamlineSegmentGenerator::SpawnMergedStreamlineSegments(const TArray<FCell>& NearbyCells)
{
	DestroyPreviousStreamlines();
	UWorld* WorldRef = GetOwner()->GetWorld();

	PreviousGenerationCells = NearbyCells; //Update last cells
	TMap<FString,FStreamlinePointsWrapper> StreamlinesMap = CreateStreamlinesMap();
	//GLog->Log("StreamlinesMap num:"+FString::FromInt(StreamlinesMap.Num()));
	for (auto& It : StreamlinesMap)
	{
		FString StreamlineName = It.Key;
		FStreamlinePointsWrapper PointsWrapper = It.Value;
		TArray<FVCStreamlinePoint> StreamlinePoints = PointsWrapper.SortLocations();
		AStreamline::SpawnStreamline(WorldRef,StreamlineName,StreamlinePoints,StreamlineThickness,CapVertices);
	}
}

void UStreamlineSegmentGenerator::SpawnMergedStreamlineSegments_BP()
{
	TArray<FCell> CurrentNearbyCells = IdentifyNearbyCells();
	SpawnMergedStreamlineSegments(CurrentNearbyCells);
}

void UStreamlineSegmentGenerator::DynamicStreamlineSpawn()
{
	TArray<FCell> CurrentNearbyCells = IdentifyNearbyCells();
	if (NeedToRegenerateStreamlineSegments(CurrentNearbyCells))
	{
		SpawnMergedStreamlineSegments(CurrentNearbyCells);
	}
}

	
TArray<FVCStreamlinePoint> FStreamlinePointsWrapper::SortLocations() const
{
	TArray<FVCStreamlinePoint> SortedPoints;

	TArray<FVCStreamlinePoint> PointsCopy = Points;
	TArray<int32> PointsIndexCopy = PointsOriginalIndex;
	while (PointsIndexCopy.Num() > 0)
	{
		int32 PivotIndex = PointsIndexCopy[0];
		int32 FoundIndex = 0;

		for (int32 i = 1; i < PointsIndexCopy.Num(); i++)
		{
			if (PointsIndexCopy[i] < PivotIndex)
			{
				PivotIndex = PointsIndexCopy[i];
				FoundIndex=i;
			}
		}
		
		SortedPoints.Add(PointsCopy[FoundIndex]);

		PointsIndexCopy.RemoveAt(FoundIndex);
		PointsCopy.RemoveAt(FoundIndex);
	}

	return SortedPoints;
}
