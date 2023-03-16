// Fill out your copyright notice in the Description page of Project Settings.


#include "Streamline.h"
#include "VCProceduralMeshComponent.h"
#include "Components/ArrowComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "DrawDebugHelpers.h"

FVector AStreamline::GenerateRotatableVector(const FVector& CenterPoint) const
{
	float Y = FMath::Cos(360.0 / CapVertices) * StreamlineThickness;
	float Z = FMath::Sin(360.0 / CapVertices) * StreamlineThickness;
	//A = FVector(CenterPoint.X, Y, Z)
	//O = Center Point
	FVector VectorToRotate = FVector(CenterPoint.X, Y, Z) - CenterPoint;
	VectorToRotate.Normalize();
	return VectorToRotate;
}

void AStreamline::GenerateVerticesAroundPoint(const FVector& CenterPoint)
{
	if (!VCProceduralMeshComponent) return;

	TArray<FVector> GeneratedVertices;

	FVector VectorToRotate = GenerateRotatableVector(FVector(0.f));

	for (int32 i = 0; i < CapVertices; i++)
	{
		VectorToRotate = VectorToRotate.RotateAngleAxis(360 / CapVertices, StreamlineForwardVector);

		if (bActivateDebug)
		{
			//DrawDebugPoint(GetWorld(), VectorToRotate * StreamlineThickness + CenterPoint, DebugPointThickness, FColor::Green, true);
		}
		
		GeneratedVertices.Add(VectorToRotate * StreamlineThickness + CenterPoint - GetActorLocation());
	}

	VCProceduralMeshComponent->AddVertices(GeneratedVertices);

	int32 CurrentMeshSection = VCProceduralMeshComponent->GetVertexNum() / CapVertices;

	for (int32 i = 2; i <= CapVertices; i++)
	{
		//Number is corresponding to the vertex ID. For more info check the documentation!
		//14=CapVertices*CurrentMeshSection+i
		//13= CapVertices*CurrentMeshSection + i - 1
		//2=CapVertices*(CurrentMeshSection-1)+i
		//1=CapVertices*(CurrentMeshSection-1)+i-1
		int32 v14 = CapVertices * CurrentMeshSection + i;
		int32 v13 = CapVertices * CurrentMeshSection + i - 1;
		int32 v2 = CapVertices * (CurrentMeshSection - 1) + i;
		int32 v1 = CapVertices * (CurrentMeshSection - 1) + i - 1;
		VCProceduralMeshComponent->AddTriangle(v1, v13, v2);
		VCProceduralMeshComponent->AddTriangle(v2, v13, v14);
	}

	//12=CapVertices*CurrentMeshSection
	//24=CapVertices*(CurrentMeshSection+1)
	int32 v12 = CapVertices * CurrentMeshSection;
	int32 v24 = CapVertices * (CurrentMeshSection + 1);
	int32 v1 = CapVertices * (CurrentMeshSection - 1) + 1;
	int32 v13 = CapVertices * CurrentMeshSection + 1;
	VCProceduralMeshComponent->AddTriangle(v12, v24, v1);
	VCProceduralMeshComponent->AddTriangle(v1, v24, v13);	
}

void AStreamline::GenerateVerticesAroundStartingPoint(const FVector& CenterPoint)
{
	TArray<FVector> GeneratedVertices;
	GeneratedVertices.Add(CenterPoint - GetActorLocation()); //ignore the actor's location we need relative location for procedural mesh vertices
	//FVector VectorToRotate = GenerateRotatableVector(CenterPoint);
	FVector VectorToRotate = GenerateRotatableVector(FVector(0.f));
	//GLog->Log("Streamline thickness on vertex gen:"+FString::SanitizeFloat(StreamlineThickness));
	for (int32 i = 0; i < CapVertices; i++)
	{
		VectorToRotate = VectorToRotate.RotateAngleAxis(360 / CapVertices, StreamlineForwardVector);

		if (bActivateDebug)
		{
			//DrawDebugPoint(GetWorld(), VectorToRotate * StreamlineThickness + CenterPoint, DebugPointThickness, FColor::Green, true);
			DrawDebugLine(GetWorld(), CenterPoint, CenterPoint + VectorToRotate * StreamlineThickness, FColor::Red, true, 55555.f, 5, 1.f);
		}

		GeneratedVertices.Add(VectorToRotate * StreamlineThickness); // Ignore the center point since relative location is needed
	}

	//Adding cap vertices
	VCProceduralMeshComponent->AddVertices(GeneratedVertices);

	//Generating cap triangles
	VCProceduralMeshComponent->AddTriangle(0, CapVertices, 1);
	for (int32 i = 2; i <= CapVertices; i++)
	{
		VCProceduralMeshComponent->AddTriangle(0, i - 1, i); //counter clockwise
	}
}

