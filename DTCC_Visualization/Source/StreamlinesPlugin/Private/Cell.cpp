// Fill out your copyright notice in the Description page of Project Settings.


#include "Cell.h"
#include "Kismet/KismetMathLibrary.h"

FCell UCellLibrary::MakeCell(int32 X_Index, int32 Y_Index, int32 Z_Index)
{
	return FCell(X_Index, Y_Index, Z_Index);
	//return FCell();
}

void UCellLibrary::BreakCell(FCell Cell, int32& X_Index, int32& Y_Index, int32& Z_Index)
{
	X_Index = Cell.X_Index;
	Y_Index = Cell.Y_Index;
	Z_Index = Cell.Z_Index;
}

void UCellLibrary::WorldLocationToCellIndices(const FVector& WorldLocation, float CellSize, int32& X_Index, int32& Y_Index, int32& Z_Index)
{
	check(CellSize!=0.0f);
	
	X_Index = UKismetMathLibrary::Round(WorldLocation.X / CellSize);
	Y_Index = UKismetMathLibrary::Round(WorldLocation.Y / CellSize);
	Z_Index = UKismetMathLibrary::Round(WorldLocation.Z / CellSize);
}

void UCellLibrary::WorldLocationToCell(const FVector& WorldLocation, float CellSize, FCell& Cell)
{
	check(CellSize!=0.f);
	Cell = FCell(UKismetMathLibrary::Round(WorldLocation.X / CellSize), UKismetMathLibrary::Round(WorldLocation.Y / CellSize), UKismetMathLibrary::Round(WorldLocation.Z / CellSize));
}

FVector UCellLibrary::CellIndicesToWorldLocation(int32 X_Index, int32 Y_Index, int32 Z_Index, float CellSize)
{
	return FVector(X_Index, Y_Index, Z_Index) * CellSize;
}

FVector UCellLibrary::CellToWorldLocation(FCell Cell, float CellSize)
{
	return FVector(Cell.X_Index,Cell.Y_Index,Cell.Z_Index) * CellSize;
}
