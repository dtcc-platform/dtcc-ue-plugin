import sys
import unreal;

STREAMLINE_ACTOR_TAG='StreamlineActor'

MIN_VELOCITY=0
MAX_VELOCITY=1

#unreal.log_warning('Printing py sys argvs')
#unreal.log(sys.argv[0])
#unreal.log(sys.argv[1])
#unreal.log(sys.argv[2])

def paintNewVelocities(min,max):
    levelActors = unreal.EditorLevelLibrary.get_all_level_actors()
    for i in levelActors:
        if STREAMLINE_ACTOR_TAG in i.tags:
            i.paint_streamline((float)(min),(float)(max))
            #unreal.log('Updated values!')

def updateMinMaxVelocities():
    if len(sys.argv)>=2:
        global MIN_VELOCITY
        global MAX_VELOCITY
        MIN_VELOCITY=(float)(sys.argv[1])
        MAX_VELOCITY=(float)(sys.argv[2])

if __name__ == '__main__':
    updateMinMaxVelocities()
    #unreal.log_warning("Parsed min max vel:")
    #unreal.log_warning(MIN_VELOCITY)
    #unreal.log_warning(MAX_VELOCITY)
    paintNewVelocities(MIN_VELOCITY,MAX_VELOCITY)
    