// Sets default values
AStreamline::AStreamline()
{
	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = false;

	ArrowComp = CreateDefaultSubobject<UArrowComponent>(FName("RootComp"));
	if (ArrowComp) 
	{
		ArrowComp->SetVisibility(bActivateDebug);
	}
	SetRootComponent(ArrowComp);

	VCProceduralMeshComponent = CreateDefaultSubobject<UVCProceduralMeshComponent>(FName("VCProcMeshComp"));
	VCProceduralMeshComponent->SetupAttachment(GetRootComponent());

	/*StreamlineThickness = 15.f;*/
	CapVertices = 12;
	DebugPointThickness = 1.f;

}

// Called when the game starts or when spawned
void AStreamline::BeginPlay()
{
	Super::BeginPlay();

	if (ArrowComp)
	{
		ArrowComp->SetCastShadow(false);
	}

	if (VCProceduralMeshComponent)
	{
		FAttachmentTransformRules AttachmentRules = FAttachmentTransformRules(EAttachmentRule::SnapToTarget, true);
		VCProceduralMeshComponent->AttachToComponent(GetRootComponent(), AttachmentRules);
	}
}

void AStreamline::PaintStreamline(const float& MinVelocity, const float& MaxVelocity, bool bDebug)
{
	if (!VCProceduralMeshComponent) return;
	ensure(MaxVelocity>0);

	int32 Vertices = VCProceduralMeshComponent->GetVertexNum();
	TArray<FLinearColor> Colors;

	//Add unitialized 1st color; will change it later
	Colors.Add(FLinearColor::White);
	GLog->Log("Starting to paint streamline...");
	for (int32 i = 0; i < Streamline.Points.Num(); i++)
	{
		FVector Velocity = Streamline.Points[i].GetVelocity();
		float Speed = Velocity.Size();
		float NSpeed = (Speed - MinVelocity) / (MaxVelocity - MinVelocity);
		FLinearColor Color = FLinearColor(FVector(NSpeed, 0.f, 0.f));
		//GLog->Log("Vel of point #"+FString::FromInt(i) + " - " + Velocity.ToCompactString() +" Magnitude:" + FString::SanitizeFloat(Speed) + " Normalized Speed:"+FString::SanitizeFloat(NSpeed) + " | Linear color:"+Color.ToString());
		
		if (bDebug)
		{
			GLog->Log("Normalized speed:" + FString::SanitizeFloat(NSpeed) + ", speed:" + FString::SanitizeFloat(Speed));
		}
		for (int32 Vertex = 0; Vertex < CapVertices; Vertex++)
		{
			Colors.Add(Color);
		}

	}

	if (Streamline.Points.Num() > 1)
	{
		//Adjust 1st vertex (part of initial point) to match the other colors
		Colors[0] = Colors[1];

		FLinearColor ColorToAdd = Colors.Last();
		//For the last cap
		for (int32 i = 0; i < CapVertices; i++)
		{
			Colors.Add(ColorToAdd);
		}
	}

	VCProceduralMeshComponent->PaintProceduralMesh(Colors);
}

