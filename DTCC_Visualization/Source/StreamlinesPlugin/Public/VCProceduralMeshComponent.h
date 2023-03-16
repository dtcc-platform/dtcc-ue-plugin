// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ProceduralMeshComponent.h"
#include "VCProceduralMeshComponent.generated.h"

/**
 * An extended version of the official UE4 Procedural Mesh Component
 * Example usage:

 * Assume we want to create a rectangle mesh with a height of 300 and width of 200 units respectively. Let us
 * declare vertices A,B,C and D as the mesh vertices
 * A-------B
 * |	   |
 * |	   |
 * D-------C
 * To do so, we need to add 4 vertices containing the LOCAL location (based on the component's owner) of each vertex
 * So the provided coordinates for each vertex are the following (following the UE4 coordinate system):
 * A : X = -200, Y = 0, Z = 300
 * B : X =  200, Y = 0, Z = 300
 * C : X =  200, Y = 0, Z =-300
 * D : X = -200, Y = 0, Z =-300
 * After adding the above vertices to the "Vertices" array we need to call the AddTriangle function to generate the
 * triangles for the mesh. To do so, we need to provide the INDEX of each vertex in a counter-clockwise fashion
 * (otherwise the mesh will be generated in the opposite looking way)
 * Since the rectangle consists of 2 triangles we need to call the AddTriangle function using the following parameters:
 * AddTriangle(0,3,2) and AddTriangle(2,3,0) assuming we added the vertices from A to D.
 * When we have generated the required vertices and triangles call the GenerateMesh function to create the mesh.
 * A Blueprint example for the mentioned example exists in the BP_ProcMeshTest inside the Blueprints->TestingBlueprints folder
 */

UCLASS(meta = (BlueprintSpawnableComponent))
class STREAMLINESPLUGIN_API UVCProceduralMeshComponent : public UProceduralMeshComponent
{
	GENERATED_BODY()

private:

	/* Vertex colors of the generated mesh*/
	TArray<FLinearColor> VertexColors;

	/* Vertices of the generated mesh */
	TArray<FVector> Vertices;

	/* Triangles of the generated mesh */
	TArray<int32> Triangles;

	/*bool bHasFinishedVertices;
	bool bHasFinishedMeshFaces;
	bool bHasGeneratedMesh;
	bool bHasGeneratedVertexColors;*/

	/* The mesh section index in case of multiple mesh sections */
	int32 CurrentMeshSection;

	/* Empties the data containers to free resources */
	void FreeResources();

public:

	virtual void BeginPlay() override;

	/**
	 * Adds a single vertex to the vertices array
	 */
	UFUNCTION(BlueprintCallable, Category = "ProceduralMesh")
		void AddVertex(const FVector& Vertex);

	/**
	 * Adds an array of vertices to the vertices array
	 */
	UFUNCTION(BlueprintCallable, Category = "ProceduralMesh")
		void AddVertices(const TArray<FVector>& VerticesToAdd);

	/**
	 * Clears all mesh sections and erases any previously stored data
	 */
	UFUNCTION(BlueprintCallable, Category = "ProceduralMesh")
		void Init();

	/**
	 * Returns the total count of vertices of this mesh
	 */
	UFUNCTION(BlueprintCallable, Category = "ProceduralMesh")
	int32 GetVertexNum() const;

	/**
	 * Returns the last mesh section index
	 */
	int32 GetLastSection() const;

	/**
	 * Creates a triangle between the provided Vertices array (check on top of the class declaration for an example)
	 * @param VertexA - the 1st vertex that will be included in the triangle
	 * @param VertexB - the 2nd vertex
	 * @param VertexC - the 3rd vertex
	 */
	UFUNCTION(BlueprintCallable, Category = "ProceduralMesh")
		void AddTriangle(int32 VertexA, int32 VertexB, int32 VertexC);

	/**
	 * Creates a mesh connecting the provided vertices with the given triangles
	 * See the comments right before the class declaration for an example
	 */
	UFUNCTION(BlueprintCallable, Category = "ProceduralMesh")
		void GenerateMesh(bool bCreateCollision = false);

	/**
	 * Draws debug points on top of each vertex
	 * param DebugVertexColor - the color to draw for each vertex
	 */
	UFUNCTION(BlueprintCallable, Category = "ProceduralMesh")
		void DrawDebugVertices(FLinearColor DebugVertexColor);

	/**
	 * Paints the meshe's vertices
	 * param NewVertexColors - the new color for each vertex
	 */
	UFUNCTION(BlueprintCallable, Category = "ProceduralMesh")
		void PaintProceduralMesh(const TArray<FLinearColor>& NewVertexColors);

	UFUNCTION(BlueprintPure, Category = "ProceduralMesh")
		FVector GetVertexLocation(int32 VertexId) const;

	UFUNCTION(BlueprintPure, Category = "ProceduralMesh")
		TArray<FLinearColor> GetVertexColors() const { return VertexColors; }

};
