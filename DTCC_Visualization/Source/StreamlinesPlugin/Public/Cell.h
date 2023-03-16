// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Cell.generated.h"


USTRUCT(BlueprintType)
struct FCell
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category="Cell")
	int32 X_Index;

	UPROPERTY(EditAnywhere, Category = "Cell")
	int32 Y_Index;

	UPROPERTY(EditAnywhere, Category = "Cell")
	int32 Z_Index;

	FCell()
	{
		X_Index = Y_Index = Z_Index = 0;
	}

	/*FCell(int32 x_index, int32 y_index, int32 z_index) 
		: X_Index{x_index}, Y_Index{y_index}, Z_Index{z_index}
	{}*/
	/*FCell(int32 x) : X_Index{ x }
	{

	}*/

	FCell(int32 x_index, int32 y_index, int32 z_index)
	{
		X_Index=x_index;
		Y_Index=y_index;
		Z_Index=z_index;
	}

	friend bool operator==(const FCell& lhs, const FCell& rhs)
	{
		return lhs.X_Index==rhs.X_Index && lhs.Y_Index==rhs.Y_Index && lhs.Z_Index==rhs.Z_Index;
	}

	friend bool operator!=(const FCell& lhs, const FCell& rhs)
	{
		return !(lhs==rhs);
	}

	/*FORCEINLINE uint32 GetTypeHash(const FHashMeIfYouCan& Thing)
	{
		uint32 Hash = FCrc::MemCrc32(&Thing, sizeof(FHashMeIfYouCan));
		return Hash;
	}*/

	friend uint32 GetTypeHash(const FCell& Cell)
	{
		return FCrc::MemCrc32(&Cell,sizeof(FCell));
	}
};

/**
 * 
 */
UCLASS()
class STREAMLINESPLUGIN_API UCellLibrary : public UObject
{
	GENERATED_BODY()


public:

	UFUNCTION(BlueprintPure, Category = "Cell", meta = (Keywords = "construct build", NativeMakeFunc))
	static FCell MakeCell(int32 X_Index, int32 Y_Index, int32 Z_Index);

	UFUNCTION(BlueprintPure, Category="Cell", meta = (NativeBreakFunc))
	static void BreakCell(FCell Cell, int32& X_Index, int32& Y_Index, int32& Z_Index);

	UFUNCTION(BlueprintPure, Category="Cell")
	static void WorldLocationToCellIndices(const FVector& WorldLocation, float CellSize, int32& X_Index,int32& Y_Index, int32& Z_Index);

	UFUNCTION(BlueprintPure, Category = "Cell")
	static void WorldLocationToCell(const FVector& WorldLocation, float CellSize, FCell& Cell);

	UFUNCTION(BlueprintPure, CAtegory="Cell")
	static FVector CellIndicesToWorldLocation(int32 X_Index, int32 Y_Index, int32 Z_Index, float CellSize);

	UFUNCTION(BlueprintPure, Category = "Cell")
	static FVector CellToWorldLocation(FCell Cell, float CellSize);

};