void AStreamline::AddStreamlinePoint(const FVector& WorldLocation, const FVector& Velocity)
{
	Streamline.AddPoint(FVCStreamlinePoint(WorldLocation.X,WorldLocation.Y,WorldLocation.Z,Velocity.X,Velocity.Y,Velocity.Z,0.f));
	//GLog->Log("Added streamline point:" + Streamline.Points.Last().ToString());
}

void AStreamline::GenerateMesh(float NewStreamlineThickness, int32 NewCapVertices)
{
	ensure(Streamline.Points.IsValidIndex(0));
	if(Streamline.Points.Num()<=1) return;
	//Determine "forward vector" of the streamline, meaning the direction that the streamline is expanding
	//This will help us connect triangles later on
	StreamlineThickness=NewStreamlineThickness;

	//GLog->Log("Generate mesh with thickness:"+FString::SanitizeFloat(NewStreamlineThickness));
	CapVertices=NewCapVertices;

	StreamlineForwardVector = Streamline.Points[1].GetWorldLocation() - Streamline.Points[0].GetWorldLocation();
	StreamlineForwardVector.Normalize();

	SetActorLocation(Streamline.Points[0].GetLocation());
	GenerateVerticesAroundStartingPoint(Streamline.Points[0].GetLocation());

	for (int32 i = 0; i < Streamline.Points.Num(); i++)
	{
		GenerateVerticesAroundPoint(Streamline.Points[i].GetLocation());
	}
	VCProceduralMeshComponent->SetCastShadow(false);
	VCProceduralMeshComponent->GenerateMesh();
}

AStreamline* AStreamline::SpawnStreamline(UObject* WorldContext, FString StreamlineName, TArray<FVCStreamlinePoint> StreamlinePoints, float NewStreamlineThickness, int32 NewCapVertices)
{
	ensure(WorldContext);

	UWorld* WorldRef = WorldContext->GetWorld();
	
	if (WorldRef)
	{
		AStreamline* StreamlineActor = WorldRef->SpawnActor<AStreamline>(AStreamline::StaticClass());

		if (StreamlineActor)
		{
			StreamlineActor->StreamlineFileName = StreamlineName;
			StreamlineActor->Streamline = FVCStreamline(StreamlineName,StreamlinePoints);
			StreamlineActor->GenerateMesh(NewStreamlineThickness,NewCapVertices);
			return StreamlineActor;
		}
		return nullptr;
	}
	else
	{
		GLog->Log("Invalid world ref!");
	}
	return nullptr;
}

//void AStreamline::PaintStreamlines(UObject* WorldContext, float MaxVelocity)
//{
//	ensure(WorldContext);
//
//	UWorld* World = WorldContext->GetWorld();
//	if (World)
//	{
//		TArray<AActor*> Streamlines;
//		UGameplayStatics::GetAllActorsOfClass(WorldContext,AStreamline::StaticClass(),Streamlines);
//		for (int32 i = 0; i < Streamlines.Num(); i++)
//		{
//			AStreamline* Streamline = Cast<AStreamline>(Streamlines[i]);
//			if (Streamline)
//			{
//				TArray<FVCStreamlinePoint> StreamlinePoints = Streamline->Streamline.Points;
//				for (int32 j = 0; j < StreamlinePoints.Num(); j++)
//				{
//					FVector PointVelocity = StreamlinePoints[j].GetVelocity();
//					FVector NormVelocity = PointVelocity;
//					NormVelocity.X/=MaxVelocity;
//					NormVelocity.Y/=MaxVelocity;
//					NormVelocity.Z/=MaxVelocity;
//					//TODO: Add colors based on this norm vel!
//				}
//			}
//		}
//	}
//}

void AStreamline::SetStreamlineFileName(FString FileName)
{
	StreamlineFileName = FileName;
}

void AStreamline::RegenerateStreamline(float NewStreamlineThickness/*=15.f*/, int32 NewCapVertices/*=12*/)
{
	if (VCProceduralMeshComponent)
	{
		VCProceduralMeshComponent->Init();
		GenerateMesh(NewStreamlineThickness, NewCapVertices);
	}
}
