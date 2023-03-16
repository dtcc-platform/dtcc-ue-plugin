// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Cell.h"
#include "Streamline.h"
#include "StreamlineSegmentGenerator.generated.h"


class UDataTable;

//Algorithm:
//Step 1 -> Place streamline segments in cells
//Step 2 -> Identify nearby cells
//Step 3 -> Spawn streamline segments in nearby cells
//Step 4 -> Optimize step 3 (merge segments in 1 streamline)

//Step 4 algorithm:
//Gather all segments to be spawned
//Save all points belonging in same streamline in a container
//Determine the "flow" of the streamline (start from closest point to further)
//Spawn a single streamline for all the points of a streamline



USTRUCT(BlueprintType)
struct FCellDataWrapper
{
	GENERATED_BODY()

	/*UPROPERTY(EditAnywhere, Category = "CellDataWrapper")
	TArray<FStreamlineSegment> Segments;*/

	/** 
	 * The corresponding name of streamline for each segment.
	 * This array's length equals to Segments array length */
	UPROPERTY(EditAnywhere, Category="CellDataWrapper")
	TArray<FString> SegmentsOwningStreamlineName;

	UPROPERTY(EditAnywhere, Category = "CellDataWrapper")
	TArray<FVCStreamlinePoint> StreamlinePoints;

	UPROPERTY(EditAnywhere, Category = "CellDataWrapper")
	TArray<FString> PointStreamlineName;

	/** Original index from data */
	UPROPERTY(EditAnywhere, Category = "CellDataWrapper")
	TArray<int32> StreamlinePointsIndex;


	friend uint32 GetTypeHash(const FCellDataWrapper& CellDataWrapper)
	{
		return FCrc::MemCrc32(&CellDataWrapper, sizeof(FCellDataWrapper));
	}

};

/**
 * Acts as a wrapper to store both points from simulations and the original index of each point
 * The two arrays are synced
 */
struct FStreamlinePointsWrapper
{
public:

	TArray<FVCStreamlinePoint> Points;
	TArray<int32> PointsOriginalIndex;

	/**
	 * Sorts locations based on the PointsOriginalIndex array
	 * Basically, if for a single streamline we have points 1,4 and 2
	 * The function returns an array of points with their correct sequence, meaning 1,2 and 4
	 * This is needed since we're storing data into maps therefore their correct order is lost
	 */
	TArray<FVCStreamlinePoint> SortLocations() const;
};

UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class STREAMLINESPLUGIN_API UStreamlineSegmentGenerator : public UActorComponent
{
	GENERATED_BODY()

private:

	/**
	 * Checks if previous generation cells are different compared to given cells
	 */
	bool NeedToRegenerateStreamlineSegments(const TArray<FCell>& NewCells);

	/**
	 * Reference to know if current nearby cells are different compared to the last update.
	 * If so, we need to re-generate streamlines
	 */
	TArray<FCell> PreviousGenerationCells;

	/**
	 * Calculates nearby cells to the owners location based on AssignedCellSize
	 */
	TArray<FCell> IdentifyNearbyCells() const;

	void DestroyPreviousStreamlines();

	/**
	 * Identifies nearby cells
	 * Creates a map containing the streamline names and all their points with their original index
	 * The original index is later used to know the logical order which the points of the streamlines
	 * have to be connected
	 */
	TMap<FString, FStreamlinePointsWrapper> CreateStreamlinesMap();


public:	
	// Sets default values for this component's properties
	UStreamlineSegmentGenerator();

public:	

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="StreamlineSegmentGenerator")
	UDataTable* StreamlinesDT;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "StreamlineSegmentGenerator")
	float AssignedCellSize=1500.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "StreamlineSegmentGenerator")
	int32 NearbyCellCount=5;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "StreamlineSegmentGenerator")
	FVector DrawCenterPosition = FVector(0.0, 0.0, 0.0);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "StreamlineSegmentGenerator")
		float StreamlineThickness/* = 15.f*/;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "StreamlineSegmentGenerator")
		int32 CapVertices = 12;

	/**
	 * Contains the cells that were generated from the assigned streamlines dt
	 * The cells are calculated based on the AssignedCellSize and the NearbyCellCount
	 */
	static TMap<FCell,FCellDataWrapper> CellMap;

	UFUNCTION(BlueprintCallable, CallInEditor, Category="StreamlineSegmentGenerator")
	void AssignStreamlinesToCells();

	void SpawnMergedStreamlineSegments(const TArray<FCell>& NearbyCells);

	/** 
	 * BP Equivalent to SpawnMergedStreamlineSegments
	 * Omits any checks to see if we really need to update the spawned streamlines
	 */
	UFUNCTION(CallInEditor, Category = "StreamlineSegmentGenerator", meta=(DisplayName="Spawn Streamline Segments"))
	void SpawnMergedStreamlineSegments_BP();

	/**
	 * Called from within DTCCHub to dynamically spawn streamline segments
	 * While user is interacting with the actor
	 */
	UFUNCTION(BlueprintCallable, Category="StreamlineSegmentGenerator")
	void DynamicStreamlineSpawn();
};
