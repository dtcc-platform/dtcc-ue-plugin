// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Engine/DataTable.h"
#include "Streamline.generated.h"


class UStaticMeshComponent;

USTRUCT(BlueprintType)
struct FVCStreamlinePoint : public FTableRowBase
{
	GENERATED_USTRUCT_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	float x;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	float y;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	float z;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	float vx;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	float vy;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	float vz;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	float p;

	FVCStreamlinePoint()
	{
		x = y = z = vx = vy = vz = p = 0;
	}

	FVCStreamlinePoint(const FVCStreamlinePoint& OtherPoint)
	{
		x = OtherPoint.x;
		y = OtherPoint.y;
		z = OtherPoint.z;
		vx = OtherPoint.vx;
		vy = OtherPoint.vy;
		vz = OtherPoint.vz;
		p = OtherPoint.p;
	}

	FVCStreamlinePoint(float X, float Y, float Z, float V0, float V1, float V2, float P)
	{
		x = X; vx = V0;
		y = Y;	vy = V1;
		z = Z;	vz = V2;
		p = P;
	}

	FORCEINLINE FVector GetWorldLocation() const
	{
		return FVector(x, y, z);
	}

	FVector GetLocation() const
	{
		return FVector(x, y, z);
	}

	FVector GetVelocity() const
	{
		return FVector(vx, vy, vz);
	}

	FORCEINLINE void SetLocation(float X, float Y, float Z)
	{
		x = X;
		y = Y;
		z = Z;
	}

	FORCEINLINE void SetVelocity(float X, float Y, float Z)
	{
		vx = X;
		vy = Y;
		vz = Z;
	}

	FORCEINLINE FString ToString() const
	{
		return "Location:" + GetLocation().ToString() + " Velocity:" + GetVelocity().ToString();
	}

	friend bool operator==(const FVCStreamlinePoint& lhs, const FVCStreamlinePoint& rhs)
	{
		return lhs.GetLocation().Equals(rhs.GetLocation()) && lhs.GetVelocity().Equals(rhs.GetVelocity());
	}

	friend bool operator!=(const FVCStreamlinePoint& lhs, const FVCStreamlinePoint& rhs)
	{
		return !(lhs==rhs);
	}

	friend uint32 GetTypeHash(const FVCStreamlinePoint& StreamlinePoint)
	{
		return FCrc::MemCrc32(&StreamlinePoint, sizeof(FVCStreamlinePoint));
	}

	/*friend bool operator==(const FCell& lhs, const FCell& rhs)
	{
		return lhs.X_Index == rhs.X_Index && lhs.Y_Index == rhs.Y_Index && lhs.Z_Index == rhs.Z_Index;
	}

	friend bool operator!=(const FCell& lhs, const FCell& rhs)
	{
		return !(lhs == rhs);
	}*/
};

USTRUCT(BlueprintType)
struct FVCStreamline : public FTableRowBase
{
	GENERATED_USTRUCT_BODY()

public:

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	FString StreamlineName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	TArray<FVCStreamlinePoint> Points;

	FVCStreamline()
	{
		StreamlineName = FString("N/A");
	}

	FVCStreamline(FString StreamlineName)
	{
		this->StreamlineName = StreamlineName;
	}

	FVCStreamline(FString StreamlineName, const TArray<FVCStreamlinePoint>& Points)
	{
		for (int32 i = 0; i < Points.Num(); i++)
		{
			this->Points.Add(Points[i]);
		}
	}

	int32 AddPoint(const FVCStreamlinePoint& PointToAdd)
	{
		return(Points.Add(PointToAdd));
	}
};

//TODO FIXES:
//1 - Remove parsing from the good old Virtual City days
//2 - Explore batch spawning in a single mesh to reduce draw calls to 1
//3 - Should probably find a way to allow more colormaps instead of jet for coloring (maybe pack the velocity in RGB channels and the pressure in A for each Vertex to use it on the material code?)

UCLASS(Transient)
class STREAMLINESPLUGIN_API AStreamline : public AActor
{
	GENERATED_BODY()

private:

	FVector StreamlineForwardVector;

	FVector GenerateRotatableVector(const FVector& StartingPoint) const;

	/**
	 * Generates vertices & triangles around a given point
	 * @param CenterPoint - the center point around which we're going to generate vertices
	 */
	void GenerateVerticesAroundPoint(const FVector& CenterPoint);

	void GenerateVerticesAroundStartingPoint(const FVector& CenterPoint);

public:

	// Sets default values for this actor's properties
	AStreamline();

protected:

	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	class UVCProceduralMeshComponent* VCProceduralMeshComponent;

	UPROPERTY(EditAnywhere, Category="StaticStreamlines")
	float StreamlineThickness/* = 15.f*/;

	UPROPERTY(EditAnywhere, Category="StaticStreamlines")
	int32 CapVertices = 12;

	UPROPERTY(EditDefaultsOnly, Category="StaticStreamlines")
	bool bActivateDebug = false;

	//Debug only
	UPROPERTY(EditDefaultsOnly, Category="StaticStreamlines")
	float DebugPointThickness;

	/**
	 * A material that accepts a "VertexColors" param
	 */
	UPROPERTY(EditDefaultsOnly, Category="StaticStreamlines")
	class UMaterialInterface* VertexMaterial;

	UPROPERTY(VisibleAnywhere, Category="StaticStreamlines")
	class UArrowComponent* ArrowComp;

	/* The file name of the streamline that this cylinder belongs to. Used for debug only */
	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	FString StreamlineFileName;

	/**
	 * Editor-friendly debug values
	 */
	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category="StaticStreamlines")
	FVCStreamline Streamline;

public:

	FORCEINLINE FVCStreamline GetStreamline() const { return Streamline; }

	UFUNCTION(BlueprintCallable, Category = "StaticStreamlines")
	void PaintStreamline(const float& MinVelocity, const float& MaxVelocity, bool bDebug=false);

	/**
	 * To be used in python side
	 */
	UFUNCTION(BlueprintCallable, Category="StaticStreamlines")
	void AddStreamlinePoint(const FVector& WorldLocation, const FVector& Velocity);

	UFUNCTION(BlueprintCallable, Category="StaticStreamlines")
	void GenerateMesh(float NewStreamlineThickness, int32 NewCapVertices);

	UFUNCTION(BlueprintCallable, Category="StaticStreamlines")
	void SetStreamlineFileName(FString FileName);

	UFUNCTION(BlueprintCallable, Category="StaticStreamlines")
	void RegenerateStreamline(float NewStreamlineThickness=15.f, int32 NewCapVertices=12);

	UFUNCTION(BlueprintCallable, Category="StaticStreamlines")
	static AStreamline* SpawnStreamline(UObject* WorldContext, FString StreamlineName, TArray<FVCStreamlinePoint> StreamlinePoints, float NewStreamlineThickness, int32 NewCapVertices);
};