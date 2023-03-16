// Fill out your copyright notice in the Description page of Project Settings.


#include "VCProceduralMeshComponent.h"
#include "DrawDebugHelpers.h"

void UVCProceduralMeshComponent::FreeResources()
{
	CurrentMeshSection = 0;
	Vertices.Empty();
	Triangles.Empty();
	VertexColors.Empty();
}

void UVCProceduralMeshComponent::BeginPlay()
{
	Super::BeginPlay();

	CurrentMeshSection = 0;
}

void UVCProceduralMeshComponent::AddVertex(const FVector& Vertex)
{
	Vertices.Add(Vertex);
}

void UVCProceduralMeshComponent::AddVertices(const TArray<FVector>& VerticesToAdd)
{
	for (int32 i = 0; i < VerticesToAdd.Num(); i++)
	{
		this->Vertices.Add(VerticesToAdd[i]);
	}
}

void UVCProceduralMeshComponent::Init()
{
	ClearAllMeshSections();
	FreeResources();
}

int32 UVCProceduralMeshComponent::GetVertexNum() const
{
	return Vertices.Num();
}

int32 UVCProceduralMeshComponent::GetLastSection() const
{
	return CurrentMeshSection;
}

void UVCProceduralMeshComponent::AddTriangle(int32 VertexA, int32 VertexB, int32 VertexC)
{
	Triangles.Add(VertexA);
	Triangles.Add(VertexB);
	Triangles.Add(VertexC);
}

void UVCProceduralMeshComponent::GenerateMesh(bool bCreateCollision)
{
	CreateMeshSection(CurrentMeshSection, Vertices, Triangles, TArray<FVector>(), TArray<FVector2D>(), TArray<FColor>(), TArray<FProcMeshTangent>(), false);
	//CurrentMeshSection++;
}

void UVCProceduralMeshComponent::DrawDebugVertices(FLinearColor DebugVertexColor)
{
	FVector OwnerWorldLocation = GetOwner()->GetActorLocation();
	for (int32 VertexIndex = 0; VertexIndex < Vertices.Num(); VertexIndex++)
	{
		DrawDebugPoint(GetWorld(), Vertices[VertexIndex] + OwnerWorldLocation, 15.f, DebugVertexColor.ToFColor(true), true, 15.f);
	}
}

void UVCProceduralMeshComponent::PaintProceduralMesh(const TArray<FLinearColor>& NewVertexColors)
{
	VertexColors = NewVertexColors;
	UpdateMeshSection_LinearColor(CurrentMeshSection, Vertices, TArray<FVector>(), TArray<FVector2D>(), NewVertexColors, TArray<FProcMeshTangent>());
}

FVector UVCProceduralMeshComponent::GetVertexLocation(int32 VertexId) const
{
	return (VertexId >= 0 && VertexId < Vertices.Num()) ? Vertices[VertexId] : FVector(0.f);
}

